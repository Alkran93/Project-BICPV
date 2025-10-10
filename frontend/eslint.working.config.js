// Configuración ESLint funcional para SolarGrid Monitor
// Análisis estático simplificado que realmente funciona

export default [
  {
    ignores: ['dist/', 'node_modules/', 'coverage/', '.vscode/', '.idea/', 'build/']
  },
  {
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
        console: 'readonly'
      }
    },
    rules: {
      // Análisis estático básico
      'no-unused-vars': 'warn',
      'no-console': 'warn',
      'no-debugger': 'error',
      'prefer-const': 'error',
      'no-var': 'error',
      
      // Naming conventions (puntos adicionales)
      'camelcase': ['error', { 
        properties: 'never',
        allow: ['^[A-Z][A-Za-z0-9]*$'] // Permitir PascalCase para componentes
      }]
    }
  }
]