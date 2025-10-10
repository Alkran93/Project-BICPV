import asyncpg
import asyncio
from .core.config import settings

# Private connection pool variable
_pg_pool = None


async def init_db_pool(retries: int = 5, delay: int = 3) -> None:
    """
    Initializes the PostgreSQL (TimescaleDB) connection pool with retry logic.

    Purpose:
    - Establishes a connection pool to the TimescaleDB database using the configured DATABASE_URL.
    - Implements retry logic to handle transient connection issues.

    Parameters:
    - retries (int): Number of connection attempts before giving up. Default: 5.
    - delay (int): Base delay in seconds between retries, multiplied by attempt number. Default: 3.

    Returns:
    - None

    Exceptions:
    - asyncpg.exceptions.PostgresError: Raised if the connection to the database fails after all retries.
    - Exception: Raised for other unexpected errors during connection attempts.
    """
    global _pg_pool

    for attempt in range(1, retries + 1):
        try:
            # Log connection attempt
            print(f"🔌 Attempting to connect to TimescaleDB (attempt {attempt}/{retries}) -> {settings.DATABASE_URL}")

            # Create connection pool with specified parameters
            _pg_pool = await asyncpg.create_pool(
                dsn=settings.DATABASE_URL,
                min_size=1,
                max_size=10,
            )

            # Test the connection with a simple query
            async with _pg_pool.acquire() as conn:
                await conn.execute("SELECT 1;")

            # Log successful connection
            print("✅ TimescaleDB connection pool created successfully.")
            return
        except Exception as e:
            # Log the error for debugging purposes
            print(f"⚠️ Error on attempt {attempt}: {e}")
            if attempt == retries:
                # Log failure after all retries
                print("❌ Failed to connect to TimescaleDB after multiple attempts.")
                raise
            # Wait with increasing delay before retrying
            await asyncio.sleep(delay * attempt)


def get_pool() -> asyncpg.Pool | None:
    """
    Returns the current database connection pool.

    Purpose:
    - Provides access to the initialized connection pool for database operations.

    Returns:
    - asyncpg.Pool | None: The current connection pool, or None if not initialized.
    """
    return _pg_pool


async def close_db_pool() -> None:
    """
    Closes the database connection pool.

    Purpose:
    - Safely terminates all connections in the pool and resets the pool to None.

    Returns:
    - None

    Exceptions:
    - asyncpg.exceptions.PostgresError: Raised if there is an issue closing the connection pool.
    """
    global _pg_pool
    if _pg_pool:
        # Close the connection pool
        await _pg_pool.close()
        # Log closure
        print("🧹 Database connection pool closed.")
        # Reset the pool to None
        _pg_pool = None