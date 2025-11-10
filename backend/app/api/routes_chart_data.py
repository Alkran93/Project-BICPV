"""
Chart Data Routes
Provides endpoints that return JSON data for frontend chart generation.

All HU related to charts (HU06, HU07, HU09) now return structured JSON data
instead of PNG images, allowing frontend flexibility in chart rendering.
"""
from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List, Dict, Any
from ..services import storage_controller, analytics_service

router = APIRouter(prefix="/chart-data", tags=["chart-data"])


@router.get("/line/{facade_id}")
async def get_line_chart_data(
    facade_id: str,
    sensor_name: str = Query(..., description="Sensor to plot"),
    facade_type: Optional[str] = Query(None, description="Filter by facade type: 'refrigerada', 'no_refrigerada'"),
    start: Optional[str] = Query(None, description="Start date in ISO8601 format"),
    end: Optional[str] = Query(None, description="End date in ISO8601 format"),
    limit: int = Query(1000, ge=1, le=5000, description="Maximum number of data points")
):
    """
    Returns JSON data for generating a line chart for a specific sensor over time.

    HU06: View line charts to easily interpret data.

    Parameters:
    - facade_id (str): ID of the facade. Required.
    - sensor_name (str): Name of the sensor to plot. Required.
    - facade_type (Optional[str]): Filter by facade type. Default: None.
    - start (Optional[str]): Start date/time in ISO8601 format. Default: None.
    - end (Optional[str]): End date/time in ISO8601 format. Default: None.
    - limit (int): Maximum number of data points. Default: 1000.

    Returns:
    - JSON object with chart configuration and data:
      {
        "chart_type": "line",
        "facade_id": "1",
        "sensor_name": "T_M1_1",
        "facade_type": "no_refrigerada",
        "title": "T_M1_1 - Facade 1",
        "x_label": "Time",
        "y_label": "T_M1_1",
        "data": [
          {"ts": "2025-11-09T15:00:00Z", "value": 42.5},
          {"ts": "2025-11-09T15:00:03Z", "value": 42.7},
          ...
        ]
      }

    Exceptions:
    - HTTPException (404): No data available for chart generation.
    - HTTPException (500): Error retrieving data.
    """
    try:
        # Fetch measurements from storage
        measurements = await storage_controller.fetch_measurements(
            facade_id=facade_id,
            sensor=sensor_name,
            facade_type=facade_type,
            start=start,
            end=end,
            limit=limit
        )
        
        if not measurements:
            raise HTTPException(status_code=404, detail="No data available for chart generation")
        
        # Generate title
        title = f"{sensor_name} - Facade {facade_id}"
        if facade_type:
            title += f" ({facade_type})"
        
        # Prepare chart data
        chart_data = {
            "chart_type": "line",
            "facade_id": facade_id,
            "sensor_name": sensor_name,
            "facade_type": facade_type,
            "title": title,
            "x_label": "Time",
            "y_label": sensor_name,
            "unit": "°C" if "T_" in sensor_name or "Temperatura" in sensor_name else "",
            "data": [
                {
                    "ts": str(m["ts"]),
                    "value": float(m["value"]) if m["value"] is not None else None
                }
                for m in measurements
            ],
            "data_count": len(measurements)
        }
        
        return chart_data
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error retrieving line chart data: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving chart data")


