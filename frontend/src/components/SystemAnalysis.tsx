import {
  ArrowLeft,
  Thermometer,
  Activity,
  AlertTriangle,
  CheckCircle,
} from "lucide-react";
import "../styles/SystemAnalysis.css";
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

type SystemAnalysisProps = {
  title: string;
  sensors: number[];
  refrigerated: boolean;
  refrigeratedData: any;
  nonRefrigeratedData: any;
  onBack: () => void;
};

export default function SystemAnalysis({
  title,
  sensors,
  refrigeratedData,
  onBack,
}: SystemAnalysisProps) {
  // Calcular estadísticas del sistema
  const calculateSystemStats = () => {
    if (sensors.length === 0) return null;

    const validSensors = sensors.filter(temp => temp !== undefined);
    const avgTemp =
      validSensors.reduce((sum, temp) => sum + temp, 0) / validSensors.length;
    const minTemp = Math.min(...validSensors);
    const maxTemp = Math.max(...validSensors);
    const tempRange = maxTemp - minTemp;
    const alertSensors = validSensors.filter(temp => temp < 25).length;
    const modules = [];
    for (let i = 0; i < sensors.length; i += 3) {
      const moduleSensors = sensors.slice(i, i + 3);
      const avg = moduleSensors.reduce((a, b) => a + b, 0) / moduleSensors.length;
      modules.push(avg);
    }
    // Calcular medias por módulo
    const moduleAverages: number[] = [];
    for (let i = 0; i < sensors.length; i += 3) {
      const group = sensors.slice(i, i + 3);
      const avg = group.reduce((a, b) => a + b, 0) / group.length;
      moduleAverages.push(avg);
    }
    const totalAverage =
      moduleAverages.reduce((a, b) => a + b, 0) / moduleAverages.length;
    const totalAvg = modules.reduce((a, b) => a + b, 0) / modules.length;

    const chartData = {
      labels: ["Módulo 1", "Módulo 2", "Módulo 3", "Módulo 4", "Módulo 5", "Total"],
      datasets: [
        {
          label: "Temperatura Promedio (°C)",
          data: [...moduleAverages, totalAverage],
          borderColor: "#3b3b3bff",
          backgroundColor: "rgba(33, 75, 78, 0.2)",
          fill: true,
          tension: 0.3,
          pointRadius: 5,
          pointBackgroundColor: "#214B4E",
        },
      ],
    };

    const chartOptions = {
      responsive: true,
      plugins: {
        legend: {
          position: "top" as const,
        },
        title: {
          display: true,
          text: "Promedio de Temperaturas por Módulo y Total del Sistema",
        },
      },
    };

    // Análisis de eficiencia basado en temperatura
    let efficiency = "Óptima";
    let efficiencyColor = "#28a745";
    let efficiencyPercent = 95;

    if (avgTemp > 40) {
      efficiency = "Crítica";
      efficiencyColor = "#e63946";
      efficiencyPercent = 60;
    } else if (avgTemp > 35) {
      efficiency = "Baja";
      efficiencyColor = "#ffc107";
      efficiencyPercent = 75;
    } else if (avgTemp > 30) {
      efficiency = "Regular";
      efficiencyColor = "#fd7e14";
      efficiencyPercent = 85;
    }

    return {
      avgTemp,
      minTemp,
      maxTemp,
      tempRange,
      alertSensors,
      efficiency,
      efficiencyColor,
      efficiencyPercent,
      totalSensors: validSensors.length,
      modules,
      totalAvg,
      totalAverage,
      chartData,
      chartOptions,
    };
  };

  const stats = calculateSystemStats();

  if (!stats) {
    return (
      <div className="system-analysis-container">
        <button onClick={onBack} className="back-button">
          <ArrowLeft size={20} />
          <span>Volver</span>
        </button>
        <p>No hay datos disponibles para el análisis del sistema.</p>
      </div>
    );
  }

  return (
    <div className="system-analysis-container">
      {/* Header */}
      <div className="analysis-header">
        <button
          onClick={onBack}
          className="back-button"
          aria-label="Volver a vista de panel"
        >
          <ArrowLeft size={20} />
          <span>Volver</span>
        </button>

        <div className="analysis-title-section">
          <h1 className="analysis-title">
            <Thermometer size={32} />
            Análisis Térmico del Sistema - {title}
          </h1>
          <p className="analysis-subtitle">
            Análisis detallado de rendimiento térmico y eficiencia operativa
          </p>
        </div>
      </div>

      {/* Indicadores principales */}
      <div className="key-indicators">
        <div className="indicator-card primary">
          <div className="indicator-icon">
            <Thermometer size={24} />
          </div>
          <div className="indicator-content">
            <div className="indicator-value">{stats.avgTemp.toFixed(1)}°C</div>
            <div className="indicator-label">Temperatura Promedio</div>
          </div>
        </div>

        <div className="indicator-card">
          <div className="indicator-icon">
            <Activity size={24} />
          </div>
          <div className="indicator-content">
            <div className="indicator-value" style={{ color: stats.efficiencyColor }}>
              {stats.efficiencyPercent}%
            </div>
            <div className="indicator-label">Eficiencia</div>
          </div>
        </div>

        <div className="indicator-card">
          <div className="indicator-icon">
            {stats.alertSensors > 0 ? (
              <AlertTriangle size={24} />
            ) : (
              <CheckCircle size={24} />
            )}
          </div>
          <div className="indicator-content">
            <div
              className="indicator-value"
              style={{ color: stats.alertSensors > 0 ? "#e63946" : "#28a745" }}
            >
              {stats.alertSensors}
            </div>
            <div className="indicator-label">Sensores en Alerta</div>
          </div>
        </div>

        <div className="indicator-card">
          <div className="indicator-icon">
            <Activity size={24} />
          </div>
          <div className="indicator-content">
            <div className="indicator-value">{stats.tempRange.toFixed(1)}°C</div>
            <div className="indicator-label">Variación Térmica</div>
          </div>
        </div>
      </div>

      {/* Análisis detallado */}
      <div className="detailed-analysis">
        <div className="analysis-section">
          <h2 className="section-title">Distribución de Temperatura</h2>
          <div className="temp-distribution">
            <div className="temp-range-bar">
              <div className="temp-marker min">
                <span className="temp-value">{stats.minTemp}°C</span>
                <span className="temp-label">Mínima</span>
              </div>

              <div className="temp-bar">
                <div
                  className="temp-fill"
                  style={{
                    background: `linear-gradient(to right, #28a745, ${stats.avgTemp > 35 ? "#e63946" : "#ffc107"})`,
                    width: "100%",
                  }}
                ></div>
                <div
                  className="temp-avg-marker"
                  style={{
                    left: `${((stats.avgTemp - stats.minTemp) / stats.tempRange) * 100}%`,
                  }}
                >
                  <span className="avg-value">{stats.avgTemp.toFixed(1)}°C</span>
                </div>
              </div>

              <div className="temp-marker max">
                <span className="temp-value">{stats.maxTemp}°C</span>
                <span className="temp-label">Máxima</span>
              </div>
            </div>
          </div>
        </div>

        <div className="analysis-section">
          <h2 className="section-title">Gráfica de Promedios</h2>
          <Line data={stats.chartData} options={stats.chartOptions} />
        </div>

        <div className="analysis-section">
          <h2 className="section-title">Temperatura por Módulos</h2>
          <div className="modules-grid">
            {stats.modules.map((avg, i) => (
              <div key={i} className="module-card">
                <div className="module-title">Módulo {i + 1}</div>
                <div className="module-value">{avg.toFixed(1)}°C</div>
              </div>
            ))}
          </div>

          <div className="total-average">
            <strong>Media Total del Sistema:</strong> {stats.totalAverage.toFixed(1)}°C
          </div>
        </div>

        <div className="analysis-section">
          <h2 className="section-title">Estado del Sistema</h2>
          <div className="system-status">
            <div className="status-item">
              <div
                className="status-icon"
                style={{ backgroundColor: stats.efficiencyColor }}
              >
                <Activity size={20} color="white" />
              </div>
              <div className="status-content">
                <h3 className="status-title">Eficiencia del Sistema</h3>
                <p className="status-description">
                  El sistema presenta una eficiencia{" "}
                  <strong style={{ color: stats.efficiencyColor }}>
                    {stats.efficiency.toLowerCase()}
                  </strong>
                  .
                  {stats.efficiency === "Crítica" &&
                    " Se requiere intervención inmediata."}
                  {stats.efficiency === "Baja" &&
                    " Se recomienda revisión del sistema de refrigeración."}
                  {stats.efficiency === "Regular" && " Monitoreo continuo recomendado."}
                  {stats.efficiency === "Óptima" &&
                    " El sistema opera dentro de parámetros normales."}
                </p>
              </div>
            </div>

            <div className="status-item">
              <div
                className="status-icon"
                style={{ backgroundColor: refrigeratedData ? "#214B4E" : "#e63946" }}
              >
                {refrigeratedData ? (
                  <CheckCircle size={20} color="white" />
                ) : (
                  <AlertTriangle size={20} color="white" />
                )}
              </div>
              <div className="status-content">
                <h3 className="status-title">Sistema de Refrigeración</h3>
                <p className="status-description">
                  {refrigeratedData
                    ? "Sistema de refrigeración activo. Manteniendo temperaturas óptimas de operación."
                    : "Sin sistema de refrigeración activo. Las temperaturas pueden elevarse durante picos de radiación solar."}
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="analysis-section">
          <h2 className="section-title">Recomendaciones</h2>
          <div className="recommendations">
            {stats.avgTemp > 40 && (
              <div className="recommendation critical">
                <AlertTriangle size={16} />
                <span>Verificar sistema de refrigeración inmediatamente</span>
              </div>
            )}
            {stats.alertSensors > 3 && (
              <div className="recommendation warning">
                <AlertTriangle size={16} />
                <span>
                  Múltiples sensores en estado de alerta - Revisar distribución térmica
                </span>
              </div>
            )}
            {stats.tempRange > 15 && (
              <div className="recommendation info">
                <Activity size={16} />
                <span>
                  Alta variación térmica detectada - Considerar optimización de
                  ventilación
                </span>
              </div>
            )}
            {stats.efficiency === "Óptima" && (
              <div className="recommendation success">
                <CheckCircle size={16} />
                <span>
                  Sistema operando correctamente - Mantener rutinas de mantenimiento
                </span>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
