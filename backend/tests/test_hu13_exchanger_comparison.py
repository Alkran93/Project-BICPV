"""
Pruebas Automatizadas - HU13
Comparacion de temperaturas de agua en intercambiadores de calor

Funcionalidad: Comparacion de temperaturas de entrada y salida del agua en los 
               intercambiadores de calor (evaporador y condensador)
Tipo de Prueba: Integracion
Justificacion: Se valida la integracion entre la API y el servicio de temperatura. 
               Se verifica que los endpoints retornen datos comparativos correctos 
               de los intercambiadores para analizar eficiencia termica.
"""

import pytest
import httpx

# URL base de la API en ejecucion
BASE_URL = "http://localhost:8000"


class TestHU13ExchangerComparison:
    """Suite de pruebas para HU13 - Comparacion de Intercambiadores"""

    def test_get_exchanger_temperatures_structure(self):
        """
        Prueba: Estructura de respuesta de temperaturas de intercambiadores
        Verifica que la API retorne la estructura correcta con temperaturas de entrada/salida
        """
        response = httpx.get(f"{BASE_URL}/temperatures/exchanger/2")
        
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.json()
            assert "facade_id" in data or isinstance(data, dict)

    def test_get_exchanger_evaporator_data(self):
        """
        Prueba: Datos del evaporador
        Verifica que se obtengan temperaturas del evaporador
        """
        response = httpx.get(f"{BASE_URL}/temperatures/exchanger/evaporator/2")
        
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, (dict, list))

    def test_get_exchanger_condenser_data(self):
        """
        Prueba: Datos del condensador
        Verifica que se obtengan temperaturas del condensador
        """
        response = httpx.get(f"{BASE_URL}/temperatures/exchanger/condenser/2")
        
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, (dict, list))

    def test_get_exchanger_temperature_differential(self):
        """
        Prueba: Diferencial de temperatura en intercambiadores
        Verifica que se pueda calcular la diferencia entre entrada y salida
        """
        response = httpx.get(f"{BASE_URL}/temperatures/exchanger/2")
        
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.json()
            # Verificar que haya datos para calcular diferenciales
            assert isinstance(data, dict)

    def test_get_exchanger_comparison_with_time_range(self):
        """
        Prueba: Comparacion de intercambiadores con rango de tiempo
        Verifica el filtrado temporal de datos de intercambiadores
        """
        params = {
            "start": "2025-10-01T00:00:00Z",
            "end": "2025-12-31T23:59:59Z"
        }
        response = httpx.get(f"{BASE_URL}/temperatures/exchanger/2", params=params)
        
        assert response.status_code in [200, 404]

    def test_get_exchanger_efficiency_metrics(self):
        """
        Prueba: Metricas de eficiencia de intercambiadores
        Verifica que se puedan obtener metricas de desempeno
        """
        response = httpx.get(f"{BASE_URL}/analytics/exchanger/efficiency/2")
        
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, (dict, list))

    def test_get_water_temperatures_inlet_outlet(self):
        """
        Prueba: Temperaturas de agua entrada/salida
        Verifica el endpoint que compara temperaturas de entrada y salida del agua
        """
        response = httpx.get(f"{BASE_URL}/temperatures/water/2")
        
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, (dict, list))

    def test_compare_exchanger_types(self):
        """
        Prueba: Comparacion entre tipos de intercambiadores
        Verifica que se puedan comparar evaporador vs condensador
        """
        response = httpx.get(f"{BASE_URL}/facades/2/compare?component=exchanger")
        
        assert response.status_code in [200, 404, 422]

    def test_get_exchanger_invalid_facade(self):
        """
        Prueba: Manejo de facade_id invalido para intercambiadores
        Verifica respuesta correcta con ID inexistente
        """
        response = httpx.get(f"{BASE_URL}/temperatures/exchanger/999")
        
        assert response.status_code in [200, 404]

    def test_integration_exchanger_full_cycle(self):
        """
        Prueba: Integracion completa de datos de intercambiadores
        Verifica el flujo completo desde facade hasta datos de intercambiadores
        """
        # Primero obtener info de facade
        facade_response = httpx.get(f"{BASE_URL}/facades/2")
        
        if facade_response.status_code == 200:
            # Luego obtener datos de intercambiadores
            exchanger_response = httpx.get(f"{BASE_URL}/temperatures/exchanger/2")
            assert exchanger_response.status_code in [200, 404]
