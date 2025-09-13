# Facade service


from models.domain_models import PhotovoltaicSolarFacade, Sensor


class FacadeService:
    def __init__(self):
        self.facades: dict = {
            "sin_refrigeracion": PhotovoltaicSolarFacade(1, "Location1", "active"),
            "con_refrigeracion": PhotovoltaicSolarFacade(2, "Location2", "active"),
        }

    def get_facade_data(self, facade_id: str) -> dict:
        facade = self.facades.get(facade_id)
        if facade:
            return facade.get_data()
        return {}

    def add_sensor_to_facade(self, facade_id: str, sensor: Sensor):
        self.facades[facade_id].add_sensor(sensor)

    # Para múltiples sensores: registrar 20+ aquí
