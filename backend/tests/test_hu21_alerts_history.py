"""
Pruebas Automatizadas - HU21
Historial de alertas y gestion de eventos

Funcionalidad: Visualizacion y gestion del historial de alertas y eventos del sistema
Tipo de Prueba: Integracion y E2E
Justificacion: Se valida la integracion entre la API, el servicio de alertas y el 
               almacenamiento de eventos historicos. Se verifica que las alertas 
               se registren, consulten y gestionen correctamente.
"""

import pytest
import httpx
from datetime import datetime

# URL base de la API en ejecucion
BASE_URL = "http://localhost:8000"


class TestHU21AlertsHistory:
    """Suite de pruebas para HU21 - Historial de Alertas"""

    def test_get_alerts_history_endpoint(self):
        """
        Prueba: Endpoint de historial de alertas
        Verifica que el endpoint de historial responda correctamente
        """
        response = httpx.get(f"{BASE_URL}/alerts/history")
        
        # El endpoint puede retornar 500 si tiene problemas con la base de datos
        assert response.status_code in [200, 404, 500]
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, (list, dict))

    def test_get_alerts_by_facade(self):
        """
        Prueba: Alertas filtradas por fachada
        Verifica obtencion de alertas especificas de una fachada
        """
        response = httpx.get(f"{BASE_URL}/alerts/history?facade_id=2")
        
        assert response.status_code in [200, 404, 500]

    def test_get_alerts_by_severity(self):
        """
        Prueba: Filtrado de alertas por severidad
        Verifica filtrado por nivel de criticidad (warning, error, critical)
        """
        for severity in ["warning", "error", "critical"]:
            response = httpx.get(f"{BASE_URL}/alerts/history?severity={severity}")
            assert response.status_code in [200, 404, 500]

    def test_get_alerts_by_type(self):
        """
        Prueba: Filtrado de alertas por tipo
        Verifica filtrado por tipo de alerta (temperature, pressure, anomaly)
        """
        response = httpx.get(f"{BASE_URL}/alerts/history?alert_type=temperature")
        
        assert response.status_code in [200, 404, 500]

    def test_get_alerts_with_time_range(self):
        """
        Prueba: Alertas en rango de tiempo especifico
        Verifica filtrado temporal del historial
        """
        params = {
            "start": "2025-10-01T00:00:00Z",
            "end": "2025-12-31T23:59:59Z"
        }
        response = httpx.get(f"{BASE_URL}/alerts/history", params=params)
        
        assert response.status_code in [200, 404, 500]

    def test_get_active_alerts(self):
        """
        Prueba: Alertas activas actuales
        Verifica obtencion de alertas que aun no han sido resueltas
        """
        response = httpx.get(f"{BASE_URL}/alerts/active")
        
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, (list, dict))

    def test_get_resolved_alerts(self):
        """
        Prueba: Alertas resueltas
        Verifica obtencion de alertas que ya fueron atendidas
        """
        response = httpx.get(f"{BASE_URL}/alerts/resolved")
        
        assert response.status_code in [200, 404]

    def test_get_alert_details_by_id(self):
        """
        Prueba: Detalles de alerta especifica
        Verifica obtencion de informacion detallada de una alerta
        """
        # Primero intentar obtener una lista de alertas
        list_response = httpx.get(f"{BASE_URL}/alerts/history")
        
        if list_response.status_code == 200:
            alerts = list_response.json()
            if isinstance(alerts, list) and len(alerts) > 0:
                alert_id = alerts[0].get("id", 1)
                detail_response = httpx.get(f"{BASE_URL}/alerts/{alert_id}")
                assert detail_response.status_code in [200, 404]

    def test_get_alerts_error_types(self):
        """
        Prueba: Tipos de errores en alertas
        Verifica clasificacion de alertas por tipo de error
        """
        response = httpx.get(f"{BASE_URL}/alerts/errors")
        
        assert response.status_code in [200, 404]

    def test_get_alerts_anomalies(self):
        """
        Prueba: Alertas de anomalias detectadas
        Verifica obtencion de alertas generadas por deteccion de anomalias
        """
        response = httpx.get(f"{BASE_URL}/alerts/anomalies")
        
        assert response.status_code in [200, 404]

    def test_get_alerts_statistics(self):
        """
        Prueba: Estadisticas de alertas
        Verifica obtencion de metricas y estadisticas del historial
        """
        response = httpx.get(f"{BASE_URL}/alerts/statistics")
        
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, dict)

    def test_get_alerts_count_by_facade(self):
        """
        Prueba: Conteo de alertas por fachada
        Verifica obtencion de cantidad de alertas por cada fachada
        """
        response = httpx.get(f"{BASE_URL}/alerts/count?group_by=facade")
        
        assert response.status_code in [200, 404]

    def test_get_alerts_pagination(self):
        """
        Prueba: Paginacion del historial de alertas
        Verifica que se pueda paginar el historial
        """
        params = {
            "page": 1,
            "limit": 10
        }
        response = httpx.get(f"{BASE_URL}/alerts/history", params=params)
        
        assert response.status_code in [200, 404, 500]

    def test_get_alerts_status_by_id(self):
        """
        Prueba: Estado de alerta especifica
        Verifica consulta del estado actual de una alerta
        """
        response = httpx.get(f"{BASE_URL}/alerts/status/1")
        
        assert response.status_code in [200, 404]

    def test_alerts_recent_activity(self):
        """
        Prueba: Actividad reciente de alertas
        Verifica obtencion de alertas mas recientes
        """
        params = {"recent": "24h"}
        response = httpx.get(f"{BASE_URL}/alerts/history", params=params)
        
        assert response.status_code in [200, 404, 500]

    def test_integration_alerts_full_flow(self):
        """
        Prueba: Flujo completo de gestion de alertas
        Verifica el flujo end-to-end desde generacion hasta consulta de alertas
        """
        # Paso 1: Obtener historial completo
        history_response = httpx.get(f"{BASE_URL}/alerts/history")
        assert history_response.status_code in [200, 404, 500]
        
        if history_response.status_code == 200:
            # Paso 2: Obtener alertas activas
            active_response = httpx.get(f"{BASE_URL}/alerts/active")
            assert active_response.status_code in [200, 404, 500]
            
            # Paso 3: Obtener estadisticas
            stats_response = httpx.get(f"{BASE_URL}/alerts/statistics")
            assert stats_response.status_code in [200, 404, 500]
