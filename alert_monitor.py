"""
Alert Monitor Worker
Continuous monitoring service that detects anomalies and generates alerts.

HU15: Receive automatic alerts when sensor failures or refrigeration system faults are detected.
"""
import asyncio
import asyncpg
from typing import List, Dict, Any
from datetime import datetime, timezone
import os

# Environment variables
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres:postgres@timescaledb:5432/postgres"
)

# Alert thresholds (same as alerts_service.py)
ALERT_THRESHOLDS = {
    "Temperatura_Ambiente": {"min": -10, "max": 50},
    "Irradiancia": {"min": 0, "max": 1500},
    "Velocidad_Viento": {"min": 0, "max": 30},
    "Humedad": {"min": 0, "max": 100},
    "T_ValvulaExpansion": {"min": -50, "max": 50},
    "T_EntCompresor": {"min": -50, "max": 80},
    "T_SalCompresor": {"min": -50, "max": 100},
    "T_SalCondensador": {"min": -50, "max": 80},
    "T_Entrada_Agua": {"min": -10, "max": 60},
    "T_Salida_Agua": {"min": -10, "max": 60},
    "Presion_Alta": {"min": 0, "max": 500},
    "Presion_Baja": {"min": 0, "max": 30},
    "Flujo_Agua_LPM": {"min": 0, "max": 500},
}


async def check_for_anomalies(pool: asyncpg.Pool) -> None:
    """
    Checks recent measurements for anomalies and creates alert records.
    
    Anomaly types:
    - NULL or negative values (sensor errors)
    - Values outside defined thresholds
    - Missing readings (sensor inactive)
    """
    print(f"🔍 Checking for anomalies at {datetime.now(timezone.utc).isoformat()}")
    
    try:
        # Query recent measurements (last 5 minutes)
        sql = """
            SELECT facade_id, device_id, facade_type, sensor_name, value, ts
            FROM measurements
            WHERE ts >= NOW() - INTERVAL '5 minutes'
            ORDER BY ts DESC
        """
        
        async with pool.acquire() as conn:
            rows = await conn.fetch(sql)
        
        alerts_to_insert = []
        
        for row in rows:
            facade_id = row["facade_id"]
            sensor_name = row["sensor_name"]
            value = row["value"]
            ts = row["ts"]
            
            # Check for NULL or negative values
            if value is None or value < 0:
                alerts_to_insert.append({
                    "facade_id": facade_id,
                    "sensor_name": sensor_name,
                    "alert_type": "sensor_error",
                    "severity": "critical",
                    "description": f"Sensor {sensor_name} reported invalid value: {value}",
                    "value": value,
                    "threshold": None
                })
                continue
            
            # Check thresholds
            if sensor_name in ALERT_THRESHOLDS:
                threshold = ALERT_THRESHOLDS[sensor_name]
                
                if value < threshold["min"]:
                    alerts_to_insert.append({
                        "facade_id": facade_id,
                        "sensor_name": sensor_name,
                        "alert_type": "value_below_threshold",
                        "severity": "warning" if abs(value - threshold["min"]) < 5 else "critical",
                        "description": f"Sensor {sensor_name} value ({value:.2f}) below minimum ({threshold['min']})",
                        "value": value,
                        "threshold": threshold["min"]
                    })
                
                elif value > threshold["max"]:
                    alerts_to_insert.append({
                        "facade_id": facade_id,
                        "sensor_name": sensor_name,
                        "alert_type": "value_above_threshold",
                        "severity": "warning" if abs(value - threshold["max"]) < 5 else "critical",
                        "description": f"Sensor {sensor_name} value ({value:.2f}) above maximum ({threshold['max']})",
                        "value": value,
                        "threshold": threshold["max"]
                    })
        
        # Insert alerts into database
        if alerts_to_insert:
            insert_sql = """
                INSERT INTO alerts (facade_id, sensor_name, alert_type, severity, description, value, threshold)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
            """
            
            async with pool.acquire() as conn:
                async with conn.transaction():
                    for alert in alerts_to_insert:
                        await conn.execute(
                            insert_sql,
                            alert["facade_id"],
                            alert["sensor_name"],
                            alert["alert_type"],
                            alert["severity"],
                            alert["description"],
                            alert["value"],
                            alert["threshold"]
                        )
            
            print(f"✅ Generated {len(alerts_to_insert)} alerts")
        else:
            print("✅ No anomalies detected")
    
    except Exception as e:
        print(f"❌ Error checking for anomalies: {e}")


