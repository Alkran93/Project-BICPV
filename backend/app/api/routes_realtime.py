from fastapi import APIRouter, Path, Query, HTTPException
from typing import Optional
from ..services import cache_controller

router = APIRouter(prefix="/realtime", tags=["realtime"])


@router.get("/facades")
async def get_all_realtime():
    """
    Retrieves real-time data for all available facades to enable comparison of their current status.

    HU01: View an overview of both facades to compare their current status.

    Response:
    - JSON object containing real-time data for all facades (structure depends on cache_controller implementation).
    - HTTP Status Codes:
      - 200: Successful response with real-time facade data.
      - 500: Internal server error if the query fails.

    Errors:
    - HTTPException (500): Raised if an unexpected error occurs while querying real-time data for all facades.
    """
    try:
        # Query real-time data for all facades from the cache controller
        data = await cache_controller.get_all_facades_latest()
        # Return the real-time facade data
        return data
    except Exception as e:
        # Raise an HTTP exception for unexpected errors
        raise HTTPException(status_code=500, detail="Error retrieving real-time data for all facades")


@router.get("/facades/{facade_id}")
async def get_realtime_facade(
    facade_id: str = Path(..., description="ID of the facade"),
    facade_type: Optional[str] = Query(None, description="Filter by facade type: 'refrigerada', 'no_refrigerada'")
):
    """
    Retrieves the most recent real-time data for all sensors of a specific facade.

    HU02: Select a facade to view its data individually.

    Parameters:
    - facade_id (str): ID of the facade to retrieve real-time data for. Required.
    - facade_type (Optional[str]): Filter by facade type. Valid values: 'refrigerada', 'no_refrigerada'. Default: None (no filter).

    Response:
    - JSON object with real-time data (structure depends on cache_controller implementation, expected to include a 'data' key).
    - HTTP Status Codes:
      - 200: Successful response with real-time facade data.
      - 404: No real-time data available for the specified facade.
      - 500: Internal server error if the query fails.

    Errors:
    - HTTPException (404): Raised if no real-time data is available for the specified facade.
    - HTTPException (500): Raised if an unexpected error occurs while querying real-time data.
    """
    try:
        # Query real-time data for the specified facade
        data = await cache_controller.get_latest_facade(facade_id, facade_type=facade_type)
        # Check if data is available
        if not data.get("data"):
            raise HTTPException(status_code=404, detail=f"No real-time data available for facade {facade_id}")
        # Return the real-time facade data
        return data
    except HTTPException:
        raise
    except Exception as e:
        # Raise an HTTP exception for unexpected errors
        raise HTTPException(status_code=500, detail="Error retrieving real-time facade data")


@router.get("/facades/{facade_id}/sensor/{sensor_name}")
async def get_realtime_sensor(
    facade_id: str = Path(..., description="ID of the facade"),
    sensor_name: str = Path(..., description="Name of the sensor"),
    facade_type: Optional[str] = Query(None, description="Filter by facade type: 'refrigerada', 'no_refrigerada'")
):
    """
    Retrieves the most recent real-time value for a specific sensor of a facade.

    Parameters:
    - facade_id (str): ID of the facade to retrieve sensor data for. Required.
    - sensor_name (str): Name of the sensor to retrieve data for. Required.
    - facade_type (Optional[str]): Filter by facade type. Valid values: 'refrigerada', 'no_refrigerada'. Default: None (no filter).

    Response:
    - JSON object containing the sensor value (structure depends on cache_controller implementation, expected to include a 'value' key).
    - HTTP Status Codes:
      - 200: Successful response with real-time sensor data.
      - 404: No data available for the specified sensor.
      - 500: Internal server error if the query fails.

    Errors:
    - HTTPException (404): Raised if no data is available for the specified sensor.
    - HTTPException (500): Raised if an unexpected error occurs while querying sensor data.
    """
    try:
        # Query real-time data for the specified sensor
        data = await cache_controller.get_sensor_value(facade_id, sensor_name, facade_type=facade_type)
        # Check if data is available
        if not data.get("value"):
            raise HTTPException(status_code=404, detail=f"No data available for sensor {sensor_name}")
        # Return the real-time sensor data
        return data
    except HTTPException:
        raise
    except Exception as e:
        # Raise an HTTP exception for unexpected errors
        raise HTTPException(status_code=500, detail="Error retrieving real-time sensor data")


@router.get("/facades/{facade_id}/compare")
async def get_realtime_comparison(
    facade_id: str = Path(..., description="ID of the facade")
):
    """
    Compares real-time data between refrigerated and non-refrigerated facades for a specific facade ID.

    HU01: View an overview of both facades to compare their current status.
    HU17: Compare performance with and without refrigeration to validate hypotheses.

    Parameters:
    - facade_id (str): ID of the facade to compare. Required.

    Response:
    - JSON object containing real-time comparison data between facade types (structure depends on cache_controller implementation).
    - HTTP Status Codes:
      - 200: Successful response with comparison data.
      - 500: Internal server error if the query fails.

    Errors:
    - HTTPException (500): Raised if an unexpected error occurs while comparing facade types in real time.
    """
    try:
        # Query real-time comparison data for the specified facade
        data = await cache_controller.get_facade_type_comparison(facade_id)
        # Return the comparison data
        return data
    except Exception as e:
        # Raise an HTTP exception for unexpected errors
        raise HTTPException(status_code=500, detail="Error comparing facade types in real time")