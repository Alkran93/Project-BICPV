"""
Energy Efficiency Metrics Service
Calculates and provides energy efficiency metrics for the refrigeration system.

HU16: View energy efficiency metrics to evaluate system performance.
"""
from typing import Dict, Any, Optional, List
from ..db import get_pool
import asyncpg


def _interpret_thermal_gain(facade_type: str, delta_t: Optional[float], thermal_gain: Optional[float]) -> str:
    """
    Interprets thermal gain results with context-specific insights.
    
    Parameters:
    - facade_type (str): Type of facade ('refrigerada' or 'no_refrigerada')
    - delta_t (Optional[float]): Temperature difference between panel and ambient
    - thermal_gain (Optional[float]): Calculated thermal gain in Watts
    
    Returns:
    - str: Interpretation text
    """
    if delta_t is None or thermal_gain is None:
        return "Insufficient data for interpretation"
    
    if facade_type == "refrigerada":
        if delta_t < 5:
            return "Excellent cooling performance - panels maintained close to ambient temperature"
        elif delta_t < 10:
            return "Good cooling performance - refrigeration system effectively managing thermal load"
        elif delta_t < 15:
            return "Moderate cooling - consider reviewing refrigeration system efficiency"
        else:
            return "Limited cooling effectiveness - system may need maintenance or optimization"
    else:  # no_refrigerada
        if delta_t < 10:
            return "Low thermal gain - favorable environmental conditions"
        elif delta_t < 20:
            return "Moderate thermal gain - typical for passive cooling"
        elif delta_t < 30:
            return "High thermal gain - panels experiencing significant heating"
        else:
            return "Very high thermal gain - may impact PV efficiency significantly"


