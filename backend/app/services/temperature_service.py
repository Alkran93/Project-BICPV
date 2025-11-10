"""
Specialized service for retrieving specific refrigeration cycle temperature data.
Maintains single responsibility for extracting and organizing temperature measurements.
"""
from typing import List, Dict, Any, Optional
from ..db import get_pool
import asyncpg

# Mapping of refrigerant cycle temperature sensors to human-readable labels
REFRIGERANT_CYCLE_TEMPS = {
    "T_ValvulaExpansion": "Expansion Valve",
    "T_EntCompresor": "Compressor Inlet",
    "T_SalCompresor": "Compressor Outlet",
    "T_SalCondensador": "Condenser Outlet",
}

# Mapping of heat exchanger water temperature sensors to human-readable labels
EXCHANGER_TEMPS = {
    "T_Entrada_Agua": "Condenser Water Inlet",
    "T_Salida_Agua": "Condenser Water Outlet",
}

# Mapping of panel inlet temperature sensors to human-readable labels
PANEL_INLET_TEMPS = {
    "T_Entrada_M1": "Panel M1 - Inlet",
    "T_Entrada_M2": "Panel M2 - Inlet",
    "T_Entrada_M3": "Panel M3 - Inlet",
    "T_Entrada_M4": "Panel M4 - Inlet",
    "T_Entrada_M5": "Panel M5 - Inlet",
}

# Mapping of panel outlet temperature sensors to human-readable labels
PANEL_OUTLET_TEMPS = {
    "T_Salida_M1": "Panel M1 - Outlet",
    "T_Salida_M2": "Panel M2 - Outlet",
    "T_Salida_M3": "Panel M3 - Outlet",
    "T_Salida_M4": "Panel M4 - Outlet",
    "T_Salida_M5": "Panel M5 - Outlet",
}


async def get_refrigerant_cycle_temperatures(
    facade_id: str,
    start: Optional[str] = None,
    end: Optional[str] = None,
    limit: int = 500
) -> Dict[str, Any]:
    """
    Retrieves refrigerant temperatures at each point in the vapor compression refrigeration cycle.

    HU10: Monitor refrigerant temperatures at each point in the refrigeration cycle.

    Parameters:
    - facade_id (str): ID of the refrigerated facade to retrieve data for. Required.
    - start (Optional[str]): Start date/time for the data range in ISO8601 format (e.g., '2023-01-01T00:00:00Z'). Default: None (no start date filter).
    - end (Optional[str]): End date/time for the data range in ISO8601 format (e.g., '2023-01-02T00:00:00Z'). Default: None (no end date filter).
    - limit (int): Maximum number of records to return. Default: 500.

    Returns:
    - Dict[str, Any]: Dictionary containing:
      - facade_id (str): ID of the facade.
      - cycle_points (dict): Dictionary with sensor names as keys, each containing:
        - label (str): Human-readable name of the cycle point.
        - readings (list): List of measurement records with timestamp, value, and device ID.
      - error (str, optional): Error message if an exception occurs.

    Exceptions:
    - RuntimeError: Raised if the database connection pool is not initialized.
    - asyncpg.exceptions.PostgresError: Raised if a database query error occurs.
    """
    # Obtain the database connection pool
    pool = get_pool()
    if not pool:
        raise RuntimeError("Database connection pool not initialized")

    # Define sensors for refrigerant cycle temperatures
    sensors = list(REFRIGERANT_CYCLE_TEMPS.keys())
    
    # Construct SQL query to fetch refrigerant cycle temperature measurements
    sql = """
        SELECT ts, sensor_name, value, device_id
        FROM measurements
        WHERE facade_id = $1 
        AND facade_type = 'refrigerada'
        AND sensor_name = ANY($2::text[])
    """
    params = [facade_id, sensors]
    idx = 3

    if start:
        sql += f" AND ts >= ${idx}"
        params.append(start)
        idx += 1

    if end:
        sql += f" AND ts <= ${idx}"
        params.append(end)
        idx += 1

    sql += f" ORDER BY sensor_name, ts DESC LIMIT ${idx}"
    params.append(limit)

    try:
        # Acquire a database connection and execute the query
        async with pool.acquire() as conn:
            rows = await conn.fetch(sql, *params)
            
            # Initialize result structure
            result = {
                "facade_id": facade_id,
                "cycle_points": {}
            }
            
            # Organize measurements by sensor
            for row in rows:
                sensor = row["sensor_name"]
                if sensor not in result["cycle_points"]:
                    result["cycle_points"][sensor] = {
                        "label": REFRIGERANT_CYCLE_TEMPS[sensor],
                        "readings": []
                    }
                # Append measurement reading to the appropriate sensor
                result["cycle_points"][sensor]["readings"].append({
                    "ts": row["ts"],
                    "value": row["value"],
                    "device_id": row["device_id"]
                })
            
            return result
    except asyncpg.PostgresError as e:
        # Log the database error for debugging purposes
        print(f"❌ Error retrieving cycle temperatures: {e}")
        # Return error structure
        return {"facade_id": facade_id, "cycle_points": {}, "error": str(e)}
    except Exception as e:
        # Log unexpected errors for debugging purposes
        print(f"❌ Unexpected error: {e}")
        # Return error structure
        return {"facade_id": facade_id, "cycle_points": {}, "error": str(e)}


