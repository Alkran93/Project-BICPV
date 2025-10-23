# Pruebas Automatizadas - Backend API

Sistema de pruebas automatizadas para validar las funcionalidades de la API REST del sistema de monitoreo de fachadas fotovoltaicas.

## Requisitos

- Python 3.8+
- pytest 8.0+
- pytest-asyncio 0.23+
- httpx 0.27+

## Instalacion

```bash
# Activar entorno virtual
source ../venv/bin/activate

# Instalar dependencias de pruebas
pip install -r tests/requirements-test.txt
```

## Ejecucion Rapida

### Todas las pruebas
```bash
./run_tests.sh
```

### Por Historia de Usuario
```bash
./run_tests.sh hu10   # Ciclo de Refrigeracion
./run_tests.sh hu13   # Comparacion Intercambiador
./run_tests.sh hu17   # Comparacion de Rendimiento
./run_tests.sh hu18   # Exportacion CSV
./run_tests.sh hu21   # Historial de Alertas
```

### Con cobertura de codigo
```bash
./run_tests.sh coverage
```

## Ejecucion Manual

```bash
# Todas las pruebas
pytest tests/ -v

# Prueba especifica
pytest tests/test_hu10_refrigeration_cycle.py -v

# Con output detallado
pytest tests/ -v --tb=long

# Pruebas especificas por clase
pytest tests/test_hu10_refrigeration_cycle.py::TestHU10RefrigerationCycle -v
```

## Estructura de Pruebas

```
tests/
├── __init__.py
├── test_hu10_refrigeration_cycle.py    (10 pruebas)
├── test_hu13_exchanger_comparison.py   (10 pruebas)
├── test_hu17_performance_comparison.py (11 pruebas)
├── test_hu18_csv_export.py             (14 pruebas)
├── test_hu21_alerts_history.py         (16 pruebas)
└── requirements-test.txt

Total: 61 pruebas automatizadas
```

## Historias de Usuario Cubiertas

### HU10: Ciclo de Refrigeracion
**Tipo:** Integracion  
**Pruebas:** 10  
**Endpoints:**
- `/temperatures/refrigerant-cycle/{facade_id}`
- `/analytics/refrigeration/{facade_id}`
- `/sensors/refrigeration`

### HU13: Comparacion Intercambiador
**Tipo:** Escenarios / Integracion  
**Pruebas:** 10  
**Endpoints:**
- `/temperatures/exchanger/{facade_id}`
- `/facades/{facade_id}/compare`
- `/analytics/compare/{facade_id}`

### HU17: Comparacion de Rendimiento
**Tipo:** Integracion / Escenarios  
**Pruebas:** 11  
**Endpoints:**
- `/facades/`
- `/facades/{facade_id}/types`
- `/facades/{facade_id}/compare`
- `/facades/{facade_id}/average`

### HU18: Exportacion CSV
**Tipo:** Unitarias / Integracion  
**Pruebas:** 14  
**Endpoints:**
- `/exports/csv/facade/{facade_id}`
- `/exports/csv/compare/{facade_id}`

### HU21: Historial de Alertas
**Tipo:** Integracion / Escenarios  
**Pruebas:** 16  
**Endpoints:**
- `/alerts/history`
- `/alerts/errors`
- `/alerts/anomalies`
- `/alerts/status/{facade_id}`

## Tipos de Validaciones

Cada prueba valida:
- Codigo de estado HTTP (200, 404, etc.)
- Estructura de respuesta JSON
- Tipos de datos correctos
- Rangos de valores razonables
- Parametros de filtrado
- Paginacion y limites
- Consistencia entre endpoints
- Manejo de errores

## Configuracion

El archivo `pytest.ini` contiene:
- Rutas de pruebas
- Modo asincrono
- Opciones de verbosidad
- Marcadores personalizados

## Notas Tecnicas

- Las pruebas son **asincronas** usando `pytest-asyncio`
- Se utiliza `httpx.AsyncClient` para simular peticiones HTTP
- No se requiere levantar el servidor (usa `app` de FastAPI directamente)
- Las pruebas son **independientes** y pueden ejecutarse en cualquier orden

## Resultados Esperados

Al ejecutar todas las pruebas:
```
61 passed in X.XXs
```

## Documentacion Completa

Ver `TESTS_DOCUMENTATION.md` para documentacion detallada de cada prueba.

## Solucion de Problemas

### Error: "externally-managed-environment"
Usar entorno virtual:
```bash
source ../venv/bin/activate
pip install -r tests/requirements-test.txt
```

### Error: "ModuleNotFoundError: No module named 'app'"
Asegurarse de estar en el directorio `backend/`:
```bash
cd backend
pytest tests/
```

### Pruebas lentas
Ejecutar pruebas especificas en lugar de todas:
```bash
pytest tests/test_hu10_refrigeration_cycle.py
```
