import {
  ArrowLeft,
  Thermometer,
  BarChart3,
  TrendingUp,
  Activity,
  Target,
  AlertTriangle,
} from "lucide-react";
import { Line, Bar, Doughnut, Scatter } from "react-chartjs-2";
import { useState, useEffect, useRef, useCallback } from "react";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from "chart.js";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

type ComparisonChartProps = {
  onBack: () => void;
  id?: string;
};

interface SensorStats {
  sensor_id: string;
  total_readings: number;
  mean_value: number;
  std_dev: number;
  min_value: number;
  max_value: number;
  q25: number;
  median: number;
  q75: number;
  first_reading: string;
  last_reading: string;
}

export default function ComparisonChart({ onBack, id = "1" }: ComparisonChartProps) {
  const [sensorsStats, setSensorsStats] = useState<SensorStats[]>([]);
  const [loading, setLoading] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<string>("");
  const isMountedRef = useRef(true);

  // Lista de sensores de temperatura para consultar
  const temperatureSensors = [
    "Temperatura_L1_1",
    "Temperatura_L1_2",
    "Temperatura_L1_3",
    "Temperatura_L2_1",
    "Temperatura_L2_2",
    "Temperatura_L2_3",
    "Temperatura_L3_1",
    "Temperatura_L3_2",
    "Temperatura_L3_3",
    "Temperatura_L4_1",
    "Temperatura_L4_2",
    "Temperatura_L4_3",
    "Temperatura_L5_1",
    "Temperatura_L5_2",
    "Temperatura_L5_3",
  ];

  // Función para obtener estadísticas de todos los sensores
  const fetchAllSensorsStats = useCallback(async () => {
    if (!isMountedRef.current) return;

    setLoading(true);
    try {
      console.log(
        `📊 [${new Date().toLocaleTimeString()}] Fetching stats for ${temperatureSensors.length} sensors for facade ${id}...`
      );

      const promises = temperatureSensors.map(async sensorId => {
        try {
          const url = `http://127.0.0.1:8000/api/analytics/stats/${sensorId}/${id}?hours=24`;
          console.log(`🔍 Fetching: ${url}`);

          const response = await fetch(url);

          if (!response.ok) {
            console.warn(
              `⚠️ Failed to fetch stats for ${sensorId}: ${response.status} ${response.statusText}`
            );
            return null;
          }

          const data = await response.json();
          console.log(
            `✅ ${sensorId}: ${data.total_readings} readings, mean: ${data.mean_value?.toFixed(1)}°C`
          );

          return {
            sensor_id: sensorId,
            ...data,
          };
        } catch (error) {
          console.error(`💥 Error fetching ${sensorId}:`, error);
          return null;
        }
      });

      const results = await Promise.all(promises);
      const validResults = results.filter(result => result !== null) as SensorStats[];

      console.log(
        `✅ [${new Date().toLocaleTimeString()}] Successfully fetched stats for ${validResults.length}/${temperatureSensors.length} sensors`
      );

      if (validResults.length > 0 && isMountedRef.current) {
        console.log(`📊 Sample data:`, validResults[0]);
        console.log(
          `🔄 Updating state with ${validResults.length} sensors at ${new Date().toLocaleTimeString()}`
        );

        setSensorsStats(validResults);
        setLastUpdate(new Date().toLocaleString());
      } else {
        console.error(`❌ No valid sensor data received!`);
      }
    } catch (error) {
      console.error("💥 Error fetching sensors stats:", error);
    } finally {
      if (isMountedRef.current) {
        setLoading(false);
      }
    }
  }, [id]);

  // Cargar datos una sola vez al montar el componente
  useEffect(() => {
    console.log(`🚀 Component mounted - Loading data for facade ${id}`);
    isMountedRef.current = true;
    fetchAllSensorsStats();

    return () => {
      isMountedRef.current = false;
    };
  }, [fetchAllSensorsStats]);

  // Debug - observar cambios en sensorsStats
  useEffect(() => {
    console.log(`🔄 sensorsStats state updated - Count: ${sensorsStats.length}`);
    if (sensorsStats.length > 0) {
      console.log(
        `📋 Current sensors:`,
        sensorsStats.map(s => s.sensor_id)
      );
      console.log(
        `🌡️ Average temperature: ${(sensorsStats.reduce((sum, s) => sum + s.mean_value, 0) / sensorsStats.length).toFixed(1)}°C`
      );
    }
  }, [sensorsStats]);

  // Preparar datos para gráficas
  const getModuleData = () => {
    const modules = [
      { name: "L1", sensors: sensorsStats.filter(s => s.sensor_id.includes("L1_")) },
      { name: "L2", sensors: sensorsStats.filter(s => s.sensor_id.includes("L2_")) },
      { name: "L3", sensors: sensorsStats.filter(s => s.sensor_id.includes("L3_")) },
      { name: "L4", sensors: sensorsStats.filter(s => s.sensor_id.includes("L4_")) },
      { name: "L5", sensors: sensorsStats.filter(s => s.sensor_id.includes("L5_")) },
    ];

    return modules.map(module => ({
      name: module.name,
      mean:
        module.sensors.length > 0
          ? module.sensors.reduce((sum, s) => sum + s.mean_value, 0) /
            module.sensors.length
          : 0,
      max:
        module.sensors.length > 0
          ? Math.max(...module.sensors.map(s => s.max_value))
          : 0,
      min:
        module.sensors.length > 0
          ? Math.min(...module.sensors.map(s => s.min_value))
          : 0,
      std_dev:
        module.sensors.length > 0
          ? module.sensors.reduce((sum, s) => sum + s.std_dev, 0) /
            module.sensors.length
          : 0,
      readings: module.sensors.reduce((sum, s) => sum + s.total_readings, 0),
    }));
  };

  const moduleData = getModuleData();
  const overallStats =
    sensorsStats.length > 0
      ? {
          meanTemp:
            sensorsStats.reduce((sum, s) => sum + s.mean_value, 0) /
            sensorsStats.length,
          maxTemp: Math.max(...sensorsStats.map(s => s.max_value)),
          minTemp: Math.min(...sensorsStats.map(s => s.min_value)),
          totalReadings: sensorsStats.reduce((sum, s) => sum + s.total_readings, 0),
          avgStdDev:
            sensorsStats.reduce((sum, s) => sum + s.std_dev, 0) / sensorsStats.length,
          timestamp: lastUpdate, // Agregar timestamp para forzar updates
        }
      : null;

  // Gráfica de líneas - Temperatura promedio por módulo
  const lineChartData = {
    labels: moduleData.map(m => `Módulo ${m.name}`),
    datasets: [
      {
        label: "Temperatura Promedio",
        data: moduleData.map(m => m.mean),
        borderColor: "#214B4E",
        backgroundColor: "rgba(33, 75, 78, 0.1)",
        fill: true,
        tension: 0.4,
        pointRadius: 6,
        pointBackgroundColor: "#214B4E",
        pointBorderWidth: 3,
        pointBorderColor: "#fff",
        pointHoverRadius: 8,
      },
      {
        label: "Temperatura Máxima",
        data: moduleData.map(m => m.max),
        borderColor: "#e63946",
        backgroundColor: "rgba(230, 57, 70, 0.1)",
        fill: false,
        tension: 0.4,
        pointRadius: 4,
        pointBackgroundColor: "#e63946",
        borderDash: [5, 5],
      },
      {
        label: "Temperatura Mínima",
        data: moduleData.map(m => m.min),
        borderColor: "#2196f3",
        backgroundColor: "rgba(33, 150, 243, 0.1)",
        fill: false,
        tension: 0.4,
        pointRadius: 4,
        pointBackgroundColor: "#2196f3",
        borderDash: [5, 5],
      },
    ],
  };

  const lineChartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: "top" as const,
        labels: { usePointStyle: true, padding: 20 },
      },
      title: {
        display: true,
        text: "Análisis Térmico por Módulo - Panel Refrigerado",
        font: { size: 18, weight: "bold" as const },
        padding: { bottom: 30 },
      },
    },
    scales: {
      y: {
        beginAtZero: false,
        title: {
          display: true,
          text: "Temperatura (°C)",
          font: { size: 14, weight: "bold" as const },
        },
        grid: { color: "rgba(0,0,0,0.1)" },
      },
      x: {
        title: {
          display: true,
          text: "Módulos del Panel Solar",
          font: { size: 14, weight: "bold" as const },
        },
        grid: { display: false },
      },
    },
  };

  // Gráfica de barras - Desviación estándar
  const barChartData = {
    labels: moduleData.map(m => `Módulo ${m.name}`),
    datasets: [
      {
        label: "Desviación Estándar (°C)",
        data: moduleData.map(m => m.std_dev),
        backgroundColor: moduleData.map(m =>
          m.std_dev > 3 ? "#e63946" : m.std_dev > 2 ? "#ff9800" : "#4caf50"
        ),
        borderColor: "#214B4E",
        borderWidth: 2,
        borderRadius: 8,
        borderSkipped: false,
      },
    ],
  };

  const barChartOptions = {
    responsive: true,
    plugins: {
      legend: { display: false },
      title: {
        display: true,
        text: "Variabilidad Térmica por Módulo",
        font: { size: 18, weight: "bold" as const },
        padding: { bottom: 30 },
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: "Desviación Estándar (°C)",
          font: { size: 14, weight: "bold" as const },
        },
      },
    },
  };

  // Scatter plot - Distribución de sensores
  const scatterData = {
    datasets: [
      {
        label: "Sensores de Temperatura",
        data: sensorsStats.map(sensor => ({
          x: sensor.mean_value,
          y: sensor.std_dev,
          sensorId: sensor.sensor_id,
        })),
        backgroundColor: sensorsStats.map(sensor =>
          sensor.std_dev > 3 ? "#e63946" : sensor.std_dev > 2 ? "#ff9800" : "#4caf50"
        ),
        borderColor: "#214B4E",
        borderWidth: 2,
        pointRadius: 8,
        pointHoverRadius: 12,
      },
    ],
  };

  const scatterOptions = {
    responsive: true,
    plugins: {
      legend: { display: false },
      title: {
        display: true,
        text: "Dispersión: Temperatura Media vs Variabilidad",
        font: { size: 18, weight: "bold" as const },
        padding: { bottom: 30 },
      },
      tooltip: {
        callbacks: {
          label: function (context: any) {
            return `${context.raw.sensorId}: ${context.parsed.x.toFixed(1)}°C, σ=${context.parsed.y.toFixed(2)}`;
          },
        },
      },
    },
    scales: {
      x: {
        title: {
          display: true,
          text: "Temperatura Media (°C)",
          font: { size: 14, weight: "bold" as const },
        },
      },
      y: {
        title: {
          display: true,
          text: "Desviación Estándar (°C)",
          font: { size: 14, weight: "bold" as const },
        },
      },
    },
  };

  return (
    <div style={{ padding: "2rem", backgroundColor: "#f8f9fa", minHeight: "100vh" }}>
      {/* Header */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "2rem",
        }}
      >
        <div style={{ display: "flex", gap: "1rem" }}>
          <button
            onClick={onBack}
            style={{
              backgroundColor: "#214B4E",
              color: "white",
              padding: "0.75rem 1.5rem",
              borderRadius: "8px",
              border: "none",
              cursor: "pointer",
              fontWeight: "600",
              display: "flex",
              alignItems: "center",
              gap: "0.5rem",
              fontSize: "14px",
            }}
          >
            <ArrowLeft size={20} /> Volver al Dashboard
          </button>

          <button
            onClick={fetchAllSensorsStats}
            disabled={loading}
            style={{
              backgroundColor: loading ? "#6c757d" : "#28a745",
              color: "white",
              padding: "0.75rem 1.5rem",
              borderRadius: "8px",
              border: "none",
              cursor: loading ? "not-allowed" : "pointer",
              fontWeight: "600",
              display: "flex",
              alignItems: "center",
              gap: "0.5rem",
              fontSize: "14px",
            }}
          >
            {loading ? "🔄 Cargando..." : "🔄 Actualizar Datos"}
          </button>
        </div>

        <div style={{ textAlign: "right" }}>
          <h1
            style={{
              fontSize: "2rem",
              fontWeight: "bold",
              margin: "0",
              color: "#2c3e50",
              display: "flex",
              alignItems: "center",
              gap: "0.75rem",
            }}
          >
            <Thermometer size={32} color="#214B4E" />
            Análisis Térmico Avanzado - Panel Refrigerado
          </h1>
          {lastUpdate && (
            <p style={{ margin: "0.5rem 0 0 0", color: "#6c757d", fontSize: "14px" }}>
              Datos cargados: {lastUpdate} {loading && "🔄"}
            </p>
          )}
          <p
            style={{
              margin: "0.25rem 0 0 0",
              color: loading ? "#28a745" : "#6c757d",
              fontSize: "12px",
              fontWeight: loading ? "600" : "normal",
            }}
          >
            Sensores cargados: {sensorsStats.length}/15 | Fachada: {id}
            {loading && " | CARGANDO..."}
          </p>
        </div>
      </div>

      {/* Cards de métricas principales */}
      {overallStats && (
        <div
          key={`metrics-${lastUpdate}`}
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
            gap: "1.5rem",
            marginBottom: "2rem",
          }}
        >
          <div
            key={`temp-avg-${lastUpdate}`}
            style={{
              backgroundColor: "white",
              padding: "1.5rem",
              borderRadius: "12px",
              boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
              border: "1px solid #e9ecef",
            }}
          >
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: "0.75rem",
                marginBottom: "0.5rem",
              }}
            >
              <BarChart3 size={24} color="#214B4E" />
              <h3
                style={{
                  margin: 0,
                  fontSize: "14px",
                  color: "#6c757d",
                  fontWeight: "600",
                }}
              >
                TEMP. PROMEDIO
              </h3>
            </div>
            <p
              style={{
                margin: 0,
                fontSize: "2rem",
                fontWeight: "bold",
                color: "#214B4E",
              }}
            >
              {overallStats.meanTemp.toFixed(1)}°C
            </p>
          </div>

          <div
            key={`temp-max-${lastUpdate}`}
            style={{
              backgroundColor: "white",
              padding: "1.5rem",
              borderRadius: "12px",
              boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
              border: "1px solid #e9ecef",
            }}
          >
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: "0.75rem",
                marginBottom: "0.5rem",
              }}
            >
              <TrendingUp size={24} color="#e63946" />
              <h3
                style={{
                  margin: 0,
                  fontSize: "14px",
                  color: "#6c757d",
                  fontWeight: "600",
                }}
              >
                TEMP. MÁXIMA
              </h3>
            </div>
            <p
              style={{
                margin: 0,
                fontSize: "2rem",
                fontWeight: "bold",
                color: "#e63946",
              }}
            >
              {overallStats.maxTemp.toFixed(1)}°C
            </p>
          </div>

          <div
            key={`temp-min-${lastUpdate}`}
            style={{
              backgroundColor: "white",
              padding: "1.5rem",
              borderRadius: "12px",
              boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
              border: "1px solid #e9ecef",
            }}
          >
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: "0.75rem",
                marginBottom: "0.5rem",
              }}
            >
              <Activity size={24} color="#2196f3" />
              <h3
                style={{
                  margin: 0,
                  fontSize: "14px",
                  color: "#6c757d",
                  fontWeight: "600",
                }}
              >
                TEMP. MÍNIMA
              </h3>
            </div>
            <p
              style={{
                margin: 0,
                fontSize: "2rem",
                fontWeight: "bold",
                color: "#2196f3",
              }}
            >
              {overallStats.minTemp.toFixed(1)}°C
            </p>
          </div>

          <div
            key={`variability-${lastUpdate}`}
            style={{
              backgroundColor: "white",
              padding: "1.5rem",
              borderRadius: "12px",
              boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
              border: "1px solid #e9ecef",
            }}
          >
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: "0.75rem",
                marginBottom: "0.5rem",
              }}
            >
              <Target size={24} color="#28a745" />
              <h3
                style={{
                  margin: 0,
                  fontSize: "14px",
                  color: "#6c757d",
                  fontWeight: "600",
                }}
              >
                VARIABILIDAD
              </h3>
            </div>
            <p
              style={{
                margin: 0,
                fontSize: "2rem",
                fontWeight: "bold",
                color: "#28a745",
              }}
            >
              ±{overallStats.avgStdDev.toFixed(1)}°C
            </p>
          </div>

          <div
            key={`readings-${lastUpdate}`}
            style={{
              backgroundColor: "white",
              padding: "1.5rem",
              borderRadius: "12px",
              boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
              border: "1px solid #e9ecef",
            }}
          >
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: "0.75rem",
                marginBottom: "0.5rem",
              }}
            >
              <AlertTriangle size={24} color="#ff9800" />
              <h3
                style={{
                  margin: 0,
                  fontSize: "14px",
                  color: "#6c757d",
                  fontWeight: "600",
                }}
              >
                TOTAL LECTURAS
              </h3>
            </div>
            <p
              style={{
                margin: 0,
                fontSize: "2rem",
                fontWeight: "bold",
                color: "#ff9800",
              }}
            >
              {overallStats.totalReadings.toLocaleString()}
            </p>
          </div>
        </div>
      )}

      {/* Grid de gráficas */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: "2rem",
          marginBottom: "2rem",
        }}
      >
        {/* Gráfica de líneas */}
        <div
          key={`line-chart-${lastUpdate}`}
          style={{
            backgroundColor: "white",
            padding: "2rem",
            borderRadius: "16px",
            boxShadow: "0 4px 16px rgba(0,0,0,0.08)",
            border: "1px solid #e9ecef",
          }}
        >
          <Line
            data={lineChartData}
            options={lineChartOptions}
            height={300}
            key={`line-${lastUpdate}`}
          />
        </div>

        {/* Gráfica de barras */}
        <div
          key={`bar-chart-${lastUpdate}`}
          style={{
            backgroundColor: "white",
            padding: "2rem",
            borderRadius: "16px",
            boxShadow: "0 4px 16px rgba(0,0,0,0.08)",
            border: "1px solid #e9ecef",
          }}
        >
          <Bar
            data={barChartData}
            options={barChartOptions}
            height={300}
            key={`bar-${lastUpdate}`}
          />
        </div>
      </div>

      {/* Gráfica de dispersión full width */}
      <div
        key={`scatter-chart-${lastUpdate}`}
        style={{
          backgroundColor: "white",
          padding: "2rem",
          borderRadius: "16px",
          boxShadow: "0 4px 16px rgba(0,0,0,0.08)",
          border: "1px solid #e9ecef",
          marginBottom: "2rem",
        }}
      >
        <Scatter
          data={scatterData}
          options={scatterOptions}
          height={400}
          key={`scatter-${lastUpdate}`}
        />
      </div>

      {/* Tabla de datos detallados */}
      {sensorsStats.length > 0 && (
        <div
          key={`table-container-${lastUpdate}`}
          style={{
            backgroundColor: "white",
            padding: "2rem",
            borderRadius: "16px",
            boxShadow: "0 4px 16px rgba(0,0,0,0.08)",
            border: "1px solid #e9ecef",
          }}
        >
          <h3
            style={{
              margin: "0 0 1.5rem 0",
              fontSize: "1.5rem",
              fontWeight: "bold",
              color: "#2c3e50",
            }}
          >
            Datos Detallados por Sensor (Últimas 24 horas) - Cargado: {lastUpdate}
          </h3>

          <div style={{ overflowX: "auto" }}>
            <table
              key={`sensor-table-${lastUpdate}`}
              style={{
                width: "100%",
                borderCollapse: "collapse",
                fontSize: "14px",
              }}
            >
              <thead>
                <tr style={{ backgroundColor: "#f8f9fa" }}>
                  <th
                    style={{
                      padding: "12px",
                      textAlign: "left",
                      borderBottom: "2px solid #dee2e6",
                      fontWeight: "600",
                    }}
                  >
                    Sensor
                  </th>
                  <th
                    style={{
                      padding: "12px",
                      textAlign: "center",
                      borderBottom: "2px solid #dee2e6",
                      fontWeight: "600",
                    }}
                  >
                    Lecturas
                  </th>
                  <th
                    style={{
                      padding: "12px",
                      textAlign: "center",
                      borderBottom: "2px solid #dee2e6",
                      fontWeight: "600",
                    }}
                  >
                    Media
                  </th>
                  <th
                    style={{
                      padding: "12px",
                      textAlign: "center",
                      borderBottom: "2px solid #dee2e6",
                      fontWeight: "600",
                    }}
                  >
                    Mediana
                  </th>
                  <th
                    style={{
                      padding: "12px",
                      textAlign: "center",
                      borderBottom: "2px solid #dee2e6",
                      fontWeight: "600",
                    }}
                  >
                    Desv. Std
                  </th>
                  <th
                    style={{
                      padding: "12px",
                      textAlign: "center",
                      borderBottom: "2px solid #dee2e6",
                      fontWeight: "600",
                    }}
                  >
                    Min / Max
                  </th>
                  <th
                    style={{
                      padding: "12px",
                      textAlign: "center",
                      borderBottom: "2px solid #dee2e6",
                      fontWeight: "600",
                    }}
                  >
                    Q25 / Q75
                  </th>
                </tr>
              </thead>
              <tbody key={`tbody-${lastUpdate}`}>
                {sensorsStats.map((sensor, index) => (
                  <tr
                    key={`${sensor.sensor_id}-${lastUpdate}-${index}`}
                    style={{
                      backgroundColor: index % 2 === 0 ? "#fff" : "#f8f9fa",
                      borderBottom: "1px solid #dee2e6",
                    }}
                  >
                    <td
                      style={{ padding: "12px", fontWeight: "600", color: "#214B4E" }}
                    >
                      {sensor.sensor_id.replace("Temperatura_", "")}
                    </td>
                    <td style={{ padding: "12px", textAlign: "center" }}>
                      {sensor.total_readings.toLocaleString()}
                    </td>
                    <td
                      style={{
                        padding: "12px",
                        textAlign: "center",
                        fontWeight: "600",
                      }}
                    >
                      {sensor.mean_value.toFixed(1)}°C
                    </td>
                    <td style={{ padding: "12px", textAlign: "center" }}>
                      {sensor.median.toFixed(1)}°C
                    </td>
                    <td
                      style={{
                        padding: "12px",
                        textAlign: "center",
                        color:
                          sensor.std_dev > 3
                            ? "#e63946"
                            : sensor.std_dev > 2
                              ? "#ff9800"
                              : "#28a745",
                        fontWeight: "600",
                      }}
                    >
                      ±{sensor.std_dev.toFixed(2)}
                    </td>
                    <td style={{ padding: "12px", textAlign: "center" }}>
                      <span style={{ color: "#2196f3" }}>
                        {sensor.min_value.toFixed(1)}
                      </span>
                      {" / "}
                      <span style={{ color: "#e63946" }}>
                        {sensor.max_value.toFixed(1)}
                      </span>
                    </td>
                    <td style={{ padding: "12px", textAlign: "center" }}>
                      <span style={{ color: "#6c757d" }}>{sensor.q25.toFixed(1)}</span>
                      {" / "}
                      <span style={{ color: "#6c757d" }}>{sensor.q75.toFixed(1)}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Estado de carga */}
      {loading && sensorsStats.length === 0 && (
        <div
          style={{
            backgroundColor: "white",
            padding: "4rem",
            borderRadius: "16px",
            textAlign: "center",
            boxShadow: "0 4px 16px rgba(0,0,0,0.08)",
          }}
        >
          <div style={{ fontSize: "3rem", marginBottom: "1rem" }}>🔄</div>
          <h3 style={{ color: "#6c757d", margin: 0 }}>
            Cargando datos de análisis térmico...
          </h3>
          <p style={{ color: "#6c757d", margin: "0.5rem 0 0 0" }}>
            Obteniendo estadísticas de {temperatureSensors.length} sensores
          </p>
        </div>
      )}
    </div>
  );
}
