import argparse
import json
import random
import time
from datetime import datetime, timezone
from typing import Dict, List, Any

try:
    import paho.mqtt.client as mqtt
except Exception as e:
    raise SystemExit("Install paho-mqtt: pip install paho-mqtt") from e


# === MODULE AND SENSOR CONFIGURATION ===
MODULES = ["M1", "M2", "M3", "M4", "M5"]  # Module identifiers
POINTS_PER_MODULE = 3  # Number of measurement points per module


# === SENSOR MAPPING ===
def generate_sensor_map(facade_type: str = "no_refrigerada") -> Dict[str, str]:
    """
    Generates a sensor mapping based on the facade type.

    Parameters:
    - facade_type (str): Type of facade ('refrigerada' or 'no_refrigerada'). Default: 'no_refrigerada'.

    Returns:
    - Dict[str, str]: Dictionary mapping sensor IDs to sensor names.
    """
    sensor_map = {}
    
    if facade_type == "no_refrigerada":
        # Sensor IDs for non-refrigerated facade (15 temperature sensors: 5 modules × 3 points)
        sensor_ids = [
            "00000060be1e", "00000060dfc5", "000000615422",  # M1, M2, M3
            "000000619813", "00000065b191", "000000617179",  # M1, M2, M3
            "00000061fcd4", "00000062bab4", "00000061868c",  # M1, M2, M3
            "0000006395cf", "000000616636", "00000060c752",  # M1, M2, M3
            "000000609e8b", "00000062f690", "00000063ad21",  # M1, M2, M3
        ]
        for i, module in enumerate(MODULES):
            for point in range(1, POINTS_PER_MODULE + 1):
                idx = i * POINTS_PER_MODULE + (point - 1)
                if idx < len(sensor_ids):
                    sensor_map[sensor_ids[idx]] = f"Temperature_{module}_{point}"
    
    else:  # refrigerada
        # Sensor IDs for refrigerated facade (15 panel temperature sensors + refrigeration cycle sensors)
        sensor_ids = [
            "00000060be1e", "00000060dfc5", "000000615422",
            "000000619813", "00000065b191", "000000617179",
            "00000061fcd4", "00000062bab4", "00000061868c",
            "0000006395cf", "000000616636", "00000060c752",
            "000000609e8b", "00000062f690", "00000063ad21",
        ]
        for i, module in enumerate(MODULES):
            for point in range(1, POINTS_PER_MODULE + 1):
                idx = i * POINTS_PER_MODULE + (point - 1)
                if idx < len(sensor_ids):
                    sensor_map[sensor_ids[idx]] = f"Temperature_{module}_{point}"
        
        # Additional sensors for refrigeration cycle
        sensor_map.update({
            "00000063b890": "T_Entrada_Agua",
            "00000061916c": "T_ValvulaExpansion",
            "000000610398": "T_Salida_Agua",
            "000000611dc5": "T_SalCompresor",
            "000000609073": "T_EntCompresor",
            "000000625eef": "T_SalCondensador",
        })
        
        # Intermediate sensors: inlet to each module
        for i, module in enumerate(MODULES):
            sensor_map[f"0000006{i:05d}"] = f"T_Entrada_{module}"
    
    return sensor_map


# === SENSOR SIMULATION FUNCTIONS ===
def random_temp(base: float = 25.0, spread: float = 6.0) -> float:
    """Generates a random temperature value within a specified range."""
    return round(random.uniform(base - spread, base + spread), 2)


def random_humidity() -> float:
    """Generates a random humidity value between 20% and 85%."""
    return round(random.uniform(20, 85), 2)


def random_pressure(min_psi: float = 0, max_psi: float = 200) -> float:
    """Generates a random pressure value within a specified range."""
    return round(random.uniform(min_psi, max_psi), 2)


def random_flow_rate(min_lpm: float = 0, max_lpm: float = 50) -> float:
    """Generates a random flow rate value in liters per minute."""
    return round(random.uniform(min_lpm, max_lpm), 2)


def random_voltage(min_v: float = 0.1, max_v: float = 4.2) -> float:
    """Generates a random voltage value within a specified range."""
    return round(random.uniform(min_v, max_v), 3)


def calculate_irradiance(v_out: float) -> float:
    """Converts voltage output to irradiance in W/m²."""
    try:
        return round(v_out / 0.0017457, 2)
    except Exception:
        return 0.0


def calculate_wind_speed(v_out: float) -> float:
    """Calculates wind speed from voltage output."""
    if v_out < 0.5:
        return 0.0
    elif v_out > 2.0:
        return 70.0
    return round((v_out - 0.4) * 31.25 + 0.5, 2)


