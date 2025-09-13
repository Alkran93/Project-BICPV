import json
import random
import time
from datetime import datetime, timezone

import paho.mqtt.client as mqtt


SENSOR_MAP = {
    "00000060be1e": "Temperatura_L1_2",
    "00000060dfc5": "Temperatura_L1_3",
    "000000615422": "Temperatura_L1_1",
    "000000619813": "Temperatura_L2_2",
    "00000065b191": "Temperatura_L2_3",
    "000000617179": "Temperatura_L2_1",
    "00000061fcd4": "Temperatura_L3_2",
    "00000062bab4": "Temperatura_L3_3",
    "00000061868c": "Temperatura_L3_1",
    "0000006395cf": "Temperatura_L4_2",
    "000000616636": "Temperatura_L4_3",
    "00000060c752": "Temperatura_L4_1",
    "000000609e8b": "Temperatura_L5_2",
    "00000062f690": "Temperatura_L5_3",
    "00000063ad21": "Temperatura_L5_1",
    "00000063b890": "ENT_AGU",
    "00000061916c": "ENT_REF",
    "000000610398": "SAL_AGU",
    "000000611dc5": "SAL_REF",
    "000000609073": "ENT_N1",
    "000000625eef": "N1_N2",
    "000000616563": "N2_N3",
    "00000061bc99": "N3_N4",
    "00000061cf21": "N4_N5",
    "00000060d399": "N5_SAL",
}

# Simulación de valores realistas por tipo de sensor


def random_temp():
    return round(random.uniform(20, 35), 2)


def random_presion():
    return round(random.uniform(0, 100), 2)


def random_corriente():
    return round(random.uniform(-5, 5), 2)


def random_voltaje():
    return round(random.uniform(0, 5), 2)


def random_potencia():
    return round(random.uniform(0, 100), 2)


def random_irradiancia():
    return round(random.uniform(0, 1000), 2)


def random_velocidad():
    return round(random.uniform(0, 20), 2)


def build_payload():
    data = {}
    # Sensores del SENSOR_MAP
    for _sensor_id, nombre in SENSOR_MAP.items():
        if "Temperatura" in nombre:
            data[nombre] = random_temp()
        elif (
            "Presion" in nombre or "ENT_" in nombre or "SAL_" in nombre or "N" in nombre
        ):
            data[nombre] = random_presion()
        else:
            data[nombre] = random_presion()

    # Sensores adicionales de la base de datos
    data["Bus_V"] = random_voltaje()
    data["Shunt_V"] = random_voltaje()
    data["Corriente_mA"] = random_corriente()
    data["Potencia_W"] = random_potencia()
    data["Presion_IN"] = random_presion()
    data["Presion_OUT"] = random_presion()
    data["Velocidad_Viento"] = random_velocidad()
    data["Irradiancia"] = random_irradiancia()
    data["Sensor_Voltaje"] = random_voltaje()
    data["sensor_8242"] = random_temp()
    data["sensor_af8d"] = random_temp()

    payload = {
        "facade_id": "1",
        "device_id": "raspi01",
        "ts": datetime.now(timezone.utc).isoformat(),
        "data": data,
    }
    return payload


def main():
    client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
    client.connect("localhost", 1884, 60)  # Puerto cambiado a 1884
    topic = "sensors/raspi01/all"
    while True:
        payload = build_payload()
        client.publish(topic, json.dumps(payload))
        time.sleep(3)


if __name__ == "__main__":
    main()
