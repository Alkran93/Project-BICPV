import { useState, useEffect } from "react";

// Tipos basados en lo que debería devolver el endpoint realtime
interface RealtimeSensor {
  sensor_id: string;
  value: number;
  unit: string;
  last_update: string;
  device_id: string;
  sensor_type: string;
}

interface RealtimeDashboardProps {
  facadeId: string;
  autoRefresh?: boolean;
  refreshInterval?: number;
}

export default function RealtimeDashboard({
  facadeId,
  autoRefresh = true,
  refreshInterval = 5000,
}: RealtimeDashboardProps) {
  const [data, setData] = useState<RealtimeSensor[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<string>("");

  const fetchRealtimeData = async () => {
    setLoading(true);
    setError(null);

    try {
      const url = `http://localhost:8000/realtime/facades/${facadeId}`;
      console.log(`🚀 Fetching realtime data from: ${url}`);

      const response = await fetch(url);

      console.log(`📡 Response status: ${response.status} ${response.statusText}`);
      console.log(
        `📡 Response headers:`,
        Object.fromEntries(response.headers.entries())
      );

      if (!response.ok) {
        const errorText = await response.text();
        console.error(`❌ Error response:`, errorText);
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const responseData = await response.json();
      console.log(`✅ Raw response data:`, responseData);
      console.log(`📊 Data type:`, typeof responseData);

      // La respuesta tiene estructura: { facade_id, facade_type, data: {...} }
      const sensorData = responseData.data || {};
      
      // Convertir el objeto de sensores a array
      const sensorsArray = Object.entries(sensorData).map(([sensorName, sensorInfo]: [string, any]) => ({
        sensor_id: sensorName,
        sensor_name: sensorName,
        value: sensorInfo.value,
        ts: sensorInfo.ts,
        device_id: sensorInfo.device_id,
        facade_type: sensorInfo.facade_type,
        sensor_type: sensorName.startsWith('Temperature_') ? 'temperature' : 'other',
        unit: sensorName.startsWith('Temperature_') ? '°C' : 
              sensorName === 'Humedad' ? '%' :
              sensorName === 'Irradiancia' ? 'W/m²' :
              sensorName === 'Velocidad_Viento' ? 'm/s' : '',
        last_update: sensorInfo.ts
      }));

      console.log(`✅ Converted to array with ${sensorsArray.length} sensors`);
      setData(sensorsArray);
      setLastUpdate(new Date().toLocaleString());

      if (sensorsArray.length === 0) {
        console.warn("⚠️ No sensor data available");
      } else {
        console.log(`✅ Successfully loaded ${sensorsArray.length} sensors`);
        console.log(`📋 Sample sensor:`, sensorsArray[0]);
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Unknown error";
      console.error(`💥 Error fetching realtime data:`, err);
      setError(errorMessage);
      setData([]);
    } finally {
      setLoading(false);
    }
  };

  // Efecto para carga inicial
  useEffect(() => {
    fetchRealtimeData();
  }, [facadeId]);

  // Efecto para auto-refresh
  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(() => {
      fetchRealtimeData();
    }, refreshInterval);

    return () => clearInterval(interval);
  }, [autoRefresh, refreshInterval, facadeId]);

  const groupSensorsByType = (sensors: RealtimeSensor[]) => {
    return sensors.reduce(
      (groups, sensor) => {
        const type = sensor.sensor_type || "unknown";
        if (!groups[type]) {
          groups[type] = [];
        }
        groups[type].push(sensor);
        return groups;
      },
      {} as Record<string, RealtimeSensor[]>
    );
  };

  const getSensorTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      temperature: "Temperatura",
      irradiance: "Irradiancia",
      wind_speed: "Velocidad del Viento",
      pressure: "Presión",
      voltage: "Voltaje",
      current: "Corriente",
      power: "Potencia",
      flow: "Flujo",
      other: "Otros",
      unknown: "Desconocido",
    };
    return labels[type] || type;
  };

  const getStatusColor = () => {
    if (loading) return "#ffa500"; // orange
    if (error) return "#dc3545"; // red
    if (data.length === 0) return "#6c757d"; // gray
    return "#28a745"; // green
  };

  const groupedSensors = groupSensorsByType(data);

  return (
    <div
      style={{
        padding: "20px",
        fontFamily: "Arial, sans-serif",
        backgroundColor: "#f8f9fa",
        minHeight: "100vh",
      }}
    >
      <div
        style={{
          marginBottom: "20px",
          padding: "15px",
          backgroundColor: "white",
          borderRadius: "8px",
          boxShadow: "0 2px 4px rgba(0,0,0,0.1)",
        }}
      >
        <h1 style={{ margin: "0 0 10px 0" }}>
          Dashboard Tiempo Real - Fachada {facadeId}
        </h1>

        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "15px",
            flexWrap: "wrap",
          }}
        >
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "8px",
            }}
          >
            <div
              style={{
                width: "12px",
                height: "12px",
                borderRadius: "50%",
                backgroundColor: getStatusColor(),
              }}
            ></div>
            <span style={{ fontSize: "14px", color: "#666" }}>
              {loading
                ? "Cargando..."
                : error
                  ? "Error"
                  : data.length === 0
                    ? "Sin datos"
                    : `${data.length} sensores activos`}
            </span>
          </div>

          {lastUpdate && (
            <span style={{ fontSize: "12px", color: "#888" }}>
              Última actualización: {lastUpdate}
            </span>
          )}

          <button
            onClick={fetchRealtimeData}
            disabled={loading}
            style={{
              padding: "8px 16px",
              backgroundColor: "#007bff",
              color: "white",
              border: "none",
              borderRadius: "4px",
              cursor: loading ? "not-allowed" : "pointer",
              fontSize: "14px",
            }}
          >
            {loading ? "Actualizando..." : "Actualizar"}
          </button>
        </div>
      </div>

      {/* Debug info */}
      <div
        style={{
          marginBottom: "20px",
          padding: "10px",
          backgroundColor: "#e9ecef",
          borderRadius: "4px",
          fontSize: "12px",
          fontFamily: "monospace",
        }}
      >
        <strong>Debug Info:</strong>
        <br />
        URL: http://localhost:8000/realtime/facades/{facadeId}
        <br />
        Estado:{" "}
        {loading ? "Cargando" : error ? `Error: ${error}` : `OK (${data.length} items)`}
        <br />
        Auto-refresh: {autoRefresh ? `Sí (cada ${refreshInterval}ms)` : "No"}
      </div>

      {/* Error display */}
      {error && (
        <div
          style={{
            padding: "15px",
            backgroundColor: "#f8d7da",
            border: "1px solid #f5c6cb",
            borderRadius: "4px",
            color: "#721c24",
            marginBottom: "20px",
          }}
        >
          <strong>Error:</strong> {error}
        </div>
      )}

      {/* Empty state */}
      {!loading && !error && data.length === 0 && (
        <div
          style={{
            padding: "40px",
            textAlign: "center",
            backgroundColor: "white",
            borderRadius: "8px",
            boxShadow: "0 2px 4px rgba(0,0,0,0.1)",
          }}
        >
          <h3 style={{ color: "#6c757d" }}>No hay datos disponibles</h3>
          <p style={{ color: "#6c757d" }}>
            El endpoint no devolvió datos para la fachada {facadeId}
          </p>
          <p style={{ fontSize: "12px", color: "#888" }}>
            Verifica que:
            <br />
            • La API esté ejecutándose en http://localhost:8000
            <br />
            • Existan datos en la base de datos para esta fachada
            <br />• La fachada ID sea correcta
          </p>
        </div>
      )}

      {/* Data display */}
      {!loading && !error && data.length > 0 && (
        <div>
          {Object.entries(groupedSensors).map(([type, sensors]) => (
            <div
              key={type}
              style={{
                marginBottom: "25px",
                backgroundColor: "white",
                borderRadius: "8px",
                padding: "20px",
                boxShadow: "0 2px 4px rgba(0,0,0,0.1)",
              }}
            >
              <h3
                style={{
                  margin: "0 0 15px 0",
                  color: "#495057",
                  borderBottom: "2px solid #e9ecef",
                  paddingBottom: "8px",
                }}
              >
                {getSensorTypeLabel(type)} ({sensors.length})
              </h3>

              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))",
                  gap: "15px",
                }}
              >
                {sensors.map((sensor, index) => (
                  <div
                    key={index}
                    style={{
                      padding: "15px",
                      border: "1px solid #dee2e6",
                      borderRadius: "6px",
                      backgroundColor: "#f8f9fa",
                    }}
                  >
                    <div
                      style={{
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "center",
                        marginBottom: "8px",
                      }}
                    >
                      <h4 style={{ margin: 0, fontSize: "14px", color: "#495057" }}>
                        {sensor.sensor_id}
                      </h4>
                      <span
                        style={{
                          fontSize: "10px",
                          padding: "2px 6px",
                          backgroundColor: "#007bff",
                          color: "white",
                          borderRadius: "3px",
                        }}
                      >
                        {sensor.device_id}
                      </span>
                    </div>

                    <div
                      style={{
                        fontSize: "24px",
                        fontWeight: "bold",
                        color: "#28a745",
                        marginBottom: "5px",
                      }}
                    >
                      {sensor.value} {sensor.unit}
                    </div>

                    <div
                      style={{
                        fontSize: "11px",
                        color: "#6c757d",
                      }}
                    >
                      {new Date(sensor.last_update).toLocaleString()}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Raw data display for debugging */}
      {data.length > 0 && (
        <details style={{ marginTop: "30px" }}>
          <summary
            style={{
              cursor: "pointer",
              padding: "10px",
              backgroundColor: "#e9ecef",
              borderRadius: "4px",
            }}
          >
            Ver datos en crudo (JSON)
          </summary>
          <pre
            style={{
              backgroundColor: "#f8f9fa",
              padding: "15px",
              borderRadius: "4px",
              overflow: "auto",
              fontSize: "11px",
              marginTop: "10px",
            }}
          >
            {JSON.stringify(data, null, 2)}
          </pre>
        </details>
      )}
    </div>
  );
}
