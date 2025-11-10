"""
PDF Report Routes
Provides endpoints for generating PDF reports with charts.

HU19: Generate PDF reports with charts.
"""
from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import Response
from typing import Optional
from ..services import pdf_service

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/pdf/facade/{facade_id}")
async def get_facade_pdf_report(
    facade_id: str,
    facade_type: Optional[str] = Query(None, description="Filter by facade type: 'refrigerada', 'no_refrigerada'"),
    start: Optional[str] = Query(None, description="Start date in ISO8601 format"),
    end: Optional[str] = Query(None, description="End date in ISO8601 format")
):
    """
    Generates a comprehensive PDF report for a specific facade with charts and statistics.

    HU19: Generate PDF reports with charts.

    Parameters:
    - facade_id (str): ID of the facade. Required.
    - facade_type (Optional[str]): Filter by facade type. Default: None.
    - start (Optional[str]): Start date/time for report period. Default: None.
    - end (Optional[str]): End date/time for report period. Default: None.

    Returns:
    - File: PDF report as binary response.

    Exceptions:
    - HTTPException (404): Insufficient data for report generation.
    - HTTPException (500): Error generating PDF report.
    """
    try:
        pdf_bytes = await pdf_service.generate_facade_report(
            facade_id=facade_id,
            facade_type=facade_type,
            start=start,
            end=end
        )
        
        # Generate filename
        filename = f"facade_{facade_id}_report.pdf"
        if facade_type:
            filename = f"facade_{facade_id}_{facade_type}_report.pdf"
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        print(f"❌ Error generating PDF report: {e}")
        raise HTTPException(status_code=500, detail="Error generating PDF report")


@router.get("/pdf/comparison")
async def get_comparison_pdf_report(
    sensor_name: str = Query(..., description="Sensor to compare across all facades"),
    start: Optional[str] = Query(None, description="Start date in ISO8601 format"),
    end: Optional[str] = Query(None, description="End date in ISO8601 format")
):
    """
    Generates a PDF comparison report comparing a sensor ACROSS ALL facades in the system.

    HU19: Generate PDF reports with charts.
    HU17: Compare performance with and without refrigeration.
    
    This endpoint compares the specified sensor between ALL facades (e.g., facade 1 vs facade 2),
    automatically detecting which is refrigerated and which is not.

    Parameters:
    - sensor_name (str): Sensor to compare across facades. Required.
    - start (Optional[str]): Start date/time for report period. Default: None.
    - end (Optional[str]): End date/time for report period. Default: None.

    Returns:
    - File: PDF comparison report as binary response.

    Exceptions:
    - HTTPException (404): Insufficient data for report generation.
    - HTTPException (500): Error generating PDF report.
    """
    try:
        pdf_bytes = await pdf_service.generate_multi_facade_comparison_report(
            sensor_name=sensor_name,
            start=start,
            end=end
        )
        
        # Generate filename
        safe_sensor_name = sensor_name.replace(" ", "_").replace("/", "_")
        filename = f"all_facades_{safe_sensor_name}_comparison.pdf"
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        print(f"❌ Error generating PDF comparison report: {e}")
        raise HTTPException(status_code=500, detail="Error generating PDF comparison report")


@router.get("/pdf/comparison/{facade_id}")
async def get_single_facade_comparison_pdf_report(
    facade_id: str,
    sensor_name: str = Query(..., description="Sensor to compare"),
    start: Optional[str] = Query(None, description="Start date in ISO8601 format"),
    end: Optional[str] = Query(None, description="End date in ISO8601 format")
):
    """
    [DEPRECATED] Use GET /reports/pdf/comparison instead.
    
    Generates a PDF comparison report between refrigerated and non-refrigerated types
    within a single facade.

    Parameters:
    - facade_id (str): ID of the facade. Required.
    - sensor_name (str): Sensor to compare. Required.
    - start (Optional[str]): Start date/time for report period. Default: None.
    - end (Optional[str]): End date/time for report period. Default: None.

    Returns:
    - File: PDF comparison report as binary response.
    """
    try:
        pdf_bytes = await pdf_service.generate_comparison_report(
            facade_id=facade_id,
            sensor_name=sensor_name,
            start=start,
            end=end
        )
        
        # Generate filename
        safe_sensor_name = sensor_name.replace(" ", "_").replace("/", "_")
        filename = f"facade_{facade_id}_{safe_sensor_name}_comparison.pdf"
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        print(f"❌ Error generating PDF comparison report: {e}")
        raise HTTPException(status_code=500, detail="Error generating PDF comparison report")
