import { ArrowLeft, Thermometer, Sun, Wind, Droplets } from "lucide-react";
import { useState, useEffect } from "react";
import "../styles/PanelDetail.css";

type PanelDetailProps = {
  title: string;
  refrigerated: boolean;
  faults: number;
  temperature: number;
  sensors: number[];
  onBack: () => void;
  onSystemTempClick: () => void;
  id?: string; // Añadir ID para hacer las consultas API
};

interface TemperatureSensor {
  sensor_id: string;
  value: number;
  unit: string;
  last_update: string;
  sensor_type: string;
}

interface FacadeOverview {
  facade_id: string;
  total_sensors: number;
  total_devices: number;
  last_update: string;
  avg_temperature: number;
  irradiancia: number;
  velocidad_viento: number;
}

export default function PanelDetail({
  title,
  refrigerated = false,
  faults = 0,
  temperature,
  sensors = [],
  onBack,
  onSystemTempClick,
  id = "1", // ID por defecto
}: PanelDetailProps) {
  const [selectedSensor, setSelectedSensor] = useState<number | null>(null);
  const [temperatureSensors, setTemperatureSensors] = useState<TemperatureSensor[]>([]);
  const [sensorsList, setSensorsList] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [averageTemperature, setAverageTemperature] = useState<number>(temperature);
  const [environmentalData, setEnvironmentalData] = useState({
    irradiance: 0,
    windSpeed: 0,
    ambientTemp: 0,
    humidity: 65, // Este valor no viene del overview, se mantiene fijo
  });

  // Función para obtener datos de overview (condiciones ambientales)
  const fetchOverviewData = async () => {
    try {
      const url = `http://127.0.0.1:8000/api/overview/`;
      console.log(`🌍 Fetching overview data from: ${url}`);

      const response = await fetch(url);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      console.log(`📋 Overview API response:`, data);
      console.log(`🔍 Looking for facade_id: "${id}"`);

      // Buscar la fachada específica en el array
      const facadeData = data.find((facade: FacadeOverview) => facade.facade_id === id);

      if (facadeData) {
        console.log(`✅ Found facade data:`, facadeData);
        console.log(
          `�️ Setting environmental data - Irradiance: ${facadeData.irradiancia}, Wind: ${facadeData.velocidad_viento}, Temp: ${facadeData.avg_temperature}`
        );

        setEnvironmentalData({
          irradiance: facadeData.irradiancia,
          windSpeed: facadeData.velocidad_viento,
          ambientTemp: facadeData.avg_temperature,
          humidity: 65, // Valor fijo por ahora
        });
      } else {
        console.warn(`⚠️ No overview data found for facade "${id}"`);
        console.log(
          `Available facade IDs:`,
          data.map((f: FacadeOverview) => f.facade_id)
        );
      }
    } catch (error) {
      console.error("💥 Error fetching overview data:", error);
    }
  };

  // Función para obtener la lista de sensores
  const fetchSensorsList = async () => {
    try {
      const url = `http://127.0.0.1:8000/api/sensors/list/${id}`;
      const response = await fetch(url);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      setSensorsList(data);
    } catch (error) {
      console.error("Error fetching sensors list:", error);
      setSensorsList([]);
    }
  };

  // Función para obtener datos de temperatura desde la API
  const fetchTemperatureSensors = async () => {
    setLoading(true);
    try {
      const url = `http://127.0.0.1:8000/api/dashboard/realtime/${id}`;
      const response = await fetch(url);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();

      // Filtrar solo sensores de temperatura
      const tempSensors = data.filter(
        (sensor: any) =>
          sensor.sensor_type === "temperature" &&
          sensor.sensor_id.startsWith("Temperatura_")
      );

      setTemperatureSensors(tempSensors);

      // Calcular y actualizar la temperatura promedio con los datos filtrados
      if (tempSensors.length > 0) {
        const values = tempSensors.map((sensor: any) => sensor.value);
        const sum = tempSensors.reduce(
          (acc: number, sensor: any) => acc + sensor.value,
          0
        );
        const avgTemp = sum / tempSensors.length;

        console.log(`🌡️ Temperature sensors values:`, values);
        console.log(
          `🧮 Sum: ${sum}, Count: ${tempSensors.length}, Average: ${avgTemp.toFixed(2)}°C`
        );
        console.log(
          `📊 Previous average: ${averageTemperature.toFixed(2)}°C, New average: ${avgTemp.toFixed(2)}°C`
        );

        setAverageTemperature(avgTemp);
      } else {
        console.warn("⚠️ No temperature sensors found for average calculation");
        setAverageTemperature(temperature); // Fallback al valor original
      }
    } catch (error) {
      console.error("Error fetching temperature sensors:", error);
      setTemperatureSensors([]);
      setAverageTemperature(temperature); // Fallback en caso de error
    } finally {
      setLoading(false);
    }
  };

  // Efecto para cargar datos al montar el componente
  useEffect(() => {
    fetchSensorsList();
    fetchTemperatureSensors();
    fetchOverviewData();
  }, [id]);

  // Efecto para auto-refresh de temperaturas cada 5 segundos
  useEffect(() => {
    const interval = setInterval(() => {
      fetchTemperatureSensors();
      fetchOverviewData(); // También actualizar datos ambientales
    }, 5000);

    return () => clearInterval(interval);
  }, [id]);

  // Efecto para debug - observar cambios en averageTemperature
  useEffect(() => {
    console.log(
      `🔄 Average temperature state updated to: ${averageTemperature.toFixed(2)}°C`
    );
  }, [averageTemperature]);

  // Efecto para debug - observar cambios en environmentalData
  useEffect(() => {
    console.log(`🌍 Environmental data state updated:`, environmentalData);
  }, [environmentalData]);

  // Función para obtener el valor de temperatura para una posición específica
  const getTemperatureForPosition = (index: number) => {
    if (temperatureSensors.length === 0) return undefined;

    // Mapear posición del grid (0-14) a sensor reverso
    const totalSensors = 15;
    const reverseIndex = totalSensors - 1 - index;

    if (temperatureSensors[reverseIndex]) {
      return temperatureSensors[reverseIndex].value;
    }

    return sensors[index]; // Fallback
  };

  // Función para obtener el ID del sensor para una posición específica
  const getSensorIdForPosition = (index: number) => {
    if (temperatureSensors.length === 0) return `Sensor ${index + 1}`;

    const totalSensors = 15;
    const reverseIndex = totalSensors - 1 - index;

    if (temperatureSensors[reverseIndex]) {
      const sensorId = temperatureSensors[reverseIndex].sensor_id;
      const match = sensorId.match(/L\d+_\d+/);
      return match ? match[0] : sensorId;
    }

    const row = Math.floor((totalSensors - 1 - index) / 3) + 1;
    const col = ((totalSensors - 1 - index) % 3) + 1;
    return `L${row}_${col}`;
  };

  return (
    <div className="panel-detail-container">
      {/* Header con botón de regreso */}
      <div className="panel-detail-header">
        <button
          onClick={onBack}
          className="back-button"
          aria-label="Volver al dashboard principal"
        >
          <ArrowLeft size={20} />
          <span>Volver</span>
        </button>

        <div className="panel-detail-title-section">
          <h1 className="panel-detail-title">Fachada Solar Fotovoltaica - {title}</h1>
          <div className="panel-detail-status">
            <div
              className={`status-indicator ${refrigerated ? "status-ok" : "status-alert"}`}
              title={
                refrigerated
                  ? "Sistema refrigerado activo"
                  : "Sin sistema de refrigeración"
              }
            >
              <span className="status-icon">{refrigerated ? "✓" : "✖"}</span>
              <span className="status-text">
                {refrigerated ? "Refrigerado" : "Sin Refrigerar"}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Métricas principales - ahora en grid compacto */}
      <div className="metrics-summary">
        <div className="metric-card">
          <div className="metric-value">{faults}</div>
          <div className="metric-label">Fallos Detectados</div>
        </div>
        <div
          className="metric-card clickable"
          onClick={onSystemTempClick}
          role="button"
          tabIndex={0}
        >
          <div className="metric-value">
            {averageTemperature.toFixed(1)}°C {loading && "🔄"}
          </div>
          <div className="metric-label">Temperatura Promedio (Real)</div>
        </div>
        <div className="metric-card">
          <div className="metric-value">{sensorsList.length}</div>
          <div className="metric-label">Sensores Activos</div>
        </div>
        <div className="metric-card">
          <div className="metric-value">
            {temperatureSensors.length > 0
              ? `${Math.min(...temperatureSensors.map(s => s.value)).toFixed(1)}°C / ${Math.max(...temperatureSensors.map(s => s.value)).toFixed(1)}°C`
              : `${Math.min(...sensors).toFixed(1)}°C / ${Math.max(...sensors).toFixed(1)}°C`}
          </div>
          <div className="metric-label">Rango Temperatura</div>
        </div>
      </div>

      {/* Contenido principal en layout horizontal */}
      <div className="main-content">
        {/* Vista ampliada del panel */}
        <div className="panel-visual-section">
          <h2 className="section-title">Vista Detallada de Sensores</h2>
          <div className="large-panel-container">
            <svg viewBox="0 0 360 600" className="large-panel-svg">
              {/* Fondo del panel */}
              <rect
                width="360"
                height="600"
                rx="16"
                fill="#AFDAE8"
                stroke="#214B4E"
                strokeWidth="2"
              />

              {/* Grid de sensores 5x3 más grande */}
              {Array.from({ length: 5 }).map((_, row) =>
                Array.from({ length: 3 }).map((_, col) => {
                  const index = row * 3 + col;
                  const value = getTemperatureForPosition(index);
                  const sensorId = getSensorIdForPosition(index);
                  const isAlert = value !== undefined && value < 25;

                  return (
                    <g
                      key={`${row}-${col}`}
                      onClick={() => setSelectedSensor(index)}
                      style={{ cursor: "pointer" }}
                    >
                      {/* Celda del sensor */}
                      <rect
                        x={30 + col * 100}
                        y={40 + row * 110}
                        width="80"
                        height="90"
                        rx="6"
                        fill="#3568A7"
                        stroke={isAlert ? "#e63946" : "#214B4E"}
                        strokeWidth={isAlert ? "3" : "1"}
                      />

                      {/* Nombre del sensor */}
                      <text
                        x={70 + col * 100}
                        y={60 + row * 110}
                        fontSize="12"
                        fill="#A6A6A6"
                        textAnchor="middle"
                        fontWeight="500"
                      >
                        {sensorId}
                      </text>

                      {/* Valor de temperatura */}
                      {value !== undefined && (
                        <>
                          <text
                            x={70 + col * 100}
                            y={95 + row * 110}
                            fontSize="24"
                            fontWeight="bold"
                            fill={isAlert ? "#e63946" : "#FFFFFF"}
                            textAnchor="middle"
                          >
                            {Math.round(value)}°
                          </text>

                          {/* Indicador de estado */}
                          <circle
                            cx={105 + col * 100}
                            cy={50 + row * 110}
                            r="4"
                            fill={isAlert ? "#e63946" : "#28a745"}
                          />
                        </>
                      )}

                      {/* Indicador de carga */}
                      {loading && !value && (
                        <text
                          x={70 + col * 100}
                          y={95 + row * 110}
                          fontSize="16"
                          fill="#666"
                          textAnchor="middle"
                        >
                          ...
                        </text>
                      )}

                      {/* Líneas decorativas del panel solar */}
                      <line
                        x1={35 + col * 100}
                        y1={75 + row * 110}
                        x2={105 + col * 100}
                        y2={75 + row * 110}
                        stroke="#214B4E"
                        strokeWidth="0.5"
                        opacity="0.3"
                      />
                      <line
                        x1={35 + col * 100}
                        y1={95 + row * 110}
                        x2={105 + col * 100}
                        y2={95 + row * 110}
                        stroke="#214B4E"
                        strokeWidth="0.5"
                        opacity="0.3"
                      />
                    </g>
                  );
                })
              )}
            </svg>

            {/* Info del sensor seleccionado */}
            {selectedSensor !== null && (
              <div className="sensor-detail">
                <h3>Información del Sensor</h3>
                <p>
                  <strong>Sensor:</strong> {getSensorIdForPosition(selectedSensor)}
                </p>
                <p>
                  <strong>Posición:</strong> Fila {Math.floor(selectedSensor / 3) + 1},
                  Columna {(selectedSensor % 3) + 1}
                </p>
                <p>
                  <strong>Temperatura:</strong>{" "}
                  {getTemperatureForPosition(selectedSensor) !== undefined
                    ? `${Math.round(getTemperatureForPosition(selectedSensor)!)}°C`
                    : "Sin datos"}
                </p>
                <p>
                  <strong>Estado:</strong>{" "}
                  {getTemperatureForPosition(selectedSensor) !== undefined &&
                  getTemperatureForPosition(selectedSensor)! < 25
                    ? "⚠️ En alerta (baja temperatura)"
                    : "✅ Normal"}
                </p>
                {loading && <p className="loading-text">🔄 Actualizando datos...</p>}
              </div>
            )}
          </div>
        </div>

        {/* Información lateral reorganizada */}
        <div className="info-sidebar">
          {/* Variables ambientales */}
          <div className="environmental-section">
            <h3 className="info-section-title">
              Condiciones Ambientales {loading && "🔄"}
            </h3>
            <div className="environmental-grid">
              <div className="env-card">
                <div className="env-icon">
                  <Sun size={20} color="#f39c12" />
                </div>
                <div className="env-content">
                  <div className="env-value">
                    {environmentalData.irradiance.toFixed(1)}
                  </div>
                  <div className="env-unit">W/m²</div>
                  <div className="env-label">Irradiancia</div>
                </div>
              </div>

              <div className="env-card">
                <div className="env-icon">
                  <Wind size={20} color="#3498db" />
                </div>
                <div className="env-content">
                  <div className="env-value">
                    {environmentalData.windSpeed.toFixed(1)}
                  </div>
                  <div className="env-unit">m/s</div>
                  <div className="env-label">Velocidad Viento</div>
                </div>
              </div>

              <div className="env-card">
                <div className="env-icon">
                  <Thermometer size={20} color="#e74c3c" />
                </div>
                <div className="env-content">
                  <div className="env-value">
                    {environmentalData.ambientTemp.toFixed(1)}
                  </div>
                  <div className="env-unit">°C</div>
                  <div className="env-label">Temperatura Ambiente</div>
                </div>
              </div>

              <div className="env-card">
                <div className="env-icon">
                  <Droplets size={20} color="#2ecc71" />
                </div>
                <div className="env-content">
                  <div className="env-value">{environmentalData.humidity}</div>
                  <div className="env-unit">%</div>
                  <div className="env-label">Humedad</div>
                </div>
              </div>
            </div>
          </div>

          {/* Análisis de rendimiento compacto 
          <div className="performance-section">
            <h3 className="info-section-title">Análisis de Rendimiento</h3>
            <div className="performance-grid">
              <div className="performance-item">
                <span className="performance-label">Eficiencia del Sistema:</span>
                <span className="performance-value">
                  {refrigerated ? "95%" : "78%"}
                </span>
              </div>
              <div className="performance-item">
                <span className="performance-label">Estado Operativo:</span>
                <span
                  className={`performance-value ${
                    faults === 0 ? "status-ok-text" : "status-alert-text"
                  }`}
                >
                  {faults === 0 ? "Óptimo" : "Requiere Atención"}
                </span>
              </div>
              <div className="performance-item">
                <span className="performance-label">Tiempo de Operación:</span>
                <span className="performance-value">8h 24min</span>
              </div>
              <div className="performance-item">
                <span className="performance-label">Última Actualización:</span>
                <span className="performance-value">Hace 2 minutos</span>
              </div>
            </div>
          </div> */}
        </div>
      </div>
    </div>
  );
}
