import {
  ArrowLeft,
  Thermometer,
  BarChart3,
  TrendingUp,
  Activity,
  AlertTriangle,
} from "lucide-react";
import { Line, Bar, Scatter } from "react-chartjs-2";
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
import PDFExportButton from "../views/PDFExportButton";

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
  sensor_name: string;
  facade_type: string;
  avg_value: number;
  min_value: number;
  max_value: number;
  count: number;
}

export default function ComparisonChart({ onBack }: ComparisonChartProps) {
  const [refrigeradaStats, setRefrigeradaStats] = useState<SensorStats[]>([]);
  const [noRefrigeradaStats, setNoRefrigeradaStats] = useState<SensorStats[]>([]);
  const [loading, setLoading] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<string>("");
  const isMountedRef = useRef(true);

  const fetchComparisonData = useCallback(async () => {
    if (!isMountedRef.current) return;

    setLoading(true);
    try {
      console.log(
        `📊 [${new Date().toLocaleTimeString()}] Fetching comparison data from both facades...`
      );

      const url1 = `http://34.135.241.88:8000/analytics/compare/1`;
      const url2 = `http://34.135.241.88:8000/analytics/compare/2`;
      console.log(`🔍 Fetching from: ${url1} and ${url2}`);

      const [response1, response2] = await Promise.all([
        fetch(url1),
        fetch(url2)
      ]);

      if (!response1.ok) {
        throw new Error(`HTTP ${response1.status} from facade 1: ${response1.statusText}`);
      }
      if (!response2.ok) {
        throw new Error(`HTTP ${response2.status} from facade 2: ${response2.statusText}`);
      }

      const [data1, data2] = await Promise.all([
        response1.json(),
        response2.json()
      ]);
      console.log(`Facade 1 API response:`, data1);
      console.log(`Facade 2 API response:`, data2);

      const noRefrigeradaData = data1.comparison?.no_refrigerada || [];
      const refrigeradaData = data2.comparison?.refrigerada || [];

      const tempRefrigerada = refrigeradaData.filter((s: SensorStats) => 
        s.sensor_name.startsWith('Temperature_M')
      );
      const tempNoRefrigerada = noRefrigeradaData.filter((s: SensorStats) => 
        s.sensor_name.startsWith('Temperature_M')
      );

      console.log(
        `Processed data - Refrigerada: ${tempRefrigerada.length} sensors, No Refrigerada: ${tempNoRefrigerada.length} sensors`
      );

      if (isMountedRef.current) {
        setRefrigeradaStats(tempRefrigerada);
        setNoRefrigeradaStats(tempNoRefrigerada);
        setLastUpdate(new Date().toLocaleString());
      }
    } catch (error) {
      console.error("Error fetching comparison data:", error);
    } finally {
      if (isMountedRef.current) {
        setLoading(false);
      }
    }
  }, []);

  useEffect(() => {
    console.log(`Component mounted - Loading comparison data`);
    isMountedRef.current = true;
    fetchComparisonData();

    return () => {
      isMountedRef.current = false;
    };
  }, [fetchComparisonData]);

  useEffect(() => {
    console.log(`🔄 Stats updated - Refrigerada: ${refrigeradaStats.length}, No Refrigerada: ${noRefrigeradaStats.length}`);
    if (refrigeradaStats.length > 0 || noRefrigeradaStats.length > 0) {
      console.log(`Refrigerada sensors:`, refrigeradaStats.map(s => s.sensor_name));
      console.log(`No Refrigerada sensors:`, noRefrigeradaStats.map(s => s.sensor_name));
    }
  }, [refrigeradaStats, noRefrigeradaStats]);

  const allSensors = [...refrigeradaStats, ...noRefrigeradaStats];

  const getModuleData = () => {
    const modules = ["M1", "M2", "M3", "M4", "M5"];
    
    return modules.map(moduleName => {
      const refSensors = refrigeradaStats.filter(s => s.sensor_name.includes(`_${moduleName}_`));
      const noRefSensors = noRefrigeradaStats.filter(s => s.sensor_name.includes(`_${moduleName}_`));
      
      return {
        name: moduleName,
        mean_ref: refSensors.length > 0
          ? refSensors.reduce((sum, s) => sum + s.avg_value, 0) / refSensors.length
          : 0,
        mean_noref: noRefSensors.length > 0
          ? noRefSensors.reduce((sum, s) => sum + s.avg_value, 0) / noRefSensors.length
          : 0,
        max_ref: refSensors.length > 0 ? Math.max(...refSensors.map(s => s.max_value)) : 0,
        max_noref: noRefSensors.length > 0 ? Math.max(...noRefSensors.map(s => s.max_value)) : 0,
        min_ref: refSensors.length > 0 ? Math.min(...refSensors.map(s => s.min_value)) : 0,
        min_noref: noRefSensors.length > 0 ? Math.min(...noRefSensors.map(s => s.min_value)) : 0,
        count_ref: refSensors.reduce((sum, s) => sum + s.count, 0),
        count_noref: noRefSensors.reduce((sum, s) => sum + s.count, 0),
      };
    });
  };

  const moduleData = getModuleData();
  
  const overallStats = allSensors.length > 0
    ? {
        meanTemp_ref: refrigeradaStats.length > 0
          ? refrigeradaStats.reduce((sum, s) => sum + s.avg_value, 0) / refrigeradaStats.length
          : 0,
        meanTemp_noref: noRefrigeradaStats.length > 0
          ? noRefrigeradaStats.reduce((sum, s) => sum + s.avg_value, 0) / noRefrigeradaStats.length
          : 0,
        maxTemp_ref: refrigeradaStats.length > 0 ? Math.max(...refrigeradaStats.map(s => s.max_value)) : 0,
        maxTemp_noref: noRefrigeradaStats.length > 0 ? Math.max(...noRefrigeradaStats.map(s => s.max_value)) : 0,
        minTemp_ref: refrigeradaStats.length > 0 ? Math.min(...refrigeradaStats.map(s => s.min_value)) : 0,
        minTemp_noref: noRefrigeradaStats.length > 0 ? Math.min(...noRefrigeradaStats.map(s => s.min_value)) : 0,
        totalReadings_ref: refrigeradaStats.reduce((sum, s) => sum + s.count, 0),
        totalReadings_noref: noRefrigeradaStats.reduce((sum, s) => sum + s.count, 0),
        timestamp: lastUpdate,
      }
    : null;

  const lineChartData = {
    labels: moduleData.map(m => `Módulo ${m.name}`),
    datasets: [
      {
        label: "Refrigerada - Promedio",
        data: moduleData.map(m => m.mean_ref),
        borderColor: "#2196f3",
        backgroundColor: "rgba(33, 150, 243, 0.1)",
        fill: true,
        tension: 0.4,
        pointRadius: 6,
        pointBackgroundColor: "#2196f3",
        pointBorderWidth: 3,
        pointBorderColor: "#fff",
        pointHoverRadius: 8,
      },
      {
        label: "No Refrigerada - Promedio",
        data: moduleData.map(m => m.mean_noref),
        borderColor: "#e63946",
        backgroundColor: "rgba(230, 57, 70, 0.1)",
        fill: true,
        tension: 0.4,
        pointRadius: 6,
        pointBackgroundColor: "#e63946",
        pointBorderWidth: 3,
        pointBorderColor: "#fff",
        pointHoverRadius: 8,
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
        text: "Comparación Térmica: Refrigerada vs No Refrigerada",
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

  const barChartData = {
    labels: moduleData.map(m => `Módulo ${m.name}`),
    datasets: [
      {
        label: "Diferencia de Temperatura (No Ref - Ref)",
        data: moduleData.map(m => m.mean_noref - m.mean_ref),
        backgroundColor: moduleData.map(m => 
          (m.mean_noref - m.mean_ref) > 3 ? "#e63946" : 
          (m.mean_noref - m.mean_ref) > 1 ? "#ff9800" : "#4caf50"
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
        text: "Diferencia Térmica por Módulo (°C)",
        font: { size: 18, weight: "bold" as const },
        padding: { bottom: 30 },
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: "Diferencia de Temperatura (°C)",
          font: { size: 14, weight: "bold" as const },
        },
      },
    },
  };

  const scatterData = {
    datasets: [
      {
        label: "Refrigerada",
        data: refrigeradaStats.map(sensor => ({
          x: sensor.avg_value,
          y: sensor.max_value - sensor.min_value,
          sensorId: sensor.sensor_name,
        })),
        backgroundColor: "#2196f3",
        borderColor: "#1976d2",
        borderWidth: 2,
        pointRadius: 8,
        pointHoverRadius: 12,
      },
      {
        label: "No Refrigerada",
        data: noRefrigeradaStats.map(sensor => ({
          x: sensor.avg_value,
          y: sensor.max_value - sensor.min_value,
          sensorId: sensor.sensor_name,
        })),
        backgroundColor: "#e63946",
        borderColor: "#c62828",
        borderWidth: 2,
        pointRadius: 8,
        pointHoverRadius: 12,
      },
    ],
  };

  const scatterOptions = {
    responsive: true,
    plugins: {
      legend: { display: true, position: "top" as const },
      title: {
        display: true,
        text: "Dispersión: Temperatura Media vs Rango Térmico",
        font: { size: 18, weight: "bold" as const },
        padding: { bottom: 30 },
      },
      tooltip: {
        callbacks: {
          label: function (context: any) {
            return `${context.raw.sensorId}: ${context.parsed.x.toFixed(1)}°C, Rango=${context.parsed.y.toFixed(1)}°C`;
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
          text: "Rango Térmico (Max - Min, °C)",
          font: { size: 14, weight: "bold" as const },
        },
      },
    },
  };

  return (
    <div style={{ padding: "2rem", backgroundColor: "#f8f9fa", minHeight: "100vh" }}>
      {/* Header - MODIFICADO */}
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
            onClick={fetchComparisonData}
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

          {/* NUEVO: Botón PDF */}
          {!loading && allSensors.length > 0 && (
            <PDFExportButton
              title="Comparación Térmica: Refrigerada vs No Refrigerada"
              elementId="comparison-chart-pdf-content"
              filename="comparacion-termica-fachadas"
            />
          )}
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
            Comparación Térmica: Refrigerada vs No Refrigerada
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
            Sensores cargados: Ref={refrigeradaStats.length} | No Ref={noRefrigeradaStats.length}
            {loading && " | CARGANDO..."}
          </p>
        </div>
      </div>

      {/* CONTENIDO EXPORTABLE - AGREGAR DIV CON ID */}
      <div id="comparison-chart-pdf-content">
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
                  TEMP. PROM. REFRIGERADA
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
                {overallStats.meanTemp_ref.toFixed(1)}°C
              </p>
            </div>

            <div
              key={`temp-noref-${lastUpdate}`}
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
                <BarChart3 size={24} color="#e63946" />
                <h3
                  style={{
                    margin: 0,
                    fontSize: "14px",
                    color: "#6c757d",
                    fontWeight: "600",
                  }}
                >
                  TEMP. PROM. NO REFRIGERADA
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
                {overallStats.meanTemp_noref.toFixed(1)}°C
              </p>
            </div>

            <div
              key={`temp-diff-${lastUpdate}`}
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
                <TrendingUp size={24} color="#28a745" />
                <h3
                  style={{
                    margin: 0,
                    fontSize: "14px",
                    color: "#6c757d",
                    fontWeight: "600",
                  }}
                >
                  DIFERENCIA TÉRMICA
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
                {(overallStats.meanTemp_noref - overallStats.meanTemp_ref).toFixed(1)}°C
              </p>
            </div>

            <div
              key={`readings-ref-${lastUpdate}`}
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
                  LECTURAS REFRIGERADA
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
                {overallStats.totalReadings_ref.toLocaleString()}
              </p>
            </div>

            <div
              key={`readings-noref-${lastUpdate}`}
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
                <AlertTriangle size={24} color="#e63946" />
                <h3
                  style={{
                    margin: 0,
                    fontSize: "14px",
                    color: "#6c757d",
                    fontWeight: "600",
                  }}
                >
                  LECTURAS NO REFRIGERADA
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
                {overallStats.totalReadings_noref.toLocaleString()}
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
        {allSensors.length > 0 && (
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
              Datos Detallados de Comparación
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
                      Tipo Fachada
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
                      Temp. Media
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
                  </tr>
                </thead>
                <tbody key={`tbody-${lastUpdate}`}>
                  {allSensors.map((sensor, index) => (
                    <tr
                      key={`${sensor.sensor_name}-${sensor.facade_type}-${index}`}
                      style={{
                        backgroundColor: index % 2 === 0 ? "#fff" : "#f8f9fa",
                        borderBottom: "1px solid #dee2e6",
                      }}
                    >
                      <td
                        style={{ padding: "12px", fontWeight: "600", color: "#214B4E" }}
                      >
                        {sensor.sensor_name.replace("Temperature_", "")}
                      </td>
                      <td style={{ padding: "12px", textAlign: "center" }}>
                        <span
                          style={{
                            padding: "4px 12px",
                            borderRadius: "12px",
                            backgroundColor: sensor.facade_type === "refrigerada" ? "#e3f2fd" : "#ffebee",
                            color: sensor.facade_type === "refrigerada" ? "#2196f3" : "#e63946",
                            fontWeight: "600",
                            fontSize: "12px",
                          }}
                        >
                          {sensor.facade_type === "refrigerada" ? "REF" : "NO REF"}
                        </span>
                      </td>
                      <td style={{ padding: "12px", textAlign: "center" }}>
                        {sensor.count.toLocaleString()}
                      </td>
                      <td
                        style={{
                          padding: "12px",
                          textAlign: "center",
                          fontWeight: "600",
                        }}
                      >
                        {sensor.avg_value.toFixed(1)}°C
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
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
      {/* FIN DEL CONTENIDO EXPORTABLE */}

      {/* Estado de carga - FUERA del contenido PDF */}
      {loading && allSensors.length === 0 && (
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
            Cargando datos de comparación térmica...
          </h3>
          <p style={{ color: "#6c757d", margin: "0.5rem 0 0 0" }}>
            Obteniendo datos de ambas fachadas
          </p>
        </div>
      )}
    </div>
  );
}