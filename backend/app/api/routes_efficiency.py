"""
Energy Efficiency Routes
Provides endpoints for accessing energy efficiency metrics.

HU16: View energy efficiency metrics to evaluate system performance.
HU17: Compare performance with and without refrigeration to validate hypotheses.

DESIGN PHILOSOPHY:
- Efficiency is about comparing refrigerated vs non-refrigerated performance
- Each facade_id has BOTH types of data
- Endpoints should automatically compare both types to show refrigeration impact
- COP is ONE metric among many, not the only efficiency measure
"""
from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from ..services import efficiency_service

router = APIRouter(prefix="/efficiency", tags=["efficiency"])


@router.get("/{facade_id}")
async def get_efficiency_analysis(
    facade_id: str,
    start: Optional[str] = Query(None, description="Start date in ISO8601 format"),
    end: Optional[str] = Query(None, description="End date in ISO8601 format")
):
    """
    Comprehensive efficiency analysis comparing refrigerated vs non-refrigerated performance.

    HU16: View energy efficiency metrics to evaluate system performance.
    HU17: Compare performance with and without refrigeration to validate hypotheses.

    This is the MAIN efficiency endpoint that returns:
    - Temperature comparison (refrigerated vs non-refrigerated)
    - Thermal gain analysis for both types
    - COP metrics (only for refrigerated, when available)
    - Temperature reduction achieved by refrigeration
    - Efficiency improvement percentage
    - PV performance impact estimation

    Parameters:
    - facade_id (str): ID of the facade to analyze. Required.
    - start (Optional[str]): Start date/time for analysis period. Default: None.
    - end (Optional[str]): End date/time for analysis period. Default: None.

    Returns:
    - Dict: Comprehensive efficiency analysis with comparison metrics.

    Exceptions:
    - HTTPException (404): Insufficient data for analysis.
    - HTTPException (500): Error calculating efficiency analysis.
    """
    try:
        analysis = await efficiency_service.calculate_comprehensive_efficiency(
            facade_id, start=start, end=end
        )
        return analysis
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        print(f"❌ Error calculating efficiency analysis: {e}")
        raise HTTPException(status_code=500, detail="Error calculating efficiency analysis")


@router.get("/{facade_id}/cop")
async def get_cop(
    facade_id: str,
    start: Optional[str] = Query(None, description="Start date in ISO8601 format"),
    end: Optional[str] = Query(None, description="End date in ISO8601 format")
):
    """
    Calculates Coefficient of Performance (COP) for refrigerated facade configuration.

    HU16: View energy efficiency metrics to evaluate system performance.

    COP is a SPECIFIC metric for refrigeration systems:
    - COP = Cooling Power / Electrical Power Input
    - Only applicable to refrigerated facade type
    - Higher COP means better refrigeration efficiency

    Note: This is ONE component of overall efficiency. Use GET /efficiency/{facade_id}
    for comprehensive analysis including both facade types.

    Parameters:
    - facade_id (str): ID of the facade. Required.
    - start (Optional[str]): Start date/time for calculation period. Default: None.
    - end (Optional[str]): End date/time for calculation period. Default: None.

    Returns:
    - Dict: COP metrics including cooling capacity and power estimates.

    Exceptions:
    - HTTPException (404): No refrigerated data available or insufficient data.
    - HTTPException (500): Error calculating COP.
    """
    try:
        cop_data = await efficiency_service.calculate_cop(facade_id, start=start, end=end)
        return cop_data
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        print(f"❌ Error retrieving COP: {e}")
        raise HTTPException(status_code=500, detail="Error calculating COP")


@router.get("/{facade_id}/thermal-gain")
async def get_thermal_gain(
    facade_id: str,
    start: Optional[str] = Query(None, description="Start date in ISO8601 format"),
    end: Optional[str] = Query(None, description="End date in ISO8601 format")
):
    """
    Analyzes thermal gain for BOTH refrigerated and non-refrigerated configurations.

    HU16: View energy efficiency metrics to evaluate system performance.

    Thermal gain represents heat absorbed by panels from the environment:
    - Critical for BOTH facade types
    - Shows cooling system thermal load (refrigerated)
    - Shows passive thermal behavior (non-refrigerated)
    - Every 1°C increase reduces PV efficiency by ~0.4-0.5%

    Returns comparison between both types automatically.

    Parameters:
    - facade_id (str): ID of the facade. Required.
    - start (Optional[str]): Start date/time for calculation period. Default: None.
    - end (Optional[str]): End date/time for calculation period. Default: None.

    Returns:
    - Dict: Thermal gain metrics for both facade types with comparison.

    Exceptions:
    - HTTPException (404): Insufficient data for thermal gain calculation.
    - HTTPException (500): Error calculating thermal gain.
    """
    try:
        thermal_data = await efficiency_service.calculate_thermal_gain(
            facade_id, 
            facade_type=None,  # Always return both types
            start=start, 
            end=end
        )
        return thermal_data
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        print(f"❌ Error retrieving thermal gain: {e}")
        raise HTTPException(status_code=500, detail="Error calculating thermal gain")


