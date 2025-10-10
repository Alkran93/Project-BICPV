from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from ..services import storage_controller, analytics_service

router = APIRouter(prefix="/facades", tags=["facades"])


@router.get("/")
async def list_facades():
    """
    Retrieves a list of all available facades with their types for an overview comparison.

    HU01: View an overview of both facades to compare their current status.

    Response:
    - JSON object with the following structure:
      - count (int): Number of facades returned.
      - facades (list): List of facade records, each containing facade details (structure depends on storage_controller implementation).
    - HTTP Status Codes:
      - 200: Successful response with the list of facades.
      - 404: No facades available.
      - 500: Internal server error if the query fails.

    Errors:
    - HTTPException (404): Raised if no facades are available.
    - HTTPException (500): Raised if an unexpected error occurs while querying facades.
    """
    try:
        # Query all available facades from the storage controller
        facades = await storage_controller.fetch_facades()
        # Check if any facades are available
        if not facades:
            raise HTTPException(status_code=404, detail="No facades available")
        # Construct and return the response with facade data
        return {"count": len(facades), "facades": facades}
    except HTTPException:
        raise
    except Exception as e:
        # Raise an HTTP exception for unexpected errors
        raise HTTPException(status_code=500, detail="Error retrieving facades")


@router.get("/{facade_id}")
async def get_facade_overview(
    facade_id: str,
    facade_type: Optional[str] = Query(None, description="Filter by facade type: 'refrigerada', 'no_refrigerada'")
):
    """
    Retrieves general information and the latest measurements for a specific facade.

    HU02: Select a facade to view its data individually.

    Parameters:
    - facade_id (str): ID of the facade to retrieve data for. Required.
    - facade_type (Optional[str]): Filter by facade type. Valid values: 'refrigerada', 'no_refrigerada'. Default: None (no filter).

    Response:
    - JSON object with the following structure:
      - facade_id (str): The ID of the facade queried.
      - available_types (list): List of available facade types for the specified facade ID.
      - current_readings (list): List of the latest measurement records for the facade (structure depends on storage_controller implementation).
    - HTTP Status Codes:
      - 200: Successful response with facade data.
      - 404: No data available for the specified facade.
      - 500: Internal server error if the query fails.

    Errors:
    - HTTPException (404): Raised if no data is available for the specified facade.
    - HTTPException (500): Raised if an unexpected error occurs while querying the facade.
    """
    try:
        # Query the latest measurements for the facade
        latest = await storage_controller.fetch_latest_by_facade(facade_id, facade_type=facade_type)
        # Check if data is available
        if not latest:
            raise HTTPException(status_code=404, detail=f"No data available for facade {facade_id}")
        # Query available facade types
        types = await storage_controller.fetch_facade_types(facade_id)
        # Construct and return the response with facade overview
        return {
            "facade_id": facade_id,
            "available_types": types,
            "current_readings": latest
        }
    except HTTPException:
        raise
    except Exception as e:
        # Raise an HTTP exception for unexpected errors
        raise HTTPException(status_code=500, detail="Error retrieving facade")


@router.get("/{facade_id}/types")
async def get_facade_types(facade_id: str):
    """
    Retrieves the available facade types for a specific facade ID.

    Parameters:
    - facade_id (str): ID of the facade to retrieve types for. Required.

    Response:
    - JSON object with the following structure:
      - facade_id (str): The ID of the facade queried.
      - types (list): List of facade types (e.g., ['refrigerada', 'no_refrigerada']).
    - HTTP Status Codes:
      - 200: Successful response with facade types.
      - 404: No data available for the specified facade.
      - 500: Internal server error if the query fails.

    Errors:
    - HTTPException (404): Raised if no data is available for the specified facade.
    - HTTPException (500): Raised if an unexpected error occurs while querying facade types.
    """
    try:
        # Query available facade types from the storage controller
        types = await storage_controller.fetch_facade_types(facade_id)
        # Check if data is available
        if not types:
            raise HTTPException(status_code=404, detail=f"No data available for facade {facade_id}")
        # Construct and return the response with facade types
        return {"facade_id": facade_id, "types": types}
    except HTTPException:
        raise
    except Exception as e:
        # Raise an HTTP exception for unexpected errors
        raise HTTPException(status_code=500, detail="Error retrieving facade types")


