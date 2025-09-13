# Data processing service

from datetime import datetime

import numpy as np
from fastapi import FastAPI

from core.utils import log_error


class DataProcessor:
    def __init__(self, system_parameters: dict):
        self.system_parameters = system_parameters
        self.last_processing: datetime = datetime.now()
        self.error_log: list = []

    def calculate_metrics(self, data: dict) -> dict:
        # Ej: avg, min, max
        return {"avg": np.mean(list(data.values()))}  # Simplificado

    # Resto del diagrama...


async def db_writer_task(app: FastAPI):
    from repositories.timescale import TimeScaleDBStorage

    storage = TimeScaleDBStorage(app.state.pg_pool)
    while True:
        # Lógica existente, pero integra validation/processing
        item = await app.state.ingest_queue.get()
        # Validate
        # validation = DataValidation()  # TODO: Implementar clase DataValidation
        validation = None
        if validation.verify_integrity(item) and validation.validate_ranges(item):
            # Process
            processor = DataProcessor({})
            processor.calculate_metrics({"value": item[3]})
            # Store
            await storage.store([item])
        else:
            log_error("Validation failed")
        # Batch logic...