@router.get("/bar/{facade_id}/average")
async def get_bar_chart_average_data(
    facade_id: str,
    facade_type: Optional[str] = Query(None, description="Filter by facade type: 'refrigerada', 'no_refrigerada'")
):
    """
    Returns JSON data for generating a bar chart showing average values of all sensors.

    HU06: View bar charts to easily interpret data.
    HU04: View the average temperature per panel in the non-refrigerated facade.

    Parameters:
    - facade_id (str): ID of the facade. Required.
    - facade_type (Optional[str]): Filter by facade type. Default: None.

    Returns:
    - JSON object with bar chart data:
      {
        "chart_type": "bar",
        "facade_id": "1",
        "facade_type": "no_refrigerada",
        "title": "Average Sensor Values - Facade 1",
        "x_label": "Sensor",
        "y_label": "Average Value",
        "data": [
          {"sensor": "T_M1_1", "value": 42.5, "facade_type": "no_refrigerada"},
          {"sensor": "T_M1_2", "value": 43.2, "facade_type": "no_refrigerada"},
          ...
        ]
      }

    Exceptions:
    - HTTPException (404): No data available for chart generation.
    - HTTPException (500): Error retrieving data.
    """
    try:
        # Fetch average values
        averages = await analytics_service.get_facade_average(facade_id, facade_type=facade_type)
        
        if not averages:
            raise HTTPException(status_code=404, detail="No data available for chart generation")
        
        # Generate title
        title = f"Average Sensor Values - Facade {facade_id}"
        if facade_type:
            title += f" ({facade_type})"
        
        # Prepare chart data
        chart_data = {
            "chart_type": "bar",
            "facade_id": facade_id,
            "facade_type": facade_type,
            "title": title,
            "x_label": "Sensor",
            "y_label": "Average Value",
            "data": [
                {
                    "sensor": row["sensor_name"],
                    "value": float(row["avg_value"]) if row.get("avg_value") is not None else 0,
                    "facade_type": row.get("facade_type")
                }
                for row in averages if row.get("avg_value")
            ],
            "data_count": len(averages)
        }
        
        return chart_data
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error retrieving bar chart data: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving chart data")


@router.get("/comparison/{facade_id}")
async def get_comparison_chart_data(
    facade_id: str,
    sensor_name: str = Query(..., description="Sensor to compare"),
    start: Optional[str] = Query(None, description="Start date in ISO8601 format"),
    end: Optional[str] = Query(None, description="End date in ISO8601 format"),
    limit: int = Query(1000, ge=1, le=5000, description="Maximum number of data points per type")
):
    """
    Returns JSON data for generating a comparison chart between refrigerated and non-refrigerated facades.

    HU09: Graphically compare two facades by overlaying charts to evaluate performance.
    HU17: Compare performance with and without refrigeration to validate hypotheses.

    Parameters:
    - facade_id (str): ID of the facade. Required.
    - sensor_name (str): Name of the sensor to compare. Required.
    - start (Optional[str]): Start date/time in ISO8601 format. Default: None.
    - end (Optional[str]): End date/time in ISO8601 format. Default: None.
    - limit (int): Maximum number of data points per facade type. Default: 1000.

    Returns:
    - JSON object with comparison chart data:
      {
        "chart_type": "comparison",
        "facade_id": "1",
        "sensor_name": "T_M1_1",
        "title": "Comparison: T_M1_1 - Facade 1",
        "x_label": "Time",
        "y_label": "Temperature (°C)",
        "series": [
          {
            "name": "Refrigerated Facade",
            "facade_type": "refrigerada",
            "data": [{"ts": "...", "value": 35.2}, ...]
          },
          {
            "name": "Non-Refrigerated Facade",
            "facade_type": "no_refrigerada",
            "data": [{"ts": "...", "value": 48.7}, ...]
          }
        ]
      }

    Exceptions:
    - HTTPException (404): No data available for comparison.
    - HTTPException (500): Error retrieving data.
    """
    try:
        # Fetch comparison data
        comparison = await storage_controller.compare_facade_types(
            facade_id=facade_id,
            sensor=sensor_name,
            start=start,
            end=end,
            limit=limit
        )
        
        refrigerada_data = comparison.get("refrigerada", [])
        no_refrigerada_data = comparison.get("no_refrigerada", [])
        
        if not refrigerada_data and not no_refrigerada_data:
            raise HTTPException(status_code=404, detail="No data available for comparison")
        
        # Prepare series data
        series = []
        
        if refrigerada_data:
            series.append({
                "name": "Refrigerated Facade",
                "facade_type": "refrigerada",
                "color": "#1f77b4",
                "data": [
                    {"ts": str(d["ts"]), "value": float(d["value"]) if d["value"] is not None else None}
                    for d in refrigerada_data
                ]
            })
        
        if no_refrigerada_data:
            series.append({
                "name": "Non-Refrigerated Facade",
                "facade_type": "no_refrigerada",
                "color": "#ff7f0e",
                "data": [
                    {"ts": str(d["ts"]), "value": float(d["value"]) if d["value"] is not None else None}
                    for d in no_refrigerada_data
                ]
            })
        
        # Prepare chart data
        chart_data = {
            "chart_type": "comparison",
            "facade_id": facade_id,
            "sensor_name": sensor_name,
            "title": f"Comparison: {sensor_name} - Facade {facade_id}",
            "x_label": "Time",
            "y_label": sensor_name,
            "unit": "°C" if "T_" in sensor_name or "Temperatura" in sensor_name else "",
            "series": series
        }
        
        return chart_data
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error retrieving comparison chart data: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving chart data")


