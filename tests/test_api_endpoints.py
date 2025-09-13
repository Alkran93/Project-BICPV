import httpx
import pytest


# Add asyncio_mode configuration
pytestmark = pytest.mark.asyncio

BASE_URL = "http://localhost:8000/api"


async def test_overview():
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{BASE_URL}/overview/")
        assert r.status_code == 200
        assert isinstance(r.json(), list)


async def test_overview_facade():
    async with httpx.AsyncClient() as client:
        # Cambia '1' por un facade_id válido en tu base
        r = await client.get(f"{BASE_URL}/overview/1")
        assert r.status_code in (200, 404)
        if r.status_code == 200:
            assert "facade_id" in r.json()


async def test_sensors_list():
    async with httpx.AsyncClient() as client:
        # Cambia '1' por un facade_id válido
        r = await client.get(f"{BASE_URL}/sensors/list/1")
        assert r.status_code == 200
        assert isinstance(r.json(), list)


async def test_sensor_data():
    async with httpx.AsyncClient() as client:
        # Cambia 'Temperatura_L1_2' y '1' por valores válidos
        r = await client.get(f"{BASE_URL}/sensors/Temperatura_L1_2/1")
        assert r.status_code in (200, 404)
        if r.status_code == 200:
            assert isinstance(r.json(), list)


async def test_environment_variables():
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{BASE_URL}/environment/variables/1")
        assert r.status_code == 200
        assert isinstance(r.json(), list)


async def test_environment_data():
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{BASE_URL}/environment/data/Irradiancia/1")
        assert r.status_code in (200, 404)
        if r.status_code == 200:
            assert isinstance(r.json(), list)


async def test_charts_timeseries():
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{BASE_URL}/charts/timeseries/Irradiancia/1")
        assert r.status_code in (200, 404)
        if r.status_code == 200:
            assert isinstance(r.json(), list)


async def test_charts_available():
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{BASE_URL}/charts/available/1")
        assert r.status_code == 200
        assert isinstance(r.json(), list)


async def test_analytics_stats():
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{BASE_URL}/analytics/stats/Irradiancia/1")
        assert r.status_code in (200, 404)
        if r.status_code == 200:
            assert "avg" in r.json()


async def test_analytics_anomalies():
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{BASE_URL}/analytics/anomalies/Irradiancia/1")
        assert r.status_code in (200, 404)
        if r.status_code == 200:
            assert isinstance(r.json(), list)


async def test_dashboard_realtime():
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{BASE_URL}/dashboard/realtime/1")
        assert r.status_code == 200
        assert isinstance(r.json(), list)


async def test_dashboard_average():
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{BASE_URL}/dashboard/average/Irradiancia")
        assert r.status_code == 200
        assert "average" in r.json()


async def test_dashboard_facade_data():
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{BASE_URL}/dashboard/facade/1/data")
        assert r.status_code == 200
        assert isinstance(r.json(), list)


async def test_dashboard_logs():
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{BASE_URL}/dashboard/logs")
        assert r.status_code == 200
        assert isinstance(r.json(), list)