async def calculate_cop(
    facade_id: str,
    start: Optional[str] = None,
    end: Optional[str] = None
) -> Dict[str, Any]:
    """
    Calculates the Coefficient of Performance (COP) for the refrigeration system.

    COP = Cooling Capacity / Power Input
    Cooling Capacity = Water Flow * Specific Heat * Temperature Difference

    HU16: View energy efficiency metrics to evaluate system performance.

    Parameters:
    - facade_id (str): ID of the refrigerated facade. Required.
    - start (Optional[str]): Start date/time for calculation period. Default: None.
    - end (Optional[str]): End date/time for calculation period. Default: None.

    Returns:
    - Dict[str, Any]: Dictionary containing:
      - facade_id (str): ID of the facade.
      - cop_average (float): Average COP over the period.
      - cooling_capacity_avg_w (float): Average cooling capacity in Watts.
      - measurements_count (int): Number of measurements used.
      - period (dict): Start and end times of calculation period.

    Exceptions:
    - RuntimeError: Raised if the database connection pool is not initialized.
    - ValueError: Raised if insufficient data is available for COP calculation.
    """
    pool = get_pool()
    if not pool:
        raise RuntimeError("Database connection pool not initialized")
    
    # Check if this facade has refrigerated data with required sensors
    check_sql = """
        SELECT COUNT(DISTINCT sensor_name) as sensor_count
        FROM measurements
        WHERE facade_id = $1 
        AND facade_type = 'refrigerada'
        AND sensor_name IN ('T_Entrada_Agua', 'T_Salida_Agua', 'Flujo_Agua_LPM')
    """
    
    try:
        async with pool.acquire() as conn:
            check_row = await conn.fetchrow(check_sql, facade_id)
            
            if not check_row or check_row['sensor_count'] == 0:
                # No refrigeration data at all - return informative response
                return {
                    "facade_id": facade_id,
                    "cop_available": False,
                    "reason": "no_refrigeration_system",
                    "message": "This facade does not have an active refrigeration system. COP (Coefficient of Performance) only applies to refrigerated facades with water cooling circuits.",
                    "recommendation": "Use thermal_gain and temperature_comparison endpoints to analyze passive thermal behavior."
                }
            elif check_row['sensor_count'] < 3:
                # Partial data - some sensors missing
                return {
                    "facade_id": facade_id,
                    "cop_available": False,
                    "reason": "incomplete_sensor_data",
                    "message": f"Refrigeration system detected but only {check_row['sensor_count']}/3 required sensors available. COP calculation requires: T_Entrada_Agua, T_Salida_Agua, and Flujo_Agua_LPM.",
                    "recommendation": "Verify sensor connectivity and data ingestion for complete COP analysis."
                }
    except Exception as e:
        print(f"❌ Error checking facade refrigeration data: {e}")
        raise

    # Query for simultaneous water inlet/outlet temps and flow rate
    sql = """
        WITH water_data AS (
            SELECT 
                ts,
                MAX(CASE WHEN sensor_name = 'T_Entrada_Agua' THEN value END) as t_inlet,
                MAX(CASE WHEN sensor_name = 'T_Salida_Agua' THEN value END) as t_outlet,
                MAX(CASE WHEN sensor_name = 'Flujo_Agua_LPM' THEN value END) as flow_lpm
            FROM measurements
            WHERE facade_id = $1 
            AND facade_type = 'refrigerada'
            AND sensor_name IN ('T_Entrada_Agua', 'T_Salida_Agua', 'Flujo_Agua_LPM')
    """
    
    params = [facade_id]
    idx = 2
    
    if start:
        sql += f" AND ts >= ${idx}"
        params.append(start)
        idx += 1
    
    if end:
        sql += f" AND ts <= ${idx}"
        params.append(end)
        idx += 1
    
    sql += """
            GROUP BY ts
            HAVING COUNT(DISTINCT sensor_name) = 3
        )
        SELECT 
            AVG(t_inlet) as avg_t_inlet,
            AVG(t_outlet) as avg_t_outlet,
            AVG(flow_lpm) as avg_flow_lpm,
            AVG((t_outlet - t_inlet) * flow_lpm) as cooling_metric,
            COUNT(*) as sample_count
        FROM water_data
        WHERE t_inlet IS NOT NULL 
        AND t_outlet IS NOT NULL 
        AND flow_lpm IS NOT NULL
        AND flow_lpm > 0
    """
    
    try:
        async with pool.acquire() as conn:
            row = await conn.fetchrow(sql, *params)
        
        if not row or not row['sample_count'] or row['sample_count'] == 0:
            return {
                "facade_id": facade_id,
                "cop_available": False,
                "reason": "insufficient_measurements",
                "message": "Refrigeration system detected but insufficient synchronized measurements for COP calculation in the specified time period.",
                "recommendation": "Extend the time range or check that all refrigeration sensors are reporting data simultaneously.",
                "time_period": {
                    "start": start if start else "Not specified",
                    "end": end if end else "Not specified"
                }
            }
        
        # Constants
        specific_heat_water = 4.186  # kJ/(kg·K)
        water_density = 1.0  # kg/L
        
        # Calculate cooling capacity
        delta_t = row['avg_t_outlet'] - row['avg_t_inlet']
        flow_kg_s = (row['avg_flow_lpm'] * water_density) / 60.0  # kg/s
        cooling_capacity_kw = flow_kg_s * specific_heat_water * delta_t  # kW
        cooling_capacity_w = cooling_capacity_kw * 1000  # W
        
        # Estimate power input (simplified: assume 30% efficiency for heat removal)
        # In reality, this should be measured directly from compressor power consumption
        estimated_power_input_w = abs(cooling_capacity_w) / 3.0
        
        # Calculate COP
        cop = abs(cooling_capacity_w) / estimated_power_input_w if estimated_power_input_w > 0 else 0
        
        # Interpret COP value
        if cop >= 5.0:
            efficiency_rating = "Excellent - Very high efficiency refrigeration system"
        elif cop >= 3.5:
            efficiency_rating = "Good - Efficient refrigeration performance"
        elif cop >= 2.5:
            efficiency_rating = "Acceptable - Standard refrigeration efficiency"
        elif cop >= 1.5:
            efficiency_rating = "Below average - Consider system optimization"
        else:
            efficiency_rating = "Poor - System may require maintenance or reconfiguration"
        
        return {
            "facade_id": facade_id,
            "cop_available": True,
            "cop_average": round(cop, 2),
            "efficiency_rating": efficiency_rating,
            "cooling_capacity_avg_w": round(abs(cooling_capacity_w), 2),
            "estimated_power_input_w": round(estimated_power_input_w, 2),
            "water_temp_delta_avg_celsius": round(delta_t, 2),
            "water_flow_avg_lpm": round(row['avg_flow_lpm'], 2),
            "measurements_count": row['sample_count'],
            "time_period": {
                "start": start if start else "Not specified",
                "end": end if end else "Not specified"
            },
            "note": "COP calculation uses estimated power input based on typical refrigeration system efficiency. Direct power consumption measurement recommended for precise values."
        }
        
    except Exception as e:
        print(f"❌ Error calculating COP: {e}")
        raise


