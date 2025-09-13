# Entry point of the FastAPI application

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.api import router as api_router
from core.config import settings


# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestión del ciclo de vida de la aplicación"""
    logger.info("🚀 Iniciando SolarGrid Monitor API...")

    # Configurar dependencias en startup si es necesario
    # await setup_dependencies()

    yield

    logger.info("🛑 Cerrando SolarGrid Monitor API...")


# Crear la aplicación FastAPI
app = FastAPI(
    title="IoT Fachada Solar API",
    description=(
        "API profesional para monitoreo de fachadas solares con datos IoT "
        "en tiempo real"
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app = FastAPI(
    title="IoT Fachada Solar API",
    description=(
        "API profesional para monitoreo de fachadas solares con datos IoT "
        "en tiempo real"
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cambiar en prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Usar solo el router completo y funcional


app.include_router(api_router)


@app.get("/")
async def root():
    """Endpoint raíz"""
    return {
        "message": "IoT Fachada Solar API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "api": "/api",
        "endpoints": {
            "overview": "/api/overview/",
            "facade_detail": "/api/overview/{facade_id}",
            "sensors_list": "/api/sensors/list/{facade_id}",
            "sensors_details": "/api/sensors/details/{facade_id}",
            "sensor_data": "/api/sensors/{sensor_id}/{facade_id}",
            "environment": "/api/environment/variables/{facade_id}",
            "charts": "/api/charts/available/{facade_id}",
            "realtime": "/api/dashboard/realtime/{facade_id}",
            "health": "/api/health",
        },
    }
