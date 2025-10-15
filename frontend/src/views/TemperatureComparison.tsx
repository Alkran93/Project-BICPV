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
  refrigerant_temp: number;
  water_temp: number;
}

export default function TemperatureComparison({ facadeId = 1 }: { facadeId?: number }) {
  const [data, setData] = useState<TempData[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<string>("");
  const isMountedRef = useRef(true);

  const fetchTemperatureComparison = useCallback(async () => {
    if (!isMountedRef.current) return;
    setLoading(true);
    setError(null);

    try {
      const url = `http://localhost:8000/temperatures/refrigerant-cycle/${facadeId}?limit=300`;
      console.log(`🌡️ Fetching temperature comparison from: ${url}`);

      const response = await fetch(url);
      if (!response.ok) {
        if (response.status === 404)
          throw new Error("No comparison data found for this facade.");
        if (response.status === 500)
          throw new Error("Server error retrieving comparison data.");
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const json = await response.json();
      console.log("✅ Temperature comparison response:", json);

      const tempData = json.refrigerant_cycle_data || json.data || [];

      if (Array.isArray(tempData) && tempData.length > 0) {
        if (isMountedRef.current) {
          setData(tempData);
          setLastUpdate(new Date().toLocaleString());
        }
      } else {
        console.warn("⚠️ No data found in response.");
        if (isMountedRef.current) setData([]);
      }
    } catch (err) {
      console.error("💥 Error fetching temperature comparison:", err);
      if (isMountedRef.current) setError((err as Error).message);
    } finally {
      if (isMountedRef.current) setLoading(false);
    }
  }, [facadeId]);

  useEffect(() => {
    isMountedRef.current = true;
    fetchTemperatureComparison();
    return () => {
      isMountedRef.current = false;
    };
  }, [fetchTemperatureComparison]);

  const chartData = {
    labels: data.map((d) => new Date(d.timestamp).toLocaleTimeString()),
    datasets: [
      {
        label: "Temperatura Refrigerante (°C)",
        data: data.map((d) => d.refrigerant_temp),
        borderColor: "rgb(255, 99, 132)",
        backgroundColor: "rgba(255, 99, 132, 0.1)",
        tension: 0.3,
        fill: true,
      },
      {
        label: "Temperatura Agua (°C)",
        data: data.map((d) => d.water_temp),
        borderColor: "rgb(54, 162, 235)",
        backgroundColor: "rgba(54, 162, 235, 0.1)",
        tension: 0.3,
        fill: true,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: { position: "top" as const },
      title: {
        display: true,
        text: "Comparativa de Temperaturas — Ciclo Refrigerante vs Agua",
        font: { size: 18, weight: "bold" as const },
      },
    },
    scales: {
      y: {
        title: {
          display: true,
          text: "Temperatura (°C)",
        },
      },
      x: {
        title: {
          display: true,
          text: "Hora",
        },
      },
    },
  };

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
          🌡️ Comparativa de Temperaturas — Intercambiador
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

      {!loading && !error && data.length === 0 && (
        <div
          style={{
            backgroundColor: "white",
            padding: "2rem",
            borderRadius: "12px",
            textAlign: "center",
            color: "#6c757d",
          }}
        >
          No hay datos de comparación disponibles (fachada {facadeId}).
        </div>
      )}

      {data.length > 0 && (
        <div
          style={{
            backgroundColor: "white",
            padding: "2rem",
            borderRadius: "12px",
            boxShadow: "0 4px 12px rgba(0,0,0,0.1)",
          }}
        >
          <Line data={chartData} options={chartOptions} height={400} />
          {lastUpdate && (
            <p style={{ marginTop: "1rem", color: "#6c757d", fontSize: "14px" }}>
              Última actualización: {lastUpdate}
            </p>
          )}
        </div>
      )}
    </div>
  );
}
