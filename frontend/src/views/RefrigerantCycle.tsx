import { useEffect, useState, useRef } from "react";
import { Bar, Line } from "react-chartjs-2";
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
import { Thermometer, RefreshCw, AlertTriangle, Calendar } from "lucide-react";

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

// Backend response structure
interface BackendReading {
  ts: string;
  value: number;
  device_id: string;
}

interface BackendCyclePoint {
  label: string;
  readings: BackendReading[];
}

interface BackendResponse {
  facade_id: string;
  cycle_points: {
    [sensor_name: string]: BackendCyclePoint;
  };
}

// Frontend display structure
interface RefrigerantCycleRecord {
  cycle_point: string;
  avg_temperature: number;
  min_temperature: number;
  max_temperature: number;
  sample_count: number;
  timestamp_range?: {
    start: string;
    end: string;
  };
}

interface RefrigerantCycleResponse {
  facade_id: string;
  facade_type: string;
  refrigeration_cycle: RefrigerantCycleRecord[];
}

export default function RefrigerantCycle({ facadeId = "1" }: { facadeId?: string }) {
  const [responseData, setResponseData] = useState<RefrigerantCycleResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<string>("");
  const isMountedRef = useRef(true);

  // Parámetros de filtro opcionales
  const [startDate, setStartDate] = useState<string>("");
  const [endDate, setEndDate] = useState<string>("");

  const fetchRefrigerantCycle = async () => {
    if (!isMountedRef.current) return;

    setLoading(true);
    setError(null);

    try {
      const params = new URLSearchParams();
      if (startDate) params.append("start", startDate);
      if (endDate) params.append("end", endDate);

      const queryString = params.toString();
      const url = `http://localhost:8000/temperatures/refrigerant-cycle/${facadeId}${queryString ? `?${queryString}` : ''}`;
      console.log(`❄️ [${new Date().toLocaleTimeString()}] Fetching refrigerant cycle from: ${url}`);

      const response = await fetch(url);

      if (!response.ok) {
        if (response.status === 404) {
          throw new Error("No hay datos de refrigeración disponibles. Este endpoint solo aplica a fachadas refrigeradas.");
        }
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data: BackendResponse = await response.json();
      console.log("❄️ Refrigerant Cycle API response:", data);

      // Transformar datos del backend al formato del frontend
      const refrigerationCycle: RefrigerantCycleRecord[] = [];

      // Procesar cada punto del ciclo
      for (const cyclePoint of Object.values(data.cycle_points)) {
        const readings = cyclePoint.readings;
        
        if (readings && readings.length > 0) {
          // Calcular estadísticas de las lecturas
          const temperatures = readings.map(r => r.value).filter(v => v !== null && v !== undefined);
          
          if (temperatures.length > 0) {
            const avg = temperatures.reduce((sum, t) => sum + t, 0) / temperatures.length;
            const min = Math.min(...temperatures);
            const max = Math.max(...temperatures);
            const timestamps = readings.map(r => r.ts).sort();

            refrigerationCycle.push({
              cycle_point: cyclePoint.label,
              avg_temperature: avg,
              min_temperature: min,
              max_temperature: max,
              sample_count: readings.length,
              timestamp_range: timestamps.length > 0 ? {
                start: timestamps[0],
                end: timestamps[timestamps.length - 1]
              } : undefined
            });
          }
        }
      }

      const transformedData: RefrigerantCycleResponse = {
        facade_id: data.facade_id,
        facade_type: "refrigerada", // Asumimos que si hay datos, es refrigerada
        refrigeration_cycle: refrigerationCycle
      };

      if (isMountedRef.current) {
        setResponseData(transformedData);
        setLastUpdate(new Date().toLocaleString());
        console.log(`✅ Successfully loaded ${transformedData.refrigeration_cycle.length} cycle points`);
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Unknown error";
      console.error("💥 Error fetching refrigerant cycle:", err);

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
    console.log("🔄 RefrigerantCycle mounted");
    isMountedRef.current = true;
    fetchRefrigerantCycle();

    return () => {
      isMountedRef.current = false;
    };
  }, [facadeId]);

  useEffect(() => {
    if (isMountedRef.current) {
      fetchRefrigerantCycle();
    }
  }, [startDate, endDate]);

  const cycleData = responseData?.refrigeration_cycle || [];

  // Preparar datos para gráfica de barras
  const barChartData = {
    labels: cycleData.map((record) => record.cycle_point),
    datasets: [
      {
        label: "Temperatura Promedio (°C)",
        data: cycleData.map((record) => record.avg_temperature),
        backgroundColor: cycleData.map((record) => {
          // Colorear según temperatura
          if (record.avg_temperature > 60) return "rgba(230, 57, 70, 0.8)"; // Rojo (caliente)
          if (record.avg_temperature > 30) return "rgba(255, 152, 0, 0.8)"; // Naranja (medio)
          if (record.avg_temperature > 0) return "rgba(33, 150, 243, 0.8)"; // Azul (frío)
          return "rgba(76, 175, 80, 0.8)"; // Verde (muy frío)
        }),
        borderColor: "#214B4E",
        borderWidth: 2,
        borderRadius: 8,
      },
    ],
  };

  const barChartOptions = {
    responsive: true,
    plugins: {
      legend: { display: true, position: "top" as const },
      title: {
        display: true,
        text: "Temperaturas del Ciclo de Refrigeración",
        font: { size: 18, weight: "bold" as const },
        padding: { bottom: 20 },
      },
      tooltip: {
        callbacks: {
          label: function (context: any) {
            const record = cycleData[context.dataIndex];
            return [
              `Promedio: ${record.avg_temperature.toFixed(2)}°C`,
              `Mín: ${record.min_temperature.toFixed(2)}°C`,
              `Máx: ${record.max_temperature.toFixed(2)}°C`,
              `Muestras: ${record.sample_count}`,
            ];
          },
        },
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: "Temperatura (°C)",
          font: { size: 14, weight: "bold" as const },
        },
      },
      x: {
        title: {
          display: true,
          text: "Punto del Ciclo",
          font: { size: 14, weight: "bold" as const },
        },
      },
    },
  };

  // Preparar datos para gráfica de líneas (rangos)
  const lineChartData = {
    labels: cycleData.map((record) => record.cycle_point),
    datasets: [
      {
        label: "Temperatura Máxima",
        data: cycleData.map((record) => record.max_temperature),
        borderColor: "#e63946",
        backgroundColor: "rgba(230, 57, 70, 0.1)",
        tension: 0.4,
        fill: false,
        pointRadius: 5,
      },
      {
        label: "Temperatura Promedio",
        data: cycleData.map((record) => record.avg_temperature),
        borderColor: "#2196f3",
        backgroundColor: "rgba(33, 150, 243, 0.2)",
        tension: 0.4,
        fill: true,
        pointRadius: 6,
        pointBackgroundColor: "#2196f3",
      },
      {
        label: "Temperatura Mínima",
        data: cycleData.map((record) => record.min_temperature),
        borderColor: "#4caf50",
        backgroundColor: "rgba(76, 175, 80, 0.1)",
        tension: 0.4,
        fill: false,
        pointRadius: 5,
      },
    ],
  };

  const lineChartOptions = {
    responsive: true,
    plugins: {
      legend: { display: true, position: "top" as const },
      title: {
        display: true,
        text: "Rango de Temperaturas por Punto del Ciclo",
        font: { size: 18, weight: "bold" as const },
        padding: { bottom: 20 },
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: "Temperatura (°C)",
          font: { size: 14, weight: "bold" as const },
        },
      },
      x: {
        title: {
          display: true,
          text: "Punto del Ciclo",
          font: { size: 14, weight: "bold" as const },
        },
      },
    },
  };

  // Calcular estadísticas
  const stats = cycleData.length > 0 ? {
    avgOverall: cycleData.reduce((sum, r) => sum + r.avg_temperature, 0) / cycleData.length,
    maxOverall: Math.max(...cycleData.map(r => r.max_temperature)),
    minOverall: Math.min(...cycleData.map(r => r.min_temperature)),
    totalSamples: cycleData.reduce((sum, r) => sum + r.sample_count, 0),
    hottestPoint: cycleData.reduce((max, r) => r.avg_temperature > max.avg_temperature ? r : max),
    coldestPoint: cycleData.reduce((min, r) => r.avg_temperature < min.avg_temperature ? r : min),
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
              <Thermometer size={32} color="#2196f3" />
              Ciclo de Refrigeración
            </h1>
            <p style={{ margin: 0, color: "#6c757d", fontSize: "14px" }}>
              Fachada {facadeId} - {responseData?.facade_type || "Cargando..."}
            </p>
            {lastUpdate && (
              <p style={{ margin: "0.25rem 0 0 0", color: "#888", fontSize: "12px" }}>
                Última actualización: {lastUpdate}
              </p>
            )}
          </div>

          <button
            onClick={fetchRefrigerantCycle}
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

        {/* Filtros de fecha */}
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "1fr 1fr",
            gap: "1rem",
            padding: "1rem",
            backgroundColor: "#f8f9fa",
            borderRadius: "8px",
            border: "1px solid #dee2e6",
          }}
        >
          <div>
            <label style={{ display: "block", fontSize: "12px", fontWeight: "600", color: "#495057", marginBottom: "0.5rem" }}>
              <Calendar size={14} style={{ display: "inline", marginRight: "0.25rem" }} />
              Fecha Inicio (opcional)
            </label>
            <input
              type="datetime-local"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              style={{
                width: "100%",
                padding: "0.5rem",
                border: "1px solid #ced4da",
                borderRadius: "4px",
                fontSize: "14px",
              }}
            />
          </div>

          <div>
            <label style={{ display: "block", fontSize: "12px", fontWeight: "600", color: "#495057", marginBottom: "0.5rem" }}>
              Fecha Fin (opcional)
            </label>
            <input
              type="datetime-local"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              style={{
                width: "100%",
                padding: "0.5rem",
                border: "1px solid #ced4da",
                borderRadius: "4px",
                fontSize: "14px",
              }}
            />
          </div>
        </div>

        {/* Warning para fachadas no refrigeradas */}
        {responseData?.facade_type === "no_refrigerada" && (
          <div
            style={{
              marginTop: "1rem",
              padding: "0.75rem",
              backgroundColor: "#fff3cd",
              border: "1px solid #ffc107",
              borderRadius: "6px",
              fontSize: "14px",
              color: "#856404",
              display: "flex",
              alignItems: "center",
              gap: "0.5rem",
            }}
          >
            <AlertTriangle size={16} />
            <span>Esta fachada no tiene sistema de refrigeración activo.</span>
          </div>
        )}
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

      {/* Estadísticas */}
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
              TEMP. PROM. GENERAL
            </h3>
            <p style={{ margin: 0, fontSize: "2rem", fontWeight: "bold", color: "#2196f3" }}>
              {stats.avgOverall.toFixed(2)}°C
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
              RANGO TOTAL
            </h3>
            <p style={{ margin: 0, fontSize: "1.5rem", fontWeight: "bold", color: "#ff9800" }}>
              {stats.minOverall.toFixed(2)} - {stats.maxOverall.toFixed(2)}°C
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
              PUNTO MÁS CALIENTE
            </h3>
            <p style={{ margin: 0, fontSize: "1.2rem", fontWeight: "bold", color: "#e63946" }}>
              {stats.hottestPoint.cycle_point}
            </p>
            <p style={{ margin: "0.25rem 0 0 0", fontSize: "1.5rem", color: "#e63946" }}>
              {stats.hottestPoint.avg_temperature.toFixed(2)}°C
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
              PUNTO MÁS FRÍO
            </h3>
            <p style={{ margin: 0, fontSize: "1.2rem", fontWeight: "bold", color: "#4caf50" }}>
              {stats.coldestPoint.cycle_point}
            </p>
            <p style={{ margin: "0.25rem 0 0 0", fontSize: "1.5rem", color: "#4caf50" }}>
              {stats.coldestPoint.avg_temperature.toFixed(2)}°C
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
              TOTAL MUESTRAS
            </h3>
            <p style={{ margin: 0, fontSize: "2rem", fontWeight: "bold", color: "#6c757d" }}>
              {stats.totalSamples.toLocaleString()}
            </p>
          </div>
        </div>
      )}

      {/* Gráficas */}
      {!loading && !error && cycleData.length > 0 && (
        <>
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "1fr 1fr",
              gap: "2rem",
              marginBottom: "2rem",
            }}
          >
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
              Datos Detallados del Ciclo
            </h3>

            <div style={{ overflowX: "auto" }}>
              <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "14px" }}>
                <thead>
                  <tr style={{ backgroundColor: "#f8f9fa", borderBottom: "2px solid #dee2e6" }}>
                    <th style={{ padding: "12px", textAlign: "left", fontWeight: "600" }}>Punto del Ciclo</th>
                    <th style={{ padding: "12px", textAlign: "center", fontWeight: "600" }}>Temp. Promedio</th>
                    <th style={{ padding: "12px", textAlign: "center", fontWeight: "600" }}>Temp. Mínima</th>
                    <th style={{ padding: "12px", textAlign: "center", fontWeight: "600" }}>Temp. Máxima</th>
                    <th style={{ padding: "12px", textAlign: "center", fontWeight: "600" }}>Muestras</th>
                  </tr>
                </thead>
                <tbody>
                  {cycleData.map((record, index) => (
                    <tr
                      key={`${record.cycle_point}-${index}`}
                      style={{
                        backgroundColor: index % 2 === 0 ? "#fff" : "#f8f9fa",
                        borderBottom: "1px solid #dee2e6",
                      }}
                    >
                      <td style={{ padding: "12px", fontWeight: "600", color: "#214B4E" }}>
                        {record.cycle_point}
                      </td>
                      <td style={{ padding: "12px", textAlign: "center", color: "#2196f3", fontWeight: "600" }}>
                        {record.avg_temperature.toFixed(2)}°C
                      </td>
                      <td style={{ padding: "12px", textAlign: "center", color: "#4caf50" }}>
                        {record.min_temperature.toFixed(2)}°C
                      </td>
                      <td style={{ padding: "12px", textAlign: "center", color: "#e63946" }}>
                        {record.max_temperature.toFixed(2)}°C
                      </td>
                      <td style={{ padding: "12px", textAlign: "center" }}>
                        {record.sample_count.toLocaleString()}
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
      {!loading && !error && cycleData.length === 0 && (
        <div
          style={{
            padding: "4rem",
            textAlign: "center",
            backgroundColor: "white",
            borderRadius: "12px",
            boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
          }}
        >
          <AlertTriangle size={64} color="#6c757d" style={{ marginBottom: "1rem" }} />
          <h3 style={{ color: "#6c757d", margin: 0 }}>No hay datos del ciclo de refrigeración</h3>
          <p style={{ color: "#6c757d", margin: "0.5rem 0 0 0" }}>
            Este endpoint solo aplica a fachadas refrigeradas
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
          <div style={{ fontSize: "3rem", marginBottom: "1rem" }}>❄️</div>
          <h3 style={{ color: "#6c757d", margin: 0 }}>Cargando datos del ciclo de refrigeración...</h3>
        </div>
      )}

      {/* Debug info */}
      {responseData && cycleData.length > 0 && (
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