import { useEffect, useState, useRef } from "react";
import { AlertTriangle, CheckCircle, Clock, Filter } from "lucide-react";

// Backend response structure
interface BackendAnomaly {
  facade_id: string;
  device_id: string;
  facade_type: string;
  sensor_name: string;
  value: number;
  expected_range: {
    min: number;
    max: number;
  };
  ts: string;
  severity: string;
}

// Frontend display structure
interface Anomaly {
  sensor_id: string;
  anomaly_type: string;
  severity: string;
  description: string;
  timestamp: string;
  facade_id: string;
  value?: number;
  threshold?: number;
}

interface AnomaliesResponse {
  count: number;
  facade_id: string | null;
  facade_type: string | null;
  time_range_hours: number;
  anomalies: Anomaly[];
}

export default function AlertNotifications() {
  const [responseData, setResponseData] = useState<AnomaliesResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<string>("");
  const isMountedRef = useRef(true);
  
  // Filtros opcionales
  const [facadeFilter, setFacadeFilter] = useState<string>("");
  const [facadeTypeFilter, setFacadeTypeFilter] = useState<string>("");
  const [hoursFilter, setHoursFilter] = useState<number>(24);

  const fetchAlerts = async () => {
    if (!isMountedRef.current) return;

    setLoading(true);
    setError(null);

    try {
      // Construir URL con parámetros opcionales
      const params = new URLSearchParams();
      if (facadeFilter) params.append("facade_id", facadeFilter);
      if (facadeTypeFilter) params.append("facade_type", facadeTypeFilter);
      params.append("hours", hoursFilter.toString());
      
      const url = `http://localhost:8000/alerts/anomalies?${params.toString()}`;
      console.log(`🚨 [${new Date().toLocaleTimeString()}] Fetching alerts from: ${url}`);

      const response = await fetch(url);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      console.log("📊 Alerts API response:", data);

      // Transformar los datos del backend al formato del frontend
      const transformedAnomalies: Anomaly[] = (data.anomalies || []).map((anomaly: BackendAnomaly) => {
        // Determinar el tipo de anomalía basado en el valor y el rango esperado
        let anomalyType = "threshold_exceeded";
        if (anomaly.value < anomaly.expected_range.min) {
          anomalyType = "below_minimum";
        } else if (anomaly.value > anomaly.expected_range.max) {
          anomalyType = "above_maximum";
        }

        // Generar descripción clara
        const description = `Sensor ${anomaly.sensor_name} registró ${anomaly.value.toFixed(2)}°C, ` +
          `fuera del rango esperado (${anomaly.expected_range.min}°C - ${anomaly.expected_range.max}°C)`;

        return {
          sensor_id: anomaly.device_id,
          anomaly_type: anomalyType,
          severity: anomaly.severity,
          description: description,
          timestamp: anomaly.ts,
          facade_id: anomaly.facade_id,
          value: anomaly.value,
          threshold: anomaly.value > anomaly.expected_range.max ? anomaly.expected_range.max : anomaly.expected_range.min,
        };
      });

      const transformedData: AnomaliesResponse = {
        count: transformedAnomalies.length,
        facade_id: data.facade_id,
        facade_type: data.facade_type,
        time_range_hours: data.time_range_hours,
        anomalies: transformedAnomalies,
      };

      if (isMountedRef.current) {
        setResponseData(transformedData);
        setLastUpdate(new Date().toLocaleString());
        console.log(`✅ Successfully loaded ${transformedData.count} anomalies`);
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Unknown error";
      console.error("💥 Error fetching alerts:", err);
      
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

  // Efecto para carga inicial
  useEffect(() => {
    console.log("🔄 AlertNotifications mounted - Loading alerts");
    isMountedRef.current = true;
    fetchAlerts();

    return () => {
      isMountedRef.current = false;
    };
  }, []);

  // Efecto para auto-refresh cada 10 segundos
  useEffect(() => {
    const interval = setInterval(() => {
      console.log("🔄 Auto-refresh triggered");
      fetchAlerts();
    }, 10000);

    return () => clearInterval(interval);
  }, [facadeFilter, facadeTypeFilter, hoursFilter]);

  const getSeverityColor = (severity: string) => {
    const severityLower = severity?.toLowerCase() || "";
    
    if (severityLower.includes("critical") || severityLower.includes("high")) {
      return {
        bg: "#fee2e2",
        border: "#dc2626",
        text: "#991b1b",
        icon: "#dc2626"
      };
    }
    
    if (severityLower.includes("medium") || severityLower.includes("warning")) {
      return {
        bg: "#fef3c7",
        border: "#f59e0b",
        text: "#92400e",
        icon: "#f59e0b"
      };
    }
    
    return {
      bg: "#dbeafe",
      border: "#3b82f6",
      text: "#1e40af",
      icon: "#3b82f6"
    };
  };

  const getStatusColor = () => {
    if (loading) return "#ffa500";
    if (error) return "#dc3545";
    if (!responseData || responseData.count === 0) return "#28a745";
    return "#f59e0b";
  };

  const anomalies = responseData?.anomalies || [];

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
              Alertas en Tiempo Real
            </h1>
            <div style={{ display: "flex", alignItems: "center", gap: "1rem", flexWrap: "wrap" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                <div
                  style={{
                    width: "12px",
                    height: "12px",
                    borderRadius: "50%",
                    backgroundColor: getStatusColor(),
                  }}
                ></div>
                <span style={{ fontSize: "14px", color: "#6c757d" }}>
                  {loading
                    ? "Cargando..."
                    : error
                      ? "Error"
                      : responseData?.count === 0
                        ? "Sin anomalías detectadas"
                        : `${responseData?.count} anomalía${responseData?.count !== 1 ? "s" : ""} detectada${responseData?.count !== 1 ? "s" : ""}`}
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

          <button
            onClick={fetchAlerts}
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
              ID Fachada (opcional)
            </label>
            <input
              type="text"
              value={facadeFilter}
              onChange={(e) => setFacadeFilter(e.target.value)}
              placeholder="1, 2, etc."
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
              Tipo de Fachada (opcional)
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
              max="720"
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

        {/* Metadata de respuesta */}
        {responseData && (
          <div style={{ marginTop: "1rem", padding: "0.75rem", backgroundColor: "#e7f3ff", borderRadius: "6px", fontSize: "12px" }}>
            <strong>Filtros aplicados:</strong> 
            {responseData.facade_id && ` Fachada ${responseData.facade_id} |`}
            {responseData.facade_type && ` Tipo: ${responseData.facade_type} |`}
            {` Últimas ${responseData.time_range_hours} horas`}
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
          <p style={{ margin: "0.5rem 0 0 0", fontSize: "12px" }}>
            Verifica que la API esté ejecutándose en http://localhost:8000
          </p>
        </div>
      )}

      {/* Empty state - No anomalies */}
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
          <CheckCircle size={64} color="#28a745" style={{ marginBottom: "1rem" }} />
          <h3 style={{ color: "#28a745", margin: "0 0 0.5rem 0" }}>
            Sistema Operando Correctamente
          </h3>
          <p style={{ color: "#6c757d", margin: 0 }}>
            No se han detectado anomalías en las últimas {responseData.time_range_hours} horas
          </p>
          <p style={{ fontSize: "12px", color: "#888", marginTop: "1rem" }}>
            Actualización automática cada 10 segundos
          </p>
        </div>
      )}

      {/* Anomalies list */}
      {!loading && !error && anomalies.length > 0 && (
        <div style={{ display: "grid", gap: "1rem" }}>
          {anomalies.map((anomaly, index) => {
            const colors = getSeverityColor(anomaly.severity);
            
            return (
              <div
                key={`${anomaly.sensor_id}-${anomaly.timestamp}-${index}`}
                style={{
                  padding: "1.5rem",
                  backgroundColor: colors.bg,
                  borderLeft: `4px solid ${colors.border}`,
                  borderRadius: "8px",
                  boxShadow: "0 2px 4px rgba(0,0,0,0.1)",
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "0.75rem" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
                    <AlertTriangle size={24} color={colors.icon} />
                    <div>
                      <h3 style={{ margin: 0, fontSize: "1.1rem", fontWeight: "bold", color: colors.text }}>
                        {anomaly.sensor_id}
                      </h3>
                      <span
                        style={{
                          display: "inline-block",
                          marginTop: "0.25rem",
                          padding: "2px 8px",
                          backgroundColor: colors.border,
                          color: "white",
                          fontSize: "11px",
                          fontWeight: "600",
                          borderRadius: "4px",
                        }}
                      >
                        {anomaly.severity || "N/A"}
                      </span>
                    </div>
                  </div>
                  
                  <span style={{ fontSize: "12px", color: "#6c757d" }}>
                    Fachada {anomaly.facade_id}
                  </span>
                </div>

                <div style={{ marginBottom: "0.5rem" }}>
                  <strong style={{ fontSize: "14px", color: colors.text }}>Tipo: </strong>
                  <span style={{ fontSize: "14px", color: colors.text }}>{anomaly.anomaly_type}</span>
                </div>

                <div style={{ marginBottom: "0.5rem" }}>
                  <strong style={{ fontSize: "14px", color: colors.text }}>Descripción: </strong>
                  <span style={{ fontSize: "14px", color: colors.text }}>{anomaly.description}</span>
                </div>

                {anomaly.value !== undefined && (
                  <div style={{ marginBottom: "0.5rem" }}>
                    <strong style={{ fontSize: "14px", color: colors.text }}>Valor Medido: </strong>
                    <span style={{ fontSize: "14px", color: colors.text, fontWeight: "600" }}>
                      {anomaly.value.toFixed(2)}°C
                      {anomaly.threshold !== undefined && (
                        <span style={{ fontWeight: "normal" }}>
                          {" "}(Umbral {anomaly.value > anomaly.threshold ? "máximo" : "mínimo"}: {anomaly.threshold.toFixed(2)}°C)
                        </span>
                      )}
                    </span>
                  </div>
                )}

                <div style={{ fontSize: "12px", color: "#6c757d", marginTop: "0.75rem" }}>
                  <Clock size={12} style={{ display: "inline", marginRight: "0.25rem" }} />
                  {new Date(anomaly.timestamp).toLocaleString()}
                </div>
              </div>
            );
          })}
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
            Cargando alertas del sistema...
          </h3>
        </div>
      )}

      {/* Debug info */}
      {responseData && anomalies.length > 0 && (
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