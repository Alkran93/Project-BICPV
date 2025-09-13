"""
Rutas de la API IoT para el sistema de monitoreo de fachadas solares.
Este módulo contiene todos los endpoints para:
- Resúmenes del sistema
- Datos de sensores
- Variables ambientales
- Análisis temporal
- Detección de anomalías
"""

from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from repositories.timescale import TimescaleRepository


# Router principal
router = APIRouter(prefix="/api", tags=["IoT Solar Monitoring"])


@router.get("/overview")
async def get_system_overview():
    """Obtiene el resumen general del sistema IoT"""
    # Esta consulta obtiene un overview completo con datos recientes
    query = """
    WITH latest_data AS (
        SELECT DISTINCT ON (facade_id, sensor_id)
               facade_id, sensor_id, value, ts, device_id
        FROM measurements
        WHERE ts >= NOW() - INTERVAL '1 hour'
        ORDER BY facade_id, sensor_id, ts DESC
    )
    SELECT
        facade_id,
        COUNT(DISTINCT device_id) as total_devices,
        MAX(ts) as last_update,
        AVG(
            CASE WHEN sensor_id LIKE 'Temperatura_%' THEN value END
        ) as avg_temperature,
        MAX(CASE WHEN sensor_id = 'Irradiancia' THEN value END) as irradiancia,
        MAX(
            CASE WHEN sensor_id = 'Velocidad_Viento' THEN value END
        ) as velocidad_viento
    FROM latest_data
    GROUP BY facade_id
    ORDER BY facade_id;
    """

    try:
        async with TimescaleRepository() as db:
            result = await db.conn.fetch(query)
            return [dict(row) for row in result]
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving overview: {e!s}"
        ) from e


@router.get("/overview/{facade_id}")
async def get_facade_overview(facade_id: str):
    """Obtiene el resumen detallado de una fachada específica"""
    query = """
    WITH latest_readings AS (
        SELECT DISTINCT ON (sensor_id)
               sensor_id, value, unit, ts, device_id
        FROM measurements
        WHERE facade_id = $1 AND ts >= NOW() - INTERVAL '2 hours'
        ORDER BY sensor_id, ts DESC
    )
    SELECT
        facade_id,
        COUNT(*) as total_sensors,
        COUNT(DISTINCT device_id) as total_devices,
        MAX(ts) as last_update,
        json_agg(
            json_build_object(
                'sensor_id', sensor_id,
                'value', ROUND(value::numeric, 2),
                'unit', unit,
                'device_id', device_id,
                'timestamp', ts
            )
        ) as sensors_data
    FROM latest_readings
    CROSS JOIN (SELECT $1 as facade_id) f
    GROUP BY facade_id;
    """

    try:
        async with TimescaleRepository() as db:
            result = await db.conn.fetchrow(query, facade_id)
            if result:
                return dict(result)
            else:
                return {
                    "facade_id": facade_id,
                    "total_sensors": 0,
                    "total_devices": 0,
                    "last_update": None,
                    "sensors_data": [],
                }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving facade overview: {e!s}"
        ) from e


@router.get("/sensors/{facade_id}")
async def get_facade_sensors(facade_id: str):
    """Lista todos los sensores de una fachada específica"""
    query = """
    SELECT DISTINCT sensor_id
    FROM measurements
    WHERE facade_id = $1
    ORDER BY sensor_id;
    """

    try:
        async with TimescaleRepository() as db:
            result = await db.conn.fetch(query, facade_id)
            return [row["sensor_id"] for row in result]
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving sensors: {e!s}"
        ) from e