@router.get("/{facade_id}/sensors")
async def get_facade_sensors(
    facade_id: str,
    facade_type: Optional[str] = Query(None, description="Filter by facade type: 'refrigerada', 'no_refrigerada'")
):
    """
    Retrieves the list of sensors for a specific facade, optionally filtered by facade type.

    HU03: View the individual temperature of the 15 sensors in the non-refrigerated facade.

    Parameters:
    - facade_id (str): ID of the facade to retrieve sensors for. Required.
    - facade_type (Optional[str]): Filter by facade type. Valid values: 'refrigerada', 'no_refrigerada'. Default: None (no filter).

    Response:
    - JSON object with the following structure:
      - facade_id (str): The ID of the facade queried.
      - facade_type (str or null): The facade type filter applied, if any.
      - count (int): Number of sensors returned.
      - sensors (list): List of sensor names or records (structure depends on storage_controller implementation).
    - HTTP Status Codes:
      - 200: Successful response with sensor list.
      - 404: No sensors available for the specified facade.
      - 500: Internal server error if the query fails.

    Errors:
    - HTTPException (404): Raised if no sensors are available for the specified facade.
    - HTTPException (500): Raised if an unexpected error occurs while querying sensors.
    """
    try:
        # Check if facade_type filter is provided
        if facade_type:
            # Query sensors specific to the facade type
            sensors = await storage_controller.fetch_sensors_by_facade_type(facade_id, facade_type)
        else:
            # Query all latest readings for the facade
            all_readings = await storage_controller.fetch_latest_by_facade(facade_id)
            # Extract unique sensor names from readings
            sensors = list(set(r["sensor_name"] for r in all_readings))
        # Check if sensors are available
        if not sensors:
            raise HTTPException(status_code=404, detail=f"No sensors available for facade {facade_id}")
        # Construct and return the response with sensor data
        return {
            "facade_id": facade_id,
            "facade_type": facade_type,
            "count": len(sensors),
            "sensors": sensors
        }
    except HTTPException:
        raise
    except Exception as e:
        # Raise an HTTP exception for unexpected errors
        raise HTTPException(status_code=500, detail="Error retrieving sensors")


@router.get("/{facade_id}/variables")
async def get_facade_variables(
    facade_id: str,
    facade_type: Optional[str] = Query(None, description="Filter by facade type: 'refrigerada', 'no_refrigerada'"),
    sensor: Optional[str] = Query(None, description="Specific sensor to filter (optional)"),
    start: Optional[str] = Query(None, description="Start date/time in ISO8601 format"),
    end: Optional[str] = Query(None, description="End date/time in ISO8601 format"),
    limit: int = Query(500, ge=1, le=5000),
):
    """
    Retrieves measurements for a specific facade with optional filters for facade type, sensor, and time range.

    Parameters:
    - facade_id (str): ID of the facade to retrieve measurements for. Required.
    - facade_type (Optional[str]): Filter by facade type. Valid values: 'refrigerada', 'no_refrigerada'. Default: None (no filter).
    - sensor (Optional[str]): Name of a specific sensor to filter measurements. Default: None (no sensor filter).
    - start (Optional[str]): Start date/time for the data range in ISO8601 format (e.g., '2023-01-01T00:00:00Z'). Default: None (no start date filter).
    - end (Optional[str]): End date/time for the data range in ISO8601 format (e.g., '2023-01-02T00:00:00Z'). Default: None (no end date filter).
    - limit (int): Maximum number of measurement records to return. Must be between 1 and 5000. Default: 500.

    Response:
    - JSON object with the following structure:
      - facade_id (str): The ID of the facade queried.
      - facade_type (str or null): The facade type filter applied, if any.
      - sensor_filter (str or null): The sensor name filter applied, if any.
      - count (int): Number of measurement records returned.
      - measurements (list): List of measurement records (structure depends on storage_controller implementation).
    - HTTP Status Codes:
      - 200: Successful response with measurement data.
      - 500: Internal server error if the query fails.

    Errors:
    - HTTPException (500): Raised if an unexpected error occurs while querying measurements.
    """
    try:
        # Query measurements with specified filters
        measurements = await storage_controller.fetch_measurements(
            facade_id, sensor=sensor, facade_type=facade_type, start=start, end=end, limit=limit
        )
        # Construct and return the response with measurement data
        return {
            "facade_id": facade_id,
            "facade_type": facade_type,
            "sensor_filter": sensor,
            "count": len(measurements),
            "measurements": measurements
        }
    except Exception as e:
        # Raise an HTTP exception for unexpected errors
        raise HTTPException(status_code=500, detail="Error retrieving measurements")


@router.get("/{facade_id}/latest")
async def get_facade_latest(
    facade_id: str,
    facade_type: Optional[str] = Query(None, description="Filter by facade type: 'refrigerada', 'no_refrigerada'")
):
    """
    Retrieves the latest measurement for each sensor of a specific facade.

    Parameters:
    - facade_id (str): ID of the facade to retrieve latest measurements for. Required.
    - facade_type (Optional[str]): Filter by facade type. Valid values: 'refrigerada', 'no_refrigerada'. Default: None (no filter).

    Response:
    - JSON object with the following structure:
      - facade_id (str): The ID of the facade queried.
      - facade_type (str or null): The facade type filter applied, if any.
      - latest_readings (list): List of the latest measurement records for each sensor (structure depends on storage_controller implementation).
    - HTTP Status Codes:
      - 200: Successful response with latest measurements.
      - 404: No recent data available for the specified facade.
      - 500: Internal server error if the query fails.

    Errors:
    - HTTPException (404): Raised if no recent data is available for the specified facade.
    - HTTPException (500): Raised if an unexpected error occurs while querying latest measurements.
    """
    try:
        # Query the latest measurements for the facade
        latest = await storage_controller.fetch_latest_by_facade(facade_id, facade_type=facade_type)
        # Check if data is available
        if not latest:
            raise HTTPException(status_code=404, detail="No recent data available")
        # Construct and return the response with latest measurements
        return {
            "facade_id": facade_id,
            "facade_type": facade_type,
            "latest_readings": latest
        }
    except HTTPException:
        raise
    except Exception as e:
        # Raise an HTTP exception for unexpected errors
        raise HTTPException(status_code=500, detail="Error retrieving latest measurements")


