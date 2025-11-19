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
} from "chart.js";
import PDFExportButton from "./PDFExportButton";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

interface TempData {
  timestamp: string;
  temperature: number;
}

export default function TemperatureComparison() {
  const [refrigeratedData, setRefrigeratedData] = useState<TempData[]>([]);
  const [nonRefrigeratedData, setNonRefrigeratedData] = useState<TempData[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<string>("");
  const isMountedRef = useRef(true);
  const dataHistoryRef = useRef<{ ref: TempData[], noRef: TempData[] }>({ ref: [], noRef: [] });

  const fetchTemperatureComparison = useCallback(async () => {
    if (!isMountedRef.current) return;
    setLoading(true);
    setError(null);

    try {
      const facadesUrl = `http://localhost:8000/facades/`;
      console.log(`🔍 Fetching facades list from: ${facadesUrl}`);

      const facadesResponse = await fetch(facadesUrl);
      if (!facadesResponse.ok) {
        throw new Error(`Error fetching facades: ${facadesResponse.statusText}`);
      }

      const facadesJson = await facadesResponse.json();
      console.log("Facades response:", facadesJson);

      const facades = facadesJson.facades || [];
      
      if (facades.length < 2) {
        throw new Error("No se encontraron suficientes fachadas disponibles");
      }

      // Identificar las fachadas por tipo
      const refrigeradaFacade = facades.find((f: any) => f.facade_type === "refrigerada");
      const noRefrigeradaFacade = facades.find((f: any) => f.facade_type === "no_refrigerada");

      if (!refrigeradaFacade || !noRefrigeradaFacade) {
        throw new Error("No se encontraron ambos tipos de fachadas");
      }

      console.log(`🔎 Fachada refrigerada ID: ${refrigeradaFacade.facade_id}`);
      console.log(`🔎 Fachada no refrigerada ID: ${noRefrigeradaFacade.facade_id}`);

      // Obtener datos en tiempo real de ambas fachadas (sin facade_type en query)
      const refUrl = `http://localhost:8000/realtime/facades/${refrigeradaFacade.facade_id}`;
      const nonRefUrl = `http://localhost:8000/realtime/facades/${noRefrigeradaFacade.facade_id}`;
      
      console.log(`📊 Fetching refrigerated data from: ${refUrl}`);
      console.log(`📊 Fetching non-refrigerated data from: ${nonRefUrl}`);

      const [refResponse, nonRefResponse] = await Promise.all([
        fetch(refUrl),
        fetch(nonRefUrl)
      ]);
      
      if (!refResponse.ok || !nonRefResponse.ok) {
        throw new Error("Error fetching temperature data from one or both facades");
      }

      const refData = await refResponse.json();
      const nonRefData = await nonRefResponse.json();
      
      console.log("Refrigerated data:", refData);
      console.log("Non-refrigerated data:", nonRefData);

      // Extraer sensores de temperatura y calcular promedio manualmente
      const calculateAverageTemp = (data: any) => {
        const sensorData = data.data || {};
        const tempSensors: number[] = [];
        
        Object.entries(sensorData).forEach(([sensorName, sensorInfo]: [string, any]) => {
          // Buscar sensores T_M (formato: T_M1_1, T_M2_3, etc.)
          if (sensorName.startsWith("T_M") && sensorInfo?.value !== null && sensorInfo?.value !== undefined) {
            tempSensors.push(sensorInfo.value);
          }
        });
        
        console.log(`Sensores encontrados: ${tempSensors.length}, valores:`, tempSensors);
        
        if (tempSensors.length === 0) return null;
        const sum = tempSensors.reduce((acc, val) => acc + val, 0);
        return sum / tempSensors.length;
      };

      const refAvg = calculateAverageTemp(refData);
      const nonRefAvg = calculateAverageTemp(nonRefData);

      if (refAvg === null || nonRefAvg === null) {
        throw new Error("No se encontraron sensores de temperatura válidos en una o ambas fachadas");
      }

      // Crear datos para acumular en el historial
      const now = new Date().toISOString();
      
      const newRefPoint: TempData = {
        timestamp: now,
        temperature: refAvg
      };

      const newNonRefPoint: TempData = {
        timestamp: now,
        temperature: nonRefAvg
      };

      // Acumular en el historial (máximo 30 puntos)
      dataHistoryRef.current.ref = [...dataHistoryRef.current.ref, newRefPoint].slice(-30);
      dataHistoryRef.current.noRef = [...dataHistoryRef.current.noRef, newNonRefPoint].slice(-30);

      console.log(`✅ Refrigerated avg: ${refAvg.toFixed(2)}°C, Non-refrigerated avg: ${nonRefAvg.toFixed(2)}°C`);
      console.log(`📊 History size: Ref=${dataHistoryRef.current.ref.length}, NoRef=${dataHistoryRef.current.noRef.length}`);

      if (isMountedRef.current) {
        setRefrigeratedData([...dataHistoryRef.current.ref]);
        setNonRefrigeratedData([...dataHistoryRef.current.noRef]);
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
    
    const interval = setInterval(fetchTemperatureComparison, 10000);
    
    return () => {
      isMountedRef.current = false;
      clearInterval(interval);
    };
  }, [fetchTemperatureComparison]);

  const hasData = refrigeratedData.length > 0 && nonRefrigeratedData.length > 0;
  
  // Crear datos para gráfica de líneas en función del tiempo
  const chartData = {
    labels: refrigeratedData.map(d => new Date(d.timestamp).toLocaleTimeString()),
    datasets: [
      {
        label: "Fachada Refrigerada",
        data: refrigeratedData.map(d => d.temperature),
        borderColor: "rgb(54, 162, 235)",
        backgroundColor: "rgba(54, 162, 235, 0.1)",
        tension: 0.3,
        fill: true,
        pointRadius: 4,
        pointHoverRadius: 6,
        borderWidth: 2,
      },
      {
        label: "Fachada No Refrigerada",
        data: nonRefrigeratedData.map(d => d.temperature),
        borderColor: "rgb(255, 99, 132)",
        backgroundColor: "rgba(255, 99, 132, 0.1)",
        tension: 0.3,
        fill: true,
        pointRadius: 4,
        pointHoverRadius: 6,
        borderWidth: 2,
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
          font: { size: 14 }
        }
      },
      title: {
        display: true,
        text: "Evolución Temporal: Refrigerada vs No Refrigerada",
        font: { size: 18, weight: "bold" as const },
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
    interaction: {
      mode: 'nearest' as const,
      axis: 'x' as const,
      intersect: false,
    },
    scales: {
      y: {
        beginAtZero: false,
        title: {
          display: true,
          text: "Temperatura (°C)",
          font: { size: 14 }
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
          font: { size: 14 }
        },
        ticks: {
          maxRotation: 45,
          minRotation: 45
        }
      },
    },
  };

  const tempDifference = hasData 
    ? (nonRefrigeratedData[nonRefrigeratedData.length - 1]?.temperature || 0) - 
      (refrigeratedData[refrigeratedData.length - 1]?.temperature || 0)
    : 0;

  return (
    <div style={{ padding: "2rem", backgroundColor: "#f8f9fa", minHeight: "100vh" }}>
      {/* Header - MODIFICADO */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "1.5rem",
        }}
      >
        <h2 style={{ fontSize: "1.75rem", fontWeight: "bold", color: "#214B4E" }}>
          🌡️ Comparativa de Temperaturas
        </h2>

        {/* BOTONES - MODIFICADO */}
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
            {loading ? "Cargando..." : "Actualizar"}
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

      {/* Empty state - FUERA del contenido PDF */}
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
                }}
              >
                <h3 style={{ fontSize: "1rem", color: "#6c757d", marginBottom: "0.5rem" }}>
                  🧊 Fachada Refrigerada
                </h3>
                <p style={{ fontSize: "2rem", fontWeight: "bold", color: "#0d6efd", margin: 0 }}>
                  {refrigeratedData[0].temperature.toFixed(2)}°C
                </p>
              </div>

              <div
                style={{
                  backgroundColor: "white",
                  padding: "1.5rem",
                  borderRadius: "12px",
                  boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
                }}
              >
                <h3 style={{ fontSize: "1rem", color: "#6c757d", marginBottom: "0.5rem" }}>
                  🌡️ Fachada No Refrigerada
                </h3>
                <p style={{ fontSize: "2rem", fontWeight: "bold", color: "#dc3545", margin: 0 }}>
                  {nonRefrigeratedData[0].temperature.toFixed(2)}°C
                </p>
              </div>

              <div
                style={{
                  backgroundColor: "white",
                  padding: "1.5rem",
                  borderRadius: "12px",
                  boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
                }}
              >
                <h3 style={{ fontSize: "1rem", color: "#6c757d", marginBottom: "0.5rem" }}>
                  📊 Diferencia
                </h3>
                <p style={{ fontSize: "2rem", fontWeight: "bold", color: "#198754", margin: 0 }}>
                  {tempDifference.toFixed(2)}°C
                </p>
                <p style={{ fontSize: "0.875rem", color: "#6c757d", marginTop: "0.5rem" }}>
                  {tempDifference > 0 
                    ? `La refrigeración reduce ${tempDifference.toFixed(2)}°C`
                    : "Sin diferencia significativa"}
                </p>
              </div>
            </div>

            <div
              style={{
                backgroundColor: "white",
                padding: "2rem",
                borderRadius: "12px",
                boxShadow: "0 4px 12px rgba(0,0,0,0.1)",
                height: "350px",
              }}
            >
              <Line data={chartData} options={chartOptions} />
              {lastUpdate && (
                <p style={{ marginTop: "1rem", color: "#6c757d", fontSize: "14px", textAlign: "center" }}>
                  Última actualización: {lastUpdate} | Puntos acumulados: {refrigeratedData.length}
                </p>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
}