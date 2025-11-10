import json
from typing import Dict, Any, Optional
import redis.asyncio as aioredis
from ..core.config import settings

# Global Redis client instance
redis_client: aioredis.Redis | None = None


async def init_redis() -> None:
    """
    Initializes the global Redis client using the configured Redis URL.

    Purpose:
    - Establishes a connection to the Redis server for caching operations.

    Returns:
    - None

    Exceptions:
    - redis.exceptions.ConnectionError: Raised if the connection to the Redis server fails.
    """
    global redis_client
    # Create a Redis client instance with the configured URL
    redis_client = aioredis.from_url(
        settings.REDIS_URL,
        decode_responses=True
    )


async def close_redis() -> None:
    """
    Closes the global Redis client connection.

    Purpose:
    - Safely terminates the Redis connection and resets the client to None.

    Returns:
    - None

    Exceptions:
    - redis.exceptions.ConnectionError: Raised if there is an issue closing the connection.
    """
    global redis_client
    if redis_client:
        # Close the Redis connection and reset the client
        await redis_client.close()
        redis_client = None


async def get_latest_facade(facade_id: str, facade_type: Optional[str] = None) -> Dict[str, Any]:
    """
    Retrieves the most recent data for a specific facade from Redis, stored as a HASH.

    HU02: Select a facade to view its data individually.

    Parameters:
    - facade_id (str): ID of the facade to retrieve data for. Required.
    - facade_type (Optional[str]): Filter by facade type. Valid values: 'refrigerada', 'no_refrigerada'. Default: None (retrieve data for both types if available).

    Returns:
    - Dict[str, Any]: Dictionary containing:
      - facade_id (str): ID of the facade.
      - facade_type (str or null): The facade type filter applied, if any.
      - data (dict or null): The latest facade data, or None if no data is available.
      - message (str, optional): Descriptive message if no data is available.
      - error (str, optional): Error message if an exception occurs.

    Exceptions:
    - RuntimeError: Raised if the Redis client is not initialized.
    - redis.exceptions.RedisError: Raised if a Redis operation fails.
    """
    global redis_client

    # Check if Redis client is initialized
    if not redis_client:
        raise RuntimeError("Redis client not initialized")

    try:
        # Generate Redis key based on facade type
        if facade_type:
            key = f"facade:{facade_id}:{facade_type}:latest"
        else:
            key = f"facade:{facade_id}:latest"

        # Retrieve all fields from the Redis HASH
        data = await redis_client.hgetall(key)

        # Return a message if no data is found
        if not data:
            return {
                "facade_id": facade_id,
                "facade_type": facade_type,
                "data": None,
                "message": "No recent data in Redis"
            }

        # Decode JSON values if necessary
        try:
            decoded_data = {
                k: json.loads(v) if isinstance(v, str) and v.startswith("{") else v
                for k, v in data.items()
            }
        except Exception:
            decoded_data = data

        # Construct and return the response
        return {
            "facade_id": facade_id,
            "facade_type": facade_type,
            "data": decoded_data
        }

    except Exception as e:
        # Log the error for debugging purposes
        print(f"❌ Error retrieving real-time data for facade {facade_id}: {e}")
        # Return error details
        return {
            "facade_id": facade_id,
            "facade_type": facade_type,
            "data": None,
            "error": str(e)
        }