async def calculate_thermal_gain(
    facade_id: str,
    facade_type: Optional[str] = None,
    start: Optional[str] = None,
    end: Optional[str] = None
) -> Dict[str, Any]:
    """
    Calculates thermal gain/loss through the panel system for ANY facade type.

    HU16: View energy efficiency metrics to evaluate system performance.
    
    This metric is relevant for BOTH refrigerated and non-refrigerated facades:
    - Non-refrigerated: Shows heat absorption from environment
    - Refrigerated: Shows thermal load that refrigeration system must handle

    Parameters:
    - facade_id (str): ID of the facade. Required.
    - facade_type (Optional[str]): Filter by facade type. Default: None (calculates for all types).
    - start (Optional[str]): Start date/time for calculation period. Default: None.
    - end (Optional[str]): End date/time for calculation period. Default: None.

    Returns:
    - Dict[str, Any]: Dictionary containing thermal gain metrics.

    Exceptions:
    - RuntimeError: Raised if the database connection pool is not initialized.
    - ValueError: Raised if insufficient data is available.
    """
    pool = get_pool()
    if not pool:
        raise RuntimeError("Database connection pool not initialized")
    
    # Query panel temperature sensors (15 sensors: T_M1_1 to T_M5_3)
    sql = """
        SELECT AVG(value) as avg_temp, facade_type, COUNT(*) as sample_count
        FROM measurements
        WHERE facade_id = $1
        AND sensor_name LIKE 'T_M%'
        AND value IS NOT NULL
    """
    
    params = [facade_id]
    idx = 2
    
    if facade_type:
        sql += f" AND facade_type = ${idx}"
        params.append(facade_type)
        idx += 1
    
    if start:
        sql += f" AND ts >= ${idx}"
        params.append(start)
        idx += 1
    
    if end:
        sql += f" AND ts <= ${idx}"
        params.append(end)
        idx += 1
    
    sql += " GROUP BY facade_type"
    
    try:
        async with pool.acquire() as conn:
            rows = await conn.fetch(sql, *params)
        
        if not rows:
            raise ValueError("Insufficient panel temperature data")
        
        # Get ambient temperature for comparison
        ambient_sql = """
            SELECT AVG(value) as avg_ambient
            FROM measurements
            WHERE facade_id = $1
            AND sensor_name = 'Temperatura_Ambiente'
            AND value IS NOT NULL
        """
        
        ambient_params = [facade_id]
        ambient_idx = 2
        
        if facade_type:
            ambient_sql += f" AND facade_type = ${ambient_idx}"
            ambient_params.append(facade_type)
            ambient_idx += 1
        
        if start:
            ambient_sql += f" AND ts >= ${ambient_idx}"
            ambient_params.append(start)
            ambient_idx += 1
        
        if end:
            ambient_sql += f" AND ts <= ${ambient_idx}"
            ambient_params.append(end)
        
        async with pool.acquire() as conn:
            ambient_row = await conn.fetchrow(ambient_sql, *ambient_params)
        
        avg_ambient = ambient_row['avg_ambient'] if ambient_row and ambient_row['avg_ambient'] else None
        
        # Process results for each facade type
        results = {}
        panel_area = 10.0  # m² (5 modules × 2m² per module)
        u_value = 5.0  # W/(m²·K), estimated for PV panels
        
        for row in rows:
            f_type = row['facade_type']
            avg_panel_temp = row['avg_temp']
            sample_count = row['sample_count']
            
            # Calculate temperature difference
            delta_t = avg_panel_temp - avg_ambient if avg_ambient else None
            
            # Estimate thermal gain
            thermal_gain_w = delta_t * panel_area * u_value if delta_t else None
            
            results[f_type] = {
                "facade_type": f_type,
                "avg_panel_temperature": round(avg_panel_temp, 2),
                "avg_ambient_temperature": round(avg_ambient, 2) if avg_ambient else None,
                "temperature_difference": round(delta_t, 2) if delta_t else None,
                "estimated_thermal_gain_w": round(thermal_gain_w, 2) if thermal_gain_w else None,
                "panel_area_m2": panel_area,
                "measurements_count": sample_count,
                "interpretation": _interpret_thermal_gain(f_type, delta_t, thermal_gain_w)
            }
        
        # Return single type if filtered, otherwise return both
        if facade_type and facade_type in results:
            return {
                "facade_id": facade_id,
                **results[facade_type]
            }
        else:
            return {
                "facade_id": facade_id,
                "thermal_analysis": results,
                "ambient_reference": round(avg_ambient, 2) if avg_ambient else None
            }
        
    except Exception as e:
        print(f"❌ Error calculating thermal gain: {e}")
        raise


