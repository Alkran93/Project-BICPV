from fastapi import APIRouter, Path, Query, HTTPException
from typing import Optional
from ..services import temperature_service

router = APIRouter(prefix="/temperatures", tags=["temperatures"])


@router.get("/refrigerant-cycle/{facade_id}")
async def get_refrigerant_cycle(
    facade_id: str = Path(..., description="ID of the facade"),
    start: Optional[str] = Query(None, description="Start date/time in ISO8601 format"),
    end: Optional[str] = Query(None, description="End date/time in ISO8601 format"),
    limit: int = Query(500, ge=1, le=5000, description="Maximum number of records")
):
    """
    Retrieves temperature measurements for each point in the refrigeration cycle of a specific facade.

    HU10: View the refrigerant temperature at each point in the refrigeration cycle.

    The endpoint provides temperatures at the following points:
    - Expansion Valve
    - Compressor Inlet
    - Compressor Outlet
    - Condenser Outlet

    Parameters:
    - facade_id (str): ID of the facade to retrieve refrigeration cycle data for. Required.
    - start (Optional[str]): Start date/time for the data range in ISO8601 format (e.g., '2023-01-01T00:00:00Z'). Default: None (no start date filter).
    - end (Optional[str]): End date/time for the data range in ISO8601 format (e.g., '2023-01-02T00:00:00Z'). Default: None (no end date filter).
    - limit (int): Maximum number of records to return. Must be between 1 and 5000. Default: 500.

    Response:
    - JSON object containing refrigeration cycle temperature data (structure depends on temperature_service implementation, expected to include a 'cycle_points' key).
    - HTTP Status Codes:
      - 200: Successful response with refrigeration cycle temperature data.
      - 404: No refrigeration cycle data available for the specified facade or time range.
      - 500: Internal server error if the query fails.

    Errors:
    - HTTPException (404): Raised if no refrigeration cycle data is available for the specified parameters.
    - HTTPException (500): Raised if an unexpected error occurs while querying refrigeration cycle temperatures.
    """
    try:
        # Query refrigeration cycle temperatures from the temperature service
        result = await temperature_service.get_refrigerant_cycle_temperatures(
            facade_id, start=start, end=end, limit=limit
        )
        # Check if data is available
        if not result.get("cycle_points"):
            raise HTTPException(status_code=404, detail="No refrigeration cycle temperature data available")
        # Return the refrigeration cycle temperature data
        return result
    except HTTPException:
        raise
    except Exception as e:
        # Raise an HTTP exception for unexpected errors
        raise HTTPException(status_code=500, detail="Error retrieving refrigeration cycle temperatures")


@router.get("/exchanger/{facade_id}")
async def get_exchanger_temps(
    facade_id: str = Path(..., description="ID of the facade"),
    start: Optional[str] = Query(None, description="Start date/time in ISO8601 format"),
    end: Optional[str] = Query(None, description="End date/time in ISO8601 format"),
    limit: int = Query(500, ge=1, le=5000, description="Maximum number of records")
):
    """
    Retrieves water temperature measurements at the inlet and outlet of the heat exchanger for a specific facade.

    HU12: View the water temperature at the inlet and outlet of the heat exchanger.

    The endpoint provides:
    - Condenser water inlet temperature
    - Condenser water outlet temperature

    Parameters:
    - facade_id (str): ID of the facade to retrieve exchanger data for. Required.
    - start (Optional[str]): Start date/time for the data range in ISO8601 format (e.g., '2023-01-01T00:00:00Z'). Default: None (no start date filter).
    - end (Optional[str]): End date/time for the data range in ISO8601 format (e.g., '2023-01-02T00:00:00Z'). Default: None (no end date filter).
    - limit (int): Maximum number of records to return. Must be between 1 and 5000. Default: 500.

    Response:
    - JSON object containing heat exchanger temperature data (structure depends on temperature_service implementation, expected to include an 'exchanger_data' key).
    - HTTP Status Codes:
      - 200: Successful response with exchanger temperature data.
      - 404: No exchanger data available for the specified facade or time range.
      - 500: Internal server error if the query fails.

    Errors:
    - HTTPException (404): Raised if no exchanger data is available for the specified parameters.
    - HTTPException (500): Raised if an unexpected error occurs while querying exchanger temperatures.
    """
    try:
        # Query exchanger temperatures from the temperature service
        result = await temperature_service.get_exchanger_temperatures(
            facade_id, start=start, end=end, limit=limit
        )
        # Check if data is available
        if not result.get("exchanger_data"):
            raise HTTPException(status_code=404, detail="No exchanger temperature data available")
        # Return the exchanger temperature data
        return result
    except HTTPException:
        raise
    except Exception as e:
        # Raise an HTTP exception for unexpected errors
        raise HTTPException(status_code=500, detail="Error retrieving exchanger temperatures")


@router.get("/panels/{facade_id}")
async def get_panels_temps(
    facade_id: str = Path(..., description="ID of the facade"),
    panel_id: Optional[int] = Query(None, description="Panel ID (1-5) or None for all panels"),
    start: Optional[str] = Query(None, description="Start date/time in ISO8601 format"),
    end: Optional[str] = Query(None, description="End date/time in ISO8601 format"),
    limit: int = Query(500, ge=1, le=5000, description="Maximum number of records")
):
    """
    Retrieves inlet and outlet temperature measurements for one or all panels of a specific facade.

    If panel_id is specified (1-5), returns data for that specific panel. If None, returns data for all five panels.

    Parameters:
    - facade_id (str): ID of the facade to retrieve panel temperatures for. Required.
    - panel_id (Optional[int]): ID of the specific panel (1-5). Default: None (returns data for all panels).
    - start (Optional[str]): Start date/time for the data range in ISO8601 format (e.g., '2023-01-01T00:00:00Z'). Default: None (no start date filter).
    - end (Optional[str]): End date/time for the data range in ISO8601 format (e.g., '2023-01-02T00:00:00Z'). Default: None (no end date filter).
    - limit (int): Maximum number of records to return. Must be between 1 and 5000. Default: 500.

    Response:
    - JSON object containing panel temperature data (structure depends on temperature_service implementation, expected to include a 'panels' key).
    - HTTP Status Codes:
      - 200: Successful response with panel temperature data.
      - 400: Invalid panel_id (not between 1 and 5).
      - 404: No panel data available for the specified facade or panel.
      - 500: Internal server error if the query fails.

    Errors:
    - HTTPException (400): Raised if panel_id is provided but is not between 1 and 5.
    - HTTPException (404): Raised if no panel data is available for the specified parameters.
    - HTTPException (500): Raised if an unexpected error occurs while querying panel temperatures.
    """
    try:
        # Validate panel_id if provided
        if panel_id and (panel_id < 1 or panel_id > 5):
            raise HTTPException(status_code=400, detail="panel_id must be between 1 and 5")
        # Query panel temperatures from the temperature service
        result = await temperature_service.get_panel_temperatures(
            facade_id, panel_id=panel_id, start=start, end=end, limit=limit
        )
        # Check if data is available
        if not result.get("panels"):
            raise HTTPException(status_code=404, detail="No panel temperature data available")
        # Return the panel temperature data
        return result
    except HTTPException:
        raise
    except Exception as e:
        # Raise an HTTP exception for unexpected errors
        raise HTTPException(status_code=500, detail="Error retrieving panel temperatures")