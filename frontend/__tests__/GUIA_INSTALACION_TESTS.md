# Guía Rápida: Instalación y Ejecución de Pruebas

## 📦 Paso 1: Instalar Dependencias

Las pruebas requieren las siguientes dependencias que ya están listadas en `package.json`:

```bash
cd frontend
npm install
```

Esto instalará:
- ✅ `vitest` (^2.1.8) - Framework de testing
- ✅ `@testing-library/react` (^16.1.0) - Utilidades para testing de React
- ✅ `@testing-library/jest-dom` (^6.6.3) - Matchers para DOM
- ✅ `@testing-library/user-event` (^14.5.2) - Simulación de eventos de usuario
- ✅ `jsdom` (^25.0.1) - Simulación de DOM en Node.js
- ✅ `@vitest/ui` (^2.1.8) - Interfaz visual para tests
- ✅ `@vitest/coverage-v8` (^2.1.8) - Reportes de cobertura

## 🚀 Paso 2: Ejecutar las Pruebas

### Opción A: Ejecutar todas las pruebas
```bash
npm run test
```

### Opción B: Ejecutar en modo watch (desarrollo)
```bash
npm run test:watch
```

### Opción C: Ejecutar con interfaz gráfica
```bash
npm run test:ui
```

### Opción D: Ejecutar con cobertura
```bash
npm run test:coverage
```

### Opción E: Ejecutar solo la prueba de RefrigerantCycle
```bash
npm run test RefrigerantCycleDetail.integration.test.tsx
```

### Opción F: Ejecutar un caso específico
```bash
npm run test -- -t "debería cargar y mostrar los 15 sensores"
```

## 📊 Paso 3: Interpretar Resultados

### ✅ Éxito (todos los tests pasan)
```
✓ __tests__/integration/RefrigerantCycleDetail.integration.test.tsx (23)
   ✓ Suite 1: Carga Inicial de Datos de Sensores (3)
   ✓ Suite 2: Visualización del Grid 5x3 de Sensores (3)
   ...
   
Test Files  1 passed (1)
     Tests  23 passed (23)
  Start at  10:30:00
  Duration  487ms
```

### ❌ Fallo (algún test no pasa)
```
✓ Caso 1: Carga de 15 sensores
✗ Caso 2: Temperatura promedio calculada
   Error: expected "28.0°C" to be in the document
   
Test Files  1 failed (1)
     Tests  22 passed | 1 failed (23)
```

**Cómo debuggear:**
1. Lee el mensaje de error - indica qué esperaba y qué obtuvo
2. Ejecuta solo ese test: `npm run test -- -t "Temperatura promedio"`
3. Revisa el stack trace para ver en qué línea falló
4. Verifica que el componente esté consumiendo la API correcta

## 🔧 Paso 4: Debugging Común

### Problema: "Cannot find module 'vitest'"
**Solución**: No se instalaron las dependencias
```bash
npm install
```

### Problema: Test timeout
**Solución**: Aumentar timeout en el test
```typescript
await waitFor(() => expect(...), { timeout: 5000 })
```

### Problema: fetch no está mockeado
**Solución**: Verificar que el test tenga:
```typescript
const mockFetch = vi.fn();
global.fetch = mockFetch;
```

### Problema: Timers no avanzan
**Solución**: Usar fake timers:
```typescript
vi.useFakeTimers();
vi.advanceTimersByTime(5000);
```

### Problema: "Element not found"
**Solución**: Esperar a que el elemento aparezca:
```typescript
await waitFor(() => {
  const element = screen.getByText(/texto/i);
  expect(element).toBeInTheDocument();
});
```

## 📝 Archivos Creados

1. **`vitest.config.ts`** - Configuración de Vitest
2. **`src/__tests__/setup.ts`** - Setup global (mocks de DOM APIs)
3. **`__tests__/integration/RefrigerantCycleDetail.integration.test.tsx`** - 23 casos de prueba
4. **`__tests__/DOCUMENTACION_PRUEBA_CICLO_REFRIGERACION.md`** - Documentación formal
5. **`__tests__/TEST_SPECIFICATION_CICLO.md`** - Especificación técnica

## 🎯 Verificación Rápida

Después de instalar, verifica que todo funciona:

```bash
# 1. Instalar
npm install

# 2. Ejecutar tests
npm run test

# 3. Ver cobertura (opcional)
npm run test:coverage
```

## ⚡ Comandos Útiles

```bash
# Ver lista de scripts disponibles
npm run

# Limpiar node_modules y reinstalar
rm -rf node_modules package-lock.json
npm install

# Ejecutar tests con logs detallados
npm run test -- --reporter=verbose

# Ejecutar tests y generar reporte HTML
npm run test:coverage
# Luego abrir: coverage/index.html
```

## 🎓 Notas Importantes

- Los tests NO requieren el backend ejecutándose (usa mocks)
- Los tests NO requieren el frontend ejecutándose (`npm run dev`)
- Vitest usa jsdom para simular el navegador
- Los mocks están en el mismo archivo de prueba
- El setup global está en `src/__tests__/setup.ts`

---

**Si algo falla después de seguir estos pasos, comparte el error completo y lo revisaré.**
