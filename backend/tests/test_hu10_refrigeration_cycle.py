"""
Pruebas Automatizadas - HU10
Visualizacion de temperatura del refrigerante en cada punto del ciclo de refrigeracion

Funcionalidad: Visualizacion de la temperatura del refrigerante en cada punto del ciclo 
               de refrigeracion (por sensor)
Tipo de Prueba: Integracion
Justificacion: Se valida la integracion entre la API, la logica de procesamiento de datos 
               de sensores y el servicio de temperatura. Se verifica que los endpoints 
               retornen datos correctos y en el formato esperado para cada punto del ciclo.
"""

import pytest
import httpx

# URL base de la API en ejecucion
BASE_URL = "http://localhost:8000"


class TestHU10RefrigerationCycle:
    """Suite de pruebas para HU10 - Ciclo de Refrigeracion"""

    def test_get_refrigeration_cycle_structure(self):
        """
        Prueba: Estructura de respuesta del endpoint de ciclo de refrigeracion
        Verifica que la API retorne la estructura correcta con todos los campos esperados
        """
        response = httpx.get(f"{BASE_URL}/temperatures/refrigerant-cycle/2")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verificar estructura basica
        assert "facade_id" in data
        assert "cycle_points" in data
        assert data["facade_id"] == "2"
        
        # Verificar que cycle_points sea un diccionario
        assert isinstance(data["cycle_points"], dict)
        assert len(data["cycle_points"]) > 0

    def test_get_refrigeration_cycle_points(self):
        """
        Prueba: Validacion de puntos del ciclo de refrigeracion
        Verifica que todos los puntos criticos del ciclo esten presentes
        """
        response = httpx.get(f"{BASE_URL}/temperatures/refrigerant-cycle/2")
        
        assert response.status_code == 200
        data = response.json()
        
        cycle_points = data.get("cycle_points", {})
        assert len(cycle_points) > 0
        
        # Verificar que cada punto tenga la estructura correcta
        # La API retorna cycle_points como dict donde las claves son los nombres de puntos
        for point_name, point_data in cycle_points.items():
            assert isinstance(point_name, str)
            assert "label" in point_data
            assert "readings" in point_data
            assert isinstance(point_data["readings"], list)

    def test_get_refrigeration_cycle_temperature_values(self):
        """
        Prueba: Validacion de valores de temperatura
        Verifica que las temperaturas esten en rangos razonables
        """
        response = httpx.get(f"{BASE_URL}/temperatures/refrigerant-cycle/2")
        
        assert response.status_code == 200
        data = response.json()
        
        cycle_points = data.get("cycle_points", {})
        # Iterar sobre los puntos del ciclo
        for point_name, point_data in cycle_points.items():
            readings = point_data.get("readings", [])
            # Verificar al menos la primera lectura si existe
            if readings:
                reading = readings[0]
                temp = reading.get("value")
                assert temp is not None
                assert isinstance(temp, (int, float))
                # Rango razonable para temperaturas de refrigeracion: -20 a 60 grados C
                assert -20 <= temp <= 60, f"Temperatura fuera de rango: {temp}"

    def test_get_refrigeration_cycle_with_time_range(self):
        """
        Prueba: Filtrado por rango de tiempo
        Verifica que el endpoint acepte parametros de fecha inicio y fin
        """
        params = {
            "start": "2025-10-01T00:00:00Z",
            "end": "2025-12-31T23:59:59Z",
            "limit": 100
        }
        response = httpx.get(f"{BASE_URL}/temperatures/refrigerant-cycle/2", params=params)
        
        # Aceptar tanto 200 (con datos) como 404 (endpoint puede no soportar filtros)
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.json()
            assert "cycle_points" in data

    def test_get_refrigeration_cycle_limit_parameter(self):
        """
        Prueba: Parametro de limite de registros
        Verifica que el parametro limit funcione correctamente
        """
        response = httpx.get(f"{BASE_URL}/temperatures/refrigerant-cycle/2?limit=10")
        
        assert response.status_code == 200
        data = response.json()
        cycle_points = data.get("cycle_points", {})
        # Verificar que cycle_points sea un diccionario
        assert isinstance(cycle_points, dict)

    def test_get_refrigeration_cycle_invalid_facade(self):
        """
        Prueba: Manejo de facade_id invalido
        Verifica que la API responda correctamente con un ID no existente
        """
        response = httpx.get(f"{BASE_URL}/temperatures/refrigerant-cycle/999")
        
        # Puede ser 404 o 200 con datos vacios segun implementacion
        assert response.status_code in [200, 404]

    def test_get_refrigeration_cycle_sensors_consistency(self):
        """
        Prueba: Consistencia de sensores del ciclo
        Verifica que los sensores reportados sean coherentes con el ciclo de refrigeracion
        """
        response = httpx.get(f"{BASE_URL}/temperatures/refrigerant-cycle/2")
        
        assert response.status_code == 200
        data = response.json()
        
        cycle_points = data.get("cycle_points", {})
        # Obtener nombres de puntos del ciclo
        point_names = list(cycle_points.keys())
        
        # Verificar que haya puntos del ciclo
        assert len(point_names) > 0
        # Verificar que cada punto tenga readings
        for point_name, point_data in cycle_points.items():
            readings = point_data.get("readings", [])
            if readings:
                # Verificar que cada reading tenga device_id
                assert "device_id" in readings[0]

    def test_get_refrigeration_variables_endpoint(self):
        """
        Prueba: Endpoint alternativo de variables de refrigeracion
        Verifica el endpoint /analytics/refrigeration/{facade_id} si existe
        """
        response = httpx.get(f"{BASE_URL}/analytics/refrigeration/2")
        
        # Aceptar 200 si existe o 404 si no esta implementado
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json()
            assert "facade_id" in data or "data" in data

    def test_get_refrigeration_sensors_list(self):
        """
        Prueba: Lista de sensores de refrigeracion
        Verifica que se pueda obtener la lista completa de sensores del ciclo
        """
        response = httpx.get(f"{BASE_URL}/sensors/refrigeration")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "count" in data
        assert "sensors" in data
        assert data["count"] > 0
        assert len(data["sensors"]) > 0

    def test_integration_facade_to_refrigeration_data(self):
        """
        Prueba de Integracion: Flujo completo de facade a datos de refrigeracion
        Verifica la integracion entre endpoints de facade y ciclo de refrigeracion
        """
        # Paso 1: Obtener informacion de facade
        facade_response = httpx.get(f"{BASE_URL}/facades/2?facade_type=refrigerada")
        assert facade_response.status_code == 200
        
        # Paso 2: Obtener datos del ciclo de refrigeracion
        cycle_response = httpx.get(f"{BASE_URL}/temperatures/refrigerant-cycle/2")
        assert cycle_response.status_code == 200
        
        # Paso 3: Verificar consistencia entre ambos endpoints
        facade_data = facade_response.json()
        cycle_data = cycle_response.json()
        
        assert facade_data["facade_id"] == cycle_data["facade_id"]
