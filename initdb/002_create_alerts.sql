-- Crear tabla de alertas si no existe
CREATE TABLE IF NOT EXISTS alerts (
    id SERIAL PRIMARY KEY,
    facade_id TEXT NOT NULL,
    sensor_name TEXT NOT NULL,
    alert_type TEXT NOT NULL,         -- p. ej. 'temperature_high', 'pressure_low'
    severity TEXT DEFAULT 'medium',   -- 'low', 'medium', 'high', 'critical'
    description TEXT,
    value DOUBLE PRECISION,
    threshold DOUBLE PRECISION,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