@router.get("/{facade_id}/average")
async def get_facade_average(
    facade_id: str,
    facade_type: Optional[str] = Query(None, description="Filter by facade type: 'refrigerada', 'no_refrigerada'")
):
    """
    Retrieves the average values of all variables for a specific facade.

    HU08: View a graph of the average temperatures for both facades.
    HU04: View the average temperature per panel in the non-refrigerated facade.

    Parameters:
    - facade_id (str): ID of the facade to calculate averages for. Required.
    - facade_type (Optional[str]): Filter by facade type. Valid values: 'refrigerada', 'no_refrigerada'. Default: None (no filter).

    Response:
    - JSON object with the following structure:
      - facade_id (str): The ID of the facade queried.
      - facade_type (str or null): The facade type filter applied, if any.
      - averages (list): List of average values for variables (structure depends on analytics_service implementation).
    - HTTP Status Codes:
      - 200: Successful response with average data.
      - 404: No data available to calculate averages.
      - 500: Internal server error if the query fails.

    Errors:
    - HTTPException (404): Raised if no data is available to calculate averages.
    - HTTPException (500): Raised if an unexpected error occurs while querying averages.
    """
    try:
        # Query average values from the analytics service
        averages = await analytics_service.get_facade_average(facade_id, facade_type=facade_type)
        # Check if data is available
        if not averages:
            raise HTTPException(status_code=404, detail="No data available to calculate averages")
        # Construct and return the response with average data
        return {
            "facade_id": facade_id,
            "facade_type": facade_type,
            "averages": averages
        }
    except HTTPException:
        raise
    except Exception as e:
        # Raise an HTTP exception for unexpected errors
        raise HTTPException(status_code=500, detail="Error retrieving averages")


@router.get("/{facade_id}/compare")
async def compare_facade_types(
    facade_id: str,
    sensor: str = Query(..., description="Name of the sensor to compare"),
    start: Optional[str] = Query(None, description="Start date/time in ISO8601 format"),
    end: Optional[str] = Query(None, description="End date/time in ISO8601 format"),
    limit: int = Query(500, ge=1, le=5000)
):
    """
    Compares measurements for a specific sensor between refrigerated and non-refrigerated facades.

    HU13: View a comparative graph of refrigerant and water temperatures in the heat exchanger.
    HU17: Compare performance with and without refrigeration to validate hypotheses.

    Returns two arrays: one for each facade type.

    Parameters:
    - facade_id (str): ID of the facade to compare. Required.
    - sensor (str): Name of the sensor to compare. Required.
    - start (Optional[str]): Start date/time for the data range in ISO8601 format (e.g., '2023-01-01T00:00:00Z'). Default: None (no start date filter).
    - end (Optional[str]): End date/time for the data range in ISO8601 format (e.g., '2023-01-02T00:00:00Z'). Default: None (no end date filter).
    - limit (int): Maximum number of measurement records to return. Must be between 1 and 5000. Default: 500.

    Response:
    - JSON object with the following structure:
      - facade_id (str): The ID of the facade queried.
      - sensor (str): The name of the sensor being compared.
      - comparison (dict): Dictionary with two keys, 'refrigerada' and 'no_refrigerada', each containing a list of measurement records (structure depends on storage_controller implementation).
    - HTTP Status Codes:
      - 200: Successful response with comparison data.
      - 404: No data available for comparison.
      - 500: Internal server error if the query fails.

    Errors:
    - HTTPException (404): Raised if no data is available for comparison.
    - HTTPException (500): Raised if an unexpected error occurs while comparing facade types.
    """
    try:
        # Query comparison data for the specified sensor and facade types
        comparison = await storage_controller.compare_facade_types(
            facade_id, sensor, start=start, end=end, limit=limit
        )
        # Check if any data is available for either facade type
        if not comparison.get("refrigerada") and not comparison.get("no_refrigerada"):
            raise HTTPException(status_code=404, detail="No data available for comparison")
        # Construct and return the response with comparison data
        return {
            "facade_id": facade_id,
            "sensor": sensor,
            "comparison": comparison
        }
    except HTTPException:
        raise
    except Exception as e:
        # Raise an HTTP exception for unexpected errors
        raise HTTPException(status_code=500, detail="Error comparing facade types")