@router.get("/sensors/{facade_id}/details")
async def get_sensors_details(facade_id: str):
    """Obtiene detalles completos de todos los sensores de una fachada"""
    query = """
        SELECT
            sensor_id,
            COUNT(*) as total_readings,
            MIN(ts) as first_reading,
            MAX(ts) as last_reading,
            ROUND(AVG(value)::numeric, 2) as avg_value,
            ROUND(MIN(value)::numeric, 2) as min_value,
            ROUND(MAX(value)::numeric, 2) as max_value,
            array_agg(DISTINCT unit) as units,
            array_agg(DISTINCT device_id) as devices,
            CASE
                WHEN sensor_id LIKE 'Temperatura_%' THEN 'Temperatura'
                WHEN sensor_id LIKE '%_mA' THEN 'Corriente'
                WHEN sensor_id LIKE '%_W' THEN 'Potencia'
                WHEN sensor_id LIKE 'ENT_%' OR sensor_id LIKE 'SAL_%'
                     OR sensor_id LIKE 'N%_%' THEN 'Flujo'
                ELSE 'Otro'
            END as category
        FROM measurements
        WHERE facade_id = $1
        GROUP BY sensor_id, category
        ORDER BY category, sensor_id;
    """

    try:
        async with TimescaleRepository() as db:
            result = await db.conn.fetch(query, facade_id)
            return [dict(row) for row in result]
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving sensor details: {e!s}"
        ) from e


@router.get("/sensor/{sensor_id}/data/{facade_id}")
async def get_sensor_data(
    sensor_id: str,
    facade_id: str,
    hours: int = Query(default=24, ge=1, le=168),
    limit: int = Query(default=1000, ge=1, le=10000),
):
    """Obtiene datos históricos de un sensor específico"""
    # Validar que hours sea un entero seguro para la consulta
    if not isinstance(hours, int) or hours < 1 or hours > 168:
        raise HTTPException(status_code=400, detail="Hours must be between 1 and 168")

    query = """
    SELECT
        ts,
        ROUND(value::numeric, 2) as value,
        unit,
        device_id
    FROM measurements
    WHERE sensor_id = $1 AND facade_id = $2
    AND ts >= NOW() - INTERVAL $4
    ORDER BY ts DESC
    LIMIT $3
    """

    try:
        async with TimescaleRepository() as db:
            interval = f"{hours} hours"
            result = await db.conn.fetch(query, sensor_id, facade_id, limit, interval)
            return [dict(row) for row in result]
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving sensor data: {e!s}"
        ) from e


@router.get("/environment/{facade_id}")
async def get_environment_data(facade_id: str):
    """Obtiene las últimas lecturas de variables ambientales"""
    query = """
    WITH environmental_sensors AS (
        SELECT DISTINCT ON (sensor_id)
               sensor_id, value, unit, ts, device_id
        FROM measurements
        WHERE facade_id = $1
        AND sensor_id IN ('Irradiancia', 'Velocidad_Viento',
                          'Direccion_Viento', 'Humedad_Relativa')
        AND ts >= NOW() - INTERVAL '2 hours'
        ORDER BY sensor_id, ts DESC
    )
    SELECT
        sensor_id as variable,
        ROUND(value::numeric, 2) as current_value,
        unit,
        ts as timestamp,
        device_id
    FROM environmental_sensors
    ORDER BY sensor_id;
    """

    try:
        async with TimescaleRepository() as db:
            result = await db.conn.fetch(query, facade_id)
            return [dict(row) for row in result]
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving environment data: {e!s}"
        ) from e


@router.get("/environment/{variable}/history/{facade_id}")
async def get_environment_history(
    variable: str,
    facade_id: str,
    hours: int = Query(default=24, ge=1, le=168),
    limit: int = Query(default=500, ge=1, le=5000),
):
    """Obtiene datos históricos de una variable ambiental específica"""
    # Validar que hours sea seguro
    if not isinstance(hours, int) or hours < 1 or hours > 168:
        raise HTTPException(status_code=400, detail="Hours must be between 1 and 168")

    query = """
    SELECT
        ts,
        ROUND(value::numeric, 2) as value,
        unit
    FROM measurements
    WHERE sensor_id = $1 AND facade_id = $2
    AND ts >= NOW() - INTERVAL $4
    ORDER BY ts DESC
    LIMIT $3
    """

    try:
        async with TimescaleRepository() as db:
            interval = f"{hours} hours"
            result = await db.conn.fetch(query, variable, facade_id, limit, interval)
            return [dict(row) for row in result]
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving environment data: {e!s}"
        ) from e


