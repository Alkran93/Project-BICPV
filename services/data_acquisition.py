import asyncio
import contextlib
import json
from datetime import datetime
from typing import Any, Optional

import asyncpg
import paho.mqtt.client as mqtt
from pydantic import BaseModel

from core.config import settings
from repositories.timescale import TimeScaleDBStorage


async def mqtt_consumer_task():
    """
    Tarea asíncrona profesional para consumir datos MQTT y guardarlos en TimescaleDB.
    """
    acquisition = DataAcquisition(settings.MQTT_CONNECTION_CONFIG)
    while True:
        try:
            await acquisition.receive_data()
        except Exception as e:
            await acquisition.log_error(
                "Error en mqtt_consumer_task", "high", {"error": str(e)}
            )
        await asyncio.sleep(0.1)  # Evita bucle apretado


class Error(BaseModel):
    timestamp: datetime
    message: str
    severity: str  # 'low', 'medium', 'high'
    details: Optional[dict[str, Any]] = None


class DataAcquisition:
    def __init__(self, connection_config: dict[str, str]):
        self.connection_config = connection_config
        self.data_buffer: list[dict] = []
        self.collection_frequency = 1.0
        self.register_sensors: dict[str, dict] = {}  # sensor_id -> sensor_data
        self.error_log: list[Error] = []
        self.db_storage: Optional[TimeScaleDBStorage] = None

    async def init_db(self):
        try:
            conn = await asyncpg.connect(settings.DATABASE_URL)
            self.db_storage = TimeScaleDBStorage(conn)
        except Exception as e:
            await self.log_error(
                "Error conectando a TimescaleDB", "high", {"error": str(e)}
            )

    async def receive_data(self) -> None:
        """Recibe datos del broker MQTT de forma continua"""
        while True:
            try:
                # Configurar cliente MQTT
                client = mqtt.Client()
                connected = False
                messages_queue = asyncio.Queue()

                def on_connect(client, userdata, flags, rc):
                    nonlocal connected
                    if rc == 0:
                        client.subscribe(settings.TOPIC_FILTER)
                        connected = True
                    else:
                        error_messages = {
                            1: "Versión de protocolo incorrecta",
                            2: "ID de cliente inválido",
                            3: "Servidor no disponible",
                            4: "Usuario/contraseña incorrectos",
                            5: "No autorizado",
                            7: "No hay conexión",
                        }
                        error_messages.get(rc, f"Error desconocido: {rc}")
                        connected = False

                def on_message(client, userdata, msg, queue=messages_queue):
                    with contextlib.suppress(asyncio.QueueFull):
                        queue.put_nowait(msg)

                def on_disconnect(client, userdata, rc):
                    nonlocal connected
                    connected = False

                client.on_connect = on_connect
                client.on_message = on_message
                client.on_disconnect = on_disconnect

                # Conectar al broker
                client.connect(
                    settings.MQTT_CONNECTION_CONFIG["host"],
                    settings.MQTT_CONNECTION_CONFIG["port"],
                    settings.MQTT_CONNECTION_CONFIG["keepalive"],
                )

                # Iniciar loop en thread separado
                client.loop_start()

                # Esperar conexión
                timeout = 10
                while not connected and timeout > 0:
                    await asyncio.sleep(0.1)
                    timeout -= 0.1

                if not connected:
                    raise Exception("No se pudo conectar al broker MQTT")

                # Procesar mensajes
                while connected:
                    try:
                        msg = await asyncio.wait_for(messages_queue.get(), timeout=1.0)
                        payload = json.loads(msg.payload.decode())
                        data = {
                            "topic": str(msg.topic),
                            "payload": payload,
                            "timestamp": datetime.utcnow(),
                        }
                        await self.save_to_timescale(data)
                    except asyncio.TimeoutError:
                        # Agregar indicador de vida cada 30 segundos
                        if (
                            not hasattr(self, "_last_heartbeat")
                            or (datetime.utcnow() - self._last_heartbeat).seconds > 30
                        ):
                            self._last_heartbeat = datetime.utcnow()
                        continue
                    except json.JSONDecodeError as e:
                        await self.log_error(
                            "Error decodificando JSON",
                            "high",
                            {"error": str(e), "raw_payload": str(msg.payload)},
                        )

            except Exception as e:
                await self.log_error("Error en receive_data", "high", {"error": str(e)})
                await asyncio.sleep(5)
            finally:
                try:
                    client.loop_stop()
                    client.disconnect()
                except Exception:
                    # Log cleanup error but continue shutdown
                    pass

    async def save_to_timescale(self, raw_data: dict) -> None:
        """Guarda los datos en TimescaleDB"""
        if not self.db_storage:
            await self.init_db()

        # Asegurar que las tablas existan
        await self.db_storage.ensure_tables_exist()

        structured_list = await self.structure_data(raw_data)
        timescale_tuples = [
            (
                structured["timestamp"],
                structured["device_id"],
                structured["sensor_id"],
                structured["value"],
                structured["unit"],
                json.dumps(structured["metadata"]),
                structured.get("facade_id", None),
            )
            for structured in structured_list
        ]
        try:
            await self.db_storage.store(timescale_tuples)
        except Exception as e:
            await self.log_error(
                "Error guardando en TimescaleDB",
                "high",
                {"error": str(e), "data": timescale_tuples},
            )

    async def structure_data(self, raw_data: dict) -> list[dict]:
        """Estructura los datos recibidos para múltiples sensores en 'data'."""
        try:
            from dateutil import parser as date_parser

            topic_parts = raw_data["topic"].split("/")
            payload = raw_data["payload"]
            device_id = payload.get(
                "device_id", topic_parts[1] if len(topic_parts) > 1 else "unknown"
            )
            facade_id = payload.get("facade_id")
            timestamp = payload.get("ts", raw_data["timestamp"])
            # Convertir timestamp a datetime si es string
            if isinstance(timestamp, str):
                try:
                    timestamp = date_parser.parse(timestamp)
                except Exception:
                    timestamp = raw_data["timestamp"]
            data_dict = payload.get("data", {})
            structured_list = []
            for sensor_id, value in data_dict.items():
                structured_list.append(
                    {
                        "device_id": device_id,
                        "sensor_id": sensor_id,
                        "value": value,
                        "unit": "N/A",  # Puedes mapear unidades si las tienes
                        "timestamp": timestamp,
                        "facade_id": facade_id,
                        "metadata": {
                            "topic": raw_data["topic"],
                            "raw_payload": payload,
                        },
                    }
                )
            return structured_list
        except Exception as e:
            await self.log_error(
                "Error estructurando datos",
                "medium",
                {"error": str(e), "raw_data": raw_data},
            )
            raise

    async def send_to_validation(self, data: dict) -> bool:
        """Envía los datos a validación"""
        try:
            # Validaciones básicas
            required_fields = ["device_id", "sensor_id", "value", "timestamp"]
            if not all(field in data for field in required_fields):
                await self.log_error(
                    "Datos incompletos",
                    "medium",
                    {"missing_fields": [f for f in required_fields if f not in data]},
                )
                return False
            return True
        except Exception as e:
            await self.log_error(
                "Error en validación", "high", {"error": str(e), "data": data}
            )
            return False

    async def process_data(self, data: dict) -> dict:
        """Procesa los datos estructurados"""
        try:
            # Aquí iría la lógica de procesamiento específica
            result = {**data, "processed_at": datetime.utcnow(), "status": "processed"}
            # Guardar en el buffer
            self.data_buffer.append(result)
            return {"success": True, "data": result}
        except Exception as e:
            await self.log_error(
                "Error procesando datos", "high", {"error": str(e), "data": data}
            )
            return {"success": False, "error": str(e)}

    async def log_error(
        self, message: str, severity: str, details: Optional[dict] = None
    ) -> bool:
        """Registra un error en el log"""
        try:
            error = Error(
                timestamp=datetime.utcnow(),
                message=message,
                severity=severity,
                details=details or {},
            )
            self.error_log.append(error)
            # También podrías guardar en un log externo aquí
            if details:
                pass
            return True
        except Exception:
            return False

    def get_errors(self) -> list[Error]:
        """Obtiene la lista de errores"""
        return self.error_log
