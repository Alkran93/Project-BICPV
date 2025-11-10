from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

from .api import (
    routes_alerts,
    routes_analytics,
    routes_charts,
    routes_chart_data,
    routes_control,
    routes_efficiency,
    routes_export,
    routes_facades,
    routes_realtime,
    routes_reports,
    routes_sensors,
    routes_temperature,
)

from .db import init_db_pool, close_db_pool, get_pool
from .services import cache_controller


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages the lifecycle of the FastAPI application, initializing and closing connections.

    Purpose:
    - Initializes Redis and TimescaleDB connection pools on startup.
    - Ensures connections are properly closed on shutdown.
    - Raises an error if connections fail to initialize.

    Parameters:
    - app (FastAPI): The FastAPI application instance.

    Yields:
    - None: Allows the application to run while connections are active.

    Exceptions:
    - RuntimeError: Raised if either Redis or TimescaleDB connection pools fail to initialize.
    - Exception: Raised for other unexpected errors during initialization or shutdown.
    """
    print("⏳ Initializing connections...")

    try:
        # Initialize Redis and TimescaleDB connection pools
        await cache_controller.init_redis()
        await init_db_pool()

        # Verify that both connection pools are initialized
        if not cache_controller.redis_client or not get_pool():
            raise RuntimeError("❌ Database or Redis connection pool not initialized properly.")

        print("🚀 Connections initialized (Redis and TimescaleDB)")
        yield

    except Exception as e:
        # Log initialization errors
        print(f"❌ Error initializing connections: {e}")
        raise

    finally:
        # Ensure connections are closed on shutdown
        await cache_controller.close_redis()
        await close_db_pool()
        print("🛑 Connections closed (Redis and TimescaleDB)")


# -------------------------------------------------------------------------
# APPLICATION CONFIGURATION
# -------------------------------------------------------------------------
app = FastAPI(
    title="Solar Facades API",
    description="API for querying, analyzing, and monitoring photovoltaic solar facades.",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------------------------------------------------------
# BASIC ENDPOINTS
# -------------------------------------------------------------------------
@app.get("/health", tags=["system"])
async def health_check():
    """
    Checks the health status of the service.

    Returns:
    - Dict[str, str]: A dictionary with the status of the service.
    """
    return {"status": "ok"}


# -------------------------------------------------------------------------
# ROUTERS
# -------------------------------------------------------------------------
app.include_router(routes_facades.router)
app.include_router(routes_sensors.router)
app.include_router(routes_analytics.router)
app.include_router(routes_realtime.router)
app.include_router(routes_alerts.router)
app.include_router(routes_export.router)
app.include_router(routes_temperature.router)
app.include_router(routes_charts.router)
app.include_router(routes_chart_data.router)
app.include_router(routes_control.router)
app.include_router(routes_efficiency.router)
app.include_router(routes_reports.router)


# -------------------------------------------------------------------------
# ROOT ENDPOINT
# -------------------------------------------------------------------------
@app.get("/", include_in_schema=False)
async def root():
    """
    Root endpoint providing a welcome message and links to API documentation.

    Returns:
    - Dict[str, str]: A dictionary with a welcome message, documentation links, and version info.
    """
    return {
        "message": "Welcome to the Solar Facades API 🌞",
        "docs": "/docs",
        "redoc": "/redoc",
        "version": "1.0.0",
    }