@router.get("/timeseries/{sensor_id}/{facade_id}")
async def get_timeseries_data(
    sensor_id: str,
    facade_id: str,
    hours: int = Query(default=24, ge=1, le=168),
    interval: str = Query(default="1h", regex="^(5m|15m|1h|6h|1d)$"),
):
    """Obtiene datos de series temporales agregados por intervalos"""
    # Mapeo de intervalos válidos
    interval_map = {
        "5m": "5 minutes",
        "15m": "15 minutes",
        "1h": "1 hour",
        "6h": "6 hours",
        "1d": "1 day",
    }

    if interval not in interval_map:
        raise HTTPException(status_code=400, detail="Invalid interval")

    # Validar hours
    if not isinstance(hours, int) or hours < 1 or hours > 168:
        raise HTTPException(status_code=400, detail="Hours must be between 1 and 168")

    query = f"""
    SELECT
        time_bucket(INTERVAL '{interval_map[interval]}', ts) as time_bucket,
        ROUND(AVG(value)::numeric, 2) as avg_value,
        ROUND(MIN(value)::numeric, 2) as min_value,
        ROUND(MAX(value)::numeric, 2) as max_value,
        COUNT(*) as data_points
    FROM measurements
    WHERE sensor_id = $1 AND facade_id = $2
    AND ts >= NOW() - INTERVAL '{hours} hours'
    GROUP BY time_bucket
    ORDER BY time_bucket
    """

    try:
        async with TimescaleRepository() as db:
            result = await db.conn.fetch(query, sensor_id, facade_id)
            return [dict(row) for row in result]
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving timeseries data: {e!s}"
        ) from e


@router.get("/analytics/{sensor_id}/{facade_id}")
async def get_sensor_analytics(
    sensor_id: str, facade_id: str, hours: int = Query(default=24, ge=1, le=168)
):
    """Obtiene estadísticas analíticas de una variable"""
    # Validar hours
    if not isinstance(hours, int) or hours < 1 or hours > 168:
        raise HTTPException(status_code=400, detail="Hours must be between 1 and 168")

    query = f"""
    SELECT
        COUNT(*) as total_readings,
        ROUND(AVG(value)::numeric, 2) as mean_value,
        ROUND(STDDEV(value)::numeric, 2) as std_dev,
        ROUND(MIN(value)::numeric, 2) as min_value,
        ROUND(MAX(value)::numeric, 2) as max_value,
        ROUND(PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY value)::numeric, 2) as q25,
        ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY value)::numeric, 2) as median,
        ROUND(PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY value)::numeric, 2) as q75,
        MIN(ts) as first_reading,
        MAX(ts) as last_reading
    FROM measurements
    WHERE sensor_id = $1 AND facade_id = $2
    AND ts >= NOW() - INTERVAL '{hours} hours'
    """

    try:
        async with TimescaleRepository() as db:
            result = await db.conn.fetchrow(query, sensor_id, facade_id)
            if result:
                return dict(result)
            else:
                return {"error": "No data found for the specified parameters"}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving analytics: {e!s}"
        ) from e


@router.get("/anomalies/{sensor_id}/{facade_id}")
async def detect_anomalies(
    sensor_id: str,
    facade_id: str,
    hours: int = Query(default=24, ge=1, le=168),
    threshold: float = Query(default=2.0, ge=1.0, le=5.0),
):
    """Detecta anomalías usando desviación estándar"""
    # Validar parámetros
    if not isinstance(hours, int) or hours < 1 or hours > 168:
        raise HTTPException(status_code=400, detail="Hours must be between 1 and 168")

    query = f"""
    WITH stats AS (
        SELECT
            AVG(value) as mean_val,
            STDDEV(value) as std_val
        FROM measurements
        WHERE sensor_id = $1 AND facade_id = $2
        AND ts >= NOW() - INTERVAL '{hours} hours'
    ),
    anomalies AS (
        SELECT
            ts,
            ROUND(value::numeric, 2) as value,
            ROUND(ABS(value - stats.mean_val) / stats.std_val::numeric, 2) as z_score
        FROM measurements, stats
        WHERE sensor_id = $1 AND facade_id = $2
        AND ts >= NOW() - INTERVAL '{hours} hours'
        AND ABS(value - stats.mean_val) > ($3 * stats.std_val)
    )
    SELECT * FROM anomalies
    ORDER BY z_score DESC, ts DESC
    LIMIT 50
    """

    try:
        async with TimescaleRepository() as db:
            result = await db.conn.fetch(query, sensor_id, facade_id, threshold)
            return [dict(row) for row in result]
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error detecting anomalies: {e!s}"
        ) from e


