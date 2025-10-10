CREATE INDEX IF NOT EXISTS idx_alerts_facade_id ON alerts(facade_id);
CREATE INDEX IF NOT EXISTS idx_alerts_created_at ON alerts(created_at DESC);