@router.get("/{facade_id}/temperature-reduction")
async def get_temperature_reduction(
    facade_id: str,
    start: Optional[str] = Query(None, description="Start date in ISO8601 format"),
    end: Optional[str] = Query(None, description="End date in ISO8601 format")
):
    """
    Calculates temperature reduction achieved by refrigeration system.

    HU17: Compare performance with and without refrigeration to validate hypotheses.

    This metric directly shows refrigeration effectiveness:
    - Compares avg panel temps: refrigerated vs non-refrigerated
    - Calculates absolute temperature reduction (°C)
    - Estimates PV efficiency improvement (%)
    - Provides ROI context for refrigeration system

    Parameters:
    - facade_id (str): ID of the facade. Required.
    - start (Optional[str]): Start date/time for calculation period. Default: None.
    - end (Optional[str]): End date/time for calculation period. Default: None.

    Returns:
    - Dict: Temperature reduction metrics and PV efficiency impact.

    Exceptions:
    - HTTPException (404): Insufficient data for comparison.
    - HTTPException (500): Error calculating temperature reduction.
    """
    try:
        reduction_data = await efficiency_service.calculate_temperature_reduction(
            facade_id, start=start, end=end
        )
        return reduction_data
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        print(f"❌ Error calculating temperature reduction: {e}")
        raise HTTPException(status_code=500, detail="Error calculating temperature reduction")


@router.get("/summary/{facade_id}")
async def get_efficiency_summary(
    facade_id: str,
    facade_type: Optional[str] = Query(None, description="Filter by facade type: 'refrigerada', 'no_refrigerada'"),
    start: Optional[str] = Query(None, description="Start date in ISO8601 format"),
    end: Optional[str] = Query(None, description="End date in ISO8601 format")
):
    """
    Provides a summary of key efficiency metrics for a facade.

    HU16: View energy efficiency metrics to evaluate system performance.
    
    Returns metrics for BOTH facade types when no filter is applied:
    - Non-refrigerated: Thermal gain analysis, temperature behavior
    - Refrigerated: Thermal gain + COP analysis
    
    This allows proper comparison between both configurations.

    Parameters:
    - facade_id (str): ID of the facade. Required.
    - facade_type (Optional[str]): Filter by facade type. Default: None (returns both).
    - start (Optional[str]): Start date/time for calculation period. Default: None.
    - end (Optional[str]): End date/time for calculation period. Default: None.

    Returns:
    - Dict: Summary of efficiency metrics tailored to facade type.

    Exceptions:
    - HTTPException (500): Error calculating efficiency summary.
    """
    try:
        summary = {
            "facade_id": facade_id,
            "facade_type": facade_type,
            "metrics": {}
        }
        
        # Get thermal gain for all facades (works for both types)
        try:
            thermal = await efficiency_service.calculate_thermal_gain(
                facade_id, 
                facade_type=facade_type,
                start=start, 
                end=end
            )
            summary["metrics"]["thermal_gain"] = thermal
        except Exception as e:
            print(f"⚠️  Thermal gain calculation error: {e}")
            summary["metrics"]["thermal_gain"] = None
        
        # Get COP only for refrigerated facades (requires water loop sensors)
        # Only attempt if facade_type is 'refrigerada' or None
        if facade_type == "refrigerada":
            try:
                cop = await efficiency_service.calculate_cop(facade_id, start, end)
                summary["metrics"]["cop"] = cop
            except ValueError as e:
                # Expected for non-refrigerated facades
                summary["metrics"]["cop"] = {"error": str(e)}
            except Exception as e:
                print(f"⚠️  COP calculation error: {e}")
                summary["metrics"]["cop"] = None
        elif facade_type is None:
            # Try to get COP, but don't fail if it's not available
            try:
                cop = await efficiency_service.calculate_cop(facade_id, start, end)
                summary["metrics"]["cop"] = cop
            except:
                summary["metrics"]["cop"] = {
                    "note": "COP calculation only available for refrigerated facades"
                }
                summary["metrics"]["cop"] = None
        
        return summary
        
    except Exception as e:
        print(f"❌ Error generating efficiency summary: {e}")
        raise HTTPException(status_code=500, detail="Error generating efficiency summary")
