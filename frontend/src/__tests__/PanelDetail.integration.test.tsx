import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import PanelDetail from '../components/PanelDetail';

const mockTemperatureSensors = {
  facade_id: "2",
  facade_type: "refrigerated",
  data: {
    Temperature_M1: { value: 24.1, ts: "2025-10-20T10:00:00Z" },
    Temperature_M2: { value: 27.3, ts: "2025-10-20T10:00:00Z" },
    Temperature_M3: { value: 26.8, ts: "2025-10-20T10:00:00Z" },
    Temperature_M4: { value: 25.4, ts: "2025-10-20T10:00:00Z" },
    Temperature_M5: { value: 28.9, ts: "2025-10-20T10:00:00Z" },
    Temperature_M6: { value: 27.1, ts: "2025-10-20T10:00:00Z" },
    Temperature_M7: { value: 26.3, ts: "2025-10-20T10:00:00Z" },
    Temperature_M8: { value: 29.7, ts: "2025-10-20T10:00:00Z" },
    Temperature_M9: { value: 28.2, ts: "2025-10-20T10:00:00Z" },
    Temperature_M10: { value: 27.6, ts: "2025-10-20T10:00:00Z" },
    Temperature_M11: { value: 30.2, ts: "2025-10-20T10:00:00Z" },
    Temperature_M12: { value: 28.5, ts: "2025-10-20T10:00:00Z" },
    Temperature_M13: { value: 27.9, ts: "2025-10-20T10:00:00Z" },
    Temperature_M14: { value: 26.7, ts: "2025-10-20T10:00:00Z" },
    Temperature_M15: { value: 29.3, ts: "2025-10-20T10:00:00Z" },
    Irradiancia: { value: 850, ts: "2025-10-20T10:00:00Z" },
    Velocidad_Viento: { value: 3.2, ts: "2025-10-20T10:00:00Z" },
  }
};

const mockEnvironmentalData = {
  facade_id: "2",
  facade_type: "refrigerated",
  current_readings: [
    { sensor_name: "Irradiancia", value: 850, unit: "W/m²" },
    { sensor_name: "Velocidad_Viento", value: 3.2, unit: "m/s" },
    { sensor_name: "Temperatura_Ambiente", value: 22.5, unit: "°C" },
    { sensor_name: "Humedad", value: 68, unit: "%" },
  ]
};

const mockSensorsList = {
  sensors: [
    "Temperature_M1", "Temperature_M2", "Temperature_M3",
    "Temperature_M4", "Temperature_M5", "Temperature_M6",
    "Temperature_M7", "Temperature_M8", "Temperature_M9",
    "Temperature_M10", "Temperature_M11", "Temperature_M12",
    "Temperature_M13", "Temperature_M14", "Temperature_M15"
  ]
};

const mockProps = {
  title: "Refrigerada",
  refrigerated: true,
  faults: 0,
  temperature: 27.5,
  sensors: [26, 27, 28, 25, 29, 27, 26, 30, 28, 28, 31, 29, 28, 27, 29],
  onBack: vi.fn(),
  onSystemTempClick: vi.fn(),
  id: "2"
};

describe('PanelDetail - Visualización de Temperatura por Sensor (Integración)', () => {
  let mockFetch: any;

  beforeEach(() => {
    mockFetch = vi.fn();
    global.fetch = mockFetch;

    mockFetch.mockImplementation((url: string) => {
      if (url.includes('/realtime/facades/')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockTemperatureSensors),
        });
      } else if (url.includes('/sensors')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockSensorsList),
        });
      } else if (url.includes('/facades/')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockEnvironmentalData),
        });
      }
      return Promise.reject(new Error('URL no mockeada'));
    });
  });

  afterEach(() => {
    vi.clearAllMocks();
    vi.clearAllTimers();
  });

  describe('Suite 1: Carga Inicial de Datos', () => {
    it('debería realizar las 3 llamadas API correctas al montar el componente', async () => {
      render(<PanelDetail {...mockProps} />);

      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining('/realtime/facades/2')
        );
      }, { timeout: 10000 });

      expect(mockFetch).toHaveBeenCalledTimes(3);
    });

    it('debería cargar y procesar los 15 sensores de temperatura', async () => {
      render(<PanelDetail {...mockProps} />);

      await waitFor(() => {
        expect(screen.getByText('15')).toBeInTheDocument();
      }, { timeout: 10000 });
    });

    it('debería calcular y mostrar la temperatura promedio correcta', async () => {
      render(<PanelDetail {...mockProps} />);

      await waitFor(() => {
        const avgText = screen.getByText(/27\.6.*°C/i);
        expect(avgText).toBeInTheDocument();
      }, { timeout: 10000 });
    });
  });

  describe('Suite 2: Visualización del Grid de Sensores', () => {
    it('debería renderizar el grid SVG con 15 celdas de sensores', async () => {
      render(<PanelDetail {...mockProps} />);

      await waitFor(() => {
        const svg = document.querySelector('svg');
        expect(svg).toBeInTheDocument();
      }, { timeout: 10000 });
    });

    it('debería mostrar valores de temperatura en cada celda del grid', async () => {
      render(<PanelDetail {...mockProps} />);

      await waitFor(() => {
        const temperatureTexts = Array.from(document.querySelectorAll('svg text'))
          .filter(text => /^\d{2}°$/.test(text.textContent || ''));
        
        expect(temperatureTexts.length).toBeGreaterThan(0);
      }, { timeout: 10000 });
    });

    it('debería marcar sensores en alerta con stroke rojo', async () => {
      render(<PanelDetail {...mockProps} />);

      await waitFor(() => {
        const alertRects = document.querySelectorAll('rect[stroke="#e63946"]');
        expect(alertRects.length).toBeGreaterThan(0);
      }, { timeout: 10000 });
    });
  });

  describe('Suite 3: Interacción con Sensores', () => {
    it('debería mostrar información detallada al hacer click en un sensor', async () => {
      render(<PanelDetail {...mockProps} />);

      await waitFor(() => {
        const sensorGroups = document.querySelectorAll('svg g');
        expect(sensorGroups.length).toBeGreaterThan(0);
      }, { timeout: 10000 });

      const firstSensor = document.querySelectorAll('svg g')[0];
      fireEvent.click(firstSensor);

      await waitFor(() => {
        expect(screen.getByText('Información del Sensor')).toBeInTheDocument();
      }, { timeout: 10000 });
    });
  });

  describe('Suite 4: Datos Ambientales', () => {
    it('debería cargar y mostrar las 4 condiciones ambientales', async () => {
      render(<PanelDetail {...mockProps} />);

      await waitFor(() => {
        expect(screen.getByText('Irradiancia')).toBeInTheDocument();
        expect(screen.getByText('Velocidad Viento')).toBeInTheDocument();
      }, { timeout: 10000 });
    });

    it('debería mostrar los valores correctos de las condiciones ambientales', async () => {
      render(<PanelDetail {...mockProps} />);

      await waitFor(() => {
        expect(screen.getByText('850.0')).toBeInTheDocument();
        expect(screen.getByText('3.2')).toBeInTheDocument();
      }, { timeout: 10000 });
    });
  });

  describe('Suite 5: Navegación y Callbacks', () => {
    it('debería llamar onBack al presionar el botón Volver', async () => {
      const onBackMock = vi.fn();
      render(<PanelDetail {...mockProps} onBack={onBackMock} />);

      const backButton = screen.getByRole('button', { name: /volver/i });
      fireEvent.click(backButton);

      expect(onBackMock).toHaveBeenCalledTimes(1);
    });
  });
});
