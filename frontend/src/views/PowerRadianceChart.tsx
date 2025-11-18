// PowerRadianceChart.tsx
import { useEffect, useState, useRef } from "react";
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
  TimeScale,
} from "chart.js";
import { Sun, Zap, Calendar, RefreshCw, Download } from "lucide-react";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
  TimeScale
);

interface PowerRadianceDataPoint {
  timestamp: string;
  power_generated: number; // W (no kW)
  irradiance: number; // W/m²
}

interface PowerRadianceResponse {
  facade_id: string;
  facade_type: string;
  data: PowerRadianceDataPoint[];
  summary: {
    total_power: number; // W
    avg_irradiance: number; // W/m²
    max_power: number; // W
    max_irradiance: number; // W/m²
    period: {
      start: string;
      end: string;
    };
  };
}

export default function PowerRadianceChart({ facadeId = "1" }: { facadeId?: string }) {
  const [data, setData] = useState<PowerRadianceResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<string>("");
  const isMountedRef = useRef(true);

  const [startDate, setStartDate] = useState<string>("");
  const [endDate, setEndDate] = useState<string>("");
  const [timeRange, setTimeRange] = useState<string>("24h"); // 24h, 7d, 30d


  const fetchPowerRadianceData = async () => {
    if (!isMountedRef.current) return;

    setLoading(true);
    setError(null);

    try {
      const params = new URLSearchParams();
      if (startDate) params.append("start", startDate);
      if (endDate) params.append("end", endDate);
      if (timeRange && !startDate && !endDate) {
        // Si no hay fechas específicas, usar el rango de tiempo
        params.append("range", timeRange);
      }

      const queryString = params.toString();
      const url = `http://34.135.241.88:8000/chart-data/power-irradiance/${facadeId}${queryString ? `?${queryString}` : ''}`;
      
      console.log(`⚡ [${new Date().toLocaleTimeString()}] Fetching power/radiance data from: ${url}`);

      const response = await fetch(url);

      if (!response.ok) {
        if (response.status === 404) {
          throw new Error("No hay datos de potencia e irradiancia disponibles.");
        }
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const responseData = await response.json();
      console.log("⚡ Power/Irradiance API response:", responseData);

      if (isMountedRef.current) {
        // Transformar los datos del nuevo formato
        const transformedData = transformPowerIrradianceData(responseData);
        setData(transformedData);
        setLastUpdate(new Date().toLocaleString());
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Error desconocido";
      console.error("💥 Error fetching power/irradiance data:", err);

      if (isMountedRef.current) {
        setError(errorMessage);
        setData(null);
      }
    } finally {
      if (isMountedRef.current) {
        setLoading(false);
      }
    }
  };

  const transformPowerIrradianceData = (apiData: any): PowerRadianceResponse => {
    console.log("📊 Transformando datos de API:", apiData);
    
    // Buscar las series por nombre exacto según la documentación
    const irradianceSeries = apiData.series.find((s: any) => s.name === "Irradiance");
    const powerSeries = apiData.series.find((s: any) => s.name === "Generated Power");
    
    const dataPoints: PowerRadianceDataPoint[] = [];
    
    console.log("🔍 Series encontradas:", {
      irradiance: irradianceSeries?.name,
      power: powerSeries?.name,
      irradianceCount: irradianceSeries?.data?.length,
      powerCount: powerSeries?.data?.length
    });

    // Si tenemos ambas series, combinarlas por timestamp
    if (irradianceSeries && powerSeries) {
      // Crear un mapa de irradiancia por timestamp para fácil acceso
      const irradianceMap = new Map();
      irradianceSeries.data.forEach((point: any) => {
        irradianceMap.set(point.ts, point.value);
      });

      // Para cada punto de potencia, buscar la irradiancia correspondiente
      powerSeries.data.forEach((point: any) => {
        const irradianceValue = irradianceMap.get(point.ts);
        if (irradianceValue !== undefined) {
          dataPoints.push({
            timestamp: point.ts,
            power_generated: point.value,
            irradiance: irradianceValue
          });
        }
      });

      // Si no hay coincidencias, usar el método de índice (fallback)
      if (dataPoints.length === 0) {
        const minLength = Math.min(irradianceSeries.data.length, powerSeries.data.length);
        for (let i = 0; i < minLength; i++) {
          dataPoints.push({
            timestamp: irradianceSeries.data[i].ts || powerSeries.data[i].ts,
            power_generated: powerSeries.data[i].value,
            irradiance: irradianceSeries.data[i].value
          });
        }
      }
    }
    // Si solo tenemos irradiancia, calcular la potencia
    else if (irradianceSeries && !powerSeries) {
      const panelArea = apiData.calculation?.panel_area_m2 || 10;
      const efficiency = apiData.calculation?.efficiency || 0.15;
      
      irradianceSeries.data.forEach((point: any) => {
        const powerGenerated = point.value * panelArea * efficiency;
        dataPoints.push({
          timestamp: point.ts,
          power_generated: powerGenerated,
          irradiance: point.value
        });
      });
    }
    // Si solo tenemos potencia
    else if (!irradianceSeries && powerSeries) {
      powerSeries.data.forEach((point: any) => {
        dataPoints.push({
          timestamp: point.ts,
          power_generated: point.value,
          irradiance: 0
        });
      });
    }

    console.log("📈 Puntos de datos transformados:", dataPoints.length);

    // Calcular resumen
    const totalPower = dataPoints.reduce((sum, point) => sum + point.power_generated, 0);
    const avgIrradiance = dataPoints.length > 0 ? 
      dataPoints.reduce((sum, point) => sum + point.irradiance, 0) / dataPoints.length : 0;

    return {
      facade_id: apiData.facade_id || facadeId,
      facade_type: apiData.facade_type || "no_refrigerada",
      data: dataPoints,
      summary: {
        total_power: totalPower,
        avg_irradiance: avgIrradiance,
        max_power: dataPoints.length > 0 ? Math.max(...dataPoints.map(p => p.power_generated)) : 0,
        max_irradiance: dataPoints.length > 0 ? Math.max(...dataPoints.map(p => p.irradiance)) : 0,
        period: {
          start: dataPoints[0]?.timestamp || "",
          end: dataPoints[dataPoints.length - 1]?.timestamp || ""
        }
      }
    };
  };

  useEffect(() => {
    console.log("🔄 PowerRadianceChart mounted");
    isMountedRef.current = true;
    fetchPowerRadianceData();

    return () => {
      isMountedRef.current = false;
    };
  }, [facadeId]);

  useEffect(() => {
    if (isMountedRef.current) {
      fetchPowerRadianceData();
    }
  }, [startDate, endDate, timeRange]);

  // Preparar datos para el gráfico
  const chartData = {
    labels: data?.data.map(point => new Date(point.timestamp).toLocaleTimeString()) || [],
    datasets: [
      {
        label: "Potencia Generada (kW)",
        data: data?.data.map(point => point.power_generated) || [],
        borderColor: "#ff6b00",
        backgroundColor: "rgba(255, 107, 0, 0.1)",
        borderWidth: 3,
        tension: 0.4,
        fill: true,
        yAxisID: 'y',
        pointRadius: 2,
        pointHoverRadius: 6,
      },
      {
        label: "Irradiancia (W/m²)",
        data: data?.data.map(point => point.irradiance) || [],
        borderColor: "#ffd700",
        backgroundColor: "rgba(255, 215, 0, 0.1)",
        borderWidth: 2,
        tension: 0.4,
        fill: true,
        yAxisID: 'y1',
        pointRadius: 2,
        pointHoverRadius: 6,
      }
    ],
  };

  const chartOptions = {
    responsive: true,
    interaction: {
      mode: 'index' as const,
      intersect: false,
    },
    plugins: {
      legend: { 
        display: true, 
        position: "top" as const,
        labels: {
          usePointStyle: true,
          padding: 20,
        }
      },
      title: {
        display: true,
        text: "Potencia Generada vs Irradiancia en el Tiempo",
        font: { size: 18, weight: "bold" as const },
        padding: { bottom: 20 },
      },
      tooltip: {
        callbacks: {
          label: function (context: any) {
            let label = context.dataset.label || '';
            if (label) {
              label += ': ';
            }
            if (context.parsed.y !== null) {
              if (context.dataset.label.includes('Potencia')) {
                label += `${context.parsed.y.toFixed(2)} kW`;
              } else {
                label += `${context.parsed.y.toFixed(0)} W/m²`;
              }
            }
            return label;
          },
        },
      },
    },
    scales: {
      x: {
        title: {
          display: true,
          text: "Tiempo",
          font: { size: 14, weight: "bold" as const },
        },
        grid: {
          color: "rgba(0,0,0,0.1)",
        }
      },
      y: {
        type: 'linear' as const,
        display: true,
        position: 'left' as const,
        title: {
          display: true,
          text: "Potencia (W)",
          font: { size: 14, weight: "bold" as const },
        },
        grid: {
          color: "rgba(255, 107, 0, 0.1)",
        }
      },
      y1: {
        type: 'linear' as const,
        display: true,
        position: 'right' as const,
        title: {
          display: true,
          text: "Irradiancia (W/m²)",
          font: { size: 14, weight: "bold" as const },
        },
        grid: {
          drawOnChartArea: false,
        },
      },
    },
  };

  const handleExportCSV = () => {
    if (!data) return;

    const headers = ["Timestamp", "Potencia_Generada_kW", "Irradiancia_W_m2"];
    const csvData = data.data.map(point => [
      point.timestamp,
      point.power_generated,
      point.irradiance
    ]);

    const csvContent = [
      headers.join(","),
      ...csvData.map(row => row.join(","))
    ].join("\n");

    const blob = new Blob([csvContent], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `potencia-irradiancia-fachada-${facadeId}.csv`;
    link.click();
    URL.revokeObjectURL(url);
  };

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
              <Zap size={32} color="#ff6b00" />
              Potencia e Irradiancia
            </h1>
            <p style={{ margin: 0, color: "#6c757d", fontSize: "14px" }}>
              Fachada {facadeId} - {data?.facade_type || "Cargando..."}
            </p>
            {lastUpdate && (
              <p style={{ margin: "0.25rem 0 0 0", color: "#888", fontSize: "12px" }}>
                Última actualización: {lastUpdate}
              </p>
            )}
          </div>

          <div style={{ display: "flex", gap: "1rem" }}>
            <button
              onClick={fetchPowerRadianceData}
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

            {!loading && data && (
              <button
                onClick={handleExportCSV}
                style={{
                  padding: "0.75rem 1.5rem",
                  backgroundColor: "#28a745",
                  color: "white",
                  border: "none",
                  borderRadius: "8px",
                  cursor: "pointer",
                  fontSize: "14px",
                  fontWeight: "600",
                  display: "flex",
                  alignItems: "center",
                  gap: "0.5rem",
                }}
              >
                <Download size={16} />
                Exportar CSV
              </button>
            )}
          </div>
        </div>

        {/* Filtros */}
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "1fr 1fr 1fr",
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
              Rango de Tiempo
            </label>
            <select
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value)}
              style={{
                width: "100%",
                padding: "0.5rem",
                border: "1px solid #ced4da",
                borderRadius: "4px",
                fontSize: "14px",
              }}
            >
              <option value="24h">Últimas 24 horas</option>
              <option value="7d">Últimos 7 días</option>
              <option value="30d">Últimos 30 días</option>
            </select>
          </div>

          <div>
            <label style={{ display: "block", fontSize: "12px", fontWeight: "600", color: "#495057", marginBottom: "0.5rem" }}>
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
      {data?.summary && (
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
              textAlign: "center",
            }}
          >
            <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "0.5rem", marginBottom: "0.5rem" }}>
              <Zap size={20} color="#ff6b00" />
              <h3 style={{ margin: 0, fontSize: "14px", color: "#6c757d", fontWeight: "600" }}>
                POTENCIA TOTAL
              </h3>
            </div>
            <p style={{ margin: 0, fontSize: "2rem", fontWeight: "bold", color: "#ff6b00" }}>
              {data.summary.total_power.toFixed(2)} kW
            </p>
          </div>

          <div
            style={{
              backgroundColor: "white",
              padding: "1.5rem",
              borderRadius: "12px",
              boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
              border: "1px solid #e9ecef",
              textAlign: "center",
            }}
          >
            <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "0.5rem", marginBottom: "0.5rem" }}>
              <Sun size={20} color="#ffd700" />
              <h3 style={{ margin: 0, fontSize: "14px", color: "#6c757d", fontWeight: "600" }}>
                IRRADIANCIA PROMEDIO
              </h3>
            </div>
            <p style={{ margin: 0, fontSize: "2rem", fontWeight: "bold", color: "#ffd700" }}>
              {data.summary.avg_irradiance.toFixed(0)} W/m²
            </p>
          </div>

          <div
            style={{
              backgroundColor: "white",
              padding: "1.5rem",
              borderRadius: "12px",
              boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
              border: "1px solid #e9ecef",
              textAlign: "center",
            }}
          >
            <h3 style={{ margin: "0 0 0.5rem 0", fontSize: "14px", color: "#6c757d", fontWeight: "600" }}>
              PICO DE POTENCIA
            </h3>
            <p style={{ margin: 0, fontSize: "1.5rem", fontWeight: "bold", color: "#28a745" }}>
              {data.summary.max_power.toFixed(2)} kW
            </p>
          </div>

          <div
            style={{
              backgroundColor: "white",
              padding: "1.5rem",
              borderRadius: "12px",
              boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
              border: "1px solid #e9ecef",
              textAlign: "center",
            }}
          >
            <h3 style={{ margin: "0 0 0.5rem 0", fontSize: "14px", color: "#6c757d", fontWeight: "600" }}>
              PICO DE IRRADIANCIA
            </h3>
            <p style={{ margin: 0, fontSize: "1.5rem", fontWeight: "bold", color: "#dc3545" }}>
              {data.summary.max_irradiance.toFixed(0)} W/m²
            </p>
          </div>
        </div>
      )}

      {/* Gráfico principal */}
      {!loading && !error && data && (
        <div
          style={{
            backgroundColor: "white",
            padding: "2rem",
            borderRadius: "16px",
            boxShadow: "0 4px 16px rgba(0,0,0,0.08)",
            marginBottom: "2rem",
          }}
        >
          <Line data={chartData} options={chartOptions} height={400} />
        </div>
      )}

      {/* Información adicional */}
      {data?.summary?.period && (
        <div
          style={{
            backgroundColor: "#e7f3ff",
            padding: "1rem",
            borderRadius: "8px",
            border: "1px solid #b3d9ff",
            marginBottom: "2rem",
          }}
        >
          <h4 style={{ margin: "0 0 0.5rem 0", color: "#0066cc" }}>📅 Período de Datos</h4>
          <div style={{ fontSize: "0.9rem", color: "#0066cc" }}>
            <strong>Inicio:</strong> {new Date(data.summary.period.start).toLocaleString()} | 
            <strong> Fin:</strong> {new Date(data.summary.period.end).toLocaleString()} |
            <strong> Total de puntos:</strong> {data.data.length}
          </div>
        </div>
      )}

      {/* Empty state */}
      {!loading && !error && (!data || data.data.length === 0) && (
        <div
          style={{
            padding: "4rem",
            textAlign: "center",
            backgroundColor: "white",
            borderRadius: "12px",
            boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
          }}
        >
          <Sun size={64} color="#6c757d" style={{ marginBottom: "1rem" }} />
          <h3 style={{ color: "#6c757d", margin: 0 }}>No hay datos de potencia e irradiancia</h3>
          <p style={{ color: "#6c757d", margin: "0.5rem 0 0 0" }}>
            Intenta ajustar los filtros de fecha o verifica la conexión con el sistema.
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
          <div style={{ fontSize: "3rem", marginBottom: "1rem" }}>⚡</div>
          <h3 style={{ color: "#6c757d", margin: 0 }}>Cargando datos de potencia e irradiancia...</h3>
        </div>
      )}
    </div>
  );
}