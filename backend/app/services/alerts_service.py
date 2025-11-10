from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta, timezone
from ..db import get_pool
import asyncpg

# Define alert thresholds for different sensor types
ALERT_THRESHOLDS = {
    "Temperatura_Ambiente": {"min": -10, "max": 50},
    "Irradiancia": {"min": 0, "max": 1500},
    "Velocidad_Viento": {"min": 0, "max": 30},
    "Humedad": {"min": 0, "max": 100},
    "T_ValvulaExpansion": {"min": -50, "max": 50},
    "T_EntCompresor": {"min": -50, "max": 80},
    "T_SalCompresor": {"min": -50, "max": 100},
    "T_SalCondensador": {"min": -50, "max": 80},
    "T_Entrada_Agua": {"min": -10, "max": 60},
    "T_Salida_Agua": {"min": -10, "max": 60},
    "Presion_Alta": {"min": 0, "max": 50},
    "Presion_Baja": {"min": 0, "max": 30},
    "Flujo_Agua_LPM": {"min": 0, "max": 500},
}


async def get_sensor_errors(
    limit: int = 100,
    facade_type: Optional[str] = None,
    hours: int = 24
) -> List[Dict[str, Any]]:
    """
    Retrieves sensor records with errors, defined as NULL or negative values, within a specified time range.

    Parameters:
    - limit (int): Maximum number of error records to return. Must be between 1 and 1000. Default: 100.
    - facade_type (Optional[str]): Filter by facade type. Valid values: 'refrigerada', 'no_refrigerada'. Default: None (no filter).
    - hours (int): Time range in hours to consider for recent errors. Must be between 1 and 720. Default: 24.

    Returns:
    - List[Dict[str, Any]]: List of error records, each containing:
      - facade_id (str): ID of the facade.
      - device_id (str): ID of the device.
      - facade_type (str): Type of the facade.
      - sensor_name (str): Name of the sensor.
      - value (float or None): Recorded sensor value.
      - ts (datetime): Timestamp of the measurement.

    Exceptions:
    - RuntimeError: Raised if the database connection pool is not initialized.
    - asyncpg.exceptions.PostgresError: Raised if a database query error occurs.
    """
    # Obtain the database connection pool
    pool = get_pool()
    if not pool:
        raise RuntimeError("Database connection pool not initialized")

    # Validate input parameters
    limit = max(1, min(limit, 1000))
    hours = max(1, min(hours, 720))

    # Construct SQL query to fetch error records
    sql = """
        SELECT facade_id, device_id, facade_type, sensor_name, value, ts
        FROM measurements
        WHERE (value IS NULL OR value < 0)
          AND ts >= NOW() - INTERVAL '%s hours'
    """ % hours
    params = []
    if facade_type:
        sql += " AND facade_type = $1"
        params.append(facade_type)

    sql += f" ORDER BY ts DESC LIMIT {limit}"

    try:
        # Acquire a database connection and execute the query
        async with pool.acquire() as conn:
            rows = await conn.fetch(sql, *params)
            # Convert database rows to list of dictionaries
            return [dict(r) for r in rows]
    except Exception as e:
        # Log the error for debugging purposes
        print(f"❌ Error retrieving sensor errors: {e}")
        # Raise the exception to be handled by the caller
        raise


