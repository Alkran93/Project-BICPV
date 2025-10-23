#!/bin/bash

# Script para ejecutar las pruebas automatizadas del backend
# Asegurar que estamos en el directorio correcto

cd "$(dirname "$0")"

# Activar entorno virtual si existe
if [ -d "../venv" ]; then
    source ../venv/bin/activate
fi

echo "=========================================="
echo "  Pruebas Automatizadas - Backend API"
echo "=========================================="
echo ""

# Verificar instalacion de pytest
if ! command -v pytest &> /dev/null; then
    echo "ERROR: pytest no esta instalado"
    echo "Ejecute: pip install -r tests/requirements-test.txt"
    exit 1
fi

# Ejecutar pruebas segun argumentos
case "$1" in
    hu10)
        echo "Ejecutando pruebas HU10 - Ciclo de Refrigeracion"
        pytest tests/test_hu10_refrigeration_cycle.py -v
        ;;
    hu13)
        echo "Ejecutando pruebas HU13 - Comparacion Intercambiador"
        pytest tests/test_hu13_exchanger_comparison.py -v
        ;;
    hu15)
        echo "Ejecutando pruebas HU15 - Alertas Automaticas de Fallos"
        pytest tests/test_hu15_automatic_alerts.py -v
        ;;
    hu17)
        echo "Ejecutando pruebas HU17 - Comparacion de Rendimiento"
        pytest tests/test_hu17_performance_comparison.py -v
        ;;
    hu18)
        echo "Ejecutando pruebas HU18 - Exportacion CSV"
        pytest tests/test_hu18_csv_export.py -v
        ;;
    hu21)
        echo "Ejecutando pruebas HU21 - Historial de Alertas"
        pytest tests/test_hu21_alerts_history.py -v
        ;;
    coverage)
        echo "Ejecutando pruebas con cobertura de codigo"
        pytest tests/ --cov=app --cov-report=html --cov-report=term
        echo ""
        echo "Reporte HTML generado en: htmlcov/index.html"
        ;;
    *)
        echo "Ejecutando TODAS las pruebas"
        pytest tests/ -v
        ;;
esac

echo ""
echo "=========================================="
echo "  Ejecucion de pruebas completada"
echo "=========================================="
