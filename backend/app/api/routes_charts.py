"""
Chart generation routes
Provides endpoints for generating various types of charts and visualizations.

HU06: View line and bar charts to easily interpret data.
HU07: Generate a chart with generated power and irradiance over time.
HU09: Graphically compare two facades by overlaying charts to evaluate performance.
"""
from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import Response
from typing import Optional
from ..services import chart_manager, storage_controller, analytics_service

router = APIRouter(prefix="/charts", tags=["charts"])


@router.get("/line/{facade_id}")
async def get_line_chart(
    facade_id: str,
    sensor_name: str = Query(..., description="Sensor to plot"),
    facade_type: Optional[str] = Query(None, description="Filter by facade type: 'refrigerada', 'no_refrigerada'"),
    start: Optional[str] = Query(None, description="Start date in ISO8601 format"),
    end: Optional[str] = Query(None, description="End date in ISO8601 format"),
    limit: int = Query(1000, ge=1, le=5000, description="Maximum number of data points")
):
    """
    Generates a line chart for a specific sensor over time.

    HU06: View line charts to easily interpret data.

    Parameters:
    - facade_id (str): ID of the facade. Required.
    - sensor_name (str): Name of the sensor to plot. Required.
    - facade_type (Optional[str]): Filter by facade type. Default: None.
    - start (Optional[str]): Start date/time in ISO8601 format. Default: None.
    - end (Optional[str]): End date/time in ISO8601 format. Default: None.
    - limit (int): Maximum number of data points. Default: 1000.

    Returns:
    - Image: PNG chart as binary response.

    Exceptions:
    - HTTPException (404): No data available for chart generation.
    - HTTPException (500): Error generating chart.
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
        
        # Generate line chart
        title = f"{sensor_name} - Facade {facade_id}"
        if facade_type:
            title += f" ({facade_type})"
        
        chart_bytes = chart_manager.generate_line_chart(
            data=measurements,
            x_field="ts",
            y_field="value",
            title=title,
            xlabel="Time",
            ylabel=sensor_name
        )
        
        return Response(content=chart_bytes, media_type="image/png")
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error generating line chart: {e}")
        raise HTTPException(status_code=500, detail="Error generating chart")


@router.get("/bar/{facade_id}/average")
async def get_bar_chart_average(
    facade_id: str,
    facade_type: Optional[str] = Query(None, description="Filter by facade type: 'refrigerada', 'no_refrigerada'")
):
    """
    Generates a bar chart showing average values of all sensors for a facade.

    HU06: View bar charts to easily interpret data.
    HU04: View the average temperature per panel in the non-refrigerated facade.

    Parameters:
    - facade_id (str): ID of the facade. Required.
    - facade_type (Optional[str]): Filter by facade type. Default: None.

    Returns:
    - Image: PNG chart as binary response.

    Exceptions:
    - HTTPException (404): No data available for chart generation.
    - HTTPException (500): Error generating chart.
    """
    try:
        # Fetch average values
        averages = await analytics_service.get_facade_average(facade_id, facade_type=facade_type)
        
        if not averages:
            raise HTTPException(status_code=404, detail="No data available for chart generation")
        
        # Convert to dict for bar chart
        data_dict = {row["sensor_name"]: float(row["avg_value"]) for row in averages if row.get("avg_value")}
        
        # Generate bar chart
        title = f"Average Sensor Values - Facade {facade_id}"
        if facade_type:
            title += f" ({facade_type})"
        
        chart_bytes = chart_manager.generate_bar_chart(
            data=data_dict,
            title=title,
            xlabel="Sensor",
            ylabel="Average Value"
        )
        
        return Response(content=chart_bytes, media_type="image/png")
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error generating bar chart: {e}")
        raise HTTPException(status_code=500, detail="Error generating chart")


@router.get("/comparison/{facade_id}")
async def get_comparison_chart(
    facade_id: str,
    sensor_name: str = Query(..., description="Sensor to compare"),
    start: Optional[str] = Query(None, description="Start date in ISO8601 format"),
    end: Optional[str] = Query(None, description="End date in ISO8601 format"),
    limit: int = Query(1000, ge=1, le=5000, description="Maximum number of data points per type")
):
    """
    Generates an overlay comparison chart between refrigerated and non-refrigerated facades.

    HU09: Graphically compare two facades by overlaying charts to evaluate performance.
    HU17: Compare performance with and without refrigeration to validate hypotheses.

    Parameters:
    - facade_id (str): ID of the facade. Required.
    - sensor_name (str): Name of the sensor to compare. Required.
    - start (Optional[str]): Start date/time in ISO8601 format. Default: None.
    - end (Optional[str]): End date/time in ISO8601 format. Default: None.
    - limit (int): Maximum number of data points per facade type. Default: 1000.

    Returns:
    - Image: PNG chart as binary response.

    Exceptions:
    - HTTPException (404): No data available for comparison.
    - HTTPException (500): Error generating chart.
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
        
        # Generate comparison chart
        chart_bytes = chart_manager.generate_comparison_chart(
            data1=refrigerada_data,
            data2=no_refrigerada_data,
            label1="Refrigerated Facade",
            label2="Non-Refrigerated Facade",
            x_field="ts",
            y_field="value",
            title=f"Comparison: {sensor_name} - Facade {facade_id}",
            xlabel="Time",
            ylabel=sensor_name
        )
        
        return Response(content=chart_bytes, media_type="image/png")
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error generating comparison chart: {e}")
        raise HTTPException(status_code=500, detail="Error generating chart")


@router.get("/power-irradiance/{facade_id}")
async def get_power_irradiance_chart(
    facade_id: str,
    facade_type: Optional[str] = Query(None, description="Filter by facade type: 'refrigerada', 'no_refrigerada'"),
    start: Optional[str] = Query(None, description="Start date in ISO8601 format"),
    end: Optional[str] = Query(None, description="End date in ISO8601 format"),
    limit: int = Query(1000, ge=1, le=5000, description="Maximum number of data points")
):
    """
    Generates a chart showing generated power and irradiance over time.

    HU07: Generate a chart with generated power and irradiance over time.

    Note: Power is calculated using a simplified model based on irradiance and panel area.

    Parameters:
    - facade_id (str): ID of the facade. Required.
    - facade_type (Optional[str]): Filter by facade type. Default: None.
    - start (Optional[str]): Start date/time in ISO8601 format. Default: None.
    - end (Optional[str]): End date/time in ISO8601 format. Default: None.
    - limit (int): Maximum number of data points. Default: 1000.

    Returns:
    - Image: PNG chart as binary response with dual y-axes.

    Exceptions:
    - HTTPException (404): No irradiance data available.
    - HTTPException (500): Error generating chart.
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
        
        power_data = []
        for record in irradiance_data:
            irradiance_w_m2 = record.get("value", 0)
            power_w = irradiance_w_m2 * panel_area * efficiency
            power_data.append({
                "ts": record["ts"],
                "value": power_w,
                "device_id": record["device_id"],
                "facade_type": record.get("facade_type")
            })
        
        # Generate dual-axis chart (irradiance and power)
        chart_bytes = chart_manager.generate_multi_series_chart(
            data_series=[
                (irradiance_data, "Irradiance (W/m²)"),
                (power_data, "Generated Power (W)")
            ],
            x_field="ts",
            y_field="value",
            title=f"Power Generation & Irradiance - Facade {facade_id}",
            xlabel="Time",
            ylabel="Mixed Units"
        )
        
        return Response(content=chart_bytes, media_type="image/png")
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error generating power/irradiance chart: {e}")
        raise HTTPException(status_code=500, detail="Error generating chart")
