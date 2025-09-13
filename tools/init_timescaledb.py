#!/usr/bin/env python3
"""
Script para inicializar TimescaleDB con las tablas necesarias
para el proyecto IoT Fachada Solar
"""

import asyncio
import sys
from pathlib import Path

import asyncpg


# Agregar el directorio raíz del proyecto al path
sys.path.append(str(Path(__file__).parent.parent))

from core.config import settings


async def init_database():
    """Inicializa la base de datos TimescaleDB"""

    try:
        # Conectar a la base de datos
        conn = await asyncpg.connect(settings.DATABASE_URL)

        # Leer el archivo SQL de inicialización
        sql_file = Path(__file__).parent / "db" / "init_timescaledb.sql"
        if not sql_file.exists():
            sql_file = Path(__file__).parent.parent / "db" / "init_timescaledb.sql"

        with open(sql_file, encoding="utf-8") as f:
            sql_script = f.read()

        # Ejecutar el script SQL
        await conn.execute(sql_script)

        # Verificar que la tabla fue creada
        result = await conn.fetch("""
            SELECT table_name, table_type
            FROM information_schema.tables
            WHERE table_name = 'measurements'
        """)

        if result:
            # Verificar hypertable
            hypertable_info = await conn.fetch("""
                SELECT * FROM timescaledb_information.hypertables
                WHERE hypertable_name = 'measurements'
            """)

            if hypertable_info:
                pass

            # Mostrar índices creados
            indexes = await conn.fetch("""
                SELECT indexname, indexdef
                FROM pg_indexes
                WHERE tablename = 'measurements'
                ORDER BY indexname
            """)

            for _idx in indexes:
                pass

        await conn.close()

        # Probar inserción de datos de prueba
        await test_insertion()

    except Exception:
        raise


async def test_insertion():
    """Prueba la inserción de datos en la tabla"""

    try:
        conn = await asyncpg.connect(settings.DATABASE_URL)

        # Datos de prueba
        test_data = [
            (
                "2024-01-01 12:00:00+00",
                "raspi01",
                "Temperatura_L1_1",
                25.5,
                "°C",
                '{"test": true}',
                "1",
            ),
            (
                "2024-01-01 12:00:00+00",
                "raspi01",
                "Irradiancia",
                850.2,
                "W/m²",
                '{"test": true}',
                "1",
            ),
            (
                "2024-01-01 12:00:00+00",
                "raspi01",
                "Velocidad_Viento",
                3.2,
                "m/s",
                '{"test": true}',
                "1",
            ),
        ]

        # Insertar datos de prueba
        await conn.executemany(
            """
            INSERT INTO measurements (
                ts, device_id, sensor_id, value, unit, tags, facade_id
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7)
        """,
            test_data,
        )

        # Verificar inserción
        await conn.fetchval("SELECT COUNT(*) FROM measurements")

        # Limpiar datos de prueba
        await conn.execute("DELETE FROM measurements WHERE tags->>'test' = 'true'")

        await conn.close()

    except Exception:
        raise


async def show_database_info():
    """Muestra información de la base de datos"""

    try:
        conn = await asyncpg.connect(settings.DATABASE_URL)

        # Información de TimescaleDB
        version_info = await conn.fetch("SELECT * FROM timescaledb_information.license")
        if version_info:
            for _info in version_info:
                pass

        # Información de hypertables
        hypertables = await conn.fetch(
            "SELECT * FROM timescaledb_information.hypertables"
        )
        for _ht in hypertables:
            pass

        # Información de chunks
        chunks = await conn.fetch("""
            SELECT chunk_schema, chunk_name, range_start, range_end
            FROM timescaledb_information.chunks
            WHERE hypertable_name = 'measurements'
            ORDER BY range_start DESC
            LIMIT 5
        """)
        for _chunk in chunks:
            pass

        await conn.close()

    except Exception:
        pass


if __name__ == "__main__":

    async def main():
        await init_database()
        await show_database_info()

    asyncio.run(main())
