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

interface ExchangerData {
  timestamp: string;
  inlet_temp: number;
  outlet_temp: number;
}

export default function WaterTemperatures({ facadeId = 1 }: { facadeId?: number }) {
  const [temps, setTemps] = useState<ExchangerData[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<string>("");
  const isMountedRef = useRef(true);

  const fetchWaterTemps = useCallback(async () => {
    if (!isMountedRef.current) return;
    setLoading(true);
    setError(null);

    try {
      const url = `http://localhost:8000/temperatures/exchanger/${facadeId}?limit=200`;
      console.log(`💧 Fetching exchanger temperatures from: ${url}`);

      const response = await fetch(url);
      if (!response.ok) {
        if (response.status === 404) throw new Error("No exchanger data found for this facade.");
        if (response.status === 500) throw new Error("Internal server error retrieving exchanger data.");
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const json = await response.json();
      console.log("✅ Raw exchanger response:", json);

      const data = json.exchanger_data || [];
      if (Array.isArray(data) && data.length > 0) {
        if (isMountedRef.current) {
          setTemps(data);
          setLastUpdate(new Date().toLocaleString());
        }
      } else {
        if (isMountedRef.current) setTemps([]);
        console.warn("⚠️ exchanger_data is empty");
      }
    } catch (err) {
      console.error("💥 Error fetching exchanger temperatures:", err);
      if (isMountedRef.current) setError((err as Error).message);
    } finally {
      if (isMountedRef.current) setLoading(false);
    }
  }, [facadeId]);

  useEffect(() => {
    isMountedRef.current = true;
    fetchWaterTemps();
    return () => {
      isMountedRef.current = false;
    };
  }, [fetchWaterTemps]);

  const chartData = {
    labels: temps.map((t) => new Date(t.timestamp).toLocaleTimeString()),
    datasets: [
      {
        label: "Temperatura Entrada (°C)",
        data: temps.map((t) => t.inlet_temp),
        borderColor: "#2196f3",
        backgroundColor: "rgba(33,150,243,0.1)",
        tension: 0.3,
        fill: true,
      },
      {
        label: "Temperatura Salida (°C)",
        data: temps.map((t) => t.outlet_temp),
        borderColor: "#ff9800",
        backgroundColor: "rgba(255,152,0,0.1)",
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
        text: "Temperaturas del Agua — Intercambiador",
        font: { size: 18, weight: "bold" as const },
      },
    },
    scales: {
      y: {
        beginAtZero: false,
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
          💧 Temperaturas del Agua — Intercambiador
        </h2>

        <button
          onClick={fetchWaterTemps}
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

      {!loading && !error && temps.length === 0 && (
        <div
          style={{
            backgroundColor: "white",
            padding: "2rem",
            borderRadius: "12px",
            textAlign: "center",
            color: "#6c757d",
          }}
        >
          No hay datos disponibles para el intercambiador (fachada {facadeId}).
        </div>
      )}

      {temps.length > 0 && (
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
