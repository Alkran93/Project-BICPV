import os
import json
import asyncio
import logging
from datetime import datetime

import asyncpg
import redis.asyncio as aioredis
from aiomqtt import Client, MqttError

# ==============================
# Logging Configuration
# ==============================
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("ingestor")

# ==============================
# Environment Variables
# ==============================
MQTT_BROKER = os.getenv("MQTT_BROKER", "mosquitto")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "sensors/+/all")

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres:postgres@timescaledb:5432/postgres"
)


# ==============================
# Payload Processing
# ==============================
async def handle_payload(payload: dict, redis_conn: aioredis.Redis, pg_pool: asyncpg.Pool) -> None:
    """
    Processes and stores a message received from MQTT in Redis and TimescaleDB.

    Parameters:
    - payload (dict): The MQTT message payload containing sensor data.
    - redis_conn (aioredis.Redis): Redis connection for caching latest sensor data.
    - pg_pool (asyncpg.Pool): TimescaleDB connection pool for persistent storage.

    Purpose:
    - Extracts and validates timestamp, facade ID, device ID, facade type, and sensor data.
    - Stores latest sensor readings in Redis as a HASH.
    - Persists sensor readings in TimescaleDB for historical analysis.

    Exceptions:
    - ValueError: Raised if the payload is malformed or missing required fields.
    - asyncpg.exceptions.PostgresError: Raised if a database operation fails.
    - redis.exceptions.RedisError: Raised if a Redis operation fails.
    """
    # Extract and validate timestamp, defaulting to current UTC time if not provided
    ts_str = payload.get("ts", datetime.utcnow().isoformat() + "Z")
    if ts_str.endswith("Z"):
        ts_str = ts_str.replace("Z", "+00:00")
    try:
        ts_dt = datetime.fromisoformat(ts_str)
    except ValueError as e:
        log.error(f"Invalid timestamp format in payload: {ts_str}, error: {e}")
        return

    # Extract facade and device information
    facade_id = str(payload.get("facade_id", "unknown"))
    device_id = str(payload.get("device_id", "unknown"))
    facade_type = str(payload.get("facade_type", "unknown"))
    data = payload.get("data", {})

    if not data:
        log.warning(f"No sensor data in payload for device {device_id} ({facade_type})")
        return

    # Store in Redis (HASH with all sensors for the facade)
    key = f"facade:{facade_id}:latest"
    try:
        pipe = redis_conn.pipeline()
        for sensor_name, value in data.items():
            entry = json.dumps({
                "value": value,
                "ts": ts_str,
                "device_id": device_id,
                "facade_type": facade_type
            })
            pipe.hset(key, sensor_name, entry)
        await pipe.execute()
        log.debug(f"Stored {len(data)} sensor readings in Redis for {key}")
    except redis.exceptions.RedisError as e:
        log.error(f"Failed to store data in Redis for {key}: {e}")

    # Prepare records for TimescaleDB
    records = []
    for sensor_name, value in data.items():
        try:
            val = float(value)
        except (ValueError, TypeError):
            val = None
            log.warning(f"Invalid value for sensor {sensor_name}: {value}, storing as NULL")
        records.append((facade_id, device_id, facade_type, sensor_name, val, ts_dt))

    # Insert into TimescaleDB
    try:
        async with pg_pool.acquire() as conn:
            async with conn.transaction():
                await conn.executemany(
                    """
                    INSERT INTO measurements (facade_id, device_id, facade_type, sensor_name, value, ts)
                    VALUES ($1, $2, $3, $4, $5, $6)
                    """,
                    records,
                )
        log.info(f"📩 Processed: {device_id} ({facade_type}) - {len(data)} sensors")
    except asyncpg.exceptions.PostgresError as e:
        log.error(f"Failed to insert data into TimescaleDB: {e}")


# ==============================
# Main Loop
# ==============================
async def main() -> None:
    """
    Main process for the MQTT data ingestor.

    Purpose:
    - Initializes connections to Redis and TimescaleDB.
    - Subscribes to the configured MQTT topic and processes incoming messages.
    - Implements reconnection logic for MQTT broker failures.

    Exceptions:
    - MqttError: Handled with reconnection attempts for MQTT connection issues.
    - Exception: Logged for unexpected errors, with reconnection attempts.
    """
    # Initialize Redis and TimescaleDB connections
    try:
        redis_conn = aioredis.from_url(REDIS_URL, decode_responses=True)
        pg_pool = await asyncpg.create_pool(dsn=DATABASE_URL, min_size=1, max_size=10)
        log.info("Initialized Redis and TimescaleDB connections")
    except Exception as e:
        log.error(f"Failed to initialize connections: {e}")
        raise

    reconnect_interval = 5  # Seconds between reconnection attempts

    while True:
        try:
            log.info(f"Connecting to MQTT broker {MQTT_BROKER}:{MQTT_PORT} ...")
            async with Client(hostname=MQTT_BROKER, port=MQTT_PORT) as client:
                log.info(f"Subscribed to {MQTT_TOPIC}")
                await client.subscribe(MQTT_TOPIC)
                
                # Process incoming MQTT messages
                async for message in client.messages:
                    try:
                        payload = json.loads(message.payload.decode())
                        await handle_payload(payload, redis_conn, pg_pool)
                    except json.JSONDecodeError as e:
                        log.error(f"Invalid JSON in MQTT message: {e}")
                    except Exception as e:
                        log.error(f"Error processing MQTT message: {e}")

        except MqttError as me:
            log.warning(f"MQTT disconnected: {me}. Reconnecting in {reconnect_interval}s ...")
            await asyncio.sleep(reconnect_interval)
        except Exception as e:
            log.exception(f"Unexpected error in ingestor: {e}")
            await asyncio.sleep(reconnect_interval)

    # Note: The following cleanup is unreachable due to the infinite loop but included for completeness
    try:
        if redis_conn:
            await redis_conn.close()
        if pg_pool:
            await pg_pool.close()
    except Exception as e:
        log.error(f"Error closing connections: {e}")


if __name__ == "__main__":
    asyncio.run(main())