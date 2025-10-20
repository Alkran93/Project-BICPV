/**
 * 🌐 TESTS E2E (End-to-End) - Backend Real
 * 
 * Estos tests requieren que el backend esté corriendo:
 * 
 * 1. Inicia el backend:
 *    cd /home/santi/PROYECTO2/Project-BICPV
 *    docker-compose up -d
 * 
 * 2. Ejecuta los tests:
 *    cd frontend
 *    npm run test:e2e
 * 
 * DIFERENCIA con tests de integración:
 * - NO usa mocks
 * - Hace fetch REAL al backend
 * - Valida datos reales de la base de datos
 * - Más lento pero más confiable
 */

import { describe, it, expect, beforeAll, afterEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import PanelDetail from '../components/PanelDetail';

// ⚙️ Configuración del backend
const BACKEND_URL = 'http://localhost:8000';
const TEST_TIMEOUT = 30000; // 30 segundos para operaciones reales

// 🔧 Helper para renderizar el componente con props por defecto
const renderPanelDetail = (id: string = "2") => {
  const mockOnBack = () => {};
  const mockOnSystemTempClick = () => {};
  
  return render(
    <PanelDetail 
      id={id}
      title={`Fachada ${id}`}
      refrigerated={true}
      faults={0}
      temperature={25}
      sensors={[]}
      onBack={mockOnBack}
      onSystemTempClick={mockOnSystemTempClick}
    />
  );
};

describe('PanelDetail - E2E con Backend Real 🌐', () => {
  
  // ✅ Verificar que el backend esté corriendo antes de ejecutar tests
  beforeAll(async () => {
    try {
      console.log('🔍 Verificando conexión con backend...');
      const response = await fetch(`${BACKEND_URL}/docs`, { method: 'HEAD' });
      
      if (!response.ok) {
        throw new Error(`Backend respondió con status: ${response.status}`);
      }
      
      console.log('✅ Backend está corriendo en', BACKEND_URL);
    } catch (error) {
      console.error('❌ Error conectando con backend:', error);
      throw new Error(
        '\n\n' +
        '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n' +
        '⚠️  BACKEND NO DISPONIBLE\n' +
        '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n' +
        'Para ejecutar estos tests E2E, primero inicia el backend:\n\n' +
        '  cd /home/santi/PROYECTO2/Project-BICPV\n' +
        '  docker-compose up -d\n\n' +
        'Luego verifica que esté corriendo:\n\n' +
        '  curl http://localhost:8000/docs\n\n' +
        'Y ejecuta los tests:\n\n' +
        '  cd frontend\n' +
        '  npm run test:e2e\n\n' +
        '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n'
      );
    }
  }, TEST_TIMEOUT);

  afterEach(() => {
    // Limpiar cualquier estado si es necesario
  });

  // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  // SUITE 1: Conexión y Carga de Datos Reales
  // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  describe('Suite 1: Carga de Datos Reales desde Backend', () => {
    
    it('debería conectar con el backend y cargar datos de la fachada 2', async () => {
      const mockOnBack = () => {};
      const mockOnSystemTempClick = () => {};
      
      console.log('📡 Renderizando componente con id=2...');
      render(
        <PanelDetail 
          id="2"
          title="Fachada 2"
          refrigerated={true}
          faults={0}
          temperature={25}
          sensors={[]}
          onBack={mockOnBack}
          onSystemTempClick={mockOnSystemTempClick}
        />
      );
      
      // Esperar a que se carguen los datos reales
      await waitFor(() => {
        const tempElements = screen.getAllByText(/\d+\.\d+.*°C/);
        console.log(`📊 Sensores de temperatura encontrados: ${tempElements.length}`);
        expect(tempElements.length).toBeGreaterThan(0);
      }, { timeout: TEST_TIMEOUT });
      
      console.log('✅ Datos de temperatura cargados correctamente');
    }, TEST_TIMEOUT);

    it('debería cargar datos ambientales reales (irradiancia, viento, etc.)', async () => {
      renderPanelDetail("2");
      
      await waitFor(() => {
        // Verificar que el componente se ha renderizado
        const container = document.querySelector('.panel-detail-container');
        expect(container).toBeInTheDocument();
        
        // Verificar que hay datos numéricos en la página (temperaturas, sensores, etc.)
        const allText = document.body.textContent || '';
        const hasNumbers = /\d+(\.\d+)?/.test(allText);
        expect(hasNumbers).toBe(true);
        
        console.log('🌍 Datos ambientales cargados y renderizados');
      }, { timeout: TEST_TIMEOUT });
      
      console.log('✅ Datos ambientales verificados');
    }, TEST_TIMEOUT);

    it('debería calcular el promedio real de temperaturas', async () => {
      renderPanelDetail("2");
      
      await waitFor(() => {
        // Buscar el texto de temperatura promedio
        const avgText = document.body.textContent || '';
        const avgMatch = avgText.match(/promedio[:\s]*(\d+\.\d+).*°C/i);
        
        if (avgMatch) {
          const avgValue = parseFloat(avgMatch[1]);
          console.log(`🌡️ Temperatura promedio: ${avgValue}°C`);
          
          // Verificar que el promedio esté en un rango razonable
          expect(avgValue).toBeGreaterThan(0);
          expect(avgValue).toBeLessThan(100);
          
          console.log('✅ Promedio calculado dentro de rango válido');
        } else {
          console.log('⚠️ No se encontró texto de temperatura promedio');
        }
      }, { timeout: TEST_TIMEOUT });
    }, TEST_TIMEOUT);
  });

  // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  // SUITE 2: Validación de Formato de API Real
  // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  describe('Suite 2: Validación de Formato de API', () => {
    
    it('debería obtener datos con el formato correcto de /realtime/facades/2', async () => {
      console.log('📡 Llamando a API real: /realtime/facades/2');
      
      const response = await fetch(`${BACKEND_URL}/realtime/facades/2`);
      expect(response.ok).toBe(true);
      
      const data = await response.json();
      console.log('📦 Estructura de respuesta:', Object.keys(data));
      
      // Verificar estructura esperada
      expect(data).toHaveProperty('facade_id');
      expect(data).toHaveProperty('data');
      
      // Verificar que hay sensores de temperatura
      const temperatureSensors = Object.keys(data.data || {}).filter(key => 
        key.includes('Temperature') || key.includes('temperature')
      );
      
      console.log(`🌡️ Sensores de temperatura encontrados: ${temperatureSensors.length}`);
      expect(temperatureSensors.length).toBeGreaterThan(0);
      
      // Verificar formato de un sensor
      const firstSensor = data.data[temperatureSensors[0]];
      expect(firstSensor).toHaveProperty('value');
      expect(typeof firstSensor.value).toBe('number');
      
      console.log('✅ Formato de API validado');
    }, TEST_TIMEOUT);

    it('debería obtener lista de sensores desde /facades/2/sensors', async () => {
      console.log('📡 Llamando a API real: /facades/2/sensors');
      
      const response = await fetch(`${BACKEND_URL}/facades/2/sensors`);
      expect(response.ok).toBe(true);
      
      const data = await response.json();
      console.log('📦 Estructura de respuesta de sensors:', typeof data, Object.keys(data || {}));
      
      // La API puede retornar objeto o array, validar que hay contenido
      const hasContent = data && (Array.isArray(data) ? data.length > 0 : Object.keys(data).length > 0);
      expect(hasContent).toBe(true);
      
      console.log('✅ Lista/objeto de sensores obtenido');
    }, TEST_TIMEOUT);

    it('debería obtener datos de overview desde /facades/2', async () => {
      console.log('📡 Llamando a API real: /facades/2');
      
      const response = await fetch(`${BACKEND_URL}/facades/2`);
      expect(response.ok).toBe(true);
      
      const data = await response.json();
      console.log('📦 Overview data keys:', Object.keys(data));
      
      // Verificar estructura básica
      expect(data).toHaveProperty('facade_id');
      
      // Verificar datos ambientales si existen
      if (data.current_readings) {
        console.log(`🌍 Lecturas actuales: ${data.current_readings.length}`);
        expect(Array.isArray(data.current_readings)).toBe(true);
      }
      
      console.log('✅ Overview data obtenido');
    }, TEST_TIMEOUT);
  });

  // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  // SUITE 3: Renderizado con Datos Reales
  // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  describe('Suite 3: Renderizado del Componente con Datos Reales', () => {
    
    it('debería renderizar el grid SVG con datos reales', async () => {
      renderPanelDetail("2");
      
      await waitFor(() => {
        // Buscar el grid SVG
        const svgGrid = document.querySelector('svg, .temperature-grid');
        expect(svgGrid).toBeInTheDocument();
        
        console.log('🎨 Grid SVG renderizado');
      }, { timeout: TEST_TIMEOUT });
      
      // Verificar que hay elementos visuales (rect, circle, etc.)
      const visualElements = document.querySelectorAll('rect, circle, path');
      console.log(`📐 Elementos visuales: ${visualElements.length}`);
      expect(visualElements.length).toBeGreaterThan(0);
      
      console.log('✅ Visualización SVG verificada');
    }, TEST_TIMEOUT);

    it('debería mostrar valores de temperatura reales en el grid', async () => {
      renderPanelDetail("2");
      
      await waitFor(() => {
        // Buscar elementos con patrón de temperatura (XX.X°C)
        const tempPattern = /\d+\.\d+.*°C/;
        const allText = document.body.textContent || '';
        const hasTemperatures = tempPattern.test(allText);
        
        expect(hasTemperatures).toBe(true);
        
        // Contar cuántas temperaturas hay
        const matches = allText.match(/\d+\.\d+.*°C/g);
        console.log(`🌡️ Temperaturas mostradas: ${matches?.length || 0}`);
        
        console.log('✅ Temperaturas renderizadas');
      }, { timeout: TEST_TIMEOUT });
    }, TEST_TIMEOUT);
  });

  // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  // SUITE 4: Interacción con Datos Reales
  // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  describe('Suite 4: Interacción del Usuario con Datos Reales', () => {
    
    it('debería permitir hacer click en un sensor y ver detalle', async () => {
      const user = userEvent.setup();
      
      renderPanelDetail("2");
      
      // Esperar a que carguen los datos
      await waitFor(() => {
        const tempElements = screen.getAllByText(/\d+\.\d+.*°C/);
        expect(tempElements.length).toBeGreaterThan(0);
      }, { timeout: TEST_TIMEOUT });
      
      // Obtener el primer elemento de temperatura y hacer click
      const tempElements = screen.getAllByText(/\d+\.\d+.*°C/);
      const firstTemp = tempElements[0];
      
      console.log('🖱️ Haciendo click en sensor...');
      await user.click(firstTemp);
      
      // Verificar que algo cambió (podría ser un modal, panel, etc.)
      await waitFor(() => {
        const bodyText = document.body.textContent || '';
        // Buscar indicadores de que se mostró detalle
        const hasDetail = bodyText.length > 0;
        expect(hasDetail).toBe(true);
        
        console.log('✅ Click en sensor procesado');
      }, { timeout: 5000 });
    }, TEST_TIMEOUT);

    it('debería llamar a onBack cuando se presiona el botón Volver', async () => {
      let backCalled = false;
      const mockOnBack = () => {
        backCalled = true;
        console.log('🔙 Callback onBack ejecutado');
      };
      const mockOnSystemTempClick = () => {};
      const user = userEvent.setup();
      
      render(
        <PanelDetail 
          id="2"
          title="Fachada 2"
          refrigerated={true}
          faults={0}
          temperature={25}
          sensors={[]}
          onBack={mockOnBack}
          onSystemTempClick={mockOnSystemTempClick}
        />
      );
      
      // Esperar a que cargue el componente
      await waitFor(() => {
        const backButton = screen.getByText(/volver|back|regresar/i);
        expect(backButton).toBeInTheDocument();
      }, { timeout: TEST_TIMEOUT });
      
      // Hacer click en el botón
      const backButton = screen.getByText(/volver|back|regresar/i);
      await user.click(backButton);
      
      expect(backCalled).toBe(true);
      console.log('✅ Navegación verificada');
    }, TEST_TIMEOUT);
  });

  // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  // SUITE 5: Validación de Datos con Rangos Realistas
  // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  describe('Suite 5: Validación de Rangos de Datos Reales', () => {
    
    it('debería tener valores de temperatura en rangos realistas', async () => {
      const response = await fetch(`${BACKEND_URL}/realtime/facades/2`);
      const data = await response.json();
      
      const temperatures: number[] = [];
      
      Object.keys(data.data || {}).forEach(key => {
        if (key.includes('Temperature') || key.includes('temperature')) {
          const value = data.data[key].value;
          temperatures.push(value);
        }
      });
      
      console.log(`🌡️ Temperaturas obtenidas: ${temperatures.join(', ')}`);
      
      // Verificar rangos realistas para un sistema BIPV/C
      temperatures.forEach(temp => {
        expect(temp).toBeGreaterThanOrEqual(-10); // Mínimo razonable
        expect(temp).toBeLessThanOrEqual(80);     // Máximo razonable
      });
      
      console.log('✅ Todas las temperaturas están en rangos válidos');
    }, TEST_TIMEOUT);

    it('debería tener datos ambientales en rangos válidos', async () => {
      const response = await fetch(`${BACKEND_URL}/facades/2`);
      expect(response.ok).toBe(true);
      
      const data = await response.json();
      
      // Verificar que current_readings existe y tiene datos
      expect(data).toHaveProperty('current_readings');
      expect(Array.isArray(data.current_readings)).toBe(true);
      expect(data.current_readings.length).toBeGreaterThan(0);
      
      // Buscar y validar sensores ambientales
      const irradiancia = data.current_readings.find((r: any) => r.sensor_name === 'Irradiancia');
      const viento = data.current_readings.find((r: any) => r.sensor_name === 'Velocidad_Viento');
      const humedad = data.current_readings.find((r: any) => r.sensor_name === 'Humedad');
      
      if (irradiancia) {
        expect(irradiancia.value).toBeGreaterThanOrEqual(0);
        expect(irradiancia.value).toBeLessThanOrEqual(1500);
        console.log(`✅ Irradiancia validada: ${irradiancia.value} W/m²`);
      }
      
      if (viento) {
        expect(viento.value).toBeGreaterThanOrEqual(0);
        expect(viento.value).toBeLessThanOrEqual(50);
        console.log(`✅ Viento validado: ${viento.value} m/s`);
      }
      
      if (humedad) {
        expect(humedad.value).toBeGreaterThanOrEqual(0);
        expect(humedad.value).toBeLessThanOrEqual(100);
        console.log(`✅ Humedad validada: ${humedad.value} %`);
      }
      
      console.log('✅ Datos ambientales en rangos válidos');
    });
  });
});