async def check_inactive_sensors(pool: asyncpg.Pool) -> None:
    """
    Checks for sensors that haven't reported data recently (inactive sensors).
    """
    print(f"📡 Checking for inactive sensors at {datetime.now(timezone.utc).isoformat()}")
    
    try:
        # Find sensors with no data in last 10 minutes
        sql = """
            WITH latest_readings AS (
                SELECT DISTINCT ON (facade_id, sensor_name)
                    facade_id, sensor_name, ts
                FROM measurements
                ORDER BY facade_id, sensor_name, ts DESC
            )
            SELECT facade_id, sensor_name, ts
            FROM latest_readings
            WHERE ts < NOW() - INTERVAL '10 minutes'
        """
        
        async with pool.acquire() as conn:
            rows = await conn.fetch(sql)
        
        if rows:
            insert_sql = """
                INSERT INTO alerts (facade_id, sensor_name, alert_type, severity, description)
                VALUES ($1, $2, $3, $4, $5)
            """
            
            async with pool.acquire() as conn:
                async with conn.transaction():
                    for row in rows:
                        await conn.execute(
                            insert_sql,
                            row["facade_id"],
                            row["sensor_name"],
                            "sensor_inactive",
                            "medium",
                            f"Sensor {row['sensor_name']} inactive for > 10 minutes. Last reading: {row['ts']}"
                        )
            
            print(f"⚠️ Found {len(rows)} inactive sensors")
        else:
            print("✅ All sensors active")
    
    except Exception as e:
        print(f"❌ Error checking inactive sensors: {e}")


async def cleanup_old_alerts(pool: asyncpg.Pool) -> None:
    """
    Cleans up alerts older than 30 days to prevent database bloat.
    """
    try:
        sql = "DELETE FROM alerts WHERE created_at < NOW() - INTERVAL '30 days'"
        
        async with pool.acquire() as conn:
            result = await conn.execute(sql)
        
        # Extract count from result string like "DELETE 42"
        count = int(result.split()[-1]) if result.split()[-1].isdigit() else 0
        
        if count > 0:
            print(f"🧹 Cleaned up {count} old alerts")
    
    except Exception as e:
        print(f"❌ Error cleaning up old alerts: {e}")


async def main():
    """
    Main monitoring loop that runs continuously.
    """
    print("🚀 Starting Alert Monitor Worker...")
    
    # Initialize database connection
    try:
        pool = await asyncpg.create_pool(dsn=DATABASE_URL, min_size=1, max_size=5)
        print("✅ Connected to TimescaleDB")
    except Exception as e:
        print(f"❌ Failed to connect to database: {e}")
        return
    
    # Monitoring intervals
    anomaly_check_interval = 60  # Check every 60 seconds
    inactive_check_interval = 300  # Check every 5 minutes
    cleanup_interval = 86400  # Clean up once per day
    
    last_inactive_check = 0
    last_cleanup = 0
    
    try:
        while True:
            current_time = asyncio.get_event_loop().time()
            
            # Check for anomalies
            await check_for_anomalies(pool)
            
            # Check for inactive sensors (every 5 minutes)
            if current_time - last_inactive_check >= inactive_check_interval:
                await check_inactive_sensors(pool)
                last_inactive_check = current_time
            
            # Cleanup old alerts (once per day)
            if current_time - last_cleanup >= cleanup_interval:
                await cleanup_old_alerts(pool)
                last_cleanup = current_time
            
            # Wait before next check
            await asyncio.sleep(anomaly_check_interval)
    
    except KeyboardInterrupt:
        print("\n🛑 Alert Monitor stopped by user")
    except Exception as e:
        print(f"❌ Fatal error in Alert Monitor: {e}")
    finally:
        if pool:
            await pool.close()
            print("🛑 Database connection closed")


if __name__ == "__main__":
    asyncio.run(main())
