import { useEffect, useState, useRef } from "react";
import { Clock, AlertCircle, Filter, Download, Calendar } from "lucide-react";

interface Alert {
  alert_id: string;
  timestamp: string;
  alert_type: string;
  severity: string;
  sensor_id: string;
  facade_id: string;
  description: string;
  resolved: boolean;
  resolved_at?: string;
}

interface AlertsHistoryResponse {
  count: number;
  facade_type: string | null;
  time_range_hours: number;
  alerts: Alert[];
}

export default function AlertsHistory() {
  const [responseData, setResponseData] = useState<AlertsHistoryResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<string>("");
  const isMountedRef = useRef(true);

  // Filtros
  const [limitFilter, setLimitFilter] = useState<number>(100);
  const [facadeTypeFilter, setFacadeTypeFilter] = useState<string>("");
  const [hoursFilter, setHoursFilter] = useState<number>(168); // 1 semana por defecto

  const fetchAlertsHistory = async () => {
    if (!isMountedRef.current) return;

    setLoading(true);
    setError(null);

    try {
      // Usar endpoint de anomalías que combina errores y umbrales
      const params = new URLSearchParams();
      params.append("limit", limitFilter.toString());
      if (facadeTypeFilter) params.append("facade_type", facadeTypeFilter);
      params.append("hours", hoursFilter.toString());

      const url = `http://localhost:8000/alerts/anomalies?${params.toString()}`;
      console.log(`📜 [${new Date().toLocaleTimeString()}] Fetching alerts history from: ${url}`);

      const response = await fetch(url);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      console.log("📊 Alerts History API response:", data);

      // Transformar anomalías al formato de alertas
      const transformedAlerts: Alert[] = (data.anomalies || []).map((anomaly: any) => {
        const anomalyType = anomaly.value < anomaly.expected_range.min 
          ? "below_minimum" 
          : anomaly.value > anomaly.expected_range.max 
            ? "above_maximum" 
            : "threshold_exceeded";

        return {
          alert_id: `anomaly_${anomaly.device_id}_${new Date(anomaly.ts).getTime()}`,
          timestamp: anomaly.ts,
          alert_type: anomalyType,
          severity: anomaly.severity || "warning",
          sensor_id: anomaly.device_id,
          facade_id: anomaly.facade_id,
          description: `Sensor ${anomaly.sensor_name} registró ${anomaly.value?.toFixed(2)}°C, fuera del rango esperado (${anomaly.expected_range.min}°C - ${anomaly.expected_range.max}°C)`,
          resolved: false,
        };
      });

      const transformedData: AlertsHistoryResponse = {
        count: transformedAlerts.length,
        facade_type: data.facade_type,
        time_range_hours: data.time_range_hours,
        alerts: transformedAlerts,
      };

      if (isMountedRef.current) {
        setResponseData(transformedData);
        setLastUpdate(new Date().toLocaleString());
        console.log(`✅ Successfully loaded ${transformedData.count} alerts from history`);
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Unknown error";
      console.error("💥 Error fetching alerts history:", err);

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
    console.log("🔄 AlertsHistory mounted - Loading history");
    isMountedRef.current = true;
    fetchAlertsHistory();

    return () => {
      isMountedRef.current = false;
    };
  }, []);

  // Recargar cuando cambian los filtros
  useEffect(() => {
    if (isMountedRef.current) {
      fetchAlertsHistory();
    }
  }, [limitFilter, facadeTypeFilter, hoursFilter]);

  const getSeverityColor = (severity: string) => {
    const severityLower = severity?.toLowerCase() || "";

    if (severityLower.includes("critical") || severityLower.includes("high")) {
      return "#dc2626";
    }

    if (severityLower.includes("medium") || severityLower.includes("warning")) {
      return "#f59e0b";
    }

    return "#3b82f6";
  };

  const getSeverityBadgeStyle = (severity: string) => {
    const severityLower = severity?.toLowerCase() || "";

    if (severityLower.includes("critical") || severityLower.includes("high")) {
      return { bg: "#fee2e2", color: "#991b1b", border: "#dc2626" };
    }

    if (severityLower.includes("medium") || severityLower.includes("warning")) {
      return { bg: "#fef3c7", color: "#92400e", border: "#f59e0b" };
    }

    return { bg: "#dbeafe", color: "#1e40af", border: "#3b82f6" };
  };

  const exportToCSV = () => {
    if (!responseData || responseData.alerts.length === 0) return;

    const headers = ["Timestamp", "Alert ID", "Type", "Severity", "Sensor", "Facade", "Description", "Resolved"];
    const rows = responseData.alerts.map(alert => [
      alert.timestamp,
      alert.alert_id,
      alert.alert_type,
      alert.severity,
      alert.sensor_id,
      alert.facade_id,
      alert.description,
      alert.resolved ? "Yes" : "No"
    ]);

    const csvContent = [
      headers.join(","),
      ...rows.map(row => row.map(cell => `"${cell}"`).join(","))
    ].join("\n");

    const blob = new Blob([csvContent], { type: "text/csv" });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `alerts_history_${new Date().toISOString().split("T")[0]}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  const alerts = responseData?.alerts || [];

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
            <h1 style={{ margin: "0 0 0.5rem 0", fontSize: "2rem", fontWeight: "bold", color: "#2c3e50" }}>
              Historial de Alertas
            </h1>
            <div style={{ display: "flex", alignItems: "center", gap: "1rem", flexWrap: "wrap" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                <Calendar size={14} color="#6c757d" />
                <span style={{ fontSize: "14px", color: "#6c757d" }}>
                  {loading
                    ? "Cargando historial..."
                    : error
                      ? "Error al cargar"
                      : `${responseData?.count || 0} alerta${responseData?.count !== 1 ? "s" : ""} registrada${responseData?.count !== 1 ? "s" : ""}`}
                </span>
              </div>

              {lastUpdate && (
                <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                  <Clock size={14} color="#6c757d" />
                  <span style={{ fontSize: "12px", color: "#888" }}>
                    Última actualización: {lastUpdate}
                  </span>
                </div>
              )}
            </div>
          </div>

          <div style={{ display: "flex", gap: "0.75rem" }}>
            <button
              onClick={exportToCSV}
              disabled={!responseData || responseData.count === 0}
              style={{
                padding: "0.75rem 1.5rem",
                backgroundColor: responseData && responseData.count > 0 ? "#28a745" : "#6c757d",
                color: "white",
                border: "none",
                borderRadius: "8px",
                cursor: responseData && responseData.count > 0 ? "pointer" : "not-allowed",
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

            <button
              onClick={fetchAlertsHistory}
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
              }}
            >
              {loading ? "🔄 Actualizando..." : "🔄 Actualizar"}
            </button>
          </div>
        </div>

        {/* Filtros */}
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
            gap: "1rem",
            padding: "1rem",
            backgroundColor: "#f8f9fa",
            borderRadius: "8px",
            border: "1px solid #dee2e6",
          }}
        >
          <div>
            <label style={{ display: "block", fontSize: "12px", fontWeight: "600", color: "#495057", marginBottom: "0.5rem" }}>
              <Filter size={14} style={{ display: "inline", marginRight: "0.25rem" }} />
              Límite de registros
            </label>
            <input
              type="number"
              value={limitFilter}
              onChange={(e) => setLimitFilter(Number(e.target.value))}
              min="1"
              max="1000"
              style={{
                width: "100%",
                padding: "0.5rem",
                border: "1px solid #ced4da",
                borderRadius: "4px",
                fontSize: "14px",
              }}
            />
            <span style={{ fontSize: "10px", color: "#6c757d" }}>Máx: 1000</span>
          </div>

          <div>
            <label style={{ display: "block", fontSize: "12px", fontWeight: "600", color: "#495057", marginBottom: "0.5rem" }}>
              Tipo de Fachada
            </label>
            <select
              value={facadeTypeFilter}
              onChange={(e) => setFacadeTypeFilter(e.target.value)}
              style={{
                width: "100%",
                padding: "0.5rem",
                border: "1px solid #ced4da",
                borderRadius: "4px",
                fontSize: "14px",
              }}
            >
              <option value="">Todas</option>
              <option value="refrigerada">Refrigerada</option>
              <option value="no_refrigerada">No Refrigerada</option>
            </select>
          </div>

          <div>
            <label style={{ display: "block", fontSize: "12px", fontWeight: "600", color: "#495057", marginBottom: "0.5rem" }}>
              Rango de Tiempo (horas)
            </label>
            <input
              type="number"
              value={hoursFilter}
              onChange={(e) => setHoursFilter(Number(e.target.value))}
              min="1"
              max="2160"
              style={{
                width: "100%",
                padding: "0.5rem",
                border: "1px solid #ced4da",
                borderRadius: "4px",
                fontSize: "14px",
              }}
            />
            <span style={{ fontSize: "10px", color: "#6c757d" }}>Máx: 2160 (90 días)</span>
          </div>
        </div>

        {/* Metadata */}
        {responseData && (
          <div style={{ marginTop: "1rem", padding: "0.75rem", backgroundColor: "#e7f3ff", borderRadius: "6px", fontSize: "12px" }}>
            <strong>Consulta actual:</strong>
            {` ${responseData.count} alertas`}
            {responseData.facade_type && ` | Tipo: ${responseData.facade_type}`}
            {` | Últimas ${responseData.time_range_hours} horas`}
            {` | Límite: ${limitFilter}`}
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
          <p style={{ margin: "0.5rem 0 0 0", fontSize: "14px" }}>
            Verifica que la API esté ejecutándose en http://localhost:8000
          </p>
          <p style={{ margin: "0.5rem 0 0 0", fontSize: "12px", color: "#856404" }}>
            💡 Nota: Este historial muestra anomalías detectadas en tiempo real. Si no hay registros, significa que el sistema está funcionando correctamente.
          </p>
        </div>
      )}

      {/* Empty state */}
      {!loading && !error && responseData && responseData.count === 0 && (
        <div
          style={{
            padding: "4rem",
            textAlign: "center",
            backgroundColor: "white",
            borderRadius: "12px",
            boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
          }}
        >
          <AlertCircle size={64} color="#28a745" style={{ marginBottom: "1rem" }} />
          <h3 style={{ color: "#28a745", margin: "0 0 0.5rem 0" }}>
            ¡Excelente! No hay alertas
          </h3>
          <p style={{ color: "#6c757d", margin: "0 0 0.5rem 0" }}>
            No se detectaron anomalías en las últimas {responseData.time_range_hours} horas
          </p>
          <p style={{ color: "#888", margin: 0, fontSize: "14px" }}>
            Todos los sensores están operando dentro de los rangos esperados
          </p>
        </div>
      )}

      {/* Alerts table */}
      {!loading && !error && alerts.length > 0 && (
        <div
          style={{
            backgroundColor: "white",
            borderRadius: "12px",
            boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
            overflow: "hidden",
          }}
        >
          <div style={{ overflowX: "auto" }}>
            <table
              style={{
                width: "100%",
                borderCollapse: "collapse",
                fontSize: "14px",
              }}
            >
              <thead>
                <tr style={{ backgroundColor: "#f8f9fa", borderBottom: "2px solid #dee2e6" }}>
                  <th style={{ padding: "1rem", textAlign: "left", fontWeight: "600", color: "#495057" }}>
                    Fecha/Hora
                  </th>
                  <th style={{ padding: "1rem", textAlign: "left", fontWeight: "600", color: "#495057" }}>
                    ID Alerta
                  </th>
                  <th style={{ padding: "1rem", textAlign: "center", fontWeight: "600", color: "#495057" }}>
                    Severidad
                  </th>
                  <th style={{ padding: "1rem", textAlign: "left", fontWeight: "600", color: "#495057" }}>
                    Tipo
                  </th>
                  <th style={{ padding: "1rem", textAlign: "left", fontWeight: "600", color: "#495057" }}>
                    Sensor
                  </th>
                  <th style={{ padding: "1rem", textAlign: "center", fontWeight: "600", color: "#495057" }}>
                    Fachada
                  </th>
                  <th style={{ padding: "1rem", textAlign: "left", fontWeight: "600", color: "#495057" }}>
                    Descripción
                  </th>
                  <th style={{ padding: "1rem", textAlign: "center", fontWeight: "600", color: "#495057" }}>
                    Estado
                  </th>
                </tr>
              </thead>
              <tbody>
                {alerts.map((alert, index) => {
                  const badgeStyle = getSeverityBadgeStyle(alert.severity);

                  return (
                    <tr
                      key={`${alert.alert_id}-${index}`}
                      style={{
                        backgroundColor: index % 2 === 0 ? "#fff" : "#f8f9fa",
                        borderBottom: "1px solid #dee2e6",
                      }}
                    >
                      <td style={{ padding: "1rem", color: "#495057" }}>
                        {new Date(alert.timestamp).toLocaleString()}
                      </td>
                      <td style={{ padding: "1rem", fontFamily: "monospace", fontSize: "12px", color: "#6c757d" }}>
                        {alert.alert_id}
                      </td>
                      <td style={{ padding: "1rem", textAlign: "center" }}>
                        <span
                          style={{
                            padding: "4px 12px",
                            borderRadius: "12px",
                            backgroundColor: badgeStyle.bg,
                            color: badgeStyle.color,
                            border: `1px solid ${badgeStyle.border}`,
                            fontWeight: "600",
                            fontSize: "11px",
                            display: "inline-block",
                          }}
                        >
                          {alert.severity}
                        </span>
                      </td>
                      <td style={{ padding: "1rem", color: "#495057" }}>
                        {alert.alert_type}
                      </td>
                      <td style={{ padding: "1rem", fontWeight: "600", color: "#214B4E" }}>
                        {alert.sensor_id}
                      </td>
                      <td style={{ padding: "1rem", textAlign: "center", color: "#495057" }}>
                        {alert.facade_id}
                      </td>
                      <td style={{ padding: "1rem", color: "#495057" }}>
                        {alert.description}
                      </td>
                      <td style={{ padding: "1rem", textAlign: "center" }}>
                        <span
                          style={{
                            padding: "4px 12px",
                            borderRadius: "12px",
                            backgroundColor: alert.resolved ? "#d1fae5" : "#fee2e2",
                            color: alert.resolved ? "#065f46" : "#991b1b",
                            fontWeight: "600",
                            fontSize: "11px",
                            display: "inline-block",
                          }}
                        >
                          {alert.resolved ? "Resuelta" : "Activa"}
                        </span>
                        {alert.resolved && alert.resolved_at && (
                          <div style={{ fontSize: "10px", color: "#6c757d", marginTop: "0.25rem" }}>
                            {new Date(alert.resolved_at).toLocaleString()}
                          </div>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Loading state */}
      {loading && !responseData && (
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
          <h3 style={{ color: "#6c757d", margin: 0 }}>
            Cargando historial de alertas...
          </h3>
        </div>
      )}

      {/* Debug info */}
      {responseData && alerts.length > 0 && (
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