# Core domain models

from abc import ABC, abstractmethod


class User(ABC):
    def __init__(
        self, user_id: str, name: str, email: str, password: str, role: str, status: str
    ):
        self.id = user_id
        self.name = name
        self.email = email
        self.password = password  # Hash in prod
        self.role = role
        self.status = status
        self.last_login = None

    @abstractmethod
    def login(self, email: str, password: str) -> str:
        pass

    # Resto de métodos del diagrama...


class Researcher(User):
    def fetch_real_time_data(self) -> dict:
        # Lógica para datos realtime
        pass

    # Resto: fetch_historical_data, display_charts, etc.


class Admin(User):
    def system_parameter_configuration(self, config: dict) -> bool:
        pass

    # Resto...


class SessionManager:
    def __init__(self):
        self.settings: dict = {}
        self.active_sessions: dict = {}

    def authenticate_user(self, email: str, password: str) -> str:
        # Token generation
        pass

    # Resto...


class Sensor(ABC):
    def __init__(
        self,
        sensor_id: int,
        facade_id: int,
        sensor_type: str,
        measured_variables: list[str],
        ranges: dict,
        location: str,
        status: str,
    ):
        self.id = sensor_id
        self.facade_id = facade_id
        self.type = sensor_type
        self.measured_variables = measured_variables
        self.ranges = ranges
        self.location = location
        self.status = status
        self.reading_frequency = 1.0
        self.last_reading = None

    @abstractmethod
    def get_data(self) -> dict:
        pass

    # Resto: update_status, record_reading, check_connection


class PhotovoltaicSolarFacade:
    def __init__(self, facade_id: int, location: str, status: str):
        self.id = facade_id
        self.location = location
        self.status = status
        self.registered_sensors: list[Sensor] = []
        self.registered_actuators: list[Actuator] = []

    def get_data(self) -> dict:
        data = {}
        for sensor in self.registered_sensors:
            data[sensor.id] = sensor.get_data()
        return data

    def add_sensor(self, sensor: Sensor) -> bool:
        self.registered_sensors.append(sensor)
        return True

    # Resto...


class Actuator:
    def __init__(
        self, actuator_id: int, facade_id: str, actuator_type: str, status: str
    ):
        self.id = actuator_id
        self.facade_id = facade_id
        self.type = actuator_type
        self.status = status

    def get_status(self) -> str:
        return self.status

    # Resto...


# Resto de clases del diagrama: DataAcquisition, etc.
# Las implementamos en services para lógica.
# DataAcquisition, DataValidation, etc., se mueven a services/ como clases concretas.
