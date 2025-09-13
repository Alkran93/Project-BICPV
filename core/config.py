# Application configuration and settings

from typing import Any

from dotenv import load_dotenv
from pydantic_settings import BaseSettings


load_dotenv()


class Settings(BaseSettings):
    # Database Configuration - Sin contraseña
    DATABASE_URL: str = "postgresql://postgres@localhost:5432/iot"
    REDIS_URL: str = "redis://localhost:6379/0"
    # MQTT Configuration
    MQTT_CONNECTION_CONFIG: dict[str, Any] = {
        "host": "localhost",
        "port": 1884,  # Cambiado del puerto 1883 estándar a 1884
        "keepalive": 60,
        "username": None,
        "password": None,
    }

    TOPIC_FILTER: str = "sensors/+/all"
    BATCH_MAX: int = 200
    BATCH_INTERVAL: float = 1.0
    REDIS_LATEST_EX: int = 120


settings = Settings()
