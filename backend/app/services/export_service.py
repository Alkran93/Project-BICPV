import csv
import io
from typing import List, Dict, Any, Optional
from datetime import datetime
from ..db import get_pool
import asyncpg


async def generate_csv_export(
    facade_id: str,
    facade_type: Optional[str] = None,
    sensor: Optional[str] = None,
    start: Optional[str] = None,
    end: Optional[str] = None,
) -> tuple[str, bytes]:
    """
    Generates a CSV file containing measurement data for a specific facade.

    HU18: Export data in CSV format for analysis in external tools.

    Parameters:
    - facade_id (str): ID of the facade to retrieve data for. Required.
    - facade_type (Optional[str]): Filter by facade type. Valid values: 'refrigerada', 'no_refrigerada'. Default: None (no filter).
    - sensor (Optional[str]): Filter by specific sensor name. Default: None (all sensors).
    - start (Optional[str]): Start date/time for the data range in ISO8601 format (e.g., '2023-01-01T00:00:00Z'). Default: None (no start date filter).
    - end (Optional[str]): End date/time for the data range in ISO8601 format (e.g., '2023-01-02T00:00:00Z'). Default: None (no end date filter).

    Returns:
    - tuple[str, bytes]: A tuple containing:
      - filename (str): The generated CSV filename, including facade ID, filters, and timestamp.
      - content (bytes): The CSV content encoded in UTF-8.

    Exceptions:
    - RuntimeError: Raised if the database connection pool is not initialized.
    - ValueError: Raised if no data is available for the specified parameters.
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

    sql += " ORDER BY ts ASC LIMIT 50000"

    try:
        # Acquire a database connection and execute the query
        async with pool.acquire() as conn:
            rows = await conn.fetch(sql, *params)

        # Check if data is available
        if not rows:
            raise ValueError("No data available for export")

        # Generate filename with timestamp and filters
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filters = []
        if facade_type:
            filters.append(facade_type)
        if sensor:
            filters.append(sensor.replace(" ", "_"))
        
        filter_str = "_".join(filters) if filters else "all"
        filename = f"facade_{facade_id}_{filter_str}_{timestamp}.csv"

        # Create CSV content in memory
        output = io.StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=["timestamp", "sensor_name", "value", "device_id", "facade_type"]
        )
        writer.writeheader()

        # Write each row to the CSV
        for row in rows:
            writer.writerow({
                "timestamp": row["ts"].isoformat() if hasattr(row["ts"], "isoformat") else str(row["ts"]),
                "sensor_name": row["sensor_name"],
                "value": row["value"],
                "device_id": row["device_id"],
                "facade_type": row["facade_type"]
            })

        # Encode CSV content to bytes
        csv_content = output.getvalue().encode("utf-8")
        return filename, csv_content

    except asyncpg.PostgresError as e:
        # Log the database error for debugging purposes
        print(f"❌ Error generating CSV: {e}")
        # Raise the exception to be handled by the caller
        raise
    except Exception as e:
        # Log unexpected errors for debugging purposes
        print(f"❌ Unexpected error: {e}")
        # Raise the exception to be handled by the caller
        raise


async def generate_comparison_csv_export(
    facade_id: str,
    sensor: str,
    start: Optional[str] = None,
    end: Optional[str] = None,
) -> tuple[str, bytes]:
    """
    Generates a CSV file comparing data for a specific sensor between refrigerated and non-refrigerated facades.

    HU17: Compare performance with and without refrigeration to validate hypotheses.

    Parameters:
    - facade_id (str): ID of the facade to compare. Required.
    - sensor (str): Name of the sensor to compare. Required.
    - start (Optional[str]): Start date/time for the data range in ISO8601 format (e.g., '2023-01-01T00:00:00Z'). Default: None (no start date filter).
    - end (Optional[str]): End date/time for the data range in ISO8601 format (e.g., '2023-01-02T00:00:00Z'). Default: None (no end date filter).

    Returns:
    - tuple[str, bytes]: A tuple containing:
      - filename (str): The generated CSV filename, including facade ID, sensor, and timestamp.
      - content (bytes): The CSV content encoded in UTF-8, with columns for timestamp, refrigerated, and non-refrigerated values.

    Exceptions:
    - RuntimeError: Raised if the database connection pool is not initialized.
    - ValueError: Raised if no data is available for comparison.
    - asyncpg.exceptions.PostgresError: Raised if a database query error occurs.
    """
    # Obtain the database connection pool
    pool = get_pool()
    if not pool:
        raise RuntimeError("Database connection pool not initialized")

    # Construct SQL query with dynamic conditions
    sql = """
        SELECT ts, facade_type, value, device_id
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

    sql += " ORDER BY ts ASC LIMIT 50000"

    try:
        # Acquire a database connection and execute the query
        async with pool.acquire() as conn:
            rows = await conn.fetch(sql, *params)

        # Check if data is available
        if not rows:
            raise ValueError("No data available for comparison")

        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"comparison_{facade_id}_{sensor}_{timestamp}.csv"

        # Group data by timestamp
        data_by_time = {}
        for row in rows:
            ts = row["ts"]
            if ts not in data_by_time:
                data_by_time[ts] = {}
            data_by_time[ts][row["facade_type"]] = row["value"]

        # Create CSV content in memory
        output = io.StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=["timestamp", "refrigerada", "no_refrigerada"]
        )
        writer.writeheader()

        # Write rows sorted by timestamp
        for ts in sorted(data_by_time.keys()):
            row_data = data_by_time[ts]
            writer.writerow({
                "timestamp": ts.isoformat() if hasattr(ts, "isoformat") else str(ts),
                "refrigerada": row_data.get("refrigerada", ""),
                "no_refrigerada": row_data.get("no_refrigerada", "")
            })

        # Encode CSV content to bytes
        csv_content = output.getvalue().encode("utf-8")
        return filename, csv_content

    except asyncpg.PostgresError as e:
        # Log the database error for debugging purposes
        print(f"❌ Error generating comparison CSV: {e}")
        # Raise the exception to be handled by the caller
        raise
    except Exception as e:
        # Log unexpected errors for debugging purposes
        print(f"❌ Unexpected error: {e}")
        # Raise the exception to be handled by the caller
        raise