import { useState, useEffect } from "react";

type PanelProps = {
  title: string;
  refrigerated?: boolean;
  faults: number;
  temperature: number;
  viewMode?: "Fachada" | "Temperatura";
  sensors?: number[];
  onClick?: () => void;
  id?: string; // Añadir ID para hacer la consulta API
};

interface TemperatureSensor {
  sensor_id: string;
  value: number;
  unit: string;
  last_update: string;
}

export default function Panel({
  title,
  refrigerated = false,
  faults = 0,
  temperature,
  viewMode = "Fachada",
  sensors = [],
  onClick,
  id = "1", // ID por defecto
}: PanelProps) {
  const [temperatureSensors, setTemperatureSensors] = useState<TemperatureSensor[]>([]);
  const [loading, setLoading] = useState(false);

  // Función para obtener datos de temperatura desde la API
  const fetchTemperatureSensors = async () => {
    if (viewMode !== "Temperatura" || !id) return;

    setLoading(true);
    try {
      const url = `http://localhost:8000/realtime/facades/${id}`;
      const response = await fetch(url);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      console.log("🔍 Panel - Realtime API response:", data);

      // La respuesta tiene estructura: { facade_id, facade_type, data: {...} }
      const sensorData = data.data || {};
      
      // Filtrar solo sensores de temperatura y convertir a formato esperado
      const tempSensors: TemperatureSensor[] = [];
      
      Object.entries(sensorData).forEach(([sensorName, sensorInfo]: [string, any]) => {
        if (sensorName.startsWith("Temperature_M")) {
          tempSensors.push({
            sensor_id: sensorName,
            value: sensorInfo.value,
            unit: "°C",
            last_update: sensorInfo.ts
          });
        }
      });

      console.log("🌡️ Panel - Processed temperature sensors:", tempSensors);
      setTemperatureSensors(tempSensors);
    } catch (error) {
      console.error("Error fetching temperature sensors:", error);
      setTemperatureSensors([]);
    } finally {
      setLoading(false);
    }
  };

  // Efecto para cargar datos cuando cambia el modo de vista o el ID
  useEffect(() => {
    fetchTemperatureSensors();
  }, [viewMode, id]);

  // Efecto para auto-refresh cuando está en modo Temperatura
  useEffect(() => {
    if (viewMode !== "Temperatura") return;

    // Intervalo de actualización cada 5 segundos
    const interval = setInterval(() => {
      fetchTemperatureSensors();
    }, 5000);

    // Limpiar intervalo cuando el componente se desmonta o cambia el modo
    return () => clearInterval(interval);
  }, [viewMode, id]);

  // Función para obtener el valor de temperatura para una posición específica
  const getTemperatureForPosition = (index: number) => {
    if (temperatureSensors.length === 0) return undefined;

    // Mapear posición del grid (0-14) a sensor reverso
    // Empezar desde L5_3 y ir hacia atrás
    const totalSensors = 15; // 5 filas x 3 columnas
    const reverseIndex = totalSensors - 1 - index;

    // Si hay sensores de la API, usar esos datos
    if (temperatureSensors[reverseIndex]) {
      return temperatureSensors[reverseIndex].value;
    }

    // Fallback a datos dummy si no hay suficientes sensores
    return sensors[index];
  };

  // Función para obtener el ID del sensor para una posición específica
  const getSensorIdForPosition = (index: number) => {
    if (temperatureSensors.length === 0) return `Sensor ${index + 1}`;

    // Mapear posición del grid a sensor reverso
    const totalSensors = 15;
    const reverseIndex = totalSensors - 1 - index;

    if (temperatureSensors[reverseIndex]) {
      // Extraer solo la parte LX_X del sensor_id
      const sensorId = temperatureSensors[reverseIndex].sensor_id;
      const match = sensorId.match(/L\d+_\d+/);
      return match ? match[0] : sensorId;
    }

    // Calcular el nombre del sensor basado en la posición reversa
    // Posición 0 del grid = L5_3, posición 1 = L5_2, etc.
    const row = Math.floor((totalSensors - 1 - index) / 3) + 1; // L1 a L5
    const col = ((totalSensors - 1 - index) % 3) + 1; // 1 a 3
    return `L${row}_${col}`;
  };

  return (
    <div
      className={`panel ${refrigerated ? "panel-ok" : "panel-alert"} ${onClick ? "panel-clickable" : ""}`}
      role="region"
      aria-labelledby={`${title}-title`}
      onClick={onClick}
      tabIndex={onClick ? 0 : undefined}
      onKeyDown={
        onClick
          ? e => {
              if (e.key === "Enter" || e.key === " ") {
                e.preventDefault();
                onClick();
              }
            }
          : undefined
      }
      aria-label={onClick ? `Ver detalles de la fachada ${title}` : undefined}
    >
      {/* Header interno */}
      <div className="panel-header">
        <h2 id={`${title}-title`} className="panel-title">
          {title}
        </h2>
        <div
          className="panel-status"
          title={refrigerated ? "Refrigerado" : "Sin refrigerar"}
        >
          <div
            style={{
              width: "28px",
              height: "28px",
              borderRadius: "50%",
              backgroundColor: refrigerated ? "#214B4E" : "#e63946",
              color: "white",
              fontWeight: "bold",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: "16px",
              boxShadow: "0 2px 6px rgba(0,0,0,0.2)",
            }}
          >
            {refrigerated ? "✓" : "✖"}
          </div>
        </div>
      </div>

      {/* Ilustración del panel solar */}
      <div className="panel-visual">
        <svg width="100%" height="300" viewBox="0 0 180 300">
          <rect width="180" height="300" rx="12" fill="#AFDAE8" />

          {/* 5 filas x 3 columnas */}
          {Array.from({ length: 5 }).map((_, row) =>
            Array.from({ length: 3 }).map((_, col) => {
              const index = row * 3 + col;
              const value = getTemperatureForPosition(index);
              const sensorId = getSensorIdForPosition(index);

              return (
                <g key={`${row}-${col}`}>
                  <rect
                    x={15 + col * 50}
                    y={20 + row * 55}
                    width="40"
                    height="45"
                    rx="3"
                    fill="#3568A7"
                  />
                  {viewMode === "Temperatura" && (
                    <>
                      {/* Nombre del sensor */}
                      <text
                        x={35 + col * 50}
                        y={30 + row * 55}
                        fontSize="7"
                        fill="#A6A6A6"
                        textAnchor="middle"
                      >
                        {sensorId}
                      </text>

                      {/* Valor de temperatura */}
                      {value !== undefined && (
                        <text
                          x={35 + col * 50}
                          y={54 + row * 55}
                          fontSize="18"
                          fontWeight="bold"
                          fill={value < 25 ? "#e63946" : "white"}
                          textAnchor="middle"
                        >
                          {Math.round(value)}°
                        </text>
                      )}

                      {/* Indicador de carga */}
                      {loading && viewMode === "Temperatura" && (
                        <text
                          x={35 + col * 50}
                          y={54 + row * 55}
                          fontSize="12"
                          fill="#666"
                          textAnchor="middle"
                        >
                          ...
                        </text>
                      )}
                    </>
                  )}
                </g>
              );
            })
          )}
        </svg>
      </div>

      {/* Info de métricas */}
      <div className="panel-info">
        <div className="panel-cards">
          <div className="info-card">
            <div className="info-value">{faults}</div>
            <div className="info-label">Fallos detectados</div>
          </div>
          <div className="info-card">
            <div className="info-value">
              {temperature !== undefined ? temperature.toFixed(1) : "--"}°C
            </div>
            <div className="info-label">Temperatura General</div>
          </div>
        </div>
      </div>

      {/* Indicador de que es clickeable */}
      {onClick && (
        <div className="click-indicator">
          <span>Ver detalles →</span>
        </div>
      )}
    </div>
  );
}
