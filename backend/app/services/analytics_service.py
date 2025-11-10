from ..db import get_pool
from typing import List, Dict, Any, Optional

# List of environmental sensor names
ENVIRONMENTAL_SENSORS = [
    "Irradiancia",
    "Velocidad_Viento",
    "Temperatura_Ambiente",
    "Humedad"
]

# List of refrigeration cycle sensor names
REFRIGERATION_SENSORS = [
    # Refrigerant temperatures in the vapor compression cycle
    "T_ValvulaExpansion",        # Start of the panel circuit
    "T_EntCompresor",            # Compressor inlet
    "T_SalCompresor",            # Compressor outlet (condenser inlet)
    "T_SalCondensador",          # Condenser outlet
    # Module inlet temperatures
    "T_Entrada_M1",
    "T_Entrada_M2",
    "T_Entrada_M3",
    "T_Entrada_M4",
    "T_Entrada_M5",
    # Module outlet temperatures
    "T_Salida_M1",
    "T_Salida_M2",
    "T_Salida_M3",
    "T_Salida_M4",
    "T_Salida_M5",
    # Water temperatures
    "T_Entrada_Agua",            # Condenser water inlet
    "T_Salida_Agua",             # Condenser water outlet
    # Compressor pressures
    "Presion_Alta",              # High pressure (compressor outlet)
    "Presion_Baja",              # Low pressure (compressor inlet)
    # Flow control and solenoid valve
    "Flujo_Agua_LPM",            # Water flow in liters per minute
    "Estado_Electrovalvula"      # Valve state: 0 (closed) or 1 (open)
]


async def get_all_sensors(limit: int = 100, facade_type: Optional[str] = None) -> List[str]:
    """
    Retrieves a list of distinct sensor names registered in the database.

    Parameters:
    - limit (int): Maximum number of distinct sensors to return. Must be between 1 and 1000. Default: 100.
    - facade_type (Optional[str]): Filter by facade type. Valid values: 'refrigerada', 'no_refrigerada'. Default: None (no filter).

    Returns:
    - List[str]: List of unique sensor names.

    Exceptions:
    - RuntimeError: Raised if the database connection pool is not initialized.
    - asyncpg.exceptions.PostgresError: Raised if a database query error occurs.
    """
    # Obtain the database connection pool
    pool = get_pool()
    if not pool:
        raise RuntimeError("Database connection pool not initialized")

    # Construct SQL query based on whether facade_type is provided
    if facade_type:
        sql = """
            SELECT DISTINCT sensor_name 
            FROM measurements 
            WHERE facade_type = $1
            LIMIT $2
        """
        params = [facade_type, limit]
    else:
        sql = "SELECT DISTINCT sensor_name FROM measurements LIMIT $1"
        params = [limit]

    try:
        # Acquire a database connection and execute the query
        async with pool.acquire() as conn:
            rows = await conn.fetch(sql, *params)
            # Extract sensor names from query results
            return [r["sensor_name"] for r in rows]
    except Exception as e:
        # Log the error for debugging purposes
        print(f"❌ Error retrieving sensor list: {e}")
        # Raise the exception to be handled by the caller
        raise


async def get_sensor_average(sensor_name: str, facade_type: Optional[str] = None) -> Dict[str, Any]:
    """
    Retrieves the historical average value for a specific sensor, optionally filtered by facade type.

    Parameters:
    - sensor_name (str): Name of the sensor to calculate the average for. Required.
    - facade_type (Optional[str]): Filter by facade type. Valid values: 'refrigerada', 'no_refrigerada'. Default: None (no filter).

    Returns:
    - Dict[str, Any]: Dictionary containing:
      - sensor_name (str): Name of the sensor.
      - facade_type (str or null): The facade type filter applied, if any.
      - average (float or null): The historical average value, or None if no data is available.

    Exceptions:
    - RuntimeError: Raised if the database connection pool is not initialized.
    - asyncpg.exceptions.PostgresError: Raised if a database query error occurs.
    """
    # Obtain the database connection pool
    pool = get_pool()
    if not pool:
        raise RuntimeError("Database connection pool not initialized")

    # Construct SQL query based on whether facade_type is provided
    if facade_type:
        sql = """
            SELECT AVG(value) AS avg_value 
            FROM measurements 
            WHERE sensor_name=$1 AND facade_type=$2
        """
        params = [sensor_name, facade_type]
    else:
        sql = "SELECT AVG(value) AS avg_value FROM measurements WHERE sensor_name=$1"
        params = [sensor_name]

    try:
        # Acquire a database connection and execute the query
        async with pool.acquire() as conn:
            row = await conn.fetchrow(sql, *params)
            # Construct and return the response with average data
            return {
                "sensor_name": sensor_name,
                "facade_type": facade_type,
                "average": row["avg_value"] if row else None
            }
    except Exception as e:
        # Log the error for debugging purposes
        print(f"❌ Error retrieving average for {sensor_name}: {e}")
        # Raise the exception to be handled by the caller
        raise


