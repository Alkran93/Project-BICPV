# Pydantic models for request/response validation

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class IngestPayload(BaseModel):
    ts: datetime
    sensor_id: str = Field(min_length=1)
    value: float
    unit: Optional[str] = "°C"
    tags: Optional[dict] = {}


class AggregatedPoint(BaseModel):
    time_bucket: datetime
    facade_id: str  # Agregado para fachadas
    sensor_id: str
    avg_value: float
    min_value: float
    max_value: float
    count: int


class DeviceStats(BaseModel):
    facade_id: str
    sensor_id: str
    total_readings: int
    avg_value: float
    # ... (resto de main.py)


class ChartData(BaseModel):
    labels: list[str]
    datasets: list[dict[str, Any]]
    metadata: dict[str, Any]


class AnalyticsResult(BaseModel):
    correlation_matrix: dict[str, dict[str, float]]
    trends: dict[str, dict[str, float]]
    anomalies: list[dict[str, Any]]
    predictions: dict[str, list[float]]
    quality_metrics: dict[str, float]


# Agregar para HU: FacadeOverview, SensorStatus, etc.
class FacadeOverview(BaseModel):
    facade_id: str
    avg_temperature: Optional[float] = None
    avg_irradiance: Optional[float] = None
    avg_power: Optional[float] = None
    sensors: list[str] = []


class SensorStatus(BaseModel):
    sensor_id: str
    status: str  # "active"/"inactive"
    last_reading: datetime
