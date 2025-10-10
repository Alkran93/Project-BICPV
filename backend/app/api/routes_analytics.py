from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from ..services import analytics_service

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/environment/{facade_id}")
async def get_environmental_variables(
    facade_id: str,
    facade_type: Optional[str] = Query(None, description="Filter by facade type: 'refrigerada', 'no_refrigerada'")
):
    """
    Retrieves average environmental variables such as irradiance, wind speed, ambient temperature, and humidity for a specific facade.

    HU05: Visualize environmental variables including irradiance, wind speed, temperature, and ambient humidity.

    Parameters:
    - facade_id (str): ID of the facade to retrieve environmental data for. Required.
    - facade_type (Optional[str]): Filter by facade type. Valid values: 'refrigerada', 'no_refrigerada'. Default: None (no filter).

    Response:
    - JSON object with the following structure:
      - facade_id (str): The ID of the facade queried.
      - facade_type (str or null): The facade type filter applied, if any.
      - environmental_variables (list): List of environmental variable records, each containing details such as irradiance, wind speed, temperature, and humidity (structure depends on analytics_service implementation).
    - HTTP Status Codes:
      - 200: Successful response with environmental data.
      - 404: No environmental data available for the specified facade.
      - 500: Internal server error if the query fails.

    Errors:
    - HTTPException (404): Raised if no environmental data is available for the specified facade.
    - HTTPException (500): Raised if an unexpected error occurs while querying environmental variables.
    """
    try:
        # Query environmental variables from the analytics service
        result = await analytics_service.get_environmental_variables(facade_id, facade_type=facade_type)
        # Check if data is available
        if not result:
            raise HTTPException(status_code=404, detail="No environmental data available")
        # Construct and return the response with environmental data
        return {
            "facade_id": facade_id,
            "facade_type": facade_type,
            "environmental_variables": result
        }
    except HTTPException:
        raise
    except Exception as e:
        # Raise an HTTP exception for unexpected errors
        raise HTTPException(status_code=500, detail="Error retrieving environmental variables")


@router.get("/refrigeration/{facade_id}")
async def get_refrigeration_variables(
    facade_id: str,
    start: Optional[str] = Query(None, description="Start date in ISO8601 format"),
    end: Optional[str] = Query(None, description="End date in ISO8601 format"),
    limit: int = Query(500, ge=1, description="Maximum number of records to return")
):
    """
    Retrieves average historical refrigerant cycle temperatures for a specific refrigerated facade.

    HU10: Monitor the refrigerant temperature at each point in the refrigeration cycle.

    Only applicable to refrigerated facades.

    Parameters:
    - facade_id (str): ID of the refrigerated facade to retrieve data for. Required.
    - start (Optional[str]): Start date for the data range in ISO8601 format (e.g., '2023-01-01T00:00:00Z'). Default: None (no start date filter).
    - end (Optional[str]): End date for the data range in ISO8601 format (e.g., '2023-01-02T00:00:00Z'). Default: None (no end date filter).
    - limit (int): Maximum number of records to return. Must be at least 1. Default: 500.

    Response:
    - JSON object with the following structure:
      - facade_id (str): The ID of the facade queried.
      - facade_type (str): Always 'refrigerada' as this endpoint is specific to refrigerated facades.
      - refrigeration_variables (list): List of refrigeration cycle temperature records (structure depends on analytics_service implementation).
    - HTTP Status Codes:
      - 200: Successful response with refrigeration data.
      - 404: No refrigeration data available for the specified facade or time range.
      - 500: Internal server error if the query fails.

    Errors:
    - HTTPException (404): Raised if no refrigeration data is available for the specified facade or time range.
    """
    try:
        # Query refrigeration cycle temperatures from the analytics service
        result = await analytics_service.get_refrigerant_cycle_temperatures(
            facade_id, start=start, end=end, limit=limit
        )
        # Check if data is available
        if not result:
            raise HTTPException(status_code=404, detail="No refrigeration data available")
        # Construct and return the response with refrigeration data
        return {
            "facade_id": facade_id,
            "facade_type": "refrigerada",
            "refrigeration_variables": result
        }
    except HTTPException:
        raise
    except Exception as e:
        # Raise an HTTP exception for unavailable data or unexpected errors
        raise HTTPException(status_code=404, detail="No refrigeration data available")


@router.get("/compare/{facade_id}")
async def compare_facade_types(
    facade_id: str,
    sensor_name: Optional[str] = Query(None, description="Specific sensor to filter (optional)")
):
    """
    Compares average performance metrics (e.g., refrigerant and water temperatures) between refrigerated and non-refrigerated facades.

    HU13: Visualize a comparative graph of refrigerant and water temperatures.
    HU17: Compare performance with and without refrigeration to validate hypotheses.

    Parameters:
    - facade_id (str): ID of the facade to compare. Required.
    - sensor_name (Optional[str]): Name of a specific sensor to filter comparison data. Default: None (no sensor filter).

    Response:
    - JSON object with the following structure:
      - facade_id (str): The ID of the facade queried.
      - sensor_filter (str or null): The sensor name filter applied, if any.
      - comparison (list): List of comparison records between facade types (structure depends on analytics_service implementation).
    - HTTP Status Codes:
      - 200: Successful response with comparison data.
      - 404: No comparison data available for the specified facade or sensor.
      - 500: Internal server error if the query fails.

    Errors:
    - HTTPException (404): Raised if no comparison data is available for the specified facade or sensor.
    - HTTPException (500): Raised if an unexpected error occurs while comparing facade types.
    """
    try:
        # Query comparison data between facade types from the analytics service
        result = await analytics_service.compare_facade_types_average(facade_id, sensor_name=sensor_name)
        # Check if data is available
        if not result:
            raise HTTPException(status_code=404, detail="No comparison data available")
        # Construct and return the response with comparison data
        return {
            "facade_id": facade_id,
            "sensor_filter": sensor_name,
            "comparison": result
        }
    except HTTPException:
        raise
    except Exception as e:
        # Raise an HTTP exception for unexpected errors
        raise HTTPException(status_code=500, detail="Error comparing facade types")


@router.get("/sensors")
async def get_sensors_by_type(
    facade_type: Optional[str] = Query(None, description="Filter by facade type: 'refrigerada', 'no_refrigerada'"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of sensors to return")
):
    """
    Retrieves a list of available sensors, optionally filtered by facade type.

    Parameters:
    - facade_type (Optional[str]): Filter by facade type. Valid values: 'refrigerada', 'no_refrigerada'. Default: None (no filter).
    - limit (int): Maximum number of sensors to return. Must be between 1 and 1000. Default: 100.

    Response:
    - JSON object with the following structure:
      - facade_type (str or null): The facade type filter applied, if any.
      - count (int): Number of sensor records returned.
      - sensors (list): List of sensor records, each containing sensor details (structure depends on analytics_service implementation).
    - HTTP Status Codes:
      - 200: Successful response with sensor list.
      - 500: Internal server error if the query fails.

    Errors:
    - HTTPException (500): Raised if an unexpected error occurs while querying sensors.
    """
    try:
        # Query available sensors from the analytics service
        sensors = await analytics_service.get_all_sensors(limit=limit, facade_type=facade_type)
        # Construct and return the response with sensor data
        return {
            "facade_type": facade_type,
            "count": len(sensors),
            "sensors": sensors
        }
    except Exception as e:
        # Raise an HTTP exception for unexpected errors
        raise HTTPException(status_code=500, detail="Error retrieving sensors")