async def get_all_facades_latest() -> Dict[str, Any]:
    """
    Retrieves the most recent data for all facades from Redis.

    HU01: View an overview of both facades to compare their current status.

    Returns:
    - Dict[str, Any]: Dictionary containing:
      - data (dict or null): Nested dictionary with facade IDs as keys and facade type data as values, or None if no data is available.
      - message (str, optional): Descriptive message if no data is available.
      - error (str, optional): Error message if an exception occurs.

    Exceptions:
    - RuntimeError: Raised if the Redis client is not initialized.
    - redis.exceptions.RedisError: Raised if a Redis operation fails.
    """
    global redis_client

    # Check if Redis client is initialized
    if not redis_client:
        raise RuntimeError("Redis client not initialized")

    try:
        # Find all keys matching the facade pattern
        keys = await redis_client.keys("facade:*:latest")

        # Return a message if no keys are found
        if not keys:
            return {
                "data": None,
                "message": "No recent data in Redis"
            }

        result = {}
        # Process each key to extract facade data
        for key in keys:
            # Extract facade_id and facade_type from the key
            parts = key.split(":")
            if len(parts) >= 2:
                facade_id = parts[1]
                facade_type = parts[2] if len(parts) > 3 else "unknown"
                
                # Retrieve all fields from the Redis HASH
                data = await redis_client.hgetall(key)
                
                # Decode JSON values if necessary
                try:
                    decoded_data = {
                        k: json.loads(v) if isinstance(v, str) and v.startswith("{") else v
                        for k, v in data.items()
                    }
                except Exception:
                    decoded_data = data

                # Initialize facade_id in result if not present
                if facade_id not in result:
                    result[facade_id] = {}
                
                # Store data under the appropriate facade type
                result[facade_id][facade_type] = decoded_data

        # Return the collected facade data
        return {"data": result}

    except Exception as e:
        # Log the error for debugging purposes
        print(f"❌ Error retrieving all facades: {e}")
        # Return error details
        return {"data": None, "error": str(e)}


async def get_sensor_value(facade_id: str, sensor_name: str, facade_type: Optional[str] = None) -> Dict[str, Any]:
    """
    Retrieves the most recent value for a specific sensor from Redis.

    Parameters:
    - facade_id (str): ID of the facade to retrieve sensor data for. Required.
    - sensor_name (str): Name of the sensor to retrieve data for. Required.
    - facade_type (Optional[str]): Filter by facade type. Valid values: 'refrigerada', 'no_refrigerada'. Default: None (no filter).

    Returns:
    - Dict[str, Any]: Dictionary containing:
      - facade_id (str): ID of the facade.
      - sensor_name (str): Name of the sensor.
      - facade_type (str or null): The facade type filter applied, if any.
      - value (Any or null): The latest sensor value, or None if not found.
      - message (str, optional): Descriptive message if the sensor is not found.
      - error (str, optional): Error message if an exception occurs.

    Exceptions:
    - RuntimeError: Raised if the Redis client is not initialized.
    - redis.exceptions.RedisError: Raised if a Redis operation fails.
    """
    global redis_client

    # Check if Redis client is initialized
    if not redis_client:
        raise RuntimeError("Redis client not initialized")

    try:
        # Generate Redis key based on facade type
        if facade_type:
            key = f"facade:{facade_id}:{facade_type}:latest"
        else:
            key = f"facade:{facade_id}:latest"

        # Retrieve the sensor value from the Redis HASH
        value = await redis_client.hget(key, sensor_name)

        # Return a message if no value is found
        if not value:
            return {
                "facade_id": facade_id,
                "sensor_name": sensor_name,
                "facade_type": facade_type,
                "value": None,
                "message": "Sensor not found"
            }

        # Decode JSON value if necessary
        try:
            if isinstance(value, str) and value.startswith("{"):
                decoded_value = json.loads(value)
            else:
                decoded_value = value
        except Exception:
            decoded_value = value

        # Construct and return the response
        return {
            "facade_id": facade_id,
            "sensor_name": sensor_name,
            "facade_type": facade_type,
            "value": decoded_value
        }

    except Exception as e:
        # Log the error for debugging purposes
        print(f"❌ Error retrieving sensor {sensor_name}: {e}")
        # Return error details
        return {
            "facade_id": facade_id,
            "sensor_name": sensor_name,
            "error": str(e)
        }


