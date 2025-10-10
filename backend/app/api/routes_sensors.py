from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from ..services import analytics_service

router = APIRouter(prefix="/sensors", tags=["sensors"])


@router.get("/all")
async def get_all_sensors(
    facade_type: Optional[str] = Query(None, description="Filter by facade type: 'refrigerada', 'no_refrigerada'"),
    limit: int = Query(100, ge=1, le=1000)
):
    """
    Retrieves a list of distinct registered sensors, optionally filtered by facade type.

    Parameters:
    - facade_type (Optional[str]): Filter by facade type. Valid values: 'refrigerada', 'no_refrigerada'. Default: None (no filter).
    - limit (int): Maximum number of sensors to return. Must be between 1 and 1000. Default: 100.

    Response:
    - JSON object with the following structure:
      - count (int): Number of sensors returned.
      - facade_type (str or null): The facade type filter applied, if any.
      - sensors (list): List of sensor records, each containing sensor details (structure depends on analytics_service implementation).
    - HTTP Status Codes:
      - 200: Successful response with sensor list.
      - 404: No sensors available for the specified criteria.
      - 500: Internal server error if the query fails.

    Errors:
    - HTTPException (404): Raised if no sensors are available for the specified criteria.
    - HTTPException (500): Raised if an unexpected error occurs while querying sensors.
    """
    try:
        # Query distinct sensors from the analytics service
        sensors = await analytics_service.get_all_sensors(limit=limit, facade_type=facade_type)
        # Check if sensors are available
        if not sensors:
            raise HTTPException(status_code=404, detail="No sensors available")
        # Construct and return the response with sensor data
        return {
            "count": len(sensors),
            "facade_type": facade_type,
            "sensors": sensors
        }
    except HTTPException:
        raise
    except Exception as e:
        # Raise an HTTP exception for unexpected errors
        raise HTTPException(status_code=500, detail="Error retrieving sensors")


@router.get("/average")
async def get_average(
    sensor_name: str = Query(..., description="Name of the sensor"),
    facade_type: Optional[str] = Query(None, description="Filter by facade type: 'refrigerada', 'no_refrigerada'")
):
    """
    Retrieves the historical average value for a specific sensor, optionally filtered by facade type.

    Parameters:
    - sensor_name (str): Name of the sensor to calculate the average for. Required.
    - facade_type (Optional[str]): Filter by facade type. Valid values: 'refrigerada', 'no_refrigerada'. Default: None (no filter).

    Response:
    - JSON object containing the sensor average (structure depends on analytics_service implementation, expected to include an 'average' key).
    - HTTP Status Codes:
      - 200: Successful response with the sensor average.
      - 404: No data available for the specified sensor.
      - 500: Internal server error if the query fails.

    Errors:
    - HTTPException (404): Raised if no data is available for the specified sensor.
    - HTTPException (500): Raised if an unexpected error occurs while querying the sensor average.
    """
    try:
        # Query the historical average for the specified sensor
        result = await analytics_service.get_sensor_average(
            sensor_name=sensor_name,
            facade_type=facade_type
        )
        # Check if data is available
        if not result.get("average"):
            raise HTTPException(status_code=404, detail=f"No data available for sensor '{sensor_name}'")
        # Return the sensor average data
        return result
    except HTTPException:
        raise
    except Exception as e:
        # Raise an HTTP exception for unexpected errors
        raise HTTPException(status_code=500, detail="Error retrieving sensor average")


@router.get("/environmental")
async def get_environmental_sensors():
    """
    Retrieves the list of available environmental sensors.

    HU05: Visualize environmental variables such as irradiance, wind speed, temperature, and ambient humidity.

    Response:
    - JSON object with the following structure:
      - count (int): Number of environmental sensors.
      - sensors (list): List of environmental sensor names or details (defined in analytics_service.ENVIRONMENTAL_SENSORS).
    - HTTP Status Codes:
      - 200: Successful response with environmental sensor list.
      - 500: Internal server error if the query fails.

    Errors:
    - HTTPException (500): Raised if an unexpected error occurs while retrieving environmental sensors.
    """
    try:
        # Import the predefined environmental sensors list
        from ..services.analytics_service import ENVIRONMENTAL_SENSORS
        # Construct and return the response with environmental sensor data
        return {
            "count": len(ENVIRONMENTAL_SENSORS),
            "sensors": ENVIRONMENTAL_SENSORS
        }
    except Exception as e:
        # Raise an HTTP exception for unexpected errors
        raise HTTPException(status_code=500, detail="Error retrieving environmental sensors")


@router.get("/refrigeration")
async def get_refrigeration_sensors():
    """
    Retrieves the list of sensors associated with the refrigeration cycle.

    Response:
    - JSON object with the following structure:
      - count (int): Number of refrigeration sensors.
      - sensors (list): List of refrigeration sensor names or details (defined in analytics_service.REFRIGERATION_SENSORS).
    - HTTP Status Codes:
      - 200: Successful response with refrigeration sensor list.
      - 500: Internal server error if the query fails.

    Errors:
    - HTTPException (500): Raised if an unexpected error occurs while retrieving refrigeration sensors.
    """
    try:
        # Import the predefined refrigeration sensors list
        from ..services.analytics_service import REFRIGERATION_SENSORS
        # Construct and return the response with refrigeration sensor data
        return {
            "count": len(REFRIGERATION_SENSORS),
            "sensors": REFRIGERATION_SENSORS
        }
    except Exception as e:
        # Raise an HTTP exception for unexpected errors
        raise HTTPException(status_code=500, detail="Error retrieving refrigeration sensors")