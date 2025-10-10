CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Borrar la tabla si existe (para reinicios limpios en desarrollo)
DROP TABLE IF EXISTS measurements;

-- Crear la tabla con la estructura correcta
CREATE TABLE IF NOT EXISTS measurements (
    id SERIAL,
    facade_id TEXT NOT NULL,
    device_id TEXT NOT NULL,
    facade_type TEXT NOT NULL,  -- 'refrigerada' o 'no_refrigerada'
    sensor_name TEXT NOT NULL,
    value DOUBLE PRECISION,
    ts TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (facade_id, device_id, facade_type, sensor_name, ts)
);

-- Crear la hypertable (TimescaleDB)
SELECT create_hypertable('measurements', 'ts', if_not_exists => TRUE);

-- Crear índices para queries comunes
CREATE INDEX IF NOT EXISTS idx_facade_id ON measurements (facade_id);
CREATE INDEX IF NOT EXISTS idx_device_id ON measurements (device_id);
CREATE INDEX IF NOT EXISTS idx_facade_type ON measurements (facade_type);
CREATE INDEX IF NOT EXISTS idx_sensor_name ON measurements (sensor_name);
CREATE INDEX IF NOT EXISTS idx_facade_device_type ON measurements (facade_id, device_id, facade_type);