async def get_facade_type_comparison(facade_id: str) -> Dict[str, Any]:
    """
    Compares real-time data between refrigerated and non-refrigerated facades for a specific facade ID.

    HU01: View an overview of both facades to compare their current status.
    HU17: Compare performance with and without refrigeration to validate hypotheses.

    Parameters:
    - facade_id (str): ID of the facade to compare. Required.

    Returns:
    - Dict[str, Any]: Dictionary containing:
      - facade_id (str): ID of the facade.
      - comparison (dict): Dictionary with two keys:
        - 'refrigerada' (dict or null): Latest data for the refrigerated facade.
        - 'no_refrigerada' (dict or null): Latest data for the non-refrigerated facade.
      - error (str, optional): Error message if an exception occurs.

    Exceptions:
    - RuntimeError: Raised if the Redis client is not initialized.
    - redis.exceptions.RedisError: Raised if a Redis operation fails.
    """
    global redis_client

    # Check if Redis client is initialized
    if not redis_client:
        raise RuntimeError("Redis client not initialized")

    try:
        # Define Redis key (all sensor data for the facade is stored in a single hash)
        key = f"facade:{facade_id}:latest"

        # Retrieve all sensor data for the facade
        all_data = await redis_client.hgetall(key)

        if not all_data:
            return {
                "facade_id": facade_id,
                "comparison": {
                    "refrigerada": None,
                    "no_refrigerada": None
                }
            }

        # Separate data by facade_type
        refrigerada_data = {}
        no_refrigerada_data = {}

        for sensor_name, value_str in all_data.items():
            try:
                # Decode JSON value
                value_obj = json.loads(value_str) if isinstance(value_str, str) and value_str.startswith("{") else {"value": value_str}
                
                # Get facade_type from the value object
                facade_type = value_obj.get("facade_type", "unknown")
                
                # Separate by facade_type
                if facade_type == "refrigerada":
                    refrigerada_data[sensor_name] = value_obj
                elif facade_type == "no_refrigerada":
                    no_refrigerada_data[sensor_name] = value_obj
                    
            except Exception as e:
                # Log decode errors but continue processing
                print(f"⚠️  Error decoding sensor {sensor_name}: {e}")
                continue

        # Construct and return the comparison response
        return {
            "facade_id": facade_id,
            "comparison": {
                "refrigerada": refrigerada_data if refrigerada_data else None,
                "no_refrigerada": no_refrigerada_data if no_refrigerada_data else None
            }
        }

    except Exception as e:
        # Log the error for debugging purposes
        print(f"❌ Error comparing facade types: {e}")
        # Return error details
        return {"facade_id": facade_id, "error": str(e)}


async def invalidate_facade_cache(facade_id: str, facade_type: Optional[str] = None) -> Dict[str, str]:
    """
    Invalidates the Redis cache for a specific facade or facade type.

    Parameters:
    - facade_id (str): ID of the facade to invalidate cache for. Required.
    - facade_type (Optional[str]): Filter by facade type. Valid values: 'refrigerada', 'no_refrigerada'. Default: None (invalidate both types).

    Returns:
    - Dict[str, str]: Dictionary containing:
      - message (str): Confirmation message indicating cache invalidation.
      - error (str, optional): Error message if an exception occurs.

    Exceptions:
    - RuntimeError: Raised if the Redis client is not initialized.
    - redis.exceptions.RedisError: Raised if a Redis operation fails.
    """
    global redis_client

    # Check if Redis client is initialized
    if not redis_client:
        raise RuntimeError("Redis client not initialized")

    try:
        if facade_type:
            # Invalidate cache for specific facade type
            key = f"facade:{facade_id}:{facade_type}:latest"
            await redis_client.delete(key)
            return {"message": f"Cache invalidated for {facade_id} ({facade_type})"}
        else:
            # Invalidate cache for all types of the facade
            keys = await redis_client.keys(f"facade:{facade_id}:*:latest")
            if keys:
                await redis_client.delete(*keys)
            return {"message": f"Cache invalidated for {facade_id} (all types)"}

    except Exception as e:
        # Log the error for debugging purposes
        print(f"❌ Error invalidating cache: {e}")
        # Return error details
        return {"error": str(e)}