async def get_exchanger_temperatures(
    facade_id: str,
    start: Optional[str] = None,
    end: Optional[str] = None,
    limit: int = 500
) -> Dict[str, Any]:
    """
    Retrieves water temperatures at the inlet and outlet of the heat exchanger.

    HU12: View water temperatures at the inlet and outlet of the heat exchanger.

    Parameters:
    - facade_id (str): ID of the refrigerated facade to retrieve data for. Required.
    - start (Optional[str]): Start date/time for the data range in ISO8601 format. Default: None (no start date filter).
    - end (Optional[str]): End date/time for the data range in ISO8601 format. Default: None (no end date filter).
    - limit (int): Maximum number of records to return. Default: 500.

    Returns:
    - Dict[str, Any]: Dictionary containing:
      - facade_id (str): ID of the facade.
      - exchanger_data (dict): Dictionary with 'inlet' and 'outlet' keys, each containing:
        - label (str): Human-readable name of the temperature point.
        - readings (list): List of measurement records with timestamp, value, and device ID.
      - error (str, optional): Error message if an exception occurs.

    Exceptions:
    - RuntimeError: Raised if the database connection pool is not initialized.
    - asyncpg.exceptions.PostgresError: Raised if a database query error occurs.
    """
    # Obtain the database connection pool
    pool = get_pool()
    if not pool:
        raise RuntimeError("Database connection pool not initialized")

    # Define sensors for heat exchanger temperatures
    sensors = list(EXCHANGER_TEMPS.keys())
    
    # Construct SQL query that gets data from BOTH sensors independently
    # Using UNION to ensure balanced results from inlet and outlet
    sql = """
        (SELECT ts, sensor_name, value, device_id
         FROM measurements
         WHERE facade_id = $1 
         AND facade_type = 'refrigerada'
         AND sensor_name = 'T_Entrada_Agua'
    """
    params = [facade_id]
    idx = 2

    if start:
        sql += f" AND ts >= ${idx}"
        params.append(start)
        idx += 1

    if end:
        sql += f" AND ts <= ${idx}"
        params.append(end)
        idx += 1

    sql += f" ORDER BY ts DESC LIMIT ${idx})"
    params.append(limit)
    idx += 1
    
    sql += f"""
        UNION ALL
        (SELECT ts, sensor_name, value, device_id
         FROM measurements
         WHERE facade_id = ${idx}
         AND facade_type = 'refrigerada'
         AND sensor_name = 'T_Salida_Agua'
    """
    params.append(facade_id)  # Add facade_id again for second query
    idx += 1
    
    # Add start/end filters for outlet query
    if start:
        sql += f" AND ts >= ${idx}"
        params.append(start)
        idx += 1

    if end:
        sql += f" AND ts <= ${idx}"
        params.append(end)
        idx += 1

    sql += f" ORDER BY ts DESC LIMIT ${idx})"
    params.append(limit)
    
    sql += " ORDER BY ts DESC"

    try:
        # Acquire a database connection and execute the query
        async with pool.acquire() as conn:
            rows = await conn.fetch(sql, *params)
            
            # Initialize result structure with exchanger data
            result = {
                "facade_id": facade_id,
                "exchanger_data": {
                    "inlet": {"label": EXCHANGER_TEMPS.get("T_Entrada_Agua"), "readings": []},
                    "outlet": {"label": EXCHANGER_TEMPS.get("T_Salida_Agua"), "readings": []}
                }
            }
            
            # Organize measurements by inlet/outlet
            for row in rows:
                sensor = row["sensor_name"]
                reading = {"ts": row["ts"], "value": row["value"], "device_id": row["device_id"]}
                
                if sensor == "T_Entrada_Agua":
                    result["exchanger_data"]["inlet"]["readings"].append(reading)
                elif sensor == "T_Salida_Agua":
                    result["exchanger_data"]["outlet"]["readings"].append(reading)
            
            return result
    except asyncpg.PostgresError as e:
        # Log the database error for debugging purposes
        print(f"❌ Error retrieving exchanger temperatures: {e}")
        # Return error structure
        return {"facade_id": facade_id, "exchanger_data": {}, "error": str(e)}
    except Exception as e:
        # Log unexpected errors for debugging purposes
        print(f"❌ Unexpected error: {e}")
        # Return error structure
        return {"facade_id": facade_id, "exchanger_data": {}, "error": str(e)}


