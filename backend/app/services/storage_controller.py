from typing import Optional, List, Dict, Any
from ..db import get_pool
import asyncpg


async def fetch_measurements(
    facade_id: str,
    sensor: Optional[str] = None,
    facade_type: Optional[str] = None,
    start: Optional[str] = None,
    end: Optional[str] = None,
    limit: int = 500,
) -> List[Dict[str, Any]]:
    """
    Retrieves measurement data from TimescaleDB with optional filters.

    HU02: Select a facade to view its data individually.

    Parameters:
    - facade_id (str): ID of the facade to retrieve measurements for. Required.
    - sensor (Optional[str]): Filter by specific sensor name. Default: None (all sensors).
    - facade_type (Optional[str]): Filter by facade type. Valid values: 'refrigerada', 'no_refrigerada'. Default: None (no filter).
    - start (Optional[str]): Start date/time for the data range in ISO8601 format (e.g., '2023-01-01T00:00:00Z'). Default: None (no start date filter).
    - end (Optional[str]): End date/time for the data range in ISO8601 format (e.g., '2023-01-02T00:00:00Z'). Default: None (no end date filter).
    - limit (int): Maximum number of records to return. Default: 500.

    Returns:
    - List[Dict[str, Any]]: List of measurement records, each containing:
      - ts (datetime): Timestamp of the measurement.
      - sensor_name (str): Name of the sensor.
      - value (float or null): Recorded sensor value.
      - device_id (str): ID of the device.
      - facade_type (str): Type of the facade.

    Exceptions:
    - RuntimeError: Raised if the database connection pool is not initialized.
    - asyncpg.exceptions.PostgresError: Raised if a database query error occurs.
    """
    # Obtain the database connection pool
    pool = get_pool()
    if not pool:
        raise RuntimeError("Database connection pool not initialized")

    # Construct SQL query with dynamic conditions
    sql = """
        SELECT ts, sensor_name, value, device_id, facade_type
        FROM measurements
        WHERE facade_id = $1
    """
    params = [facade_id]
    idx = 2

    if facade_type:
        sql += f" AND facade_type = ${idx}"
        params.append(facade_type)
        idx += 1

    if sensor:
        sql += f" AND sensor_name = ${idx}"
        params.append(sensor)
        idx += 1

    if start:
        sql += f" AND ts >= ${idx}"
        params.append(start)
        idx += 1

    if end:
        sql += f" AND ts <= ${idx}"
        params.append(end)
        idx += 1

    sql += f" ORDER BY ts DESC LIMIT ${idx}"
    params.append(limit)

    try:
        # Acquire a database connection and execute the query
        async with pool.acquire() as conn:
            rows = await conn.fetch(sql, *params)
            # Convert query results to a list of dictionaries
            return [dict(r) for r in rows]
    except asyncpg.PostgresError as e:
        # Log the database error for debugging purposes
        print(f"❌ SQL error retrieving measurements: {e}")
        # Return empty list on error
        return []
    except Exception as e:
        # Log unexpected errors for debugging purposes
        print(f"❌ Unexpected error retrieving measurements: {e}")
        # Return empty list on error
        return []


