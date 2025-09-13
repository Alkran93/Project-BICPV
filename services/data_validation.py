# Data validation service

from datetime import datetime


class DataValidation:
    def __init__(self):
        self.last_validation: datetime = datetime.now()
        self.error_log: list = []

    def verify_integrity(self, data: dict) -> bool:
        # Chequear si data tiene todos los campos
        required = ["ts", "value"]
        return all(key in data for key in required)

    def validate_ranges(self, data: dict) -> bool:
        # Ej: temperatura entre 0-100
        return 0 <= data["value"] <= 100

    def detect_sensor_failures(self, data: dict) -> list:
        errors = []
        if not self.verify_integrity(data):
            errors.append("Integrity failure")
        return errors

    def send_to_processing(self, data: dict) -> bool:
        # Si válido, enviar a next in pipeline
        return True

    # Resto...
