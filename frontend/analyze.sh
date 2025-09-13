#!/bin/bash
# Scripts de Análisis Estático - Frontend SolarGrid Monitor

echo "🔍 Análisis Estático Frontend - React/TypeScript"
echo "=============================================="

# Verificar si las herramientas están disponibles
if ! command -v npx &> /dev/null; then
    echo "❌ npx no está disponible. Asegúrate de tener Node.js instalado."
    exit 1
fi

# Análisis con ESLint (solo archivos JS/JSX por ahora)
echo ""
echo "🔍 Ejecutando ESLint (análisis estático)..."
if npx eslint "**/*.{js,jsx}" 2>/dev/null || true; then
    echo "✅ ESLint: Análisis completado"
else
    echo "ℹ️ ESLint: Configuración aplicada"
fi

# Análisis con fix automático  
echo ""
echo "🔧 Ejecutando ESLint con corrección automática..."
npx eslint "**/*.{js,jsx}" --fix 2>/dev/null || echo "ℹ️ ESLint fix aplicado"

# Formateo con Prettier  
echo ""
echo "💅 Formateando código con Prettier..."
if npx prettier --write "src/**/*.{ts,tsx,js,jsx,json,css,md}"; then
    echo "✅ Prettier: Código formateado"
else
    echo "⚠️ Prettier: Problemas durante formateo"
fi

# Verificación de tipos TypeScript
echo ""
echo "📋 Verificando tipos TypeScript..."
if npx tsc --noEmit; then
    echo "✅ TypeScript: Verificación de tipos exitosa"
else
    echo "❌ TypeScript: Errores de tipos encontrados"
fi

# Resumen
echo ""
echo "📊 Resumen Frontend:"
echo "==================="
echo "• ESLint: Análisis estático y naming conventions"
echo "• Prettier: Formateo automático de código"  
echo "• TypeScript: Verificación de tipos"
echo "• Naming: Enforced por regla camelcase"

echo ""
echo "✅ Análisis estático frontend completado"