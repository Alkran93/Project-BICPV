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

  const fetchTemperatureComparison = useCallback(async () => {
    if (!isMountedRef.current) return;
    setLoading(true);
    setError(null);

    try {
      // Primero obtener la lista de fachadas
      const facadesUrl = `http://localhost:8000/facades`;
      console.log(`� Fetching facades list from: ${facadesUrl}`);

      const facadesResponse = await fetch(facadesUrl);
      if (!facadesResponse.ok) {
        throw new Error(`Error fetching facades: ${facadesResponse.statusText}`);
      }

      const facadesJson = await facadesResponse.json();
      console.log("Facades response:", facadesJson);

      const facades = facadesJson.facades || [];
      
      // Identificar las fachadas refrigerada y no refrigerada
      const refrigerated = facades.find((f: any) => f.facade_type === "refrigerada");
      const nonRefrigerated = facades.find((f: any) => f.facade_type === "no_refrigerada");

      if (!refrigerated || !nonRefrigerated) {
        throw new Error("No se encontraron ambas fachadas (refrigerada y no refrigerada)");
      }

      console.log(`🔍 Fachada refrigerada: ${refrigerated.facade_id}, No refrigerada: ${nonRefrigerated.facade_id}`);

      // Hacer peticiones en paralelo para ambas fachadas
      const [refResponse, nonRefResponse] = await Promise.all([
        fetch(`http://localhost:8000/realtime/facades/${refrigerated.facade_id}`),
        fetch(`http://localhost:8000/realtime/facades/${nonRefrigerated.facade_id}`)
      ]);

      if (!refResponse.ok || !nonRefResponse.ok) {
        throw new Error("Error fetching temperature data for comparison");
      }

      const refData = await refResponse.json();
      const nonRefData = await nonRefResponse.json();

      console.log("Refrigerated data:", refData);
      console.log("Non-refrigerated data:", nonRefData);

      // Extraer temperaturas promedio de los sensores de temperatura
      const extractTemperatures = (facadeData: any): TempData[] => {
        const data = facadeData.data || {};
        const tempSensors = Object.entries(data).filter(([key]) => 
          key.startsWith("Temperature_M") || key.startsWith("Temperatura_")
        );

        if (tempSensors.length === 0) return [];

        // Calcular temperatura promedio
        const avgTemp = tempSensors.reduce((sum, [, sensor]: [string, any]) => 
          sum + (sensor.value || 0), 0
        ) / tempSensors.length;

        return [{
          timestamp: new Date().toISOString(),
          temperature: avgTemp
        }];
      };

      const refTemps = extractTemperatures(refData);
      const nonRefTemps = extractTemperatures(nonRefData);

      if (isMountedRef.current) {
        setRefrigeratedData(refTemps);
        setNonRefrigeratedData(nonRefTemps);
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
    
    // Auto-refresh cada 10 segundos
    const interval = setInterval(fetchTemperatureComparison, 10000);
    
    return () => {
      isMountedRef.current = false;
      clearInterval(interval);
    };
  }, [fetchTemperatureComparison]);

  // Preparar datos para el gráfico
  const hasData = refrigeratedData.length > 0 && nonRefrigeratedData.length > 0;
  
  const chartData = {
    labels: hasData ? ["Temperatura Promedio"] : [],
    datasets: [
      {
        label: "Fachada Refrigerada (°C)",
        data: refrigeratedData.map((d) => d.temperature),
        borderColor: "rgb(54, 162, 235)",
        backgroundColor: "rgba(54, 162, 235, 0.5)",
        borderWidth: 2,
      },
      {
        label: "Fachada No Refrigerada (°C)",
        data: nonRefrigeratedData.map((d) => d.temperature),
        borderColor: "rgb(255, 99, 132)",
        backgroundColor: "rgba(255, 99, 132, 0.5)",
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
        text: "Comparativa de Temperaturas — Fachada Refrigerada vs No Refrigerada",
        font: { size: 18, weight: "bold" as const },
      },
      tooltip: {
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
          text: "Tipo de Fachada",
          font: { size: 14 }
        },
      },
    },
  };

  // Calcular diferencia de temperatura
  const tempDifference = hasData 
    ? nonRefrigeratedData[0].temperature - refrigeratedData[0].temperature 
    : 0;

  return (
    <div style={{ padding: "2rem", backgroundColor: "#f8f9fa", minHeight: "100vh" }}>
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

      {hasData && (
        <>
          {/* Estadísticas comparativas */}
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

          {/* Gráfico de barras */}
          <div
            style={{
              backgroundColor: "white",
              padding: "2rem",
              borderRadius: "12px",
              boxShadow: "0 4px 12px rgba(0,0,0,0.1)",
              height: "500px",
            }}
          >
            <Line data={chartData} options={chartOptions} />
            {lastUpdate && (
              <p style={{ marginTop: "1rem", color: "#6c757d", fontSize: "14px", textAlign: "center" }}>
                Última actualización: {lastUpdate} | Actualización automática cada 10 segundos
              </p>
            )}
          </div>
        </>
      )}
    </div>
  );
}
