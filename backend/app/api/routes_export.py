from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import StreamingResponse
from typing import Optional
import io
from ..services import export_service

router = APIRouter(prefix="/exports", tags=["exports"])


@router.get("/csv/facade/{facade_id}")
async def export_facade_csv(
    facade_id: str,
    facade_type: Optional[str] = Query(None, description="Filter by facade type: 'refrigerada', 'no_refrigerada'"),
    sensor: Optional[str] = Query(None, description="Specific sensor to filter (optional)"),
    start: Optional[str] = Query(None, description="Start date in ISO8601 format"),
    end: Optional[str] = Query(None, description="End date in ISO8601 format"),
):
    """
    Exports facade data in CSV format for analysis in external tools.

    HU18: Export data in CSV format for analysis in other tools.

    Supports filtering by facade type, specific sensor, and time range.

    Parameters:
    - facade_id (str): ID of the facade to export data for. Required.
    - facade_type (Optional[str]): Filter by facade type. Valid values: 'refrigerada', 'no_refrigerada'. Default: None (no filter).
    - sensor (Optional[str]): Name of a specific sensor to filter data. Default: None (no sensor filter).
    - start (Optional[str]): Start date for the data range in ISO8601 format (e.g., '2023-01-01T00:00:00Z'). Default: None (no start date filter).
    - end (Optional[str]): End date for the data range in ISO8601 format (e.g., '2023-01-02T00:00:00Z'). Default: None (no end date filter).

    Response:
    - File: CSV file containing facade data, returned as a StreamingResponse.
      - File type: text/csv
      - Encoding: UTF-8
      - Content-Disposition: attachment; filename={generated_filename}
    - HTTP Status Codes:
      - 200: Successful response with CSV file.
      - 404: No data available for the specified facade, sensor, or time range.
      - 500: Internal server error if the CSV generation fails.

    Errors:
    - HTTPException (404): Raised if no data is available for the specified parameters.
    - HTTPException (500): Raised if an unexpected error occurs during CSV generation.
    """
    try:
        # Generate CSV content using the export service
        filename, csv_content = await export_service.generate_csv_export(
            facade_id=facade_id,
            facade_type=facade_type,
            sensor=sensor,
            start=start,
            end=end
        )
        # Return the CSV file as a streaming response
        return StreamingResponse(
            io.BytesIO(csv_content),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except ValueError as e:
        # Raise an HTTP exception for invalid input or no data
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        # Log the error for debugging purposes
        print(f"❌ Error generating CSV for facade {facade_id}: {e}")
        # Raise an HTTP exception for unexpected errors
        raise HTTPException(status_code=500, detail="Error generating CSV file")


@router.get("/csv/compare/{facade_id}")
async def export_comparison_csv(
    facade_id: str,
    sensor: str = Query(..., description="Sensor to compare"),
    start: Optional[str] = Query(None, description="Start date in ISO8601 format"),
    end: Optional[str] = Query(None, description="End date in ISO8601 format"),
):
    """
    Exports a comparative CSV file containing data for a specific sensor, comparing refrigerated and non-refrigerated facades.

    Parameters:
    - facade_id (str): ID of the facade to compare. Required.
    - sensor (str): Name of the sensor to compare. Required.
    - start (Optional[str]): Start date for the data range in ISO8601 format (e.g., '2023-01-01T00:00:00Z'). Default: None (no start date filter).
    - end (Optional[str]): End date for the data range in ISO8601 format (e.g., '2023-01-02T00:00:00Z'). Default: None (no end date filter).

    Response:
    - File: CSV file containing comparative data, returned as a StreamingResponse.
      - File type: text/csv
      - Encoding: UTF-8
      - Content-Disposition: attachment; filename={generated_filename}
    - HTTP Status Codes:
      - 200: Successful response with CSV file.
      - 404: No data available for the specified facade, sensor, or time range.
      - 500: Internal server error if the CSV generation fails.

    Errors:
    - HTTPException (404): Raised if no data is available for the specified parameters.
    - HTTPException (500): Raised if an unexpected error occurs during CSV generation.
    """
    try:
        # Generate comparative CSV content using the export service
        filename, csv_content = await export_service.generate_comparison_csv_export(
            facade_id=facade_id,
            sensor=sensor,
            start=start,
            end=end
        )
        # Return the CSV file as a streaming response
        return StreamingResponse(
            io.BytesIO(csv_content),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except ValueError as e:
        # Raise an HTTP exception for invalid input or no data
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        # Log the error for debugging purposes
        print(f"❌ Error generating comparative CSV for facade {facade_id}, sensor {sensor}: {e}")
        # Raise an HTTP exception for unexpected errors
        raise HTTPException(status_code=500, detail="Error generating CSV file")