async def calculate_efficiency_comparison(
    facade_id: str,
    start: Optional[str] = None,
    end: Optional[str] = None
) -> Dict[str, Any]:
    """
    Compares efficiency metrics between refrigerated and non-refrigerated facades.

    HU17: Compare performance with and without refrigeration to validate hypotheses.

    Parameters:
    - facade_id (str): ID of the facade. Required.
    - start (Optional[str]): Start date/time for calculation period. Default: None.
    - end (Optional[str]): End date/time for calculation period. Default: None.

    Returns:
    - Dict[str, Any]: Comparative efficiency metrics for both facade types.

    Exceptions:
    - RuntimeError: Raised if the database connection pool is not initialized.
    """
    try:
        # Calculate metrics for refrigerated facade
        refrigerated_thermal = await calculate_thermal_gain(facade_id, start, end)
        
        # Try to calculate COP (only for refrigerated)
        try:
            cop_metrics = await calculate_cop(facade_id, start, end)
        except:
            cop_metrics = {"note": "COP calculation not available"}
        
        # Get average temperatures for both types
        pool = get_pool()
        sql = """
            SELECT 
                facade_type,
                AVG(value) as avg_temp,
                MIN(value) as min_temp,
                MAX(value) as max_temp,
                COUNT(*) as sample_count
            FROM measurements
            WHERE facade_id = $1
            AND sensor_name LIKE 'T_M%'
            AND value IS NOT NULL
        """
        
        params = [facade_id]
        idx = 2
        
        if start:
            sql += f" AND ts >= ${idx}"
            params.append(start)
            idx += 1
        
        if end:
            sql += f" AND ts <= ${idx}"
            params.append(end)
        
        sql += " GROUP BY facade_type"
        
        async with pool.acquire() as conn:
            rows = await conn.fetch(sql, *params)
        
        comparison = {}
        for row in rows:
            comparison[row['facade_type']] = {
                "avg_temperature": round(row['avg_temp'], 2),
                "min_temperature": round(row['min_temp'], 2),
                "max_temperature": round(row['max_temp'], 2),
                "temperature_range": round(row['max_temp'] - row['min_temp'], 2),
                "measurements_count": row['sample_count']
            }
        
        # Calculate temperature reduction if both types exist
        if 'refrigerada' in comparison and 'no_refrigerada' in comparison:
            temp_reduction = comparison['no_refrigerada']['avg_temperature'] - comparison['refrigerada']['avg_temperature']
            comparison['temperature_reduction'] = round(temp_reduction, 2)
            comparison['efficiency_improvement_percent'] = round((temp_reduction / comparison['no_refrigerada']['avg_temperature']) * 100, 2)
        
        return {
            "facade_id": facade_id,
            "comparison": comparison,
            "cop_metrics": cop_metrics,
            "refrigerated_thermal_gain": refrigerated_thermal
        }
        
    except Exception as e:
        print(f"❌ Error calculating efficiency comparison: {e}")
        raise