async def fetch_latest_by_facade(
    facade_id: str,
    facade_type: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Retrieves the latest measurement for each sensor of a specific facade using DISTINCT ON.

    HU02: Select a facade to view its data individually.

    Parameters:
    - facade_id (str): ID of the facade to retrieve latest measurements for. Required.
    - facade_type (Optional[str]): Filter by facade type. Valid values: 'refrigerada', 'no_refrigerada'. Default: None (no filter).

    Returns:
    - List[Dict[str, Any]]: List of latest measurement records, each containing:
      - sensor_name (str): Name of the sensor.
      - value (float or null): Latest recorded sensor value.
      - ts (datetime): Timestamp of the measurement.
      - device_id (str): ID of the device.
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
            SELECT DISTINCT ON (sensor_name)
                sensor_name, value, ts, device_id, facade_type
            FROM measurements
            WHERE facade_id = $1 AND facade_type = $2
            ORDER BY sensor_name, ts DESC
        """
        params = [facade_id, facade_type]
    else:
        sql = """
            SELECT DISTINCT ON (sensor_name, facade_type)
                sensor_name, value, ts, device_id, facade_type
            FROM measurements
            WHERE facade_id = $1
            ORDER BY sensor_name, facade_type, ts DESC
        """
        params = [facade_id]

    try:
        # Acquire a database connection and execute the query
        async with pool.acquire() as conn:
            rows = await conn.fetch(sql, *params)
            # Convert query results to a list of dictionaries
            return [dict(r) for r in rows]
    except asyncpg.PostgresError as e:
        # Log the database error for debugging purposes
        print(f"❌ SQL error retrieving latest measurements: {e}")
        # Return empty list on error
        return []
    except Exception as e:
        # Log unexpected errors for debugging purposes
        print(f"❌ Unexpected error retrieving latest measurements: {e}")
        # Return empty list on error
        return []


async def fetch_facades() -> List[Dict[str, str]]:
    """
    Retrieves a list of unique facade IDs and their types from the database.

    Returns:
    - List[Dict[str, str]]: List of dictionaries, each containing:
      - facade_id (str): ID of the facade.
      - facade_type (str): Type of the facade ('refrigerada' or 'no_refrigerada').

    Exceptions:
    - RuntimeError: Raised if the database connection pool is not initialized.
    - asyncpg.exceptions.PostgresError: Raised if a database query error occurs.
    """
    # Obtain the database connection pool
    pool = get_pool()
    if not pool:
        raise RuntimeError("Database connection pool not initialized")

    # SQL query to fetch distinct facade IDs and types
    sql = """
        SELECT DISTINCT facade_id, facade_type 
        FROM measurements 
        ORDER BY facade_id, facade_type
    """

    try:
        # Acquire a database connection and execute the query
        async with pool.acquire() as conn:
            rows = await conn.fetch(sql)
            # Convert query results to a list of dictionaries
            return [dict(r) for r in rows]
    except asyncpg.PostgresError as e:
        # Log the database error for debugging purposes
        print(f"❌ SQL error retrieving facade list: {e}")
        # Return empty list on error
        return []
    except Exception as e:
        # Log unexpected errors for debugging purposes
        print(f"❌ Unexpected error retrieving facade list: {e}")
        # Return empty list on error
        return []


async def fetch_facade_ids() -> List[str]:
    """
    Retrieves a list of unique facade IDs from the database.

    Returns:
    - List[str]: List of unique facade IDs.

    Exceptions:
    - RuntimeError: Raised if the database connection pool is not initialized.
    - asyncpg.exceptions.PostgresError: Raised if a database query error occurs.
    """
    # Obtain the database connection pool
    pool = get_pool()
    if not pool:
        raise RuntimeError("Database connection pool not initialized")

    # SQL query to fetch distinct facade IDs
    sql = "SELECT DISTINCT facade_id FROM measurements ORDER BY facade_id"

    try:
        # Acquire a database connection and execute the query
        async with pool.acquire() as conn:
            rows = await conn.fetch(sql)
            # Extract facade IDs from query results
            return [r["facade_id"] for r in rows]
    except asyncpg.PostgresError as e:
        # Log the database error for debugging purposes
        print(f"❌ SQL error retrieving facade IDs: {e}")
        # Return empty list on error
        return []
    except Exception as e:
        # Log unexpected errors for debugging purposes
        print(f"❌ Unexpected error retrieving facade IDs: {e}")
        # Return empty list on error
        return []


async def fetch_facade_types(facade_id: str) -> List[str]:
    """
    Retrieves the available facade types for a specific facade ID.

    Parameters:
    - facade_id (str): ID of the facade to retrieve types for. Required.

    Returns:
    - List[str]: List of facade types ('refrigerada', 'no_refrigerada').

    Exceptions:
    - RuntimeError: Raised if the database connection pool is not initialized.
    - asyncpg.exceptions.PostgresError: Raised if a database query error occurs.
    """
    # Obtain the database connection pool
    pool = get_pool()
    if not pool:
        raise RuntimeError("Database connection pool not initialized")

    # SQL query to fetch distinct facade types for the given facade ID
    sql = """
        SELECT DISTINCT facade_type 
        FROM measurements 
        WHERE facade_id = $1
        ORDER BY facade_type
    """

    try:
        # Acquire a database connection and execute the query
        async with pool.acquire() as conn:
            rows = await conn.fetch(sql, facade_id)
            # Extract facade types from query results
            return [r["facade_type"] for r in rows]
    except asyncpg.PostgresError as e:
        # Log the database error for debugging purposes
        print(f"❌ SQL error retrieving facade types: {e}")
        # Return empty list on error
        return []
    except Exception as e:
        # Log unexpected errors for debugging purposes
        print(f"❌ Unexpected error retrieving facade types: {e}")
        # Return empty list on error
        return []


async def fetch_sensors_by_facade_type(
    facade_id: str,
    facade_type: str
) -> List[str]:
    """
    Retrieves the list of available sensor names for a specific facade and facade type.

    Parameters:
    - facade_id (str): ID of the facade to retrieve sensors for. Required.
    - facade_type (str): Type of the facade ('refrigerada' or 'no_refrigerada'). Required.

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

    # SQL query to fetch distinct sensor names for the given facade and type
    sql = """
        SELECT DISTINCT sensor_name 
        FROM measurements 
        WHERE facade_id = $1 AND facade_type = $2
        ORDER BY sensor_name
    """

    try:
        # Acquire a database connection and execute the query
        async with pool.acquire() as conn:
            rows = await conn.fetch(sql, facade_id, facade_type)
            # Extract sensor names from query results
            return [r["sensor_name"] for r in rows]
    except asyncpg.PostgresError as e:
        # Log the database error for debugging purposes
        print(f"❌ SQL error retrieving sensors: {e}")
        # Return empty list on error
        return []
    except Exception as e:
        # Log unexpected errors for debugging purposes
        print(f"❌ Unexpected error retrieving sensors: {e}")
        # Return empty list on error
        return []


async def compare_facade_types(
    facade_id: str,
    sensor: str,
    start: Optional[str] = None,
    end: Optional[str] = None,
    limit: int = 500,
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Compares measurements of a specific sensor between refrigerated and non-refrigerated facades.

    HU17: Compare performance with and without refrigeration to validate hypotheses.

    Parameters:
    - facade_id (str): ID of the facade to compare. Required.
    - sensor (str): Name of the sensor to compare. Required.
    - start (Optional[str]): Start date/time for the data range in ISO8601 format (e.g., '2023-01-01T00:00:00Z'). Default: None (no start date filter).
    - end (Optional[str]): End date/time for the data range in ISO8601 format (e.g., '2023-01-02T00:00:00Z'). Default: None (no end date filter).
    - limit (int): Maximum number of records per facade type. Default: 500.

    Returns:
    - Dict[str, List[Dict[str, Any]]]: Dictionary with two keys:
      - 'refrigerada': List of measurement records for the refrigerated facade.
      - 'no_refrigerada': List of measurement records for the non-refrigerated facade.
      Each record contains:
      - ts (datetime): Timestamp of the measurement.
      - sensor_name (str): Name of the sensor.
      - value (float or null): Recorded sensor value.
      - device_id (str): ID of the device.
      - facade_type (str): Type of the facade.

    Exceptions:
    - RuntimeError: Raised if the database connection pool is not initialized.
    - asyncpg.exceptions.PostgresError: Raised if a database query error occurs.
    """
    # Obtain the database connection pool
    pool = get_pool()
    if not pool:
        raise RuntimeError("Database connection pool not initialized")

    # Construct SQL query with dynamic conditions
    sql = """
        SELECT ts, sensor_name, value, device_id, facade_type
        FROM measurements
        WHERE facade_id = $1 AND sensor_name = $2
    """
    params = [facade_id, sensor]
    idx = 3

    if start:
        sql += f" AND ts >= ${idx}"
        params.append(start)
        idx += 1

    if end:
        sql += f" AND ts <= ${idx}"
        params.append(end)
        idx += 1

    sql += f" ORDER BY facade_type, ts DESC LIMIT ${idx}"
    params.append(limit)

    try:
        # Acquire a database connection and execute the query
        async with pool.acquire() as conn:
            rows = await conn.fetch(sql, *params)
            
            # Initialize result dictionary
            result = {
                "refrigerada": [],
                "no_refrigerada": []
            }
            
            # Organize measurements by facade type
            for row in rows:
                row_dict = dict(row)
                facade_type = row_dict.get("facade_type")
                if facade_type in result:
                    result[facade_type].append(row_dict)
            
            # Return the comparison result
            return result
    except asyncpg.PostgresError as e:
        # Log the database error for debugging purposes
        print(f"❌ SQL error comparing facade types: {e}")
        # Return empty result on error
        return {"refrigerada": [], "no_refrigerada": []}
    except Exception as e:
        # Log unexpected errors for debugging purposes
        print(f"❌ Unexpected error comparing facade types: {e}")
        # Return empty result on error
        return {"refrigerada": [], "no_refrigerada": []}