@router.get("/realtime/{facade_id}")
async def get_realtime_data(facade_id: str):
    """Obtiene datos en tiempo real (últimos 5 minutos)"""
    query = """
    SELECT
        sensor_id,
        ROUND(value::numeric, 2) as current_value,
        unit,
        ts as timestamp,
        device_id,
        CASE
            WHEN sensor_id LIKE 'Temperatura_%' THEN 'temperature'
            WHEN sensor_id LIKE '%_mA' THEN 'current'
            WHEN sensor_id LIKE '%_W' THEN 'power'
            WHEN sensor_id LIKE 'ENT_%' OR sensor_id LIKE 'SAL_%'
                 OR sensor_id LIKE 'N%_%' THEN 'flow'
            ELSE 'other'
        END as sensor_type
    FROM measurements
    WHERE facade_id = $1
    AND ts >= NOW() - INTERVAL '5 minutes'
    ORDER BY ts DESC, sensor_id;
    """

    try:
        async with TimescaleRepository() as db:
            result = await db.conn.fetch(query, facade_id)
            return [dict(row) for row in result]
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving realtime data: {e!s}"
        ) from e


@router.get("/average/{variable}")
async def get_variable_average(
    variable: str,
    hours: int = Query(default=24, ge=1, le=168),
    facade_id: Optional[str] = None,
):
    """Calcula el promedio de una variable en un periodo específico"""
    # Validar hours
    if not isinstance(hours, int) or hours < 1 or hours > 168:
        raise HTTPException(status_code=400, detail="Hours must be between 1 and 168")

    if facade_id:
        query = f"""
        SELECT
            ROUND(AVG(value)::numeric, 2) as average,
            COUNT(*) as data_points,
            MIN(ts) as period_start,
            MAX(ts) as period_end
        FROM measurements
        WHERE sensor_id = $1 AND facade_id = $2
        AND ts >= NOW() - INTERVAL '{hours} hours'
        """
        params = [variable, facade_id]
    else:
        query = f"""
        SELECT
            facade_id,
            ROUND(AVG(value)::numeric, 2) as average,
            COUNT(*) as data_points,
            MIN(ts) as period_start,
            MAX(ts) as period_end
        FROM measurements
        WHERE sensor_id = $1
        AND ts >= NOW() - INTERVAL '{hours} hours'
        GROUP BY facade_id
        ORDER BY facade_id
        """
        params = [variable]

    try:
        async with TimescaleRepository() as db:
            if facade_id:
                result = await db.conn.fetchrow(query, *params)
                if result:
                    return dict(result)
                else:
                    return {"error": "No data found"}
            else:
                result = await db.conn.fetch(query, *params)
                return [dict(row) for row in result]
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error calculating average: {e!s}"
        ) from e


@router.get("/logs/{facade_id}")
async def get_system_logs(
    facade_id: str, limit: int = Query(default=100, ge=1, le=1000)
):
    """Obtiene los logs recientes del sistema para una fachada"""
    query = """
    SELECT
        ts as timestamp,
        device_id,
        sensor_id,
        ROUND(value::numeric, 2) as value,
        unit,
        tags
    FROM measurements
    WHERE facade_id = $1
    ORDER BY ts DESC
    LIMIT $2;
    """

    try:
        async with TimescaleRepository() as db:
            result = await db.conn.fetch(query, facade_id, limit)
            return [dict(row) for row in result]
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving logs: {e!s}"
        ) from e