def calculate_pressure_from_adc(volt: float, offset: float) -> float:
    """Converts ADC voltage to pressure in PSI."""
    try:
        scale = (39000 + 100000) / 100000.0
        value = (200.0 / (4.5 - offset)) * ((volt * scale) - offset)
        return round(value, 2)
    except Exception:
        return 0.0


# === PAYLOAD BUILDERS BY FACADE TYPE ===
def build_common_environmental_data() -> Dict[str, float]:
    """
    Generates common environmental data for both facade types.

    Returns:
    - Dict[str, float]: Dictionary containing environmental sensor readings.
    """
    return {
        "Temperatura_Ambiente": random_temp(base=26, spread=8),
        "Humedad": random_humidity(),
        "Irradiancia": calculate_irradiance(random_voltage(0.05, 3.5)),
        "Velocidad_Viento": calculate_wind_speed(random_voltage(0.1, 2.2)),
    }


def build_payload_no_refrigerada(facade_id: str = "1", device_id: str = "raspi_no_ref_01") -> Dict[str, Any]:
    """
    Builds a payload for a non-refrigerated facade.

    Parameters:
    - facade_id (str): ID of the facade. Default: "1".
    - device_id (str): ID of the device. Default: "raspi_no_ref_01".

    Returns:
    - Dict[str, Any]: Payload dictionary with facade data.
    """
    data = build_common_environmental_data()
    
    # Module temperature sensors (3 points per module)
    sensor_map = generate_sensor_map("no_refrigerada")
    for _id, name in sensor_map.items():
        data[name] = random_temp(base=27, spread=10)
    
    return {
        "facade_id": str(facade_id),
        "device_id": str(device_id),
        "facade_type": "no_refrigerada",
        "ts": datetime.now(timezone.utc).isoformat(),
        "data": data,
    }


def build_payload_refrigerada(facade_id: str = "1", device_id: str = "raspi_ref_01") -> Dict[str, Any]:
    """
    Builds a payload for a refrigerated facade, including refrigeration cycle data.

    Parameters:
    - facade_id (str): ID of the facade. Default: "1".
    - device_id (str): ID of the device. Default: "raspi_ref_01".

    Returns:
    - Dict[str, Any]: Payload dictionary with facade and refrigeration cycle data.
    """
    data = build_common_environmental_data()
    
    # Module temperature sensors and refrigeration cycle sensors
    sensor_map = generate_sensor_map("refrigerada")
    for _id, name in sensor_map.items():
        data[name] = random_temp(base=27, spread=10)
    
    # Refrigeration cycle temperatures
    data["T_ValvulaExpansion"] = random_temp(base=8, spread=3)  # Low temperature at expansion valve
    data["T_EntCompresor"] = random_temp(base=5, spread=2)  # Compressor inlet
    data["T_SalCompresor"] = random_temp(base=50, spread=15)  # High temperature at compressor outlet
    data["T_SalCondensador"] = random_temp(base=40, spread=10)  # Condenser outlet
    
    # Module inlet and outlet temperatures
    t_entrada = data["T_ValvulaExpansion"]
    for i, module in enumerate(MODULES):
        # Simulate slight temperature increase through each module
        data[f"T_Entrada_{module}"] = round(t_entrada + (i * 0.5), 2)
        data[f"T_Salida_{module}"] = round(data.get(f"T_Entrada_{module}", t_entrada) + random.uniform(2, 5), 2)
    
    # Condenser water temperatures
    data["T_Entrada_Agua"] = random_temp(base=15, spread=3)  # Cooler inlet water
    data["T_Salida_Agua"] = round(data["T_Entrada_Agua"] + random.uniform(8, 15), 2)  # Warmer outlet water
    
    # Compressor pressures
    data["Presion_Alta"] = calculate_pressure_from_adc(random_voltage(1.0, 4.2), offset=0.434)
    data["Presion_Baja"] = calculate_pressure_from_adc(random_voltage(0.4, 2.0), offset=0.145)
    
    # Water flow rate
    data["Flujo_Agua_LPM"] = random_flow_rate(min_lpm=5, max_lpm=30)
    
    # Solenoid valve state (0=closed, 1=open)
    data["Estado_Electrovalvula"] = random.choice([0, 1])
    
    return {
        "facade_id": str(facade_id),
        "device_id": str(device_id),
        "facade_type": "refrigerada",
        "ts": datetime.now(timezone.utc).isoformat(),
        "data": data,
    }


