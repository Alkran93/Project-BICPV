import { useRealtimeData } from "../../contexts/RealtimeDataContext";

type PanelProps = {
  title: string;
  refrigerated?: boolean;
  faults: number;
  temperature: number;
  viewMode?: "Fachada" | "Temperatura";
  sensors?: number[];
  onClick?: () => void;
  id?: string;
};

export default function Panel({
  title,
  refrigerated = false,
  faults = 0,
  temperature,
  viewMode = "Fachada",
  sensors = [],
  onClick,
  id = "1",
}: PanelProps) {
  const { data, loading } = useRealtimeData();

  // Obtener datos específicos de esta fachada
  const facadeData = data[id] || {};
  
  // Extraer y ordenar sensores de temperatura
  const temperatureSensors = Object.entries(facadeData)
    .filter(([sensorName]) => sensorName.startsWith("T_M") && sensorName.includes("_"))
    .map(([sensorName, sensorInfo]: [string, any]) => ({
      sensor_id: sensorName,
      value: sensorInfo.value,
      unit: "°C",
      last_update: sensorInfo.ts
    }))
    .sort((a, b) => {
      const getPosition = (sensorId: string) => {
        const match = sensorId.match(/T_M(\d+)_(\d+)/);
        return match ? parseInt(match[1]) * 10 + parseInt(match[2]) : 0;
      };
      return getPosition(a.sensor_id) - getPosition(b.sensor_id);
    });

  // Calcular temperatura promedio
  const averageTemperature = temperatureSensors.length > 0
    ? temperatureSensors.reduce((sum, sensor) => sum + sensor.value, 0) / temperatureSensors.length
    : temperature;

  // Función para obtener temperatura por posición
  const getTemperatureForPosition = (index: number) => {
    if (temperatureSensors.length === 0) return undefined;
    return temperatureSensors[index]?.value || sensors[index];
  };

  // Función para obtener ID del sensor por posición
  const getSensorIdForPosition = (index: number) => {
    if (temperatureSensors.length === 0) return `Sensor ${index + 1}`;
    
    const sensor = temperatureSensors[index];
    if (sensor) {
      return sensor.sensor_id.replace("T_M", "L");
    }
    
    // Fallback: calcular basado en posición
    const row = Math.floor(index / 3) + 1;
    const col = (index % 3) + 1;
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
                      {loading && (
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
              {averageTemperature.toFixed(1)}°C
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