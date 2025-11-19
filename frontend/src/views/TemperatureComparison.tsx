import { useEffect, useState, useCallback, useRef } from "react";
import { Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from "chart.js";
import PDFExportButton from "./PDFExportButton";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

interface TempData {
  timestamp: string;
  temperature: number;
}

interface HistoricalDataPoint {
  timestamp: string;
  refrigerated: number;
  nonRefrigerated: number;
}

export default function TemperatureComparison() {
  const [historicalData, setHistoricalData] = useState<HistoricalDataPoint[]>([]);
  const [currentRefrigerated, setCurrentRefrigerated] = useState<number>(0);
  const [currentNonRefrigerated, setCurrentNonRefrigerated] = useState<number>(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<string>("");
  const isMountedRef = useRef(true);

  const MAX_DATA_POINTS = 20; // Máximo de puntos en el historial

  const fetchTemperatureComparison = useCallback(async () => {
    if (!isMountedRef.current) return;
    setLoading(true);
    setError(null);

    try {
      const facadesUrl = `http://136.115.180.156:8000/facades`;
      console.log(`🔍 Fetching facades list from: ${facadesUrl}`);

      const facadesResponse = await fetch(facadesUrl);
      if (!facadesResponse.ok) {
        throw new Error(`Error fetching facades: ${facadesResponse.statusText}`);
      }

      const facadesJson = await facadesResponse.json();
      console.log("Facades response:", facadesJson);

      const facades = facadesJson.facades || [];
      
      const refrigerated = facades.find((f: any) => f.facade_type === "refrigerada");
      const nonRefrigerated = facades.find((f: any) => f.facade_type === "no_refrigerada");

      if (!refrigerated || !nonRefrigerated) {
        throw new Error("No se encontraron ambas fachadas (refrigerada y no refrigerada)");
      }

      console.log(`🔎 Fachada refrigerada: ${refrigerated.facade_id}, No refrigerada: ${nonRefrigerated.facade_id}`);

      const [refResponse, nonRefResponse] = await Promise.all([
        fetch(`http://136.115.180.156:8000/realtime/facades/${refrigerated.facade_id}`),
        fetch(`http://136.115.180.156:8000/realtime/facades/${nonRefrigerated.facade_id}`)
      ]);

      if (!refResponse.ok || !nonRefResponse.ok) {
        throw new Error("Error fetching temperature data for comparison");
      }

      const refData = await refResponse.json();
      const nonRefData = await nonRefResponse.json();

      console.log("Refrigerated data:", refData);
      console.log("Non-refrigerated data:", nonRefData);

      const extractAverageTemperature = (facadeData: any): number => {
        const data = facadeData.data || {};
        const tempSensors = Object.entries(data).filter(([key]) => 
          key.startsWith("Temperature_M") || key.startsWith("Temperatura_") || key.startsWith("T_")
        );

        if (tempSensors.length === 0) return 0;

        const avgTemp = tempSensors.reduce((sum, [, sensor]: [string, any]) => 
          sum + (sensor.value || 0), 0
        ) / tempSensors.length;

        return Number(avgTemp.toFixed(2));
      };

      const refTemp = extractAverageTemperature(refData);
      const nonRefTemp = extractAverageTemperature(nonRefData);

      if (isMountedRef.current) {
        setCurrentRefrigerated(refTemp);
        setCurrentNonRefrigerated(nonRefTemp);

        // Agregar nuevo punto al historial
        const newDataPoint: HistoricalDataPoint = {
          timestamp: new Date().toLocaleTimeString(),
          refrigerated: refTemp,
          nonRefrigerated: nonRefTemp
        };

        setHistoricalData(prev => {
          const updated = [...prev, newDataPoint];
          // Mantener solo los últimos MAX_DATA_POINTS puntos
          return updated.length > MAX_DATA_POINTS 
            ? updated.slice(updated.length - MAX_DATA_POINTS)
            : updated;
        });

        setLastUpdate(new Date().toLocaleString());
      }
    } catch (err) {
      console.error("Error fetching temperature comparison:", err);
      if (isMountedRef.current) setError((err as Error).message);
    } finally {
      if (isMountedRef.current) setLoading(false);
    }
  }, []);

  useEffect(() => {
    isMountedRef.current = true;
    fetchTemperatureComparison();
    
    const interval = setInterval(fetchTemperatureComparison, 30000); // 30 segundos
    
    return () => {
      isMountedRef.current = false;
      clearInterval(interval);
    };
  }, [fetchTemperatureComparison]);

  const hasData = historicalData.length > 0;

  const chartData = {
    labels: historicalData.map(d => d.timestamp),
    datasets: [
      {
        label: "Fachada Refrigerada (°C)",
        data: historicalData.map(d => d.refrigerated),
        borderColor: "rgb(33, 150, 243)",
        backgroundColor: "rgba(33, 150, 243, 0.1)",
        borderWidth: 3,
        fill: true,
        tension: 0.4,
        pointRadius: 4,
        pointBackgroundColor: "rgb(33, 150, 243)",
        pointBorderColor: "#fff",
        pointBorderWidth: 2,
      },
      {
        label: "Fachada No Refrigerada (°C)",
        data: historicalData.map(d => d.nonRefrigerated),
        borderColor: "rgb(230, 57, 70)",
        backgroundColor: "rgba(230, 57, 70, 0.1)",
        borderWidth: 3,
        fill: true,
        tension: 0.4,
        pointRadius: 4,
        pointBackgroundColor: "rgb(230, 57, 70)",
        pointBorderColor: "#fff",
        pointBorderWidth: 2,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { 
        position: "top" as const,
        labels: {
          font: { size: 14 },
          usePointStyle: true,
          padding: 20,
        }
      },
      title: {
        display: true,
        text: "Evolución Temporal de Temperaturas – Refrigerada vs No Refrigerada",
        font: { size: 16, weight: "bold" as const },
        padding: { bottom: 20 }
      },
      tooltip: {
        mode: 'index' as const,
        intersect: false,
        callbacks: {
          label: function(context: any) {
            return `${context.dataset.label}: ${context.parsed.y.toFixed(2)}°C`;
          }
        }
      }
    },
    scales: {
      y: {
        beginAtZero: false,
        title: {
          display: true,
          text: "Temperatura Promedio (°C)",
          font: { size: 14, weight: "bold" as const }
        },
        grid: {
          color: "rgba(0, 0, 0, 0.1)",
        },
        ticks: {
          callback: function(value: any) {
            return value.toFixed(1) + '°C';
          }
        }
      },
      x: {
        title: {
          display: true,
          text: "Tiempo",
          font: { size: 14, weight: "bold" as const }
        },
        grid: {
          display: false
        }
      },
    },
    interaction: {
      mode: 'nearest' as const,
      axis: 'x' as const,
      intersect: false
    },
  };

  const tempDifference = currentNonRefrigerated - currentRefrigerated;

  return (
    <div style={{ padding: "2rem", backgroundColor: "#f8f9fa", minHeight: "100vh" }}>
      {/* Header */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "1.5rem",
        }}
      >
        <h2 style={{ fontSize: "1.75rem", fontWeight: "bold", color: "#214B4E" }}>
          🌡️ Comparativa de Temperaturas en Tiempo Real
        </h2>

        {/* Botones */}
        <div style={{ display: "flex", gap: "1rem" }}>
          <button
            onClick={fetchTemperatureComparison}
            disabled={loading}
            style={{
              backgroundColor: loading ? "#6c757d" : "#007bff",
              color: "white",
              padding: "0.75rem 1.5rem",
              border: "none",
              borderRadius: "8px",
              cursor: loading ? "not-allowed" : "pointer",
              fontWeight: "600",
            }}
          >
            {loading ? "🔄 Cargando..." : "🔄 Actualizar"}
          </button>

          {!loading && !error && hasData && (
            <PDFExportButton
              title="Comparativa de Temperaturas - Refrigerada vs No Refrigerada"
              elementId="comparison-pdf-content"
              filename="comparativa-temperaturas"
            />
          )}
        </div>
      </div>

      {error && (
        <div
          style={{
            backgroundColor: "#f8d7da",
            border: "1px solid #f5c6cb",
            color: "#721c24",
            padding: "1rem",
            borderRadius: "8px",
            marginBottom: "1rem",
          }}
        >
          <strong>Error:</strong> {error}
        </div>
      )}

      {/* Empty state */}
      {!loading && !error && !hasData && (
        <div
          style={{
            backgroundColor: "white",
            padding: "2rem",
            borderRadius: "12px",
            textAlign: "center",
            color: "#6c757d",
          }}
        >
          No hay datos de comparación disponibles. Verifica que ambas fachadas estén enviando datos.
        </div>
      )}

      <div id="comparison-pdf-content">
        {hasData && (
          <>
            {/* Métricas principales */}
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))",
                gap: "1rem",
                marginBottom: "1.5rem",
              }}
            >
              <div
                style={{
                  backgroundColor: "white",
                  padding: "1.5rem",
                  borderRadius: "12px",
                  boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
                  borderLeft: "4px solid #2196f3",
                }}
              >
                <h3 style={{ fontSize: "1rem", color: "#6c757d", marginBottom: "0.5rem" }}>
                  🧊 Fachada Refrigerada
                </h3>
                <p style={{ fontSize: "2rem", fontWeight: "bold", color: "#2196f3", margin: 0 }}>
                  {currentRefrigerated.toFixed(2)}°C
                </p>
                <p style={{ fontSize: "0.875rem", color: "#6c757d", marginTop: "0.5rem" }}>
                  Temperatura actual promedio
                </p>
              </div>

              <div
                style={{
                  backgroundColor: "white",
                  padding: "1.5rem",
                  borderRadius: "12px",
                  boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
                  borderLeft: "4px solid #e63946",
                }}
              >
                <h3 style={{ fontSize: "1rem", color: "#6c757d", marginBottom: "0.5rem" }}>
                  🌡️ Fachada No Refrigerada
                </h3>
                <p style={{ fontSize: "2rem", fontWeight: "bold", color: "#e63946", margin: 0 }}>
                  {currentNonRefrigerated.toFixed(2)}°C
                </p>
                <p style={{ fontSize: "0.875rem", color: "#6c757d", marginTop: "0.5rem" }}>
                  Temperatura actual promedio
                </p>
              </div>

              <div
                style={{
                  backgroundColor: "white",
                  padding: "1.5rem",
                  borderRadius: "12px",
                  boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
                  borderLeft: "4px solid #28a745",
                }}
              >
                <h3 style={{ fontSize: "1rem", color: "#6c757d", marginBottom: "0.5rem" }}>
                  📊 Diferencia Térmica
                </h3>
                <p style={{ 
                  fontSize: "2rem", 
                  fontWeight: "bold", 
                  color: tempDifference > 0 ? "#28a745" : "#6c757d", 
                  margin: 0 
                }}>
                  {Math.abs(tempDifference).toFixed(2)}°C
                </p>
                <p style={{ fontSize: "0.875rem", color: "#6c757d", marginTop: "0.5rem" }}>
                  {tempDifference > 0 
                    ? `✅ La refrigeración reduce ${tempDifference.toFixed(2)}°C`
                    : tempDifference < 0
                    ? `⚠️ La fachada refrigerada está más caliente`
                    : "⚖️ Sin diferencia significativa"}
                </p>
              </div>
            </div>

            {/* Gráfica de líneas */}
            <div
              style={{
                backgroundColor: "white",
                padding: "2rem",
                borderRadius: "12px",
                boxShadow: "0 4px 12px rgba(0,0,0,0.1)",
                height: "500px",
                marginBottom: "1rem",
              }}
            >
              <Line data={chartData} options={chartOptions} />
            </div>

            {/* Información adicional */}
            <div
              style={{
                backgroundColor: "white",
                padding: "1rem 2rem",
                borderRadius: "12px",
                boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                fontSize: "14px",
                color: "#6c757d",
              }}
            >
              <div>
                <strong>Datos mostrados:</strong> {historicalData.length} puntos temporales
              </div>
              <div>
                <strong>Intervalo de actualización:</strong> 30 segundos
              </div>
              {lastUpdate && (
                <div>
                  <strong>Última actualización:</strong> {lastUpdate}
                </div>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
}