async def get_panel_temperatures(
    facade_id: str,
    panel_id: Optional[int] = None,
    start: Optional[str] = None,
    end: Optional[str] = None,
    limit: int = 500
) -> Dict[str, Any]:
    """
    Retrieves inlet and outlet temperatures for one or all panels of a refrigerated facade.

    Parameters:
    - facade_id (str): ID of the refrigerated facade to retrieve data for. Required.
    - panel_id (Optional[int]): Specific panel ID (1-5) to retrieve data for. Default: None (all panels).
    - start (Optional[str]): Start date/time for the data range in ISO8601 format. Default: None (no start date filter).
    - end (Optional[str]): End date/time for the data range in ISO8601 format. Default: None (no end date filter).
    - limit (int): Maximum number of records to return. Default: 500.

    Returns:
    - Dict[str, Any]: Dictionary containing:
      - facade_id (str): ID of the facade.
      - panels (dict): Dictionary with panel numbers as keys (e.g., '1', '2'), each containing:
        - inlet (dict): Inlet temperature data with label and readings list.
        - outlet (dict): Outlet temperature data with label and readings list.
        - readings (list): List of measurement records with timestamp, value, and device ID.
      - error (str, optional): Error message if an exception occurs.

    Exceptions:
    - RuntimeError: Raised if the database connection pool is not initialized.
    - asyncpg.exceptions.PostgresError: Raised if a database query error occurs.
    """
    # Obtain the database connection pool
    pool = get_pool()
    if not pool:
        raise RuntimeError("Database connection pool not initialized")

    # Determine sensors based on panel_id
    if panel_id and 1 <= panel_id <= 5:
        inlet_key = f"T_Entrada_M{panel_id}"
        outlet_key = f"T_Salida_M{panel_id}"
        sensors = [inlet_key, outlet_key]
    else:
        sensors = list(PANEL_INLET_TEMPS.keys()) + list(PANEL_OUTLET_TEMPS.keys())
    
    # Construct SQL query to fetch panel temperature measurements
    sql = """
        SELECT ts, sensor_name, value, device_id
        FROM measurements
        WHERE facade_id = $1 
        AND facade_type = 'refrigerada'
        AND sensor_name = ANY($2::text[])
    """
    params = [facade_id, sensors]
    idx = 3

    if start:
        sql += f" AND ts >= ${idx}"
        params.append(start)
        idx += 1

    if end:
        sql += f" AND ts <= ${idx}"
        params.append(end)
        idx += 1

    sql += f" ORDER BY sensor_name, ts DESC LIMIT ${idx}"
    params.append(limit)

    try:
        # Acquire a database connection and execute the query
        async with pool.acquire() as conn:
            rows = await conn.fetch(sql, *params)
            
            # Initialize result structure
            result = {
                "facade_id": facade_id,
                "panels": {}
            }
            
            # Organize measurements by panel and inlet/outlet
            for row in rows:
                sensor = row["sensor_name"]
                reading = {"ts": row["ts"], "value": row["value"], "device_id": row["device_id"]}
                
                if sensor in PANEL_INLET_TEMPS:
                    # Extract panel number from sensor name (e.g., "T_Entrada_M1" -> "1")
                    panel_num = sensor.split("M")[1]
                    if panel_num not in result["panels"]:
                        result["panels"][panel_num] = {"inlet": {"readings": []}, "outlet": {"readings": []}}
                    result["panels"][panel_num]["inlet"]["label"] = PANEL_INLET_TEMPS[sensor]
                    result["panels"][panel_num]["inlet"]["readings"].append(reading)
                    
                elif sensor in PANEL_OUTLET_TEMPS:
                    # Extract panel number from sensor name (e.g., "T_Salida_M1" -> "1")
                    panel_num = sensor.split("M")[1]
                    if panel_num not in result["panels"]:
                        result["panels"][panel_num] = {"inlet": {"readings": []}, "outlet": {"readings": []}}
                    result["panels"][panel_num]["outlet"]["label"] = PANEL_OUTLET_TEMPS[sensor]
                    result["panels"][panel_num]["outlet"]["readings"].append(reading)
            
            return result
    except asyncpg.PostgresError as e:
        # Log the database error for debugging purposes
        print(f"❌ Error retrieving panel temperatures: {e}")
        # Return error structure
        return {"facade_id": facade_id, "panels": {}, "error": str(e)}
    except Exception as e:
        # Log unexpected errors for debugging purposes
        print(f"❌ Unexpected error: {e}")
        # Return error structure
        return {"facade_id": facade_id, "panels": {}, "error": str(e)}