"""
System Control Routes
Provides endpoints for controlling the refrigeration system remotely.

HU14: Turn the system on or off from the dashboard to exercise direct control.
HU11: View the high and low pressures of the refrigeration system.
"""
from fastapi import APIRouter, HTTPException, Body
from typing import Optional
from pydantic import BaseModel
from ..services import storage_controller
import os

router = APIRouter(prefix="/control", tags=["control"])


class ControlCommand(BaseModel):
    """Model for system control commands."""
    command: str  # 'start', 'stop', 'restart'
    facade_id: str
    device_id: Optional[str] = None


@router.post("/system")
async def control_system(command: ControlCommand):
    """
    Sends a control command to the refrigeration system via MQTT.

    HU14: Turn the system on or off from the dashboard to exercise direct control.

    Parameters:
    - command (ControlCommand): Control command containing action and target system info.
      - command: 'start', 'stop', or 'restart'
      - facade_id: ID of the facade to control
      - device_id: Optional device ID (defaults to facade's main controller)

    Returns:
    - Dict: Confirmation of command sent with details.

    Exceptions:
    - HTTPException (400): Invalid command.
    - HTTPException (500): Error sending command.

    Note: This is a placeholder implementation. In production, this would publish
    MQTT messages to a control topic that the facade controller subscribes to.
    """
    try:
        valid_commands = ['start', 'stop', 'restart']
        
        if command.command not in valid_commands:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid command. Must be one of: {', '.join(valid_commands)}"
            )
        
        # In a real implementation, publish MQTT command to control topic
        # Example: mqtt_client.publish(f"control/{command.facade_id}/system", command.command)
        
        # For now, log the command
        print(f"🎮 Control command: {command.command} for facade {command.facade_id}")
        
        return {
            "status": "command_sent",
            "command": command.command,
            "facade_id": command.facade_id,
            "device_id": command.device_id,
            "message": f"Control command '{command.command}' sent successfully",
            "note": "System control requires MQTT broker integration (not yet implemented)"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error sending control command: {e}")
        raise HTTPException(status_code=500, detail="Error sending control command")


@router.get("/pressure/{facade_id}")
async def get_system_pressures(
    facade_id: str,
    start: Optional[str] = None,
    end: Optional[str] = None,
    limit: int = 500
):
    """
    Retrieves high and low pressure readings from the refrigeration system.

    HU11: View the high and low pressures of the refrigeration system.

    Parameters:
    - facade_id (str): ID of the refrigerated facade. Required.
    - start (Optional[str]): Start date/time in ISO8601 format. Default: None.
    - end (Optional[str]): End date/time in ISO8601 format. Default: None.
    - limit (int): Maximum number of records to return. Default: 500.

    Returns:
    - Dict: Pressure data with high and low pressure readings.

    Exceptions:
    - HTTPException (404): No pressure data available.
    - HTTPException (500): Error retrieving pressure data.
    """
    try:
        # Fetch high pressure measurements
        high_pressure = await storage_controller.fetch_measurements(
            facade_id=facade_id,
            sensor="Presion_Alta",
            facade_type="refrigerada",
            start=start,
            end=end,
            limit=limit
        )
        
        # Fetch low pressure measurements
        low_pressure = await storage_controller.fetch_measurements(
            facade_id=facade_id,
            sensor="Presion_Baja",
            facade_type="refrigerada",
            start=start,
            end=end,
            limit=limit
        )
        
        if not high_pressure and not low_pressure:
            raise HTTPException(status_code=404, detail="No pressure data available")
        
        return {
            "facade_id": facade_id,
            "facade_type": "refrigerada",
            "pressures": {
                "high_pressure": {
                    "sensor": "Presion_Alta",
                    "unit": "PSI",
                    "count": len(high_pressure),
                    "readings": high_pressure
                },
                "low_pressure": {
                    "sensor": "Presion_Baja",
                    "unit": "PSI",
                    "count": len(low_pressure),
                    "readings": low_pressure
                }
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error retrieving pressure data: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving pressure data")


@router.get("/valve-state/{facade_id}")
async def get_valve_state(
    facade_id: str,
    start: Optional[str] = None,
    end: Optional[str] = None,
    limit: int = 500
):
    """
    Retrieves the state of the solenoid valve (open/closed) over time.

    Parameters:
    - facade_id (str): ID of the refrigerated facade. Required.
    - start (Optional[str]): Start date/time in ISO8601 format. Default: None.
    - end (Optional[str]): End date/time in ISO8601 format. Default: None.
    - limit (int): Maximum number of records to return. Default: 500.

    Returns:
    - Dict: Valve state data with timestamps and states (0=closed, 1=open).

    Exceptions:
    - HTTPException (404): No valve state data available.
    - HTTPException (500): Error retrieving valve state.
    """
    try:
        valve_states = await storage_controller.fetch_measurements(
            facade_id=facade_id,
            sensor="Estado_Electrovalvula",
            facade_type="refrigerada",
            start=start,
            end=end,
            limit=limit
        )
        
        if not valve_states:
            raise HTTPException(status_code=404, detail="No valve state data available")
        
        # Convert numeric values to readable states
        for record in valve_states:
            state_value = record.get("value")
            if state_value == 0:
                record["state_text"] = "Closed"
            elif state_value == 1:
                record["state_text"] = "Open"
            else:
                record["state_text"] = "Unknown"
        
        return {
            "facade_id": facade_id,
            "facade_type": "refrigerada",
            "sensor": "Estado_Electrovalvula",
            "count": len(valve_states),
            "states": valve_states
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error retrieving valve state: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving valve state")


@router.get("/water-flow/{facade_id}")
async def get_water_flow(
    facade_id: str,
    start: Optional[str] = None,
    end: Optional[str] = None,
    limit: int = 500
):
    """
    Retrieves water flow rate measurements from the refrigeration system.

    Parameters:
    - facade_id (str): ID of the refrigerated facade. Required.
    - start (Optional[str]): Start date/time in ISO8601 format. Default: None.
    - end (Optional[str]): End date/time in ISO8601 format. Default: None.
    - limit (int): Maximum number of records to return. Default: 500.

    Returns:
    - Dict: Water flow rate data in liters per minute (LPM).

    Exceptions:
    - HTTPException (404): No flow data available.
    - HTTPException (500): Error retrieving flow data.
    """
    try:
        flow_data = await storage_controller.fetch_measurements(
            facade_id=facade_id,
            sensor="Flujo_Agua_LPM",
            facade_type="refrigerada",
            start=start,
            end=end,
            limit=limit
        )
        
        if not flow_data:
            raise HTTPException(status_code=404, detail="No water flow data available")
        
        return {
            "facade_id": facade_id,
            "facade_type": "refrigerada",
            "sensor": "Flujo_Agua_LPM",
            "unit": "Liters per Minute",
            "count": len(flow_data),
            "readings": flow_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error retrieving water flow data: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving water flow data")
