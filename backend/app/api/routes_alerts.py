from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from ..services import alerts_service

router = APIRouter(prefix="/alerts", tags=["alerts"])

@router.get("/errors")
async def get_sensor_errors(
    limit: int = Query(100, ge=1, le=1000),
    facade_type: Optional[str] = Query(None, description="Filter by facade type: 'refrigerada', 'no_refrigerada'"),
    hours: int = Query(24, ge=1, le=720, description="Time range in hours for recent errors")
):
    """
    Retrieves recent sensor errors (NULL or negative values) for monitoring sensor functionality.

    HU20: Query the status of sensors to verify their operation.
    HU15: Receive automatic alerts when sensor failures are detected.

    Parameters:
    - limit (int): Maximum number of error records to return. Must be between 1 and 1000. Default: 100.
    - facade_type (Optional[str]): Filter by facade type. Valid values: 'refrigerada', 'no_refrigerada'. Default: None (no filter).
    - hours (int): Time range in hours to consider for recent errors. Must be between 1 and 720. Default: 24.

    Response:
    - JSON object with the following structure:
      - count (int): Number of error records returned.
      - facade_type (str or null): The facade type filter applied, if any.
      - time_range_hours (int): The time range in hours used for the query.
      - errors (list): List of error records, each containing sensor error details (structure depends on alerts_service implementation).
    - HTTP Status Codes:
      - 200: Successful response with error records.
      - 500: Internal server error if the query fails.

    Errors:
    - HTTPException (500): Raised if an unexpected error occurs while querying sensor errors.
    """
    try:
        # Query sensor errors from the alerts service
        errors = await alerts_service.get_sensor_errors(limit, facade_type=facade_type, hours=hours)
        # Construct and return the response with error details
        return {
            "count": len(errors),
            "facade_type": facade_type,
            "time_range_hours": hours,
            "errors": errors
        }
    except Exception as e:
        # Raise an HTTP exception for unexpected errors
        raise HTTPException(status_code=500, detail="Error retrieving sensor errors")


@router.get("/anomalies")
async def get_anomalies(
    facade_id: Optional[str] = Query(None, description="ID of the facade (optional)"),
    facade_type: Optional[str] = Query(None, description="Filter by facade type: 'refrigerada', 'no_refrigerada'"),
    limit: int = Query(100, ge=1, le=1000),
    hours: int = Query(24, ge=1, le=720, description="Time range in hours for recent anomalies")
):
    """
    Retrieves sensor readings that deviate from expected ranges based on defined thresholds, identifying anomalous behavior.

    Parameters:
    - facade_id (Optional[str]): ID of the facade to filter anomalies. Default: None (no filter).
    - facade_type (Optional[str]): Filter by facade type. Valid values: 'refrigerada', 'no_refrigerada'. Default: None (no filter).
    - limit (int): Maximum number of anomaly records to return. Must be between 1 and 1000. Default: 100.
    - hours (int): Time range in hours to consider for recent anomalies. Must be between 1 and 720. Default: 24.

    Response:
    - JSON object with the following structure:
      - count (int): Number of anomaly records returned.
      - facade_id (str or null): The facade ID filter applied, if any.
      - facade_type (str or null): The facade type filter applied, if any.
      - time_range_hours (int): The time range in hours used for the query.
      - anomalies (list): List of anomaly records, each containing anomaly details (structure depends on alerts_service implementation).
    - HTTP Status Codes:
      - 200: Successful response with anomaly records.
      - 500: Internal server error if the query fails.

    Errors:
    - HTTPException (500): Raised if an unexpected error occurs while querying anomalies.
    """
    try:
        # Query anomalies from the alerts service based on thresholds
        anomalies = await alerts_service.get_anomalies_by_threshold(
            facade_id=facade_id,
            facade_type=facade_type,
            limit=limit,
            hours=hours
        )
        # Construct and return the response with anomaly details
        return {
            "count": len(anomalies),
            "facade_id": facade_id,
            "facade_type": facade_type,
            "time_range_hours": hours,
            "anomalies": anomalies
        }
    except Exception as e:
        # Raise an HTTP exception for unexpected errors
        raise HTTPException(status_code=500, detail="Error retrieving anomalies")


@router.get("/status/{facade_id}")
async def get_sensors_status(
    facade_id: str,
    facade_type: Optional[str] = Query(None, description="Filter by facade type: 'refrigerada', 'no_refrigerada'"),
    minutes: int = Query(30, ge=1, le=1440, description="Time in minutes to consider a sensor inactive if no data is reported")
):
    """
    Retrieves the status (active/inactive) of all sensors for a specified facade.

    HU20: Query the status of sensors to verify their operation.

    A sensor is considered inactive if it has not reported data within the specified time period.

    Parameters:
    - facade_id (str): ID of the facade to check sensor status for. Required.
    - facade_type (Optional[str]): Filter by facade type. Valid values: 'refrigerada', 'no_refrigerada'. Default: None (no filter).
    - minutes (int): Time in minutes to determine if a sensor is inactive. Must be between 1 and 1440. Default: 30.

    Response:
    - JSON object containing sensor status details (structure depends on alerts_service implementation).
    - HTTP Status Codes:
      - 200: Successful response with sensor status.
      - 500: Internal server error if the query fails.

    Errors:
    - HTTPException (500): Raised if an unexpected error occurs while querying sensor status.
    """
    try:
        # Query sensor status from the alerts service
        status = await alerts_service.get_sensor_status(
            facade_id=facade_id,
            facade_type=facade_type,
            minutes=minutes
        )
        # Return the sensor status response
        return status
    except Exception as e:
        # Raise an HTTP exception for unexpected errors
        raise HTTPException(status_code=500, detail="Error retrieving sensor status")


@router.get("/history")
async def get_alerts_history(
    limit: int = Query(100, ge=1, le=1000),
    facade_type: Optional[str] = Query(None, description="Filter by facade type: 'refrigerada', 'no_refrigerada'"),
    hours: int = Query(168, ge=1, le=2160, description="Time range in hours for alert history (default: 1 week)")
):
    """
    Retrieves a consolidated history of all alerts (errors and anomalies) generated by the system.

    HU21: View the history of alerts generated by the system.
    HU15: Receive automatic alerts when sensor failures are detected.

    Parameters:
    - limit (int): Maximum number of alert records to return. Must be between 1 and 1000. Default: 100.
    - facade_type (Optional[str]): Filter by facade type. Valid values: 'refrigerada', 'no_refrigerada'. Default: None (no filter).
    - hours (int): Time range in hours for alert history. Must be between 1 and 2160. Default: 168 (1 week).

    Response:
    - JSON object with the following structure:
      - count (int): Number of alert records returned.
      - facade_type (str or null): The facade type filter applied, if any.
      - time_range_hours (int): The time range in hours used for the query.
      - alerts (list): List of alert records, each containing alert details (structure depends on alerts_service implementation).
    - HTTP Status Codes:
      - 200: Successful response with alert history.
      - 500: Internal server error if the query fails.

    Errors:
    - HTTPException (500): Raised if an unexpected error occurs while querying alert history.
    """
    try:
        # Query alert history from the alerts service
        history = await alerts_service.get_alert_history(
            limit=limit,
            facade_type=facade_type,
            hours=hours
        )
        # Construct and return the response with alert history details
        return {
            "count": len(history),
            "facade_type": facade_type,
            "time_range_hours": hours,
            "alerts": history
        }
    except Exception as e:
        # Raise an HTTP exception for unexpected errors
        raise HTTPException(status_code=500, detail="Error retrieving alert history")