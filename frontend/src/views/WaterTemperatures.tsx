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
import PDFExportButton from "./PDFExportButton"; // ← AGREGAR IMPORT

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

interface ExchangerDataPoint {
  ts: string;
  value: number;
}

export default function WaterTemperatures({ facadeId = 1 }: { facadeId?: number }) {
  // Removed unused state variable - using inletReadings and outletReadings instead
  // const [temps, setTemps] = useState<ExchangerDataPoint[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<string>("");
  const isMountedRef = useRef(true);

  const [inletReadings, setInletReadings] = useState<ExchangerDataPoint[]>([]);
  const [outletReadings, setOutletReadings] = useState<ExchangerDataPoint[]>([]);

  const fetchWaterTemps = useCallback(async () => {
    if (!isMountedRef.current) return;
    setLoading(true);
    setError(null);

    try {
      const facadesUrl = `http://localhost:8000/facades`;
      console.log(`🔍 Fetching facades list from: ${facadesUrl}`);

      const facadesResponse = await fetch(facadesUrl);
      if (!facadesResponse.ok) {
        throw new Error(`Error fetching facades: ${facadesResponse.statusText}`);
      }

      const facadesJson = await facadesResponse.json();
      const facades = facadesJson.facades || [];
      const refrigerated = facades.find((f: any) => f.facade_type === "refrigerada");

      if (!refrigerated) {
        throw new Error("No se encontró ninguna fachada refrigerada");
      }

      const url = `http://localhost:8000/temperatures/exchanger/${refrigerated.facade_id}?limit=100`;
      console.log(`💧 Fetching exchanger temperatures from: ${url}`);

      const response = await fetch(url);
      if (!response.ok) {
        if (response.status === 404) throw new Error("No exchanger data found for this facade.");
        if (response.status === 500) throw new Error("Internal server error retrieving exchanger data.");
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const json = await response.json();
      console.log("✅ Raw exchanger response:", json);

      const inlet = json.exchanger_data?.inlet?.readings || [];
      const outlet = json.exchanger_data?.outlet?.readings || [];

      const inletNormalized: ExchangerDataPoint[] = inlet.map((r: any) => ({
        ts: r.ts,
        value: Number(r.value),
      }));
      const outletNormalized: ExchangerDataPoint[] = outlet.map((r: any) => ({
        ts: r.ts,
        value: Number(r.value),
      }));

      console.log("inletNormalized length:", inletNormalized.length, "outletNormalized length:", outletNormalized.length);

      if (isMountedRef.current) {
        setInletReadings(inletNormalized);
        setOutletReadings(outletNormalized);
        // Removed setTemps(inletNormalized) - temps state variable was removed
        setLastUpdate(new Date().toLocaleString());
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

  const { labels, inletSeries, outletSeries } = (() => {
    const tsSet = new Set<string>();
    inletReadings.forEach((r) => tsSet.add(r.ts));
    outletReadings.forEach((r) => tsSet.add(r.ts));

    const labelsArr = Array.from(tsSet).sort((a, b) => new Date(a).getTime() - new Date(b).getTime());

    const inletMap = new Map(inletReadings.map((r) => [r.ts, r.value]));
    const outletMap = new Map(outletReadings.map((r) => [r.ts, r.value]));

    const inletData = labelsArr.map((ts) => (inletMap.has(ts) ? inletMap.get(ts)! : null));
    const outletData = labelsArr.map((ts) => (outletMap.has(ts) ? outletMap.get(ts)! : null));

    const labelsFormatted = labelsArr.map((ts) => {
      try {
        return new Date(ts).toLocaleTimeString();
      } catch {
        return ts;
      }
    });

    return { labels: labelsFormatted, inletSeries: inletData, outletSeries: outletData };
  })();

  const chartData = {
    labels,
    datasets: [
      {
        label: "Temperatura Entrada (°C)",
        data: inletSeries,
        borderColor: "#2196f3",
        backgroundColor: "rgba(33,150,243,0.1)",
        tension: 0.3,
        fill: true,
        spanGaps: true,
      },
      {
        label: "Temperatura Salida (°C)",
        data: outletSeries,
        borderColor: "#ff9800",
        backgroundColor: "rgba(255,152,0,0.1)",
        tension: 0.3,
        fill: true,
        spanGaps: true,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: { position: "top" as const },
      title: {
        display: true,
        text: "Temperaturas del Agua – Intercambiador",
        font: { size: 18, weight: "bold" as const },
      },
      tooltip: {
        mode: 'index' as const,
        intersect: false,
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

  // Calcular estadísticas
  const stats = labels.length > 0 ? {
    avgInlet: inletSeries.filter(v => v !== null).reduce((sum, v) => sum + v!, 0) / inletSeries.filter(v => v !== null).length,
    avgOutlet: outletSeries.filter(v => v !== null).reduce((sum, v) => sum + v!, 0) / outletSeries.filter(v => v !== null).length,
    maxInlet: Math.max(...inletSeries.filter(v => v !== null) as number[]),
    maxOutlet: Math.max(...outletSeries.filter(v => v !== null) as number[]),
    minInlet: Math.min(...inletSeries.filter(v => v !== null) as number[]),
    minOutlet: Math.min(...outletSeries.filter(v => v !== null) as number[]),
  } : null;

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
          💧 Temperaturas del Agua – Intercambiador
        </h2>

        {/* BOTONES - MODIFICADO */}
        <div style={{ display: "flex", gap: "1rem" }}>
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

          {/* NUEVO: Botón PDF */}
          {!loading && !error && labels.length > 0 && (
            <PDFExportButton
              title="Temperaturas del Agua - Intercambiador"
              elementId="water-temps-pdf-content"
              filename="temperaturas-intercambiador"
            />
          )}
        </div>
      </div>

      {/* Error - FUERA del contenido PDF */}
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
      {!loading && !error && labels.length === 0 && (
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

      {/* CONTENIDO EXPORTABLE - AGREGAR DIV CON ID */}
      <div id="water-temps-pdf-content">
        {labels.length > 0 && (
          <>
            {/* Estadísticas */}
            {stats && (
              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
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
                  <h3 style={{ fontSize: "0.875rem", color: "#6c757d", marginBottom: "0.5rem", fontWeight: "600" }}>
                    ENTRADA PROMEDIO
                  </h3>
                  <p style={{ fontSize: "1.75rem", fontWeight: "bold", color: "#2196f3", margin: 0 }}>
                    {stats.avgInlet.toFixed(2)}°C
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
                  <h3 style={{ fontSize: "0.875rem", color: "#6c757d", marginBottom: "0.5rem", fontWeight: "600" }}>
                    SALIDA PROMEDIO
                  </h3>
                  <p style={{ fontSize: "1.75rem", fontWeight: "bold", color: "#ff9800", margin: 0 }}>
                    {stats.avgOutlet.toFixed(2)}°C
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
                  <h3 style={{ fontSize: "0.875rem", color: "#6c757d", marginBottom: "0.5rem", fontWeight: "600" }}>
                    RANGO ENTRADA
                  </h3>
                  <p style={{ fontSize: "1.25rem", fontWeight: "bold", color: "#2196f3", margin: 0 }}>
                    {stats.minInlet.toFixed(2)} - {stats.maxInlet.toFixed(2)}°C
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
                  <h3 style={{ fontSize: "0.875rem", color: "#6c757d", marginBottom: "0.5rem", fontWeight: "600" }}>
                    RANGO SALIDA
                  </h3>
                  <p style={{ fontSize: "1.25rem", fontWeight: "bold", color: "#ff9800", margin: 0 }}>
                    {stats.minOutlet.toFixed(2)} - {stats.maxOutlet.toFixed(2)}°C
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
                  <h3 style={{ fontSize: "0.875rem", color: "#6c757d", marginBottom: "0.5rem", fontWeight: "600" }}>
                    DIFERENCIA Δ
                  </h3>
                  <p style={{ fontSize: "1.75rem", fontWeight: "bold", color: "#198754", margin: 0 }}>
                    {(stats.avgInlet - stats.avgOutlet).toFixed(2)}°C
                  </p>
                  <p style={{ fontSize: "0.75rem", color: "#6c757d", marginTop: "0.25rem" }}>
                    Entrada - Salida
                  </p>
                </div>
              </div>
            )}

            {/* Gráfico */}
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
                <p style={{ marginTop: "1rem", color: "#6c757d", fontSize: "14px", textAlign: "center" }}>
                  Última actualización: {lastUpdate}
                </p>
              )}
            </div>
          </>
        )}
      </div>
      {/* FIN DEL CONTENIDO EXPORTABLE */}
    </div>
  );
}