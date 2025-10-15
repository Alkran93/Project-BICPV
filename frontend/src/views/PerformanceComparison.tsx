import { useEffect, useState, useRef } from "react";
import { Line, Bar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from "chart.js";
import { TrendingUp, Filter, RefreshCw } from "lucide-react";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

interface ComparisonRecord {
  sensor_name: string;
  refrigerada_avg: number;
  no_refrigerada_avg: number;
  difference: number;
  refrigerada_count: number;
  no_refrigerada_count: number;
}

interface ComparisonResponse {
  facade_id: string;
  sensor_filter: string | null;
  comparison: ComparisonRecord[];
}

export default function PerformanceComparison({ facadeId = "1" }: { facadeId?: string }) {
  const [responseData, setResponseData] = useState<ComparisonResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<string>("");
  const isMountedRef = useRef(true);

  // Filtros
  const [sensorFilter, setSensorFilter] = useState<string>("");

  const fetchComparisonData = async () => {
    if (!isMountedRef.current) return;

    setLoading(true);
    setError(null);

    try {
      const params = new URLSearchParams();
      if (sensorFilter) params.append("sensor_name", sensorFilter);

      const url = `http://localhost:8000/analytics/compare/${facadeId}?${params.toString()}`;
      console.log(`📊 [${new Date().toLocaleTimeString()}] Fetching comparison from: ${url}`);

      const response = await fetch(url);

      if (!response.ok) {
        if (response.status === 404) {
          throw new Error("No hay datos de comparación disponibles para esta fachada");
        }
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data: ComparisonResponse = await response.json();
      console.log("📊 Comparison API response:", data);

      if (isMountedRef.current) {
        setResponseData(data);
        setLastUpdate(new Date().toLocaleString());
        console.log(`✅ Successfully loaded ${data.comparison.length} comparison records`);
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Unknown error";
      console.error("💥 Error fetching comparison data:", err);

      if (isMountedRef.current) {
        setError(errorMessage);
        setResponseData(null);
      }
    } finally {
      if (isMountedRef.current) {
        setLoading(false);
      }
    }
  };

  useEffect(() => {
    console.log("🔄 PerformanceComparison mounted");
    isMountedRef.current = true;
    fetchComparisonData();

    return () => {
      isMountedRef.current = false;
    };
  }, [facadeId]);

  useEffect(() => {
    if (isMountedRef.current) {
      fetchComparisonData();
    }
  }, [sensorFilter]);

  const comparisonData = responseData?.comparison || [];

  // Preparar datos para gráfica de líneas
  const lineChartData = {
    labels: comparisonData.map((record) => record.sensor_name.replace("Temperature_", "")),
    datasets: [
      {
        label: "Con Refrigeración (°C)",
        data: comparisonData.map((record) => record.refrigerada_avg),
        borderColor: "rgb(33, 150, 243)",
        backgroundColor: "rgba(33, 150, 243, 0.1)",
        tension: 0.4,
        fill: true,
        pointRadius: 6,
        pointBackgroundColor: "rgb(33, 150, 243)",
        pointBorderWidth: 2,
        pointBorderColor: "#fff",
      },
      {
        label: "Sin Refrigeración (°C)",
        data: comparisonData.map((record) => record.no_refrigerada_avg),
        borderColor: "rgb(230, 57, 70)",
        backgroundColor: "rgba(230, 57, 70, 0.1)",
        tension: 0.4,
        fill: true,
        pointRadius: 6,
        pointBackgroundColor: "rgb(230, 57, 70)",
        pointBorderWidth: 2,
        pointBorderColor: "#fff",
      },
    ],
  };

  const lineChartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: "top" as const,
        labels: { usePointStyle: true, padding: 15 },
      },
      title: {
        display: true,
        text: "Comparación de Temperatura: Con vs Sin Refrigeración",
        font: { size: 16, weight: "bold" as const },
        padding: { bottom: 20 },
      },
      tooltip: {
        callbacks: {
          label: function (context: any) {
            return `${context.dataset.label}: ${context.parsed.y.toFixed(2)}°C`;
          },
        },
      },
    },
    scales: {
      y: {
        beginAtZero: false,
        title: {
          display: true,
          text: "Temperatura Promedio (°C)",
          font: { size: 12, weight: "bold" as const },
        },
      },
      x: {
        title: {
          display: true,
          text: "Sensores",
          font: { size: 12, weight: "bold" as const },
        },
      },
    },
  };

  // Preparar datos para gráfica de barras (diferencias)
  const barChartData = {
    labels: comparisonData.map((record) => record.sensor_name.replace("Temperature_", "")),
    datasets: [
      {
        label: "Diferencia de Temperatura (°C)",
        data: comparisonData.map((record) => record.difference),
        backgroundColor: comparisonData.map((record) =>
          record.difference > 3 ? "#e63946" : record.difference > 1 ? "#ff9800" : "#4caf50"
        ),
        borderColor: "#214B4E",
        borderWidth: 2,
        borderRadius: 6,
      },
    ],
  };

  const barChartOptions = {
    responsive: true,
    plugins: {
      legend: { display: false },
      title: {
        display: true,
        text: "Diferencia Térmica por Sensor (No Ref - Ref)",
        font: { size: 16, weight: "bold" as const },
        padding: { bottom: 20 },
      },
      tooltip: {
        callbacks: {
          label: function (context: any) {
            return `Diferencia: ${context.parsed.y.toFixed(2)}°C`;
          },
        },
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: "Diferencia de Temperatura (°C)",
          font: { size: 12, weight: "bold" as const },
        },
      },
    },
  };

  // Calcular estadísticas generales
  const stats = comparisonData.length > 0 ? {
    avgRefrigerada: comparisonData.reduce((sum, r) => sum + r.refrigerada_avg, 0) / comparisonData.length,
    avgNoRefrigerada: comparisonData.reduce((sum, r) => sum + r.no_refrigerada_avg, 0) / comparisonData.length,
    maxDifference: Math.max(...comparisonData.map(r => r.difference)),
    minDifference: Math.min(...comparisonData.map(r => r.difference)),
    avgDifference: comparisonData.reduce((sum, r) => sum + r.difference, 0) / comparisonData.length,
  } : null;

  return (
    <div style={{ padding: "2rem", backgroundColor: "#f8f9fa", minHeight: "100vh" }}>
      {/* Header */}
      <div
        style={{
          marginBottom: "2rem",
          padding: "1.5rem",
          backgroundColor: "white",
          borderRadius: "12px",
          boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
        }}
      >
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "1rem" }}>
          <div>
            <h1 style={{ margin: "0 0 0.5rem 0", fontSize: "2rem", fontWeight: "bold", color: "#2c3e50", display: "flex", alignItems: "center", gap: "0.75rem" }}>
              <TrendingUp size={32} color="#214B4E" />
              Comparación de Rendimiento Térmico
            </h1>
            <p style={{ margin: 0, color: "#6c757d", fontSize: "14px" }}>
              Fachada {facadeId} - Con vs Sin Refrigeración
            </p>
            {lastUpdate && (
              <p style={{ margin: "0.25rem 0 0 0", color: "#888", fontSize: "12px" }}>
                Última actualización: {lastUpdate}
              </p>
            )}
          </div>

          <button
            onClick={fetchComparisonData}
            disabled={loading}
            style={{
              padding: "0.75rem 1.5rem",
              backgroundColor: loading ? "#6c757d" : "#007bff",
              color: "white",
              border: "none",
              borderRadius: "8px",
              cursor: loading ? "not-allowed" : "pointer",
              fontSize: "14px",
              fontWeight: "600",
              display: "flex",
              alignItems: "center",
              gap: "0.5rem",
            }}
          >
            <RefreshCw size={16} />
            {loading ? "Actualizando..." : "Actualizar"}
          </button>
        </div>

        {/* Filtro de sensores */}
        <div
          style={{
            padding: "1rem",
            backgroundColor: "#f8f9fa",
            borderRadius: "8px",
            border: "1px solid #dee2e6",
          }}
        >
          <label style={{ display: "block", fontSize: "12px", fontWeight: "600", color: "#495057", marginBottom: "0.5rem" }}>
            <Filter size={14} style={{ display: "inline", marginRight: "0.25rem" }} />
            Filtrar por sensor (opcional)
          </label>
          <input
            type="text"
            value={sensorFilter}
            onChange={(e) => setSensorFilter(e.target.value)}
            placeholder="Ej: Temperature_M1_L1_1"
            style={{
              width: "100%",
              padding: "0.5rem",
              border: "1px solid #ced4da",
              borderRadius: "4px",
              fontSize: "14px",
            }}
          />
          {responseData?.sensor_filter && (
            <p style={{ margin: "0.5rem 0 0 0", fontSize: "12px", color: "#6c757d" }}>
              Filtro aplicado: {responseData.sensor_filter}
            </p>
          )}
        </div>
      </div>

      {/* Error display */}
      {error && (
        <div
          style={{
            padding: "1.5rem",
            backgroundColor: "#f8d7da",
            border: "2px solid #f5c6cb",
            borderRadius: "8px",
            color: "#721c24",
            marginBottom: "2rem",
          }}
        >
          <strong>Error:</strong> {error}
        </div>
      )}

      {/* Estadísticas generales */}
      {stats && (
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
            gap: "1rem",
            marginBottom: "2rem",
          }}
        >
          <div
            style={{
              backgroundColor: "white",
              padding: "1.5rem",
              borderRadius: "12px",
              boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
              border: "1px solid #e9ecef",
            }}
          >
            <h3 style={{ margin: "0 0 0.5rem 0", fontSize: "14px", color: "#6c757d", fontWeight: "600" }}>
              TEMP. PROM. CON REFRIGERACIÓN
            </h3>
            <p style={{ margin: 0, fontSize: "2rem", fontWeight: "bold", color: "#2196f3" }}>
              {stats.avgRefrigerada.toFixed(2)}°C
            </p>
          </div>

          <div
            style={{
              backgroundColor: "white",
              padding: "1.5rem",
              borderRadius: "12px",
              boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
              border: "1px solid #e9ecef",
            }}
          >
            <h3 style={{ margin: "0 0 0.5rem 0", fontSize: "14px", color: "#6c757d", fontWeight: "600" }}>
              TEMP. PROM. SIN REFRIGERACIÓN
            </h3>
            <p style={{ margin: 0, fontSize: "2rem", fontWeight: "bold", color: "#e63946" }}>
              {stats.avgNoRefrigerada.toFixed(2)}°C
            </p>
          </div>

          <div
            style={{
              backgroundColor: "white",
              padding: "1.5rem",
              borderRadius: "12px",
              boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
              border: "1px solid #e9ecef",
            }}
          >
            <h3 style={{ margin: "0 0 0.5rem 0", fontSize: "14px", color: "#6c757d", fontWeight: "600" }}>
              DIFERENCIA PROMEDIO
            </h3>
            <p style={{ margin: 0, fontSize: "2rem", fontWeight: "bold", color: "#28a745" }}>
              {stats.avgDifference.toFixed(2)}°C
            </p>
          </div>

          <div
            style={{
              backgroundColor: "white",
              padding: "1.5rem",
              borderRadius: "12px",
              boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
              border: "1px solid #e9ecef",
            }}
          >
            <h3 style={{ margin: "0 0 0.5rem 0", fontSize: "14px", color: "#6c757d", fontWeight: "600" }}>
              RANGO DE DIFERENCIA
            </h3>
            <p style={{ margin: 0, fontSize: "1.5rem", fontWeight: "bold", color: "#ff9800" }}>
              {stats.minDifference.toFixed(2)} - {stats.maxDifference.toFixed(2)}°C
            </p>
          </div>
        </div>
      )}

      {/* Gráficas */}
      {!loading && !error && comparisonData.length > 0 && (
        <>
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
              style={{
                backgroundColor: "white",
                padding: "2rem",
                borderRadius: "16px",
                boxShadow: "0 4px 16px rgba(0,0,0,0.08)",
                border: "1px solid #e9ecef",
              }}
            >
              <Line data={lineChartData} options={lineChartOptions} height={300} />
            </div>

            {/* Gráfica de barras */}
            <div
              style={{
                backgroundColor: "white",
                padding: "2rem",
                borderRadius: "16px",
                boxShadow: "0 4px 16px rgba(0,0,0,0.08)",
                border: "1px solid #e9ecef",
              }}
            >
              <Bar data={barChartData} options={barChartOptions} height={300} />
            </div>
          </div>

          {/* Tabla de datos */}
          <div
            style={{
              backgroundColor: "white",
              padding: "2rem",
              borderRadius: "16px",
              boxShadow: "0 4px 16px rgba(0,0,0,0.08)",
              border: "1px solid #e9ecef",
            }}
          >
            <h3 style={{ margin: "0 0 1.5rem 0", fontSize: "1.5rem", fontWeight: "bold", color: "#2c3e50" }}>
              Datos Detallados de Comparación
            </h3>

            <div style={{ overflowX: "auto" }}>
              <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "14px" }}>
                <thead>
                  <tr style={{ backgroundColor: "#f8f9fa", borderBottom: "2px solid #dee2e6" }}>
                    <th style={{ padding: "12px", textAlign: "left", fontWeight: "600" }}>Sensor</th>
                    <th style={{ padding: "12px", textAlign: "center", fontWeight: "600" }}>Con Refrigeración</th>
                    <th style={{ padding: "12px", textAlign: "center", fontWeight: "600" }}>Sin Refrigeración</th>
                    <th style={{ padding: "12px", textAlign: "center", fontWeight: "600" }}>Diferencia</th>
                    <th style={{ padding: "12px", textAlign: "center", fontWeight: "600" }}>Lecturas (Ref)</th>
                    <th style={{ padding: "12px", textAlign: "center", fontWeight: "600" }}>Lecturas (No Ref)</th>
                  </tr>
                </thead>
                <tbody>
                  {comparisonData.map((record, index) => (
                    <tr
                      key={`${record.sensor_name}-${index}`}
                      style={{
                        backgroundColor: index % 2 === 0 ? "#fff" : "#f8f9fa",
                        borderBottom: "1px solid #dee2e6",
                      }}
                    >
                      <td style={{ padding: "12px", fontWeight: "600", color: "#214B4E" }}>
                        {record.sensor_name.replace("Temperature_", "")}
                      </td>
                      <td style={{ padding: "12px", textAlign: "center", color: "#2196f3", fontWeight: "600" }}>
                        {record.refrigerada_avg.toFixed(2)}°C
                      </td>
                      <td style={{ padding: "12px", textAlign: "center", color: "#e63946", fontWeight: "600" }}>
                        {record.no_refrigerada_avg.toFixed(2)}°C
                      </td>
                      <td
                        style={{
                          padding: "12px",
                          textAlign: "center",
                          fontWeight: "600",
                          color: record.difference > 3 ? "#e63946" : record.difference > 1 ? "#ff9800" : "#4caf50",
                        }}
                      >
                        {record.difference.toFixed(2)}°C
                      </td>
                      <td style={{ padding: "12px", textAlign: "center" }}>
                        {record.refrigerada_count.toLocaleString()}
                      </td>
                      <td style={{ padding: "12px", textAlign: "center" }}>
                        {record.no_refrigerada_count.toLocaleString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}

      {/* Empty state */}
      {!loading && !error && comparisonData.length === 0 && (
        <div
          style={{
            padding: "4rem",
            textAlign: "center",
            backgroundColor: "white",
            borderRadius: "12px",
            boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
          }}
        >
          <h3 style={{ color: "#6c757d", margin: 0 }}>No hay datos de comparación disponibles</h3>
          <p style={{ color: "#6c757d", margin: "0.5rem 0 0 0" }}>
            Verifica que existan datos para ambas fachadas (refrigerada y no refrigerada)
          </p>
        </div>
      )}

      {/* Loading state */}
      {loading && (
        <div
          style={{
            padding: "4rem",
            textAlign: "center",
            backgroundColor: "white",
            borderRadius: "12px",
            boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
          }}
        >
          <div style={{ fontSize: "3rem", marginBottom: "1rem" }}>🔄</div>
          <h3 style={{ color: "#6c757d", margin: 0 }}>Cargando datos de comparación...</h3>
        </div>
      )}

      {/* Debug info */}
      {responseData && comparisonData.length > 0 && (
        <details style={{ marginTop: "2rem" }}>
          <summary
            style={{
              cursor: "pointer",
              padding: "1rem",
              backgroundColor: "#e9ecef",
              borderRadius: "8px",
              fontWeight: "600",
            }}
          >
            Ver datos en crudo (JSON)
          </summary>
          <pre
            style={{
              backgroundColor: "#f8f9fa",
              padding: "1.5rem",
              borderRadius: "8px",
              overflow: "auto",
              fontSize: "11px",
              marginTop: "1rem",
              border: "1px solid #dee2e6",
            }}
          >
            {JSON.stringify(responseData, null, 2)}
          </pre>
        </details>
      )}
    </div>
  );
}