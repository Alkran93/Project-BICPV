from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Configuration settings for the application, loaded from environment variables or an .env file.

    Purpose:
    - Defines configuration parameters for connecting to external services such as Redis and PostgreSQL databases.

    Attributes:
    - REDIS_URL (str): The URL for the Redis instance. Default: "redis://redis:6379/0".
      - Format: Standard Redis URL (e.g., 'redis://host:port/db').
    - DATABASE_URL (str): The URL for the PostgreSQL database. Default: "postgresql://postgres:postgres@timescaledb:5432/postgres".
      - Format: Standard PostgreSQL URL (e.g., 'postgresql://user:password@host:port/dbname').

    Exceptions:
    - ValueError: Raised if the environment variables or .env file contain invalid values that cannot be parsed by Pydantic.
    - FileNotFoundError: Raised if the specified .env file is not found when loading configurations.

    Config:
    - Specifies that environment variables can be loaded from a '.env' file.
    """
    REDIS_URL: str = "redis://redis:6379/0"
    DATABASE_URL: str = "postgresql://postgres:postgres@timescaledb:5432/postgres"

    class Config:
        """
        Configuration class for Pydantic settings.

        Attributes:
        - env_file (str): Path to the .env file for loading environment variables. Default: ".env".
        """
        env_file = ".env"

# Instantiate the Settings class to load configuration values
settings = Settings()