async def get_anomalies_by_threshold(
    facade_id: Optional[str] = None,
    facade_type: Optional[str] = None,
    limit: int = 100,
    hours: int = 24
) -> List[Dict[str, Any]]:
    """
    Detects sensor readings that fall outside predefined thresholds for a given time range.

    Parameters:
    - facade_id (Optional[str]): Filter by facade ID. Default: None (no filter).
    - facade_type (Optional[str]): Filter by facade type. Valid values: 'refrigerada', 'no_refrigerada'. Default: None (no filter).
    - limit (int): Maximum number of anomaly records to return. Default: 100.
    - hours (int): Time range in hours to consider for recent anomalies. Default: 24.

    Returns:
    - List[Dict[str, Any]]: List of anomaly records, each containing:
      - facade_id (str): ID of the facade.
      - device_id (str): ID of the device.
      - facade_type (str): Type of the facade.
      - sensor_name (str): Name of the sensor.
      - value (float): Recorded sensor value.
      - expected_range (dict): Expected min and max values for the sensor.
      - ts (datetime): Timestamp of the measurement.
      - severity (str): Severity of the anomaly ('warning' or 'critical').

    Exceptions:
    - RuntimeError: Raised if the database connection pool is not initialized.
    - asyncpg.exceptions.PostgresError: Raised if a database query error occurs.
    """
    # Obtain the database connection pool
    pool = get_pool()
    if not pool:
        raise RuntimeError("Database connection pool not initialized")

    # Construct SQL query to fetch measurements
    sql = """
        SELECT facade_id, device_id, facade_type, sensor_name, value, ts
        FROM measurements
        WHERE ts >= NOW() - INTERVAL '%s hours'
    """ % hours

    params = []
    if facade_id:
        sql += f" AND facade_id = $1"
        params.append(facade_id)

    if facade_type:
        sql += f" AND facade_type = ${len(params) + 1}"
        params.append(facade_type)

    sql += f" ORDER BY ts DESC LIMIT {limit}"

    try:
        # Acquire a database connection and execute the query
        async with pool.acquire() as conn:
            rows = await conn.fetch(sql, *params)
        
        anomalies = []
        # Iterate through query results to identify anomalies
        for row in rows:
            sensor = row["sensor_name"]
            value = row["value"]
            
            # Check if the sensor has defined thresholds
            if sensor in ALERT_THRESHOLDS:
                threshold = ALERT_THRESHOLDS[sensor]
                # Determine if the value is outside the acceptable range
                if value is not None and (value < threshold["min"] or value > threshold["max"]):
                    # Calculate severity based on deviation from max threshold
                    severity = "warning" if abs(value - threshold["max"]) < 5 else "critical"
                    # Append anomaly record to the list
                    anomalies.append({
                        "facade_id": row["facade_id"],
                        "device_id": row["device_id"],
                        "facade_type": row["facade_type"],
                        "sensor_name": sensor,
                        "value": value,
                        "expected_range": threshold,
                        "ts": row["ts"],
                        "severity": severity
                    })
        
        # Return the list of detected anomalies
        return anomalies
    except Exception as e:
        # Log the error for debugging purposes
        print(f"❌ Error detecting anomalies: {e}")
        # Raise the exception to be handled by the caller
        raise


async def get_sensor_status(
    facade_id: str,
    facade_type: Optional[str] = None,
    minutes: int = 30
) -> Dict[str, Any]:
    """
    Retrieves the status (active/inactive) of sensors for a specific facade, based on recent activity.

    A sensor is considered inactive if it has not reported data within the specified time period.

    Parameters:
    - facade_id (str): ID of the facade to check sensor status for. Required.
    - facade_type (Optional[str]): Filter by facade type. Valid values: 'refrigerada', 'no_refrigerada'. Default: None (no filter).
    - minutes (int): Time in minutes to determine if a sensor is inactive. Default: 30.

    Returns:
    - Dict[str, Any]: Dictionary containing:
      - facade_id (str): ID of the facade.
      - facade_type (str or null): The facade type filter applied, if any.
      - check_time (str): Timestamp of the status check in ISO8601 format.
      - inactivity_threshold_minutes (int): The inactivity threshold used.
      - sensors (list): List of sensor status records, each containing:
        - sensor_name (str): Name of the sensor.
        - status (str): 'active' or 'inactive'.
        - last_reading (str or null): Timestamp of the last reading in ISO8601 format.
        - last_value (float or null): Last recorded value.
        - device_id (str): ID of the device.
        - minutes_since_update (float or null): Minutes since the last update.
      - summary (dict): Summary statistics with 'total', 'active', and 'inactive' counts.

    Exceptions:
    - RuntimeError: Raised if the database connection pool is not initialized.
    - asyncpg.exceptions.PostgresError: Raised if a database query error occurs.
    """
    # Obtain the database connection pool
    pool = get_pool()
    if not pool:
        raise RuntimeError("Database connection pool not initialized")

    # Construct SQL query to fetch the latest sensor readings
    sql = """
        SELECT DISTINCT ON (sensor_name) 
               sensor_name, ts, value, device_id
        FROM measurements
        WHERE facade_id = $1
    """
    params = [facade_id]

    if facade_type:
        sql += " AND facade_type = $2"
        params.append(facade_type)

    sql += " ORDER BY sensor_name, ts DESC"

    try:
        # Acquire a database connection and execute the query
        async with pool.acquire() as conn:
            rows = await conn.fetch(sql, *params)

        # Calculate the threshold time for determining inactivity
        threshold_time = datetime.now(timezone.utc) - timedelta(minutes=minutes)
        sensors_status = []

        # Process each sensor's latest reading
        for row in rows:
            last_reading = row["ts"]
            # Determine if the sensor is active based on the last reading time
            is_active = last_reading > threshold_time if last_reading else False
            # Calculate minutes since last update if applicable
            minutes_since = (datetime.now(timezone.utc) - last_reading).total_seconds() / 60 if last_reading else None
            # Append sensor status to the list
            sensors_status.append({
                "sensor_name": row["sensor_name"],
                "status": "active" if is_active else "inactive",
                "last_reading": last_reading.isoformat() if last_reading else None,
                "last_value": row["value"],
                "device_id": row["device_id"],
                "minutes_since_update": minutes_since
            })

        # Construct and return the response with sensor status and summary
        return {
            "facade_id": facade_id,
            "facade_type": facade_type,
            "check_time": datetime.now(timezone.utc).isoformat(),
            "inactivity_threshold_minutes": minutes,
            "sensors": sensors_status,
            "summary": {
                "total": len(sensors_status),
                "active": sum(1 for s in sensors_status if s["status"] == "active"),
                "inactive": sum(1 for s in sensors_status if s["status"] == "inactive")
            }
        }
    except Exception as e:
        # Log the error for debugging purposes
        print(f"❌ Error retrieving sensor status: {e}")
        # Raise the exception to be handled by the caller
        raise


