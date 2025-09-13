"""
Repositorio TimescaleDB para el sistema de monitoreo IoT.
"""

import contextlib
from typing import Optional

import asyncpg


class TimeScaleDBStorage:
    """Clase para manejar el almacenamiento en TimescaleDB"""

    def __init__(self, connection: asyncpg.Connection):
        self.conn = connection
        self._initialized = False

    async def ensure_tables_exist(self):
        """Asegura que las tablas necesarias existan, las crea si no"""
        if self._initialized:
            return

        try:
            # Verificar si la tabla measurements existe
            table_exists = await self.conn.fetchval("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_name = 'measurements'
                );
            """)

            if not table_exists:
                await self._create_database_structure()

            self._initialized = True

        except Exception:
            raise

    async def _create_database_structure(self):
        """Crea la estructura completa de la base de datos"""

        # SQL para crear la estructura completa
        create_structure_sql = """
        -- Crear extensión TimescaleDB si no existe
        CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;

        -- Crear tabla de mediciones
        CREATE TABLE IF NOT EXISTS measurements (
            ts TIMESTAMPTZ NOT NULL,
            device_id TEXT NOT NULL,
            sensor_id TEXT NOT NULL,
            value DOUBLE PRECISION NOT NULL,
            unit TEXT,
            tags JSONB,
            facade_id TEXT,
            created_at TIMESTAMPTZ DEFAULT NOW()
        );

        -- Crear hypertable con particionamiento por tiempo
        SELECT create_hypertable('measurements', 'ts', if_not_exists => TRUE);

        -- Crear índices para mejorar el rendimiento
        CREATE INDEX IF NOT EXISTS idx_measurements_device_id
            ON measurements (device_id);
        CREATE INDEX IF NOT EXISTS idx_measurements_sensor_id
            ON measurements (sensor_id);
        CREATE INDEX IF NOT EXISTS idx_measurements_facade_id
            ON measurements (facade_id);
        CREATE INDEX IF NOT EXISTS idx_measurements_device_sensor
            ON measurements (device_id, sensor_id);
        CREATE INDEX IF NOT EXISTS idx_measurements_facade_sensor
            ON measurements (facade_id, sensor_id);
        CREATE INDEX IF NOT EXISTS idx_measurements_ts_desc ON measurements (ts DESC);

        -- Índice GIN para consultas JSONB
        CREATE INDEX IF NOT EXISTS idx_measurements_tags_gin
            ON measurements USING GIN (tags);
        """

        try:
            await self.conn.execute(create_structure_sql)

            # Configurar políticas de retención y compresión (opcional)
            with contextlib.suppress(Exception):
                # La política puede fallar en versiones de TimescaleDB que no la soportan
                await self.conn.execute("""
                    SELECT add_retention_policy('measurements', INTERVAL '1 year',
                                               if_not_exists => TRUE);
                """)

            with contextlib.suppress(Exception):
                # La compresión puede fallar en versiones Community
                await self.conn.execute("""
                    SELECT add_compression_policy('measurements', INTERVAL '7 days',
                                                 if_not_exists => TRUE);
                """)

        except Exception:
            raise

    async def store(self, data: list[tuple]) -> None:
        """
        Almacena una lista de tuplas de datos en TimescaleDB

        Args:
            data: Lista de tuplas (timestamp, device_id, sensor_id, value,
                  unit, tags, facade_id)
        """
        # Asegurar que las tablas existan antes de insertar
        await self.ensure_tables_exist()

        if not data:
            return

        try:
            query = """
            INSERT INTO measurements (
                ts, device_id, sensor_id, value, unit, tags, facade_id
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            """

            await self.conn.executemany(query, data)

        except Exception:
            raise

    async def query_recent(self, limit: int = 100) -> list[dict]:
        """Consulta los datos más recientes"""
        await self.ensure_tables_exist()

        try:
            query = """
            SELECT ts, device_id, sensor_id, value, unit, facade_id, tags
            FROM measurements
            ORDER BY ts DESC
            LIMIT $1
            """

            result = await self.conn.fetch(query, limit)
            return [dict(row) for row in result]

        except Exception:
            raise

    async def get_sensor_data(
        self, sensor_id: str, facade_id: Optional[str] = None, hours: int = 24
    ) -> list[dict]:
        """Obtiene datos de un sensor específico"""
        await self.ensure_tables_exist()

        try:
            if facade_id:
                query = f"""
                SELECT ts, value, unit, device_id
                FROM measurements
                WHERE sensor_id = $1 AND facade_id = $2
                AND ts >= NOW() - INTERVAL '{hours} hours'
                ORDER BY ts DESC
                """
                result = await self.conn.fetch(query, sensor_id, facade_id)
            else:
                query = f"""
                SELECT ts, value, unit, device_id, facade_id
                FROM measurements
                WHERE sensor_id = $1
                AND ts >= NOW() - INTERVAL '{hours} hours'
                ORDER BY ts DESC
                """
                result = await self.conn.fetch(query, sensor_id)

            return [dict(row) for row in result]

        except Exception:
            raise

    async def close(self):
        """Cierra la conexión"""
        if self.conn and not self.conn.is_closed():
            await self.conn.close()
