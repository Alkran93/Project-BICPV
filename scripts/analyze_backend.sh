#!/bin/bash
# Scripts de Análisis Estático - Backend Python con Ruff

echo "🔍 Análisis Estático de Código Python - SolarGrid Monitor"
echo "========================================================"

# Verificar si Ruff está instalado
if ! command -v ruff &> /dev/null; then
    echo "❌ Ruff no está instalado. Instalando..."
    pip install ruff
fi

# Análisis estático completo
echo ""
echo "🐍 Ejecutando Ruff - Análisis estático..."
ruff check .

# Corrección automática
echo ""  
echo "🔧 Aplicando correcciones automáticas básicas..."
ruff check . --fix

# Corrección automática avanzada
echo ""
echo "🚀 Aplicando correcciones automáticas avanzadas..."
ruff check . --fix --unsafe-fixes

# Verificar si hay errores críticos
if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Se encontraron problemas de análisis estático"
    echo "💡 Ejecuta 'ruff check . --fix' para corrección automática"
else
    echo ""
    echo "✅ Análisis estático completado sin errores críticos"
fi

# Formateo automático
echo ""
echo "💅 Ejecutando Ruff - Formateo de código..."
ruff format .

# Validación de imports
echo ""
echo "📦 Validando ordenamiento de imports..."
ruff check . --select I --fix

# Resumen final
echo ""
echo "📊 Resumen de Análisis Estático:"
echo "================================"
echo "• Linting: ruff check ."
echo "• Formateo: ruff format ."  
echo "• Imports: ruff check . --select I"
echo "• Naming: Validado automáticamente por reglas N*"
echo "• Seguridad: Validado por reglas S*"

# Integración con naming validator personalizado
echo ""
echo "🎯 Ejecutando validador de nombramiento personalizado..."
python scripts/naming_validator.py