# === MQTT PUBLISHER ===
def run_publisher(
    host: str = "localhost",
    port: int = 1884,
    topic_base: str = "sensors",
    frequency: float = 3.0,
    facades_config: List[Dict[str, str]] | None = None,
    wrap: bool = False,
    retain: bool = False,
) -> None:
    """
    Publishes MQTT payloads for multiple facades (refrigerated and non-refrigerated).

    Parameters:
    - host (str): MQTT broker host. Default: "localhost".
    - port (int): MQTT broker port. Default: 1884.
    - topic_base (str): Base MQTT topic. Default: "sensors".
    - frequency (float): Publishing frequency in seconds. Default: 3.0.
    - facades_config (List[Dict[str, str]] | None): List of facade configurations, each with 'type', 'facade_id', and 'device_id'. Default: None (uses default config).
    - wrap (bool): If True, wraps payload in {"payload": ...}. Default: False.
    - retain (bool): If True, publishes messages with the retain flag. Default: False.

    Exceptions:
    - mqtt.MQTTException: Raised if MQTT connection or publishing fails.
    """
    if facades_config is None:
        # Default configuration: one non-refrigerated and one refrigerated facade
        facades_config = [
            {"type": "no_refrigerada", "facade_id": "1", "device_id": "raspi_no_ref_01"},
            {"type": "refrigerada", "facade_id": "2", "device_id": "raspi_ref_01"},
        ]
    
    # Initialize MQTT client
    try:
        client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
    except TypeError:
        client = mqtt.Client()

    client.loop_start()
    try:
        client.connect(host, port, 60)
    except Exception as e:
        print(f"[ERROR] Failed to connect to MQTT broker {host}:{port} -> {e}")
        client.loop_stop()
        return

    print(f"[SIMULATOR] Publishing to mqtt://{host}:{port} with {len(facades_config)} facade(s)")
    print(f"[SIMULATOR] Frequency: {frequency}s, topic_base: '{topic_base}'")
    
    try:
        while True:
            for facade_cfg in facades_config:
                facade_type = facade_cfg.get("type", "no_refrigerada")
                facade_id = facade_cfg.get("facade_id", "1")
                device_id = facade_cfg.get("device_id", "raspi_01")
                
                # Generate payload based on facade type
                if facade_type == "refrigerada":
                    payload = build_payload_refrigerada(facade_id=facade_id, device_id=device_id)
                else:
                    payload = build_payload_no_refrigerada(facade_id=facade_id, device_id=device_id)
                
                # Publish to MQTT
                topic = f"{topic_base}/{device_id}/all"
                to_send = {"payload": payload} if wrap else payload
                payload_json = json.dumps(to_send, ensure_ascii=False)
                
                result = client.publish(topic, payload_json, retain=retain)
                if hasattr(result, "rc") and result.rc != 0:
                    print(f"[WARN] rc={result.rc} when publishing")
                
                print(f"[PUB] type={facade_type} facade={facade_id} device={device_id} topic={topic}")
            
            time.sleep(frequency)
    
    except KeyboardInterrupt:
        print("\n[SIMULATOR] Interrupted by keyboard. Shutting down...")
    finally:
        try:
            client.disconnect()
        except Exception:
            pass
        client.loop_stop()


# === CLI ===
def cli() -> None:
    """
    Command-line interface for the MQTT simulator.

    Parses command-line arguments and runs the MQTT publisher.
    """
    parser = argparse.ArgumentParser(description="MQTT Simulator for refrigerated and non-refrigerated facades")
    parser.add_argument("--host", default="localhost", help="MQTT broker host")
    parser.add_argument("--port", type=int, default=1884, help="MQTT broker port")
    parser.add_argument("--topic-base", default="sensors", help="Base MQTT topic")
    parser.add_argument("--freq", type=float, default=3.0, help="Publishing frequency (seconds)")
    parser.add_argument(
        "--facades",
        type=str,
        default="no_refrigerada:1:raspi_no_ref_01,refrigerada:2:raspi_ref_01",
        help="Facade configuration (format: type:facade_id:device_id,type:facade_id:device_id,...)"
    )
    parser.add_argument("--wrap", action="store_true", help="Wrap payload in {'payload': ...}")
    parser.add_argument("--retain", action="store_true", help="Publish with retain flag")
    args = parser.parse_args()

    # Parse facade configuration
    facades_config = []
    for facade_str in args.facades.split(","):
        parts = facade_str.strip().split(":")
        if len(parts) == 3:
            facades_config.append({
                "type": parts[0],
                "facade_id": parts[1],
                "device_id": parts[2],
            })
    
    if not facades_config:
        print("[ERROR] No valid facades specified")
        return

    run_publisher(
        host=args.host,
        port=args.port,
        topic_base=args.topic_base,
        frequency=args.freq,
        facades_config=facades_config,
        wrap=args.wrap,
        retain=args.retain,
    )


if __name__ == "__main__":
    cli()