async def get_facade_average(facade_id: str, facade_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Retrieves the average values of all variables for a specific facade.

    HU08: View a graph of the average temperatures for both facades.
    HU04: View the average temperature per panel in the non-refrigerated facade.

    Parameters:
    - facade_id (str): ID of the facade to calculate averages for. Required.
    - facade_type (Optional[str]): Filter by facade type. Valid values: 'refrigerada', 'no_refrigerada'. Default: None (no filter).

    Returns:
    - List[Dict[str, Any]]: List of dictionaries, each containing:
      - sensor_name (str): Name of the sensor.
      - avg_value (float): Average value of the sensor measurements.
      - facade_type (str): Type of the facade.

    Exceptions:
    - RuntimeError: Raised if the database connection pool is not initialized.
    - asyncpg.exceptions.PostgresError: Raised if a database query error occurs.
    """
    # Obtain the database connection pool
    pool = get_pool()
    if not pool:
        raise RuntimeError("Database connection pool not initialized")

    # Construct SQL query based on whether facade_type is provided
    if facade_type:
        sql = """
            SELECT sensor_name, AVG(value) AS avg_value, facade_type
            FROM measurements
            WHERE facade_id=$1 AND facade_type=$2
            GROUP BY sensor_name, facade_type
        """
        params = [facade_id, facade_type]
    else:
        sql = """
            SELECT sensor_name, AVG(value) AS avg_value, facade_type
            FROM measurements
            WHERE facade_id=$1
            GROUP BY sensor_name, facade_type
        """
        params = [facade_id]

    try:
        # Acquire a database connection and execute the query
        async with pool.acquire() as conn:
            rows = await conn.fetch(sql, *params)
            # Convert query results to a list of dictionaries
            return [dict(r) for r in rows]
    except Exception as e:
        # Log the error for debugging purposes
        print(f"❌ Error retrieving facade averages for {facade_id}: {e}")
        # Raise the exception to be handled by the caller
        raise


async def get_environmental_variables(facade_id: str, facade_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Retrieves average environmental variables for a specific facade.

    HU05: Visualize environmental variables such as irradiance, wind speed, temperature, and ambient humidity.

    Parameters:
    - facade_id (str): ID of the facade to retrieve environmental data for. Required.
    - facade_type (Optional[str]): Filter by facade type. Valid values: 'refrigerada', 'no_refrigerada'. Default: None (no filter).

    Returns:
    - List[Dict[str, Any]]: List of dictionaries, each containing:
      - sensor_name (str): Name of the environmental sensor.
      - avg_value (float): Average value of the sensor measurements.
      - facade_type (str): Type of the facade.

    Exceptions:
    - RuntimeError: Raised if the database connection pool is not initialized.
    - asyncpg.exceptions.PostgresError: Raised if a database query error occurs.
    """
    # Obtain the database connection pool
    pool = get_pool()
    if not pool:
        raise RuntimeError("Database connection pool not initialized")

    # Construct SQL query based on whether facade_type is provided
    if facade_type:
        sql = """
            SELECT sensor_name, AVG(value) AS avg_value, facade_type
            FROM measurements
            WHERE facade_id = $1 AND facade_type = $2
            AND sensor_name = ANY($3::text[])
            GROUP BY sensor_name, facade_type
        """
        params = [facade_id, facade_type, ENVIRONMENTAL_SENSORS]
    else:
        sql = """
            SELECT sensor_name, AVG(value) AS avg_value, facade_type
            FROM measurements
            WHERE facade_id = $1
            AND sensor_name = ANY($2::text[])
            GROUP BY sensor_name, facade_type
        """
        params = [facade_id, ENVIRONMENTAL_SENSORS]

    try:
        # Acquire a database connection and execute the query
        async with pool.acquire() as conn:
            rows = await conn.fetch(sql, *params)
            # Convert query results to a list of dictionaries
            return [dict(r) for r in rows]
    except Exception as e:
        # Log the error for debugging purposes
        print(f"❌ Error retrieving environmental variables for facade {facade_id}: {e}")
        # Raise the exception to be handled by the caller
        raise


async def get_refrigeration_variables(facade_id: str) -> List[Dict[str, Any]]:
    """
    Retrieves average values of refrigeration cycle variables for a specific refrigerated facade.

    HU10: Monitor the refrigerant temperature at each point in the refrigeration cycle.

    Parameters:
    - facade_id (str): ID of the refrigerated facade to retrieve data for. Required.

    Returns:
    - List[Dict[str, Any]]: List of dictionaries, each containing:
      - sensor_name (str): Name of the refrigeration sensor.
      - avg_value (float): Average value of the sensor measurements.
      - facade_type (str): Type of the facade (always 'refrigerada').

    Exceptions:
    - RuntimeError: Raised if the database connection pool is not initialized.
    - asyncpg.exceptions.PostgresError: Raised if a database query error occurs.
    """
    # Obtain the database connection pool
    pool = get_pool()
    if not pool:
        raise RuntimeError("Database connection pool not initialized")

    # Construct SQL query to fetch refrigeration sensor averages
    sql = """
        SELECT sensor_name, AVG(value) AS avg_value, facade_type
        FROM measurements
        WHERE facade_id = $1 AND facade_type = 'refrigerada'
        AND sensor_name = ANY($2::text[])
        GROUP BY sensor_name, facade_type
    """

    try:
        # Acquire a database connection and execute the query
        async with pool.acquire() as conn:
            rows = await conn.fetch(sql, facade_id, REFRIGERATION_SENSORS)
            # Convert query results to a list of dictionaries
            return [dict(r) for r in rows]
    except Exception as e:
        # Log the error for debugging purposes
        print(f"❌ Error retrieving refrigeration variables for facade {facade_id}: {e}")
        # Raise the exception to be handled by the caller
        raise


async def compare_facade_types_average(facade_id: str, sensor_name: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
    """
    Compares average sensor values between refrigerated and non-refrigerated facades for a specific facade ID.

    HU13: Visualize a comparative graph of refrigerant and water temperatures.
    HU17: Compare performance with and without refrigeration to validate hypotheses.

    Parameters:
    - facade_id (str): ID of the facade to compare. Required.
    - sensor_name (Optional[str]): Specific sensor to compare. Default: None (compare all sensors).

    Returns:
    - Dict[str, List[Dict[str, Any]]]: Dictionary with two keys:
      - 'refrigerada': List of records for the refrigerated facade.
      - 'no_refrigerada': List of records for the non-refrigerated facade.
      Each record contains:
      - sensor_name (str): Name of the sensor.
      - facade_type (str): Type of the facade.
      - avg_value (float): Average value of the sensor measurements.
      - min_value (float): Minimum value of the sensor measurements.
      - max_value (float): Maximum value of the sensor measurements.
      - count (int): Number of measurements.

    Exceptions:
    - RuntimeError: Raised if the database connection pool is not initialized.
    - asyncpg.exceptions.PostgresError: Raised if a database query error occurs.
    """
    # Obtain the database connection pool
    pool = get_pool()
    if not pool:
        raise RuntimeError("Database connection pool not initialized")

    # Construct SQL query based on whether sensor_name is provided
    if sensor_name:
        sql = """
            SELECT sensor_name, facade_type, AVG(value) AS avg_value, 
                   MIN(value) AS min_value, MAX(value) AS max_value, 
                   COUNT(*) AS count
            FROM measurements
            WHERE facade_id = $1 AND sensor_name = $2
            GROUP BY sensor_name, facade_type
        """
        params = [facade_id, sensor_name]
    else:
        sql = """
            SELECT sensor_name, facade_type, AVG(value) AS avg_value,
                   MIN(value) AS min_value, MAX(value) AS max_value,
                   COUNT(*) AS count
            FROM measurements
            WHERE facade_id = $1
            GROUP BY sensor_name, facade_type
        """
        params = [facade_id]

    try:
        # Acquire a database connection and execute the query
        async with pool.acquire() as conn:
            rows = await conn.fetch(sql, *params)
            
            # Organize results by facade type
            result = {
                "refrigerada": [dict(r) for r in rows if dict(r)['facade_type'] == 'refrigerada'],
                "no_refrigerada": [dict(r) for r in rows if dict(r)['facade_type'] == 'no_refrigerada']
            }
            # Return the comparison result
            return result
    except Exception as e:
        # Log the error for debugging purposes
        print(f"❌ Error comparing facade averages: {e}")
        # Raise the exception to be handled by the caller
        raise

async def get_panel_temperature_by_module(
    facade_id: str,
    facade_type: Optional[str] = None,
    start: Optional[str] = None,
    end: Optional[str] = None
) -> Dict[str, Any]:
    """
    Calculates average panel temperatures per module (M1-M5) for a specific facade.
    
    Each module has 3 temperature sensors following the pattern T_M{module}_{point}:
    - Module 1: T_M1_1, T_M1_2, T_M1_3
    - Module 2: T_M2_1, T_M2_2, T_M2_3
    - Module 3: T_M3_1, T_M3_2, T_M3_3
    - Module 4: T_M4_1, T_M4_2, T_M4_3
    - Module 5: T_M5_1, T_M5_2, T_M5_3
    
    The function calculates the average of the 3 sensors for each module.
    
    Parameters:
    - facade_id (str): ID of the facade to analyze. Required.
    - facade_type (Optional[str]): Filter by facade type ('refrigerada' or 'no_refrigerada'). Default: None.
    - start (Optional[str]): Start date/time in ISO8601 format for data range. Default: None.
    - end (Optional[str]): End date/time in ISO8601 format for data range. Default: None.
    
    Returns:
    - Dict[str, Any]: Dictionary containing:
      - facade_id (str): ID of the facade analyzed.
      - facade_type (str or null): Facade type filter applied.
      - time_range (Dict): Start and end timestamps.
      - modules (List[Dict]): List of module statistics, each containing:
        - module (str): Module identifier (M1, M2, M3, M4, M5).
        - average_temperature (float): Average temperature across all 3 sensors.
        - min_temperature (float): Minimum temperature recorded.
        - max_temperature (float): Maximum temperature recorded.
        - sensors (List[Dict]): Individual sensor data:
          - sensor_name (str): Name of the sensor.
          - avg_value (float): Average value for this sensor.
          - sample_count (int): Number of measurements for this sensor.
    
    Exceptions:
    - RuntimeError: Raised if the database connection pool is not initialized.
    - asyncpg.exceptions.PostgresError: Raised if a database query error occurs.
    """
    # Obtain the database connection pool
    pool = get_pool()
    if not pool:
        raise RuntimeError("Database connection pool not initialized")
    
    # Build base SQL query to retrieve sensor data
    sql = """
        SELECT 
            sensor_name,
            AVG(value) AS avg_value,
            MIN(value) AS min_value,
            MAX(value) AS max_value,
            COUNT(*) AS sample_count
        FROM measurements
        WHERE facade_id = $1
        AND sensor_name ~ '^T_M[1-5]_[1-3]$'
    """
    
    params = [facade_id]
    param_idx = 2
    
    # Add optional filters
    if facade_type:
        sql += f" AND facade_type = ${param_idx}"
        params.append(facade_type)
        param_idx += 1
    
    if start:
        sql += f" AND ts >= ${param_idx}"
        params.append(start)
        param_idx += 1
    
    if end:
        sql += f" AND ts <= ${param_idx}"
        params.append(end)
        param_idx += 1
    
    sql += " GROUP BY sensor_name ORDER BY sensor_name"
    
    try:
        # Execute query
        async with pool.acquire() as conn:
            rows = await conn.fetch(sql, *params)
            
            if not rows:
                return {
                    "facade_id": facade_id,
                    "facade_type": facade_type,
                    "time_range": {"start": start, "end": end},
                    "modules": []
                }
            
            # Group sensors by module
            modules_data = {}
            for row in rows:
                sensor_name = row["sensor_name"]
                # Extract module number from sensor name (e.g., T_M1_1 -> M1)
                import re
                match = re.match(r'T_M(\d)_\d', sensor_name)
                if match:
                    module_num = match.group(1)
                    module_id = f"M{module_num}"
                    
                    if module_id not in modules_data:
                        modules_data[module_id] = {
                            "sensors": [],
                            "total_avg": 0,
                            "sensor_count": 0,
                            "all_values": []
                        }
                    
                    modules_data[module_id]["sensors"].append({
                        "sensor_name": sensor_name,
                        "avg_value": float(row["avg_value"]),
                        "sample_count": int(row["sample_count"])
                    })
                    
                    modules_data[module_id]["total_avg"] += float(row["avg_value"])
                    modules_data[module_id]["sensor_count"] += 1
                    modules_data[module_id]["all_values"].extend([
                        float(row["min_value"]),
                        float(row["max_value"])
                    ])
            
            # Calculate final statistics per module
            modules = []
            for module_id in sorted(modules_data.keys()):
                data = modules_data[module_id]
                modules.append({
                    "module": module_id,
                    "average_temperature": round(data["total_avg"] / data["sensor_count"], 2),
                    "min_temperature": round(min(data["all_values"]), 2),
                    "max_temperature": round(max(data["all_values"]), 2),
                    "sensors": data["sensors"]
                })
            
            return {
                "facade_id": facade_id,
                "facade_type": facade_type,
                "time_range": {"start": start, "end": end},
                "modules": modules
            }
            
    except Exception as e:
        print(f"❌ Error retrieving panel temperatures by module for facade {facade_id}: {e}")
        raise