@router.get("/power-irradiance/{facade_id}")
async def get_power_irradiance_chart_data(
    facade_id: str,
    facade_type: Optional[str] = Query(None, description="Filter by facade type: 'refrigerada', 'no_refrigerada'"),
    start: Optional[str] = Query(None, description="Start date in ISO8601 format"),
    end: Optional[str] = Query(None, description="End date in ISO8601 format"),
    limit: int = Query(1000, ge=1, le=5000, description="Maximum number of data points")
):
    """
    Returns JSON data for generating a chart showing generated power and irradiance over time.

    HU07: Generate a chart with generated power and irradiance over time.

    Note: Power is calculated using a simplified model based on irradiance and panel area.

    Parameters:
    - facade_id (str): ID of the facade. Required.
    - facade_type (Optional[str]): Filter by facade type. Default: None.
    - start (Optional[str]): Start date/time in ISO8601 format. Default: None.
    - end (Optional[str]): End date/time in ISO8601 format. Default: None.
    - limit (int): Maximum number of data points. Default: 1000.

    Returns:
    - JSON object with dual-series chart data:
      {
        "chart_type": "multi_series",
        "facade_id": "1",
        "facade_type": "no_refrigerada",
        "title": "Power Generation & Irradiance - Facade 1",
        "x_label": "Time",
        "series": [
          {
            "name": "Irradiance",
            "unit": "W/m²",
            "y_axis": "left",
            "data": [{"ts": "...", "value": 850}, ...]
          },
          {
            "name": "Generated Power",
            "unit": "W",
            "y_axis": "right",
            "data": [{"ts": "...", "value": 1275}, ...]
          }
        ],
        "calculation": {
          "panel_area_m2": 10,
          "efficiency": 0.15,
          "formula": "Power (W) = Irradiance (W/m²) × Area × Efficiency"
        }
      }

    Exceptions:
    - HTTPException (404): No irradiance data available.
    - HTTPException (500): Error retrieving data.
    """
    try:
        # Fetch irradiance measurements
        irradiance_data = await storage_controller.fetch_measurements(
            facade_id=facade_id,
            sensor="Irradiancia",
            facade_type=facade_type,
            start=start,
            end=end,
            limit=limit
        )
        
        if not irradiance_data:
            raise HTTPException(status_code=404, detail="No irradiance data available")
        
        # Calculate power (simplified model: Power = Irradiance * Area * Efficiency)
        # Assuming 5 modules × 2m² per module = 10m², efficiency ~15%
        panel_area = 10.0  # m²
        efficiency = 0.15
        
        # Prepare irradiance series
        irradiance_series = {
            "name": "Irradiance",
            "unit": "W/m²",
            "y_axis": "left",
            "color": "#ff7f0e",
            "data": [
                {"ts": str(record["ts"]), "value": float(record["value"]) if record["value"] is not None else 0}
                for record in irradiance_data
            ]
        }
        
        # Prepare power series
        power_series = {
            "name": "Generated Power",
            "unit": "W",
            "y_axis": "right",
            "color": "#2ca02c",
            "data": [
                {
                    "ts": str(record["ts"]),
                    "value": round(float(record["value"]) * panel_area * efficiency, 2) if record["value"] is not None else 0
                }
                for record in irradiance_data
            ]
        }
        
        # Prepare chart data
        chart_data = {
            "chart_type": "multi_series",
            "facade_id": facade_id,
            "facade_type": facade_type,
            "title": f"Power Generation & Irradiance - Facade {facade_id}",
            "x_label": "Time",
            "series": [irradiance_series, power_series],
            "calculation": {
                "panel_area_m2": panel_area,
                "efficiency": efficiency,
                "formula": "Power (W) = Irradiance (W/m²) × Area × Efficiency"
            },
            "data_count": len(irradiance_data)
        }
        
        return chart_data
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error retrieving power/irradiance chart data: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving chart data")
