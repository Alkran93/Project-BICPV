# 🌐 Guía de Tests E2E (End-to-End)

## 📋 Índice
1. [¿Qué son los Tests E2E?](#qué-son-los-tests-e2e)
2. [Diferencia con Tests de Integración](#diferencia-con-tests-de-integración)
3. [Prerequisitos](#prerequisitos)
4. [Cómo Ejecutar](#cómo-ejecutar)
5. [Estructura de Tests](#estructura-de-tests)
6. [Troubleshooting](#troubleshooting)

---

## 🎯 ¿Qué son los Tests E2E?

Los **Tests End-to-End (E2E)** validan el flujo completo de la aplicación:

```
Usuario → Frontend → API HTTP → Backend → Base de Datos → Backend → Frontend → Usuario
```

**Tests E2E validan:**
- ✅ Backend está corriendo y responde
- ✅ Base de datos tiene datos válidos
- ✅ APIs retornan el formato esperado
- ✅ Frontend procesa datos reales correctamente
- ✅ Toda la integración funciona

---

## 🔄 Diferencia con Tests de Integración

| Aspecto | Tests de Integración | Tests E2E |
|---------|---------------------|-----------|
| **Datos** | Mockeados/Constantes | Reales del backend |
| **Backend** | NO requerido | SÍ requerido |
| **Velocidad** | Rápido (3s) | Lento (30s) |
| **Confiabilidad** | Siempre igual | Puede variar |
| **Propósito** | Validar lógica | Validar integración completa |

### Archivos:

```
src/__tests__/
├── PanelDetail.integration.test.tsx  ← Tests con mocks (rápidos)
└── PanelDetail.e2e.test.tsx          ← Tests con backend real (lentos)
```

---

## ✅ Prerequisitos

### 1. Backend Corriendo

El backend **DEBE** estar corriendo antes de ejecutar tests E2E:

```bash
# Opción A: Docker Compose (Recomendado)
cd /home/santi/PROYECTO2/Project-BICPV
docker-compose up -d

# Opción B: Manual (si no usas Docker)
cd backend
python -m uvicorn app.main:app --reload
```

### 2. Verificar que el Backend Responde

```bash
# Debería retornar 200 OK
curl -I http://localhost:8000/docs

# O abre en navegador
firefox http://localhost:8000/docs
```

### 3. Base de Datos con Datos

Asegúrate de que la base de datos tenga datos de prueba:

```bash
# Si usas el publisher simulator
cd /home/santi/PROYECTO2/Project-BICPV
python publisher_simulator.py
```

---

## 🚀 Cómo Ejecutar

### Tests E2E únicamente (Backend Real)

```bash
cd frontend

# Ejecutar todos los tests E2E una vez
npm run test:e2e

# Modo watch (re-ejecuta al guardar)
npm run test:e2e:watch
```

### Tests de Integración únicamente (Con Mocks)

```bash
# Rápidos, no requieren backend
npm run test
npm run test:watch
npm run test:ui
npm run test:coverage
```

### Todos los Tests (E2E + Integración)

```bash
npm run test:all
```

---

## 📊 Estructura de Tests E2E

### Archivo: `src/__tests__/PanelDetail.e2e.test.tsx`

```typescript
describe('PanelDetail - E2E con Backend Real', () => {
  
  // ✅ Verifica conexión antes de empezar
  beforeAll(async () => {
    await fetch('http://localhost:8000/docs');
  });

  // 📡 Suite 1: Conexión y Carga
  describe('Suite 1: Carga de Datos Reales', () => {
    it('debería conectar con backend y cargar fachada 2', ...);
    it('debería cargar datos ambientales reales', ...);
    it('debería calcular promedio real', ...);
  });

  // 🔍 Suite 2: Validación de API
  describe('Suite 2: Validación de Formato de API', () => {
    it('GET /realtime/facades/2 retorna formato correcto', ...);
    it('GET /facades/2/sensors retorna array', ...);
    it('GET /facades/2 retorna overview data', ...);
  });

  // 🎨 Suite 3: Renderizado
  describe('Suite 3: Renderizado con Datos Reales', () => {
    it('debería renderizar grid SVG', ...);
    it('debería mostrar temperaturas reales', ...);
  });

  // 🖱️ Suite 4: Interacción
  describe('Suite 4: Interacción del Usuario', () => {
    it('debería permitir click en sensor', ...);
    it('debería ejecutar callback onBack', ...);
  });

  // ✔️ Suite 5: Validación de Rangos
  describe('Suite 5: Rangos de Datos Reales', () => {
    it('temperaturas en rango -10°C a 80°C', ...);
    it('datos ambientales en rangos válidos', ...);
  });
});
```

### Total: **5 Suites, 13 Tests**

---

## 🔬 Qué Validan los Tests E2E

### Suite 1: Carga de Datos Reales
```typescript
✅ Backend responde correctamente
✅ Datos se cargan en el componente
✅ Promedio calculado con datos reales
```

### Suite 2: Validación de Formato de API
```typescript
✅ /realtime/facades/{id} → { facade_id, data: {...} }
✅ /facades/{id}/sensors → Array de sensor IDs
✅ /facades/{id} → { facade_id, current_readings: [...] }
```

### Suite 3: Renderizado
```typescript
✅ Grid SVG renderizado
✅ Temperaturas mostradas en formato XX.X°C
✅ Elementos visuales (rect, circle, path)
```

### Suite 4: Interacción
```typescript
✅ Click en sensor funciona
✅ Botón "Volver" ejecuta callback
```

### Suite 5: Validación de Rangos
```typescript
✅ Temperaturas: -10°C ≤ T ≤ 80°C
✅ Irradiancia: 0 ≤ I ≤ 1500 W/m²
✅ Viento: 0 ≤ V ≤ 50 m/s
✅ Humedad: 0 ≤ H ≤ 100 %
```

---

## 🐛 Troubleshooting

### Error: "Backend NO DISPONIBLE"

```
❌ Error conectando con backend: fetch failed
```

**Solución:**
```bash
# 1. Verifica que Docker esté corriendo
docker ps

# 2. Inicia el backend
cd /home/santi/PROYECTO2/Project-BICPV
docker-compose up -d

# 3. Espera 10-20 segundos y verifica
curl http://localhost:8000/docs
```

---

### Error: Timeout después de 30 segundos

```
Error: Timeout - Waiting for waitFor callback to be truthy
```

**Posibles causas:**
1. Backend lento respondiendo
2. Base de datos sin datos
3. Componente no renderiza correctamente

**Solución:**
```bash
# 1. Verifica logs del backend
docker-compose logs backend

# 2. Verifica que hay datos en la BD
docker-compose exec timescaledb psql -U bicpv_user -d bicpv_db
SELECT COUNT(*) FROM sensor_readings;

# 3. Aumenta el timeout en el test (si necesario)
# En PanelDetail.e2e.test.tsx:
const TEST_TIMEOUT = 60000; // 60 segundos
```

---

### Error: "Cannot find element"

```
TestingLibraryElementError: Unable to find element with text matching /27\.6.*°C/
```

**Posibles causas:**
1. Datos reales diferentes a los esperados
2. Formato de texto del componente cambió
3. Componente no terminó de renderizar

**Solución:**
```typescript
// En lugar de buscar valor exacto:
expect(screen.getByText(/27\.6.*°C/)).toBeInTheDocument();

// Busca cualquier temperatura:
const temps = screen.getAllByText(/\d+\.\d+.*°C/);
expect(temps.length).toBeGreaterThan(0);
```

---

### Los datos cambian constantemente

**Problema:** Tests fallan porque los datos reales varían.

**Solución:** Usa validaciones de rango en lugar de valores exactos:

```typescript
// ❌ Mal: Valor exacto
expect(avgValue).toBe(27.6);

// ✅ Bien: Rango válido
expect(avgValue).toBeGreaterThan(0);
expect(avgValue).toBeLessThan(100);
```

---

## 📝 Comandos Rápidos

```bash
# 🔧 Preparar entorno
cd /home/santi/PROYECTO2/Project-BICPV
docker-compose up -d
curl http://localhost:8000/docs  # Verificar backend

# 🧪 Ejecutar tests
cd frontend
npm run test:e2e                  # Tests E2E
npm run test                      # Tests con mocks
npm run test:all                  # Todos los tests

# 🛑 Detener backend
cd /home/santi/PROYECTO2/Project-BICPV
docker-compose down
```

---

## 🎯 Cuándo Usar Cada Tipo de Test

### Tests de Integración (con mocks) - Usa siempre
```bash
npm run test
```
- ✅ Desarrollo diario
- ✅ CI/CD pipelines
- ✅ Validar lógica de componentes
- ✅ Rápidos y confiables

### Tests E2E (backend real) - Usa ocasionalmente
```bash
npm run test:e2e
```
- ✅ Antes de releases importantes
- ✅ Validar integración completa
- ✅ Detectar problemas de formato de API
- ✅ Verificar que todo funciona junto

---

## 📚 Recursos Adicionales

- [Vitest Documentation](https://vitest.dev/)
- [Testing Library Best Practices](https://testing-library.com/docs/queries/about)
- [React Testing Guide](https://react.dev/learn/testing)

---

## ✅ Checklist de Ejecución

Antes de ejecutar tests E2E, verifica:

- [ ] Docker está corriendo (`docker ps`)
- [ ] Backend está corriendo (`curl http://localhost:8000/docs`)
- [ ] Base de datos tiene datos (`docker-compose logs timescaledb`)
- [ ] No hay otros procesos usando puerto 8000 (`lsof -i :8000`)
- [ ] Tienes conexión a internet (si usas servicios externos)

---

**Última actualización:** Octubre 20, 2025  
**Versión:** 1.0.0