async def get_alert_history(
    limit: int = 100,
    facade_type: Optional[str] = None,
    hours: int = 168
) -> List[Dict[str, Any]]:
    """
    Retrieves a consolidated history of alerts, combining sensor errors and anomalies.

    HU21: View the history of alerts generated by the system.
    HU15: Receive automatic alerts when sensor failures are detected.

    Parameters:
    - limit (int): Maximum number of alert records to return. Default: 100.
    - facade_type (Optional[str]): Filter by facade type. Valid values: 'refrigerada', 'no_refrigerada'. Default: None (no filter).
    - hours (int): Time range in hours for alert history. Default: 168 (1 week).

    Returns:
    - List[Dict[str, Any]]: List of alert records, each containing:
      - id (str): Unique identifier for the alert.
      - type (str): Type of alert ('sensor_error' or 'threshold_exceeded').
      - facade_id (str): ID of the facade.
      - facade_type (str): Type of the facade.
      - device_id (str): ID of the device.
      - sensor_name (str): Name of the sensor.
      - message (str): Description of the alert.
      - severity (str): Severity level ('critical' or 'warning').
      - created_at (str): Timestamp of the alert in ISO8601 format.

    Exceptions:
    - RuntimeError: Raised if the database connection pool is not initialized.
    - asyncpg.exceptions.PostgresError: Raised if a database query error occurs.
    """
    # Obtain the database connection pool
    pool = get_pool()
    if not pool:
        raise RuntimeError("Database connection pool not initialized")

    alerts = []
    
    try:
        # Construct SQL query to fetch sensor errors
        error_sql = """
            SELECT facade_id, device_id, facade_type, sensor_name, value, ts
            FROM measurements
            WHERE (value IS NULL OR value < 0)
            AND ts >= NOW() - INTERVAL '%s hours'
        """ % hours

        params = []
        if facade_type:
            error_sql += f" AND facade_type = $1"
            params.append(facade_type)

        # Query sensor errors
        async with pool.acquire() as conn:
            error_rows = await conn.fetch(error_sql, *params)

            # Process error records and append to alerts list
            for row in error_rows:
                alerts.append({
                    "id": f"error_{row['device_id']}_{row['ts'].timestamp()}",
                    "type": "sensor_error",
                    "facade_id": row["facade_id"],
                    "facade_type": row["facade_type"],
                    "device_id": row["device_id"],
                    "sensor_name": row["sensor_name"],
                    "message": f"Sensor {row['sensor_name']} reported invalid value: {row['value']}",
                    "severity": "critical",
                    "created_at": row["ts"].isoformat() if hasattr(row["ts"], "isoformat") else str(row["ts"])
                })

        # Query anomalies using the get_anomalies_by_threshold function
        anomalies = await get_anomalies_by_threshold(facade_type=facade_type, hours=hours, limit=limit)
        
        # Process anomaly records and append to alerts list
        for anomaly in anomalies:
            alerts.append({
                "id": f"anomaly_{anomaly['device_id']}_{anomaly['ts'].timestamp()}",
                "type": "threshold_exceeded",
                "facade_id": anomaly["facade_id"],
                "facade_type": anomaly["facade_type"],
                "device_id": anomaly["device_id"],
                "sensor_name": anomaly["sensor_name"],
                "message": f"Sensor {anomaly['sensor_name']} out of range: {anomaly['value']} (range: {anomaly['expected_range']['min']}-{anomaly['expected_range']['max']})",
                "severity": anomaly["severity"],
                "created_at": anomaly["ts"].isoformat() if hasattr(anomaly["ts"], "isoformat") else str(anomaly["ts"])
            })

        # Sort alerts by creation time in descending order and apply limit
        alerts.sort(key=lambda x: x["created_at"], reverse=True)
        return alerts[:limit]
    except Exception as e:
        # Log the error for debugging purposes
        print(f"❌ Error retrieving alert history: {e}")
        # Raise the exception to be handled by the caller
        raise