async def calculate_comprehensive_efficiency(
    facade_id: str,
    start: Optional[str] = None,
    end: Optional[str] = None
) -> Dict[str, Any]:
    """
    Comprehensive efficiency analysis comparing refrigerated vs non-refrigerated performance.
    
    This is the MAIN efficiency function that combines all metrics.
    
    HU16: View energy efficiency metrics to evaluate system performance.
    HU17: Compare performance with and without refrigeration to validate hypotheses.
    
    Parameters:
    - facade_id (str): ID of the facade. Required.
    - start (Optional[str]): Start date/time for analysis period. Default: None.
    - end (Optional[str]): End date/time for analysis period. Default: None.
    
    Returns:
    - Dict[str, Any]: Comprehensive efficiency analysis with all metrics.
    """
    try:
        analysis = {
            "facade_id": facade_id,
            "analysis_period": {
                "start": start if start else "Not specified",
                "end": end if end else "Not specified"
            }
        }
        
        # 1. Get thermal gain for both types
        try:
            thermal = await calculate_thermal_gain(facade_id, facade_type=None, start=start, end=end)
            analysis["thermal_analysis"] = thermal.get("thermal_analysis", {})
        except Exception as e:
            print(f"⚠️  Thermal gain error: {e}")
            analysis["thermal_analysis"] = {"error": str(e)}
        
        # 2. Get temperature comparison
        try:
            temp_reduction = await calculate_temperature_reduction(facade_id, start, end)
            analysis["temperature_comparison"] = temp_reduction
        except Exception as e:
            print(f"⚠️  Temperature reduction error: {e}")
            analysis["temperature_comparison"] = {"error": str(e)}
        
        # 3. Try to get COP (only if refrigerated data exists)
        try:
            cop = await calculate_cop(facade_id, start, end)
            analysis["cop_metrics"] = cop
        except Exception as e:
            print(f"⚠️  COP calculation error: {e}")
            analysis["cop_metrics"] = {"error": str(e)}
        
        # 4. Calculate overall efficiency score
        try:
            if "temperature_comparison" in analysis and isinstance(analysis["temperature_comparison"], dict):
                temp_comp = analysis["temperature_comparison"]
                if "temperature_reduction_celsius" in temp_comp:
                    reduction = temp_comp["temperature_reduction_celsius"]
                    pv_improvement = temp_comp.get("estimated_pv_efficiency_gain_percent", 0)
                    
                    analysis["overall_assessment"] = {
                        "refrigeration_effectiveness": "Excellent" if reduction > 15 else "Good" if reduction > 10 else "Moderate" if reduction > 5 else "Limited",
                        "temperature_reduction_celsius": reduction,
                        "pv_efficiency_improvement_percent": pv_improvement,
                        "recommendation": _get_efficiency_recommendation(reduction, pv_improvement)
                    }
        except Exception as e:
            print(f"⚠️  Overall assessment error: {e}")
        
        return analysis
        
    except Exception as e:
        print(f"❌ Error calculating comprehensive efficiency: {e}")
        raise


