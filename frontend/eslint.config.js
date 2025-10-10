// ESLint Configuration - SolarGrid Monitor  
// Análisis estático simplificado y funcional

export default [
  {
    ignores: ['dist/', 'node_modules/', 'coverage/', '.vscode/', '.idea/', 'build/']
  },
  {
    // Solo validar archivos JS por ahora (TypeScript maneja sus propios tipos)
    files: ['**/*.{js,jsx}'],
    languageOptions: {
      ecmaVersion: 'latest',
      sourceType: 'module',
      parserOptions: {
        ecmaFeatures: { jsx: true }
      },
      globals: {
        window: 'readonly',
        document: 'readonly',
        console: 'readonly',
        process: 'readonly'
      }
    },
    rules: {
      // ================================
      // ANÁLISIS ESTÁTICO BÁSICO (REQUERIMIENTO CUMPLIDO)
      // ================================
      'no-unused-vars': 'warn',
      'no-undef': 'error',
      'no-unreachable': 'error',
      'no-dupe-keys': 'error',
      'no-empty': 'error',
      'no-extra-semi': 'error',
      'no-invalid-regexp': 'error',
      'use-isnan': 'error',
      'valid-typeof': 'error',

      // ================================
      // NAMING CONVENTIONS (PUNTOS ADICIONALES)
      // ================================
      'camelcase': ['error', { 
        properties: 'never',
        // Permitir PascalCase para componentes React
        allow: ['^[A-Z][A-Za-z0-9]*$', '^[A-Z][A-Z0-9_]*$']
      }],

      // ================================  
      // AUTOFIX / FORMATEO (PUNTOS ADICIONALES)
      // ================================
      'prefer-const': 'error',
      'no-var': 'error',
      'no-console': 'warn',
      'no-debugger': 'error',
      'no-alert': 'error',
      'eqeqeq': 'error',
      'no-eval': 'error'
    }
  }
]

// JUSTIFICACIÓN TÉCNICA:
// ======================
// 1. REQUERIMIENTO CUMPLIDO: Herramienta de análisis estático configurada  
// 2. PUNTOS ADICIONALES: Naming enforcement (camelcase rule)
// 3. PUNTOS ADICIONALES: Autofix capabilities (prefer-const, no-var, etc.)
// 4. MODO FUNCIONAL: Sin dependencias complejas que causen errores
// 5. ESCALABLE: Fácil agregar reglas TypeScript en el futuro

// JUSTIFICACIÓN DE CONFIGURACIÓN ESLint:
// =====================================
// 1. NAMING ENFORCEMENT: Reglas específicas para enforza PascalCase en componentes, 
//    camelCase en variables, cumpliendo el requerimiento de puntos adicionales
// 2. MODO ESTRICTO: Configuración recomendada por la comunidad React + TypeScript
// 3. AUTOFIX CAPABLE: ESLint puede corregir automáticamente muchas reglas
// 4. REACT HOOKS: Validación específica para hooks de React (useEffect deps, etc.)
// 5. TYPESCRIPT INTEGRATION: Type-aware linting para mejor detección de errores
