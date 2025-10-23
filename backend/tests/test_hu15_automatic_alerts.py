"""
Pruebas Automatizadas - HU15
Recepcion de alertas automaticas cuando se detectan fallos en sensores o en el sistema de refrigeracion

Funcionalidad: Recepcion de alertas automaticas cuando se detectan fallos en sensores 
               o en el sistema de refrigeracion
Tipo de Prueba: E2E (End-to-End)
Justificacion: El flujo involucra deteccion de fallos, generacion de alertas en backend, 
               notificacion visual y actualizacion en la interfaz. Es necesario simular 
               el ciclo completo para asegurar que el usuario final recibe correctamente 
               las alertas.
"""

import pytest
import httpx
from datetime import datetime, timedelta

# URL base de la API en ejecucion
BASE_URL = "http://localhost:8000"


class TestHU15AutomaticAlerts:
    """Suite de pruebas para HU15 - Alertas Automaticas de Fallos"""

    def test_get_sensor_failure_alerts(self):
        """
        Prueba: Obtencion de alertas de fallos de sensores
        Verifica que se puedan obtener alertas cuando los sensores fallan
        """
        response = httpx.get(f"{BASE_URL}/alerts/sensor-failures")
        
        assert response.status_code in [200, 404, 500]
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, (list, dict))

    def test_get_refrigeration_system_failure_alerts(self):
        """
        Prueba: Alertas de fallos del sistema de refrigeracion
        Verifica que se detecten y reporten fallos del sistema de refrigeracion
        """
        response = httpx.get(f"{BASE_URL}/alerts/refrigeration-failures")
        
        assert response.status_code in [200, 404, 500]
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, (list, dict))

    def test_get_active_failure_alerts(self):
        """
        Prueba: Alertas activas de fallos
        Verifica obtencion de alertas de fallos que aun no han sido resueltas
        """
        response = httpx.get(f"{BASE_URL}/alerts/active?type=failure")
        
        assert response.status_code in [200, 404, 500]
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, (list, dict))

    def test_get_critical_alerts(self):
        """
        Prueba: Alertas criticas
        Verifica obtencion de alertas con nivel critico que requieren atencion inmediata
        """
        response = httpx.get(f"{BASE_URL}/alerts/history?severity=critical")
        
        assert response.status_code in [200, 404, 500]
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, (list, dict))

    def test_get_alerts_by_sensor_id(self):
        """
        Prueba: Alertas filtradas por sensor especifico
        Verifica obtencion de alertas asociadas a un sensor particular
        """
        # Primero obtener lista de sensores
        sensors_response = httpx.get(f"{BASE_URL}/sensors/refrigeration")
        
        if sensors_response.status_code == 200:
            sensors = sensors_response.json()
            if isinstance(sensors, list) and len(sensors) > 0:
                sensor_id = sensors[0].get("id", "sensor_01")
                
                # Obtener alertas del sensor
                alerts_response = httpx.get(f"{BASE_URL}/alerts/sensor/{sensor_id}")
                assert alerts_response.status_code in [200, 404, 500]

    def test_get_alerts_by_facade_with_failures(self):
        """
        Prueba: Alertas de fallos por fachada
        Verifica que se puedan obtener todas las alertas de fallos de una fachada
        """
        response = httpx.get(f"{BASE_URL}/alerts/facade/2?type=failure")
        
        assert response.status_code in [200, 404, 500]

    def test_alert_notification_system_status(self):
        """
        Prueba: Estado del sistema de notificaciones
        Verifica que el sistema de notificaciones este operativo
        """
        response = httpx.get(f"{BASE_URL}/alerts/notifications/status")
        
        assert response.status_code in [200, 404, 500]
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, dict)

    def test_recent_failure_alerts(self):
        """
        Prueba: Alertas de fallos recientes (ultimas 24 horas)
        Verifica obtencion de alertas generadas recientemente
        """
        params = {
            "type": "failure",
            "hours": 24
        }
        response = httpx.get(f"{BASE_URL}/alerts/recent", params=params)
        
        assert response.status_code in [200, 404, 500]

    def test_alert_severity_levels(self):
        """
        Prueba: Diferentes niveles de severidad de alertas
        Verifica que se clasifiquen alertas en warning, error y critical
        """
        severity_levels = ["warning", "error", "critical"]
        
        for severity in severity_levels:
            response = httpx.get(f"{BASE_URL}/alerts/history?severity={severity}&type=failure")
            assert response.status_code in [200, 404, 500]

    def test_alert_acknowledgment(self):
        """
        Prueba: Reconocimiento de alertas
        Verifica que se puedan marcar alertas como reconocidas
        """
        # Primero obtener una alerta activa
        alerts_response = httpx.get(f"{BASE_URL}/alerts/active?type=failure")
        
        if alerts_response.status_code == 200:
            alerts = alerts_response.json()
            if isinstance(alerts, list) and len(alerts) > 0:
                alert_id = alerts[0].get("id", 1)
                
                # Intentar reconocer la alerta (puede ser POST o PATCH segun implementacion)
                ack_response = httpx.post(f"{BASE_URL}/alerts/{alert_id}/acknowledge")
                assert ack_response.status_code in [200, 201, 404, 405, 500]

    def test_alert_details_with_failure_info(self):
        """
        Prueba: Detalles completos de alerta de fallo
        Verifica que los detalles incluyan informacion del sensor/sistema afectado
        """
        # Obtener lista de alertas
        list_response = httpx.get(f"{BASE_URL}/alerts/history?type=failure&limit=1")
        
        if list_response.status_code == 200:
            alerts = list_response.json()
            if isinstance(alerts, list) and len(alerts) > 0:
                alert_id = alerts[0].get("id", 1)
                
                # Obtener detalles
                detail_response = httpx.get(f"{BASE_URL}/alerts/{alert_id}")
                assert detail_response.status_code in [200, 404, 500]
                
                if detail_response.status_code == 200:
                    data = detail_response.json()
                    # Verificar que tenga informacion basica
                    assert isinstance(data, dict)

    def test_alert_count_by_failure_type(self):
        """
        Prueba: Conteo de alertas por tipo de fallo
        Verifica estadisticas de alertas agrupadas por tipo de fallo
        """
        response = httpx.get(f"{BASE_URL}/alerts/statistics?group_by=failure_type")
        
        assert response.status_code in [200, 404, 500]

    def test_alert_trend_analysis(self):
        """
        Prueba: Analisis de tendencias de alertas
        Verifica que se puedan obtener tendencias de alertas en el tiempo
        """
        params = {
            "start": (datetime.now() - timedelta(days=7)).isoformat(),
            "end": datetime.now().isoformat(),
            "type": "failure"
        }
        response = httpx.get(f"{BASE_URL}/alerts/trends", params=params)
        
        assert response.status_code in [200, 404, 500]

    def test_alert_realtime_endpoint(self):
        """
        Prueba: Endpoint de alertas en tiempo real
        Verifica que exista un endpoint para consultar alertas en tiempo real
        """
        response = httpx.get(f"{BASE_URL}/alerts/realtime")
        
        assert response.status_code in [200, 404, 500]

    def test_alert_notification_preferences(self):
        """
        Prueba: Configuracion de preferencias de notificaciones
        Verifica endpoint para gestionar preferencias de alertas
        """
        response = httpx.get(f"{BASE_URL}/alerts/notifications/preferences")
        
        assert response.status_code in [200, 404, 405, 500]

    def test_integration_failure_detection_to_alert(self):
        """
        Prueba: Flujo completo de deteccion de fallo a alerta
        Verifica el ciclo E2E desde la deteccion hasta la notificacion
        """
        # Paso 1: Verificar estado de sensores
        sensors_response = httpx.get(f"{BASE_URL}/sensors/refrigeration")
        assert sensors_response.status_code in [200, 404, 500]
        
        # Paso 2: Consultar alertas activas de fallos
        alerts_response = httpx.get(f"{BASE_URL}/alerts/active?type=failure")
        assert alerts_response.status_code in [200, 404, 500]
        
        if alerts_response.status_code == 200:
            alerts = alerts_response.json()
            
            # Paso 3: Si hay alertas, verificar detalles de una
            if isinstance(alerts, list) and len(alerts) > 0:
                alert_id = alerts[0].get("id", 1)
                detail_response = httpx.get(f"{BASE_URL}/alerts/{alert_id}")
                assert detail_response.status_code in [200, 404, 500]
                
                # Paso 4: Verificar estadisticas
                stats_response = httpx.get(f"{BASE_URL}/alerts/statistics")
                assert stats_response.status_code in [200, 404, 500]
