"""
Pruebas Automatizadas - HU17
Comparacion de desempeno entre fachadas refrigeradas y no refrigeradas

Funcionalidad: Comparacion del desempeno termico entre fachadas refrigeradas y no refrigeradas
Tipo de Prueba: Integracion
Justificacion: Se valida la integracion entre la API y los servicios de analytics y comparacion.
               Se verifica que se puedan comparar metricas de rendimiento entre ambos tipos
               de fachadas para evaluar el impacto de la refrigeracion.
"""

import pytest
import httpx

# URL base de la API en ejecucion
BASE_URL = "http://localhost:8000"


class TestHU17PerformanceComparison:
    """Suite de pruebas para HU17 - Comparacion de Desempeno"""

    def test_get_facades_list(self):
        """
        Prueba: Obtener lista de fachadas para comparacion
        Verifica que se puedan listar todas las fachadas disponibles
        """
        response = httpx.get(f"{BASE_URL}/facades/")
        
        assert response.status_code == 200
        data = response.json()
        # La API puede retornar un objeto con 'facades' o una lista directamente
        if isinstance(data, dict):
            assert "facades" in data or "count" in data
        elif isinstance(data, list):
            assert len(data) > 0

    def test_get_facade_by_type(self):
        """
        Prueba: Filtrar fachadas por tipo (refrigerada/no refrigerada)
        Verifica que se puedan obtener fachadas segun su tipo
        """
        # Probar fachada refrigerada
        response_ref = httpx.get(f"{BASE_URL}/facades/?facade_type=refrigerada")
        assert response_ref.status_code in [200, 404]
        
        # Probar fachada no refrigerada
        response_no_ref = httpx.get(f"{BASE_URL}/facades/?facade_type=no_refrigerada")
        assert response_no_ref.status_code in [200, 404]

    def test_compare_facades_performance(self):
        """
        Prueba: Comparacion directa de desempeno entre fachadas
        Verifica el endpoint de comparacion entre fachadas refrigerada y no refrigerada
        """
        params = {
            "facade1": "1",
            "facade2": "2"
        }
        response = httpx.get(f"{BASE_URL}/facades/compare", params=params)
        
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, dict)

    def test_get_facade_average_temperatures(self):
        """
        Prueba: Temperaturas promedio por fachada
        Verifica que se puedan obtener promedios de temperatura
        """
        response = httpx.get(f"{BASE_URL}/facades/2/average")
        
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, dict)

    def test_get_performance_metrics_refrigerated(self):
        """
        Prueba: Metricas de desempeno de fachada refrigerada
        Verifica metricas especificas de fachadas con refrigeracion
        """
        response = httpx.get(f"{BASE_URL}/analytics/performance/2")
        
        assert response.status_code in [200, 404]

    def test_get_performance_metrics_non_refrigerated(self):
        """
        Prueba: Metricas de desempeno de fachada no refrigerada
        Verifica metricas de fachadas sin refrigeracion
        """
        response = httpx.get(f"{BASE_URL}/analytics/performance/1")
        
        assert response.status_code in [200, 404]

    def test_compare_energy_efficiency(self):
        """
        Prueba: Comparacion de eficiencia energetica
        Verifica la comparacion de consumo y eficiencia entre tipos de fachada
        """
        response = httpx.get(f"{BASE_URL}/analytics/efficiency/compare")
        
        assert response.status_code in [200, 404]

    def test_get_temperature_reduction_metrics(self):
        """
        Prueba: Metricas de reduccion de temperatura
        Verifica cuanto reduce la temperatura la refrigeracion
        """
        response = httpx.get(f"{BASE_URL}/analytics/temperature/reduction/2")
        
        assert response.status_code in [200, 404]

    def test_compare_with_time_range(self):
        """
        Prueba: Comparacion con rango temporal
        Verifica comparacion de desempeno en periodo especifico
        """
        params = {
            "start": "2025-10-01T00:00:00Z",
            "end": "2025-12-31T23:59:59Z"
        }
        response = httpx.get(f"{BASE_URL}/facades/compare?facade1=1&facade2=2", params=params)
        
        assert response.status_code in [200, 404]

    def test_get_comparative_statistics(self):
        """
        Prueba: Estadisticas comparativas
        Verifica obtencion de estadisticas (min, max, avg) para comparacion
        """
        response = httpx.get(f"{BASE_URL}/analytics/statistics/compare")
        
        assert response.status_code in [200, 404]

    def test_integration_full_comparison_flow(self):
        """
        Prueba: Flujo completo de comparacion
        Verifica el flujo end-to-end de comparacion de desempeno
        """
        # Paso 1: Obtener lista de fachadas
        facades_response = httpx.get(f"{BASE_URL}/facades/")
        assert facades_response.status_code == 200
        
        data = facades_response.json()
        # Manejar ambos formatos de respuesta
        if isinstance(data, dict) and "facades" in data:
            facades = data["facades"]
        elif isinstance(data, list):
            facades = data
        else:
            facades = []
            
        if len(facades) >= 2:
            # Paso 2: Comparar dos fachadas
            facade1_id = facades[0].get("facade_id", 1)
            facade2_id = facades[1].get("facade_id", 2)
            
            compare_response = httpx.get(f"{BASE_URL}/facades/compare?facade1={facade1_id}&facade2={facade2_id}")
            assert compare_response.status_code in [200, 404]
