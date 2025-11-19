## Table of Contents

- Overview
- System Architecture
- Prerequisites
- Quick Start
- Detailed Setup Instructions
  - 1. Clone the Repository
  - 2. Backend Setup
  - 3. Frontend Setup
  - 4. Database and Services
  - 5. MQTT Simulator
- Running the Full Stack
- Environment Variables
- API Documentation
- Testing
- Troubleshooting
- Project Structure
- Development Workflow
- Contributing
- Support

---

## Overview

This system monitors and analyzes temperature, environmental conditions, and performance metrics from two photovoltaic solar facades:
- **Refrigerated facade**: Equipped with active cooling system
- **Non-refrigerated facade**: Standard operation without cooling

**Key Features:**
- Real-time sensor data ingestion via MQTT
- TimescaleDB for efficient time-series storage
- RESTful API with FastAPI
- Interactive React dashboard with Chart.js visualizations
- Automated alerts and performance comparisons
- CSV data export functionality
- **Production-ready deployment on Google Kubernetes Engine (GKE)**

---

# Solar Facades Monitoring System

[![GKE Deployment](https://img.shields.io/badge/GKE-Ready-4285F4?logo=google-cloud)](docs/GKE_DEPLOYMENT_GUIDE.md)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi)](backend/)
[![React](https://img.shields.io/badge/React-19-61DAFB?logo=react)](frontend/)
[![TimescaleDB](https://img.shields.io/badge/TimescaleDB-FDB515?logo=postgresql)](docker-compose.yml)

> Real-time monitoring and analysis system for photovoltaic solar facades with active cooling
---

### 📖 Documentation

### What's Included in GKE Deployment

- ✅ **Auto-scaling**: 2-10 replicas based on load
- ✅ **High Availability**: Multi-zone deployment
- ✅ **SSL/HTTPS**: Google-managed certificates (with domain)
- ✅ **Monitoring**: Cloud Monitoring & Logging
- ✅ **CI/CD**: Automated deployments
- ✅ **Cost Optimized**: ~$520-900/month with scaling

###  URLs de Acceso Público

| Servicio | URL | Descripción |
|----------|-----|-------------|
| **Frontend** | http://136.116.162.219 | Interfaz web React |
| **Backend API** | http://136.115.180.156:8000 | API REST FastAPI |
| **API Docs** | http://136.115.180.156:8000/docs | Documentación Swagger |
| **MQTT Broker** | 136.119.67.41:1883 | Broker Mosquitto para IoT |

---

## System Architecture

```
┌─────────────────┐
│ MQTT Simulator  │ ──> Publishes sensor data
└────────┬────────┘
         │
         v
┌─────────────────┐
│ Mosquitto MQTT  │ ──> Message broker
└────────┬────────┘
         │
         v
┌─────────────────┐
│ Ingestor        │ ──> Consumes MQTT, writes to DB
│ (Python/asyncio)│
└────────┬────────┘
         │
         v
┌─────────────────┐      ┌──────────────┐
│ TimescaleDB     │ <──> │ Redis Cache  │
│ (PostgreSQL)    │      └──────────────┘
└────────┬────────┘
         │
         v
┌─────────────────┐
│ FastAPI Backend │ ──> REST API
└────────┬────────┘
         │
         v
┌─────────────────┐
│ React Frontend  │ ──> User Interface
└─────────────────┘
```

---

## Prerequisites

Ensure the following are installed on your system:

| Tool | Version | Purpose |
|------|---------|---------|
| **Docker** | >= 24.0 | Container runtime |
| **Docker Compose** | >= 2.20 | Multi-container orchestration |
| **Node.js** | >= 20.x | Frontend development |
| **npm** | >= 10.x | Package management |
| **Python** | >= 3.11 | Simulator and local testing |
| **Git** | Latest | Version control |

### Installation Commands

**Ubuntu/Debian:**
```bash
# Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Node.js 20.x
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Python 3.11
sudo apt install python3.11 python3.11-venv python3-pip
```

**Verify installations:**
```bash
docker --version
sudo docker compose --version
node -v
npm -v
python3 --version
```

---

## Quick Start

For experienced developers who want to get running immediately:

```bash
# 1. Clone and navigate
git clone <repository-url>
cd project

# 2. Start infrastructure
sudo docker compose up --build

# 3. Start MQTT simulator
python publisher_simulator.py --facades "no_refrigerada:1:raspi_no_ref_01"
python publisher_simulator.py --facades "refrigerada:2:raspi_ref_01"

# - API Docs: http://0.0.0.0:8000/docs
# - Database: localhost:5432
```

---

## Detailed Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd project
```

**Backend Structure:**
```
backend/
├── app/
│   ├── api/           # FastAPI route handlers
│   ├── services/      # Business logic layer
│   ├── core/          # Configuration
│   ├── db.py          # Database connection
│   └── main.py        # Application entry point
├── Dockerfile
└── requirements.txt
```

### 2. Database and Services

All infrastructure services run via Docker Compose:

```bash
# Start all services
sudo docker compose up  --build

# View logs
sudo docker compose logs -f

# Stop services
sudo docker compose down

# Rebuild after code changes
sudo docker compose up -d --build
```

**Services:**
- **TimescaleDB**: PostgreSQL with TimescaleDB extension (port 5432)
- **Mosquitto MQTT**: Message broker (port 1884)
- **Redis**: Caching layer (port 6379)
- **Ingestor**: MQTT consumer → Database writer
- **Backend**: FastAPI application (port 8000)

**Database Initialization:**
The database schema is automatically created via init_timescaledb.sql on first startup.

### 3. MQTT Simulator

Simulates sensor data from both facades:

```bash
# Install dependencies
pip install paho-mqtt

# Run with default settings (facade_id=1)
python3 publisher_simulator.py

# Run for specific facade
python3 publisher_simulator.py --facade_id 2 --facade_type refrigerada

# Available options:
# --facade_id      Facade identifier (default: 1)
# --facade_type    refrigerada | no_refrigerada (default: no_refrigerada)
# --interval       Publish interval in seconds (default: 5)
```

**Simulated Sensors:**
- Temperature sensors (15 per facade: 5 modules × 3 points)
- Environmental: Irradiance, Wind Speed, Ambient Temperature, Humidity
- Refrigeration cycle: Compressor, Condenser, Expansion Valve temperatures
- Water temperatures: Inlet/Outlet
- Pressures: High/Low side
- Flow rate and valve state

---

### Ingestor (`ingestor/.env`)

```env
# MQTT
MQTT_BROKER=mosquitto
MQTT_PORT=1883

# Database
DATABASE_URL=postgresql://postgres:postgres@timescaledb:5432/postgres

# Redis
REDIS_URL=redis://redis:6379/0
```

### Frontend (No .env needed)

API URL is configured in components (defaults to `http://127.0.0.1:8000`).

---

## API Documentation

Once the backend is running, access interactive documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/api/dashboard/realtime/{facade_id}` | GET | Real-time sensor data |
| `/api/analytics/environment/{facade_id}` | GET | Environmental variables |
| `/api/analytics/compare/{facade_id}` | GET | Facade type comparison |
| `/api/temperatures/refrigerant-cycle/{facade_id}` | GET | Refrigeration cycle temps |
| `/api/export/csv/{facade_id}` | GET | CSV data export |
| `/api/alerts/history/{facade_id}` | GET | Alert history |

---

## Troubleshooting

### Common Issues

#### 1. **Database connection refused**

**Symptoms:**
```
asyncpg.exceptions.ConnectionRefusedError: Connection refused
```

**Solutions:**
```bash
# Ensure TimescaleDB is running
docker compose ps timescaledb

# Check database logs
docker compose logs timescaledb

# Restart database
docker compose restart timescaledb

# Wait for health check
docker compose ps | grep healthy
```

#### 2. **MQTT simulator not publishing**

**Symptoms:**
```
Connection refused to mosquitto:1883
```

**Solutions:**
```bash
# Check Mosquitto is running
docker-compose ps mosquitto

# Verify port mapping
docker-compose ps | grep 1884

# Test MQTT connection
mosquitto_sub -h localhost -p 1884 -t "sensor/#" -v

# Use correct port in simulator
python3 publisher_simulator.py --broker localhost --port 1884
```

#### 3. **No data in database**

**Symptoms:**
Empty responses from API endpoints

**Solutions:**
```bash
# Check ingestor logs
docker compose logs ingestor

# Verify simulator is running
ps aux | grep publisher_simulator

# Query database directly
docker compose exec timescaledb psql -U postgres -d postgres -c "SELECT COUNT(*) FROM measurements;"

# Restart ingestor
docker compose restart ingestor
```

#### 5. **Port already in use**

**Symptoms:**
```
Error starting userland proxy: listen tcp 0.0.0.0:8000: bind: address already in use
```

**Solutions:**
```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>

# Or change port in docker-compose.yml
```

### Debug Mode

Enable verbose logging:

```bash
# Backend
export LOG_LEVEL=DEBUG
uvicorn app.main:app --reload --log-level debug

# Ingestor
# Add to main.py:
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## Project Structure

```
project/
├── backend/
│   ├── app/
│   │   ├── api/              # API routes (HU endpoints)
│   │   ├── services/         # Business logic (SOLID)
│   │   ├── core/             # Config & settings
│   │   ├── db.py             # Database connection pool
│   │   └── main.py           # FastAPI application
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── pages/            # Page layouts
│   │   ├── styles/           # CSS modules
│   │   └── main.tsx          # Entry point
│   ├── public/               # Static assets
│   ├── package.json
│   └── vite.config.ts
├── ingestor/
│   ├── main.py               # MQTT → DB pipeline
│   ├── Dockerfile
│   └── requirements.txt
├── initdb/
│   ├── init_timescaledb.sql  # Database schema
│   ├── 002_create_alerts.sql
│   └── 003_create_alerts_index.sql
├── mosquitto/
│   └── config/               # MQTT broker config
├── docker-compose.yml        # Service orchestration
├── publisher_simulator.py    # Sensor data simulator
└── README.md
```

---

## Support

### Documentation
- **API Docs**: http://localhost:8000/docs (when running)
- **Database Schema**: See init_timescaledb.sql
- **User Stories**: Documented in API endpoint docstrings

### Contact
- **Technical Issues**: Open GitHub issue
- **Development Questions**: Contact development team lead
- **Infrastructure**: DevOps team

### Useful Commands Reference

```bash
# Restart everything
docker compose down && docker-compose up -d

# View specific service logs
docker compose logs -f backend

# Access database shell
docker compose exec timescaledb psql -U postgres -d postgres

# Check Redis cache
docker compose exec redis redis-cli KEYS "*"

# Rebuild after dependency changes
docker compose up -d --build

# Clean everything (⚠️ deletes data)
docker compose down -v
```

---

**Project Status**: Development    