async def calculate_temperature_reduction(
    facade_id: str,
    start: Optional[str] = None,
    end: Optional[str] = None
) -> Dict[str, Any]:
    """
    Calculates temperature reduction achieved by refrigeration system.
    
    HU17: Compare performance with and without refrigeration to validate hypotheses.
    
    Parameters:
    - facade_id (str): ID of the facade. Required.
    - start (Optional[str]): Start date/time for calculation period. Default: None.
    - end (Optional[str]): End date/time for calculation period. Default: None.
    
    Returns:
    - Dict[str, Any]: Temperature reduction metrics and PV efficiency impact.
    """
    pool = get_pool()
    if not pool:
        raise RuntimeError("Database connection pool not initialized")
    
    # Query average panel temperatures for both types
    sql = """
        SELECT 
            facade_type,
            AVG(value) as avg_temp,
            MIN(value) as min_temp,
            MAX(value) as max_temp,
            STDDEV(value) as stddev_temp,
            COUNT(*) as sample_count
        FROM measurements
        WHERE facade_id = $1
        AND sensor_name LIKE 'T_M%'
        AND value IS NOT NULL
    """
    
    params = [facade_id]
    idx = 2
    
    if start:
        sql += f" AND ts >= ${idx}"
        params.append(start)
        idx += 1
    
    if end:
        sql += f" AND ts <= ${idx}"
        params.append(end)
        idx += 1
    
    sql += " GROUP BY facade_type"
    
    try:
        async with pool.acquire() as conn:
            rows = await conn.fetch(sql, *params)
        
        if not rows:
            raise ValueError("Insufficient temperature data for comparison")
        
        results = {}
        for row in rows:
            results[row['facade_type']] = {
                "avg_temperature_celsius": round(row['avg_temp'], 2),
                "min_temperature_celsius": round(row['min_temp'], 2),
                "max_temperature_celsius": round(row['max_temp'], 2),
                "stddev_celsius": round(row['stddev_temp'], 2) if row['stddev_temp'] else 0,
                "temperature_range_celsius": round(row['max_temp'] - row['min_temp'], 2),
                "sample_count": row['sample_count']
            }
        
        # Calculate reduction if both types exist
        if 'refrigerada' in results and 'no_refrigerada' in results:
            ref_avg = results['refrigerada']['avg_temperature_celsius']
            no_ref_avg = results['no_refrigerada']['avg_temperature_celsius']
            
            temp_reduction = no_ref_avg - ref_avg
            reduction_percent = (temp_reduction / no_ref_avg) * 100 if no_ref_avg > 0 else 0
            
            # PV efficiency impact: ~0.4-0.5% improvement per °C reduction
            pv_efficiency_gain = temp_reduction * 0.45  # Using 0.45% per °C as middle estimate
            
            return {
                "facade_id": facade_id,
                "refrigerated_facade": results.get('refrigerada', {}),
                "non_refrigerated_facade": results.get('no_refrigerada', {}),
                "temperature_reduction_celsius": round(temp_reduction, 2),
                "temperature_reduction_percent": round(reduction_percent, 2),
                "estimated_pv_efficiency_gain_percent": round(pv_efficiency_gain, 2),
                "interpretation": _interpret_temperature_reduction(temp_reduction),
                "note": "PV efficiency gain calculated using 0.45% improvement per °C temperature reduction"
            }
        elif 'refrigerada' in results:
            return {
                "facade_id": facade_id,
                "refrigerated_facade": results['refrigerada'],
                "non_refrigerated_facade": None,
                "note": "Only refrigerated data available - cannot calculate reduction"
            }
        elif 'no_refrigerada' in results:
            return {
                "facade_id": facade_id,
                "refrigerated_facade": None,
                "non_refrigerated_facade": results['no_refrigerada'],
                "note": "Only non-refrigerated data available - cannot calculate reduction"
            }
        else:
            raise ValueError("No temperature data available")
            
    except Exception as e:
        print(f"❌ Error calculating temperature reduction: {e}")
        raise


def _interpret_temperature_reduction(reduction: float) -> str:
    """Interprets temperature reduction results."""
    if reduction >= 20:
        return "Exceptional cooling performance - refrigeration system achieving >20°C reduction"
    elif reduction >= 15:
        return "Excellent cooling performance - significant temperature control"
    elif reduction >= 10:
        return "Good cooling performance - effective thermal management"
    elif reduction >= 5:
        return "Moderate cooling performance - system providing measurable benefit"
    elif reduction >= 1:
        return "Limited cooling performance - minimal temperature reduction"
    else:
        return "Negligible or negative cooling - system may need maintenance"


def _get_efficiency_recommendation(reduction: float, pv_gain: float) -> str:
    """Generates recommendation based on efficiency metrics."""
    if reduction >= 15 and pv_gain >= 6:
        return "Refrigeration system demonstrating excellent ROI potential. Continue monitoring for long-term validation."
    elif reduction >= 10 and pv_gain >= 4:
        return "Good refrigeration performance. Consider energy consumption analysis for complete ROI assessment."
    elif reduction >= 5 and pv_gain >= 2:
        return "Moderate refrigeration benefit. Evaluate operational costs vs. PV output improvement."
    else:
        return "Limited refrigeration benefit observed. Review system operation and consider efficiency optimization."
