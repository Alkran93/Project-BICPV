import { useRealtimeData } from "../../contexts/RealtimeDataContext";

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
  const { data, loading, error, lastUpdate, refreshData } = useRealtimeData();

  // Obtener datos específicos de esta fachada
  const facadeData = data[facadeId] || {};
  
  // Convertir el objeto de sensores a array
  const sensorsArray = Object.entries(facadeData).map(([sensorName, sensorInfo]: [string, any]) => {
    
    let sensorType = "other";
    let unit = "";
    
    if (sensorName.startsWith('T_M') && sensorName.includes('_')) {
      sensorType = 'temperature';
      unit = '°C';
    } else if (sensorName === 'Irradiancia') {
      sensorType = 'irradiance';
      unit = 'W/m²';
    } else if (sensorName === 'Velocidad_Viento') {
      sensorType = 'wind_speed';
      unit = 'm/s';
    } else if (sensorName === "Humedad") {
      sensorType = "humidity";
      unit = "%";
    } else if (sensorName === "Temperatura_Ambiente") {
      sensorType = "ambient_temperature";
      unit = "°C";
    } else if (sensorName.includes("Presion")) {
      sensorType = "pressure";
      unit = "bar";
    } else if (sensorName.includes("Flujo")) {
      sensorType = "flow";
      unit = "LPM";
    } else if (sensorName.includes("T_Salida") || sensorName.includes("T_Entrada")) {
      sensorType = "refrigerant_temperature";
      unit = "°C";
    } else if (sensorName.includes("T_Valvula") || sensorName.includes("T_EntCompresor") || sensorName.includes("T_SalCompresor")) {
      sensorType = "refrigeration_system";
      unit = "°C";
    } else if (sensorName.includes("Estado")) {
      sensorType = "system_status";
      unit = sensorInfo.value === 1 ? "ON" : "OFF";
    }

    return {
      sensor_id: sensorName,
      sensor_name: sensorName,
      value: sensorInfo.value,
      ts: sensorInfo.ts,
      device_id: sensorInfo.device_id,
      facade_type: sensorInfo.facade_type,
      sensor_type: sensorType,
      unit: unit,
      last_update: sensorInfo.ts,
    };
  });

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
      temperature: "Temperatura del Panel",
      irradiance: "Irradiancia",
      wind_speed: "Velocidad del Viento",
      humidity: "Humedad",
      ambient_temperature: "Temperatura Ambiente",
      pressure: "Presión",
      flow: "Flujo",
      refrigerant_temperature: "Temperatura del Refrigerante",
      refrigeration_system: "Sistema de Refrigeración",
      system_status: "Estado del Sistema",
      other: "Otros Sensores",
      unknown: "Desconocido",
    };
    return labels[type] || type;
  };

  const getStatusColor = () => {
    if (loading) return "#ffa500"; // orange
    if (error) return "#dc3545"; // red
    if (sensorsArray.length === 0) return "#6c757d"; // gray
    return "#28a745"; // green
  };

  const getValueColor = (sensorType: string, value: number) => {
    if (sensorType === 'temperature' && value > 40) return "#dc3545"; // red for high temp
    if (sensorType === 'temperature' && value < 20) return "#007bff"; // blue for low temp
    return "#28a745"; // green for normal
  };

  const groupedSensors = groupSensorsByType(sensorsArray);

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
                  : sensorsArray.length === 0
                    ? "Sin datos"
                    : `${sensorsArray.length} sensores activos`}
            </span>
          </div>

          {lastUpdate && (
            <span style={{ fontSize: "12px", color: "#888" }}>
              Última actualización: {lastUpdate}
            </span>
          )}

          <button
            onClick={refreshData}
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
        Fachada ID: {facadeId}
        <br />
        Estado:{" "}
        {loading ? "Cargando" : error ? `Error: ${error}` : `OK (${sensorsArray.length} sensores)`}
        <br />
        Auto-refresh: {autoRefresh ? `Sí (cada ${refreshInterval}ms)` : "No"}
        <br />
        Tipos de sensores: {Object.keys(groupedSensors).join(", ")}
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
      {!loading && !error && sensorsArray.length === 0 && (
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
            No se encontraron datos para la fachada {facadeId}
          </p>
          <p style={{ fontSize: "12px", color: "#888" }}>
            Verifica que:
            <br />
            • La fachada ID sea correcta (1 o 2)
            <br />
            • Existan datos en tiempo real para esta fachada
            <br />
            • El contexto esté cargando datos correctamente
          </p>
        </div>
      )}

      {/* Data display */}
      {!loading && !error && sensorsArray.length > 0 && (
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
                        color: getValueColor(sensor.sensor_type, sensor.value),
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
      {sensorsArray.length > 0 && (
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
            {JSON.stringify(sensorsArray, null, 2)}
          </pre>
        </details>
      )}
    </div>
  );
}