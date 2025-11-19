# 🚀 Documentación de Despliegue - Solar Facades

## 📋 Índice

1. [Resumen Ejecutivo](#resumen-ejecutivo)
2. [Arquitectura del Sistema](#arquitectura-del-sistema)
3. [Infraestructura en Google Cloud Platform](#infraestructura-en-google-cloud-platform)
4. [Componentes del Sistema](#componentes-del-sistema)
5. [Proceso de Despliegue](#proceso-de-despliegue)
6. [Configuración de CI/CD](#configuración-de-cicd)
7. [Comandos de Debug y Monitoreo](#comandos-de-debug-y-monitoreo)
8. [Gestión de Secretos y Configuración](#gestión-de-secretos-y-configuración)
9. [Escalabilidad y Alta Disponibilidad](#escalabilidad-y-alta-disponibilidad)
10. [Troubleshooting](#troubleshooting)
11. [Mejores Prácticas](#mejores-prácticas)

---

## 1. Resumen Ejecutivo

### 📊 Información General del Despliegue

| Parámetro | Valor |
|-----------|-------|
| **Proyecto GCP** | bicpv-478621 |
| **Región** | us-central1 |
| **Cluster GKE** | solar-facades-cluster |
| **Namespace** | solar-facades-prod |
| **Repositorio** | Alkran93/Project-BICPV |
| **Registry** | us-central1-docker.pkg.dev/bicpv-478621/solar-facades |

### 🌐 URLs de Acceso Público

| Servicio | URL | Descripción |
|----------|-----|-------------|
| **Frontend** | http://136.116.162.219 | Interfaz web React |
| **Backend API** | http://136.115.180.156:8000 | API REST FastAPI |
| **API Docs** | http://136.115.180.156:8000/docs | Documentación Swagger |
| **MQTT Broker** | 136.119.67.41:1883 | Broker Mosquitto para IoT |

### 🎯 Objetivos del Despliegue

El sistema Solar Facades está diseñado para monitorear en tiempo real fachadas solares refrigeradas y no refrigeradas, procesando datos de sensores IoT, almacenándolos en una base de datos de series temporales, y proporcionando análisis y alertas automáticas.

**Características clave:**
- ✅ Alta disponibilidad (múltiples réplicas)
- ✅ Escalado automático horizontal (HPA)
- ✅ CI/CD automatizado con Cloud Build
- ✅ Infraestructura como código (Terraform)
- ✅ Observabilidad completa (logs y métricas)

---

## 2. Arquitectura del Sistema

### 📐 Diagrama de Arquitectura

Ver archivo: [`docs/infrastructure.plantuml`](./infrastructure.plantuml)

Para visualizar el diagrama:
```bash
# Instalar PlantUML
sudo apt-get install plantuml

# Generar imagen
plantuml docs/infrastructure.plantuml
```

O usar: https://www.plantuml.com/plantuml/uml/

### 🏗️ Capas de la Arquitectura

#### 1. **Capa de Presentación**
- **Frontend (React)**: Interfaz de usuario web construida con React 19, TypeScript y Vite
- **Nginx**: Servidor web estático sirviendo la aplicación compilada
- **2 réplicas** para alta disponibilidad

#### 2. **Capa de Aplicación**
- **Backend (FastAPI)**: API REST con endpoints para sensores, alertas, análisis y reportes
- **2 réplicas** con balanceo de carga
- **HPA configurado** (2-10 pods según carga)

#### 3. **Capa de Ingesta de Datos**
- **Ingestor**: Consumidor MQTT que procesa mensajes de dispositivos IoT
- **2 réplicas** para procesamiento paralelo
- **Subscripción a topics**: `sensors/#`

#### 4. **Capa de Monitoreo**
- **Alert Monitor**: Worker que ejecuta análisis de anomalías cada 60 segundos
- **1 réplica** (singleton)
- Genera alertas automáticas ante fallos de sensores

#### 5. **Capa de Datos**
- **TimescaleDB**: PostgreSQL con extensión para series temporales
  - StatefulSet con 1 réplica
  - 50Gi de almacenamiento persistente
  - Hypertables para optimización
- **Redis**: Cache en memoria para mejorar rendimiento
  - 10Gi de almacenamiento persistente
  - TTL configurado en queries frecuentes
- **Mosquitto**: Broker MQTT para comunicación IoT
  - 5Gi de almacenamiento persistente
  - QoS 0 (at most once delivery)

#### 6. **Capa de Red**
- **LoadBalancer Services**: Backend y Frontend con IPs públicas
- **NodePort Service**: MQTT broker accesible externamente
- **ClusterIP Services**: Comunicación interna entre servicios
- **VPC**: Red privada virtual `solar-facades-cluster-vpc` (10.0.0.0/20)

---

## 3. Infraestructura en Google Cloud Platform

### 🔧 Recursos Desplegados con Terraform

```hcl
# Archivo: terraform/main.tf
```

#### 3.1 Red y Conectividad

**VPC (Virtual Private Cloud)**
```bash
Name: solar-facades-cluster-vpc
Subnet: 10.0.0.0/20
Region: us-central1
```

**Reglas de Firewall**
- `allow-mqtt-nodeport`: Permite tráfico TCP en puerto 1883 desde Internet
- Reglas automáticas de GKE para comunicación interna

**IPs Externas Reservadas**
```bash
gcloud compute addresses list --project=bicpv-478621
```

#### 3.2 GKE Cluster

**Configuración del Cluster**
```yaml
Name: solar-facades-cluster
Type: Regional (us-central1)
Version: 1.33.5-gke.1162000
Network: solar-facades-cluster-vpc
Workload Identity: Enabled
```

**Node Pools**

1. **General Purpose Pool**
   - Machine type: `e2-standard-4` (4 vCPUs, 16 GB RAM)
   - Min nodes: 2
   - Max nodes: 10
   - Autoscaling: Enabled
   - Workloads: Backend, Frontend, Ingestor, Alert Monitor

2. **Database Pool**
   - Machine type: `n2-standard-4` (4 vCPUs, 16 GB RAM)
   - Min nodes: 1
   - Max nodes: 3
   - Workloads: TimescaleDB, Redis, Mosquitto

#### 3.3 Artifact Registry

```bash
# Repositorio de imágenes Docker
Repository: solar-facades
Location: us-central1
Format: Docker
```

**Imágenes almacenadas:**
- `backend:latest` + `backend:{SHORT_SHA}`
- `frontend:latest` + `frontend:{SHORT_SHA}`
- `ingestor:latest` + `ingestor:{SHORT_SHA}`
- `alert-monitor:latest` + `alert-monitor:{SHORT_SHA}`

#### 3.4 Secret Manager

**Secretos almacenados:**
- `db-password`: Contraseña de TimescaleDB
- `redis-url`: URL de conexión a Redis

**Acceso mediante Workload Identity:**
```bash
# Service Accounts con permisos de lectura
- backend-sa@bicpv-478621.iam.gserviceaccount.com
- ingestor-sa@bicpv-478621.iam.gserviceaccount.com
- alert-monitor-sa@bicpv-478621.iam.gserviceaccount.com
```

#### 3.5 Cloud Storage

```bash
# Bucket para exports y reportes
Bucket: gs://bicpv-478621-solar-facades-exports
Region: us-central1
Storage Class: Standard
```

---

## 4. Componentes del Sistema

### 🖥️ Backend (FastAPI)

**Ubicación:** `backend/`

**Tecnologías:**
- FastAPI 0.109+
- asyncpg (PostgreSQL async driver)
- Redis (cache)
- paho-mqtt (MQTT client)
- matplotlib + reportlab (generación de reportes PDF)

**Endpoints principales:**
```
GET  /health                    - Health check
GET  /api/sensors/realtime      - Datos en tiempo real
GET  /api/sensors/history       - Histórico de sensores
GET  /api/alerts                - Lista de alertas
GET  /api/analytics/efficiency  - Análisis de eficiencia
GET  /api/reports/export        - Exportar datos (CSV/PDF)
POST /api/control/actions       - Acciones de control
```

**Dockerfile:** `backend/Dockerfile`
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8000"]
```

**Variables de entorno:**
- `DATABASE_URL`: Conexión a TimescaleDB (URL-encoded)
- `REDIS_URL`: Conexión a Redis
- `MQTT_BROKER`: Host del broker MQTT
- `MQTT_PORT`: Puerto MQTT (1883)

**Deployment:**
```yaml
# k8s/base/backend-deployment.yaml
replicas: 2
image: us-central1-docker.pkg.dev/bicpv-478621/solar-facades/backend:latest
resources:
  requests:
    cpu: 200m
    memory: 256Mi
  limits:
    cpu: 500m
    memory: 512Mi
```

---

### 🌐 Frontend (React)

**Ubicación:** `frontend/`

**Tecnologías:**
- React 19
- TypeScript 5.6
- Vite 7 (build tool)
- Chart.js (visualizaciones)
- Axios (HTTP client)
- TanStack Query (estado y cache)

**Build Args:**
```bash
VITE_API_URL=http://136.115.180.156:8000
```

**Dockerfile:** `frontend/Dockerfile.prod`
```dockerfile
# Multi-stage build
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
ARG VITE_API_URL
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 8080
CMD ["nginx", "-g", "daemon off;"]
```

**Configuración Nginx:**
```nginx
server {
    listen 8080;
    root /usr/share/nginx/html;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    location /health {
        access_log off;
        return 200 "OK\n";
    }
}
```

**Deployment:**
```yaml
# k8s/base/frontend-deployment.yaml
replicas: 2
image: us-central1-docker.pkg.dev/bicpv-478621/solar-facades/frontend:latest
resources:
  requests:
    cpu: 100m
    memory: 128Mi
  limits:
    cpu: 200m
    memory: 256Mi
```

---

### 📥 Ingestor (MQTT Consumer)

**Ubicación:** `ingestor/`

**Función:** Consume mensajes MQTT de dispositivos IoT y los inserta en TimescaleDB

**Tecnologías:**
- Python 3.11
- paho-mqtt
- asyncpg
- asyncio

**Lógica de procesamiento:**
1. Conecta al broker MQTT (mosquitto-service:1883)
2. Se subscribe a `sensors/#`
3. Recibe payloads JSON con datos de sensores
4. Valida y normaliza datos
5. Inserta en TimescaleDB de forma asíncrona
6. Actualiza cache en Redis

**Dockerfile:** `ingestor/Dockerfile`
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY main.py ./
CMD ["python", "main.py"]
```

**Variables de entorno:**
- `MQTT_BROKER`: mosquitto-service
- `MQTT_PORT`: 1883
- `MQTT_TOPIC`: sensors/#
- `DATABASE_URL`: Conexión a TimescaleDB

**Deployment:**
```yaml
# k8s/base/ingestor-deployment.yaml
replicas: 2
image: us-central1-docker.pkg.dev/bicpv-478621/solar-facades/ingestor:latest
```

---

### 🚨 Alert Monitor (Background Worker)

**Ubicación:** `alert_monitor.py`

**Función:** Monitoreo continuo de anomalías y generación de alertas

**Tecnologías:**
- Python 3.11
- asyncpg
- asyncio

**Lógica de monitoreo:**
```python
# Cada 60 segundos:
1. Query últimos 5 minutos de datos
2. Detectar valores fuera de rangos normales
3. Detectar sensores sin datos (fallos)
4. Insertar alertas en tabla `alerts`
5. Log de eventos críticos
```

**Thresholds de alertas:**
```python
ALERT_THRESHOLDS = {
    "Temperatura_Ambiente": {"min": -10, "max": 50},
    "Irradiancia": {"min": 0, "max": 1500},
    "Humedad": {"min": 0, "max": 100},
    "Presion_Alta": {"min": 0, "max": 300},
    "Presion_Baja": {"min": 0, "max": 100},
}
```

**Dockerfile:** `Dockerfile.alert-monitor`
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY alert_monitor.py ./
CMD ["python", "alert_monitor.py"]
```

**Deployment:**
```yaml
# k8s/base/alert-monitor-deployment.yaml
replicas: 1  # Singleton
image: us-central1-docker.pkg.dev/bicpv-478621/solar-facades/alert-monitor:latest
```

---

### 🗄️ TimescaleDB

**Configuración:** StatefulSet con 1 réplica

**Inicialización:**
```sql
-- initdb/init_timescaledb.sql
CREATE EXTENSION IF NOT EXISTS timescaledb;

CREATE TABLE sensor_data (
    ts TIMESTAMPTZ NOT NULL,
    facade_id TEXT,
    device_id TEXT,
    sensor_name TEXT,
    value DOUBLE PRECISION,
    PRIMARY KEY (ts, facade_id, device_id, sensor_name)
);

-- Convertir a hypertable para optimización
SELECT create_hypertable('sensor_data', 'ts');

-- Índices para consultas rápidas
CREATE INDEX idx_sensor_data_facade ON sensor_data(facade_id, ts DESC);
CREATE INDEX idx_sensor_data_device ON sensor_data(device_id, ts DESC);
```

**Tabla de Alertas:**
```sql
-- initdb/002_create_alerts.sql
CREATE TABLE alerts (
    id SERIAL PRIMARY KEY,
    ts TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    facade_id TEXT,
    device_id TEXT,
    sensor_name TEXT,
    alert_type TEXT,
    severity TEXT,
    value DOUBLE PRECISION,
    message TEXT
);

CREATE INDEX idx_alerts_ts ON alerts(ts DESC);
CREATE INDEX idx_alerts_severity ON alerts(severity, ts DESC);
```

**Persistent Volume:**
```yaml
volumeClaimTemplates:
  - metadata:
      name: timescaledb-data
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 50Gi
```

---

### 🔄 Redis

**Función:** Cache en memoria para queries frecuentes

**Estrategias de cache:**
- Latest sensor readings (TTL: 30s)
- Dashboard aggregations (TTL: 60s)
- Alert summaries (TTL: 120s)

**Configuración:**
```yaml
# k8s/base/redis-deployment.yaml
image: redis:7-alpine
command: ["redis-server", "--appendonly", "yes"]
```

**Persistent Volume:**
```yaml
storage: 10Gi
```

---

### 📡 Mosquitto (MQTT Broker)

**Versión:** Eclipse Mosquitto 2.0

**Configuración:**
```conf
# mosquitto/config/mosquitto.conf
listener 1883
allow_anonymous true
persistence true
persistence_location /mosquitto/data/
log_dest stdout
```

**Topics:**
- `sensors/{device_id}/all`: Payload completo de un dispositivo
- `sensors/{device_id}/{sensor}`: Sensor individual

**Servicios:**
```yaml
# ClusterIP (interno)
mosquitto-service: 1883

# NodePort (externo)
mosquitto-external: 32015 -> 1883
```

---

## 5. Proceso de Despliegue

### 📝 Pre-requisitos

```bash
# Herramientas necesarias
- gcloud CLI (>= 400.0.0)
- kubectl (>= 1.28)
- terraform (>= 1.5)
- docker (>= 24.0)
```

### 🚀 Despliegue Inicial (Manual)

#### Paso 1: Autenticación GCP

```bash
# Autenticar con GCP
gcloud auth login
gcloud config set project bicpv-478621

# Configurar credenciales para Terraform
gcloud auth application-default login
```

#### Paso 2: Habilitar APIs Necesarias

```bash
gcloud services enable \
  container.googleapis.com \
  compute.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com \
  secretmanager.googleapis.com \
  storage-api.googleapis.com \
  --project=bicpv-478621
```

#### Paso 3: Desplegar Infraestructura con Terraform

```bash
cd terraform

# Inicializar Terraform
terraform init

# Planificar cambios
terraform plan -out=tfplan

# Aplicar infraestructura
terraform apply tfplan
```

**Recursos creados:**
- VPC y subnets
- GKE cluster (tarda ~10-15 minutos)
- Artifact Registry
- Service Accounts
- Secrets en Secret Manager
- Cloud Storage bucket
- IPs estáticas reservadas

#### Paso 4: Configurar kubectl

```bash
# Obtener credenciales del cluster
gcloud container clusters get-credentials solar-facades-cluster \
  --region=us-central1 \
  --project=bicpv-478621

# Verificar conexión
kubectl cluster-info
kubectl get nodes
```

#### Paso 5: Crear Secretos en Kubernetes

```bash
# La contraseña está en Secret Manager
DB_PASSWORD=$(gcloud secrets versions access latest --secret=db-password --project=bicpv-478621)

# URL-encode la contraseña (importante para caracteres especiales)
DB_PASSWORD_ENCODED=$(python3 -c "import urllib.parse; print(urllib.parse.quote_plus('$DB_PASSWORD'))")

# Crear secret en Kubernetes
kubectl create secret generic solar-facades-secrets \
  --from-literal=DATABASE_URL="postgresql://postgres:${DB_PASSWORD_ENCODED}@timescaledb-service:5432/postgres" \
  --from-literal=REDIS_URL="redis://redis-service:6379/0" \
  -n solar-facades-prod
```

#### Paso 6: Aplicar Configuración de Kubernetes

```bash
# Aplicar en orden
kubectl apply -f k8s/base/namespace.yaml
kubectl apply -f k8s/base/configmap.yaml
kubectl apply -f k8s/base/storage.yaml
kubectl apply -f k8s/base/rbac.yaml

# Desplegar bases de datos
kubectl apply -f k8s/base/timescaledb-deployment.yaml
kubectl apply -f k8s/base/redis-deployment.yaml
kubectl apply -f k8s/base/mosquitto-deployment.yaml

# Esperar a que estén ready
kubectl wait --for=condition=ready pod -l app=timescaledb -n solar-facades-prod --timeout=300s
kubectl wait --for=condition=ready pod -l app=redis -n solar-facades-prod --timeout=120s
kubectl wait --for=condition=ready pod -l app=mosquitto -n solar-facades-prod --timeout=120s

# Aplicar servicios
kubectl apply -f k8s/base/services.yaml
kubectl apply -f k8s/base/frontend-service.yaml
```

#### Paso 7: Construir y Publicar Imágenes Docker

```bash
# Backend
docker build --no-cache -t us-central1-docker.pkg.dev/bicpv-478621/solar-facades/backend:latest \
  -f backend/Dockerfile ./backend
docker push us-central1-docker.pkg.dev/bicpv-478621/solar-facades/backend:latest

# Ingestor
docker build --no-cache -t us-central1-docker.pkg.dev/bicpv-478621/solar-facades/ingestor:latest \
  -f ingestor/Dockerfile ./ingestor
docker push us-central1-docker.pkg.dev/bicpv-478621/solar-facades/ingestor:latest

# Alert Monitor
docker build --no-cache -t us-central1-docker.pkg.dev/bicpv-478621/solar-facades/alert-monitor:latest \
  -f Dockerfile.alert-monitor .
docker push us-central1-docker.pkg.dev/bicpv-478621/solar-facades/alert-monitor:latest

# Frontend (con IP del backend)
BACKEND_IP=$(kubectl get service backend-service -n solar-facades-prod -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
docker build --no-cache --build-arg VITE_API_URL=http://${BACKEND_IP}:8000 \
  -t us-central1-docker.pkg.dev/bicpv-478621/solar-facades/frontend:latest \
  -f frontend/Dockerfile.prod ./frontend
docker push us-central1-docker.pkg.dev/bicpv-478621/solar-facades/frontend:latest
```

#### Paso 8: Desplegar Aplicaciones

```bash
# Desplegar aplicaciones
kubectl apply -f k8s/base/backend-deployment.yaml
kubectl apply -f k8s/base/ingestor-deployment.yaml
kubectl apply -f k8s/base/alert-monitor-deployment.yaml
kubectl apply -f k8s/base/frontend-deployment.yaml

# Aplicar HPA (autoscaling)
kubectl apply -f k8s/base/hpa.yaml
kubectl apply -f k8s/base/frontend-hpa.yaml

# Verificar estado
kubectl get pods -n solar-facades-prod
kubectl get services -n solar-facades-prod
```

#### Paso 9: Exponer Servicios Públicamente

```bash
# Cambiar backend y frontend a LoadBalancer
kubectl patch service backend-service -n solar-facades-prod -p '{"spec":{"type":"LoadBalancer"}}'
kubectl patch service frontend-service -n solar-facades-prod -p '{"spec":{"type":"LoadBalancer"}}'

# Exponer MQTT via NodePort
kubectl expose service mosquitto-service \
  --name=mosquitto-external \
  --type=NodePort \
  --port=1883 \
  --target-port=1883 \
  -n solar-facades-prod

# Obtener NodePort
MQTT_PORT=$(kubectl get service mosquitto-external -n solar-facades-prod -o jsonpath='{.spec.ports[0].nodePort}')

# Crear regla de firewall
gcloud compute firewall-rules create allow-mqtt-nodeport \
  --project=bicpv-478621 \
  --direction=INGRESS \
  --network=solar-facades-cluster-vpc \
  --action=ALLOW \
  --rules=tcp:${MQTT_PORT} \
  --source-ranges=0.0.0.0/0
```

#### Paso 10: Verificar Despliegue

```bash
# Obtener URLs públicas
echo "Frontend: http://$(kubectl get service frontend-service -n solar-facades-prod -o jsonpath='{.status.loadBalancer.ingress[0].ip}')"
echo "Backend: http://$(kubectl get service backend-service -n solar-facades-prod -o jsonpath='{.status.loadBalancer.ingress[0].ip}'):8000"
echo "Backend Docs: http://$(kubectl get service backend-service -n solar-facades-prod -o jsonpath='{.status.loadBalancer.ingress[0].ip}'):8000/docs"

# Verificar health
BACKEND_IP=$(kubectl get service backend-service -n solar-facades-prod -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
curl http://${BACKEND_IP}:8000/health
```

---

## 6. Configuración de CI/CD

### 🔄 Cloud Build Pipeline

El archivo `cloudbuild.yaml` define el pipeline completo de CI/CD.

#### 6.1 Configurar Cloud Build

```bash
# Habilitar Cloud Build API
gcloud services enable cloudbuild.googleapis.com --project=bicpv-478621

# Dar permisos a Cloud Build
PROJECT_NUMBER=$(gcloud projects describe bicpv-478621 --format='value(projectNumber)')
gcloud projects add-iam-policy-binding bicpv-478621 \
  --member=serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com \
  --role=roles/container.developer

gcloud projects add-iam-policy-binding bicpv-478621 \
  --member=serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com \
  --role=roles/artifactregistry.writer
```

#### 6.2 Crear Trigger en Cloud Build

**Opción A: Desde la consola web (Recomendado)**

1. Ve a: https://console.cloud.google.com/cloud-build/triggers?project=bicpv-478621
2. Click en **"CREATE TRIGGER"**
3. Conecta tu repositorio GitHub (Alkran93/Project-BICPV)
4. Configurar trigger:
   - **Name:** `solar-facades-deploy`
   - **Event:** Push to a branch
   - **Source:**
     - Repository: `Alkran93/Project-BICPV`
     - Branch: `^main$`
   - **Configuration:**
     - Type: Cloud Build configuration file
     - Location: `/cloudbuild.yaml`
   - **Region:** `us-central1`
5. Click **"CREATE"**

**Opción B: Desde la CLI**

```bash
# Requiere conectar GitHub primero desde la consola
gcloud builds triggers create github \
  --name="solar-facades-deploy" \
  --repo-name="Project-BICPV" \
  --repo-owner="Alkran93" \
  --branch-pattern="^main$" \
  --build-config="cloudbuild.yaml" \
  --project=bicpv-478621 \
  --region=us-central1
```

#### 6.3 Flujo del Pipeline

```yaml
# cloudbuild.yaml estructura:

1. Build Images (paralelo)
   - backend
   - ingestor
   - alert-monitor
   - frontend

2. Push to Artifact Registry (paralelo)
   - Tagea con SHA y latest
   - Almacena en registry

3. Get GKE Credentials
   - Conecta al cluster

4. Deploy to GKE (paralelo)
   - kubectl set image deployment/backend
   - kubectl set image deployment/ingestor
   - kubectl set image deployment/alert-monitor
   - kubectl set image deployment/frontend

5. Verify Rollout (secuencial)
   - kubectl rollout status (timeout 5min)
   - Verifica que pods estén Ready

6. Post-Deployment
   - kubectl get pods
   - Muestra estado final
```

#### 6.4 Variables del Pipeline

```yaml
substitutions:
  _REGION: us-central1
  _CLUSTER_NAME: solar-facades-cluster
  _NAMESPACE: solar-facades-prod
  _ARTIFACT_REGISTRY: ${_REGION}-docker.pkg.dev/${PROJECT_ID}/solar-facades
```

#### 6.5 Workflow Completo

```
Developer → git push origin main
    ↓
GitHub webhook → Cloud Build Trigger
    ↓
Cloud Build Pipeline Inicia
    ↓
Build 4 Docker Images (10-15 min)
    ↓
Push to Artifact Registry
    ↓
kubectl set image (actualiza deployments)
    ↓
Kubernetes Rollout (rolling update)
    ↓
Verify Pods Running
    ↓
✅ Deployment Complete
```

#### 6.6 Monitorear Builds

```bash
# Ver últimos builds
gcloud builds list --limit=10 --project=bicpv-478621

# Ver logs de un build específico
gcloud builds log <BUILD_ID> --project=bicpv-478621

# Ver builds en curso
gcloud builds list --ongoing --project=bicpv-478621

# Desde la web
# https://console.cloud.google.com/cloud-build/builds?project=bicpv-478621
```

#### 6.7 Trigger Manual

```bash
# Despliegue manual sin push a GitHub
gcloud builds submit --config=cloudbuild.yaml --project=bicpv-478621
```

---

## 7. Comandos de Debug y Monitoreo

### 🔍 Verificación de Pods

```bash
# Ver todos los pods
kubectl get pods -n solar-facades-prod

# Ver pods con más detalles
kubectl get pods -n solar-facades-prod -o wide

# Ver estado de pods específicos
kubectl get pods -l app=backend -n solar-facades-prod
kubectl get pods -l app=frontend -n solar-facades-prod
kubectl get pods -l app=ingestor -n solar-facades-prod
kubectl get pods -l app=alert-monitor -n solar-facades-prod

# Describir un pod (eventos, recursos, volúmenes)
kubectl describe pod <POD_NAME> -n solar-facades-prod

# Ver logs de un pod
kubectl logs <POD_NAME> -n solar-facades-prod

# Ver logs en tiempo real
kubectl logs -f <POD_NAME> -n solar-facades-prod

# Ver logs de todos los pods de un deployment
kubectl logs -f deployment/backend -n solar-facades-prod

# Ver logs de las últimas N líneas
kubectl logs --tail=100 <POD_NAME> -n solar-facades-prod

# Ver logs desde hace X tiempo
kubectl logs --since=10m <POD_NAME> -n solar-facades-prod

# Ver logs de contenedor previo (si crasheó)
kubectl logs <POD_NAME> --previous -n solar-facades-prod
```

### 🌐 Verificación de Servicios

```bash
# Ver todos los servicios
kubectl get services -n solar-facades-prod

# Ver servicios con IPs externas
kubectl get services -n solar-facades-prod -o wide

# Describir un servicio
kubectl describe service backend-service -n solar-facades-prod

# Ver endpoints de un servicio
kubectl get endpoints backend-service -n solar-facades-prod

# Test de conectividad interna
kubectl run test-pod --image=curlimages/curl -it --rm -n solar-facades-prod -- sh
# Dentro del pod:
curl http://backend-service:8000/health
curl http://timescaledb-service:5432
```

### 📊 Verificación de Deployments

```bash
# Ver deployments
kubectl get deployments -n solar-facades-prod

# Estado detallado de un deployment
kubectl describe deployment backend -n solar-facades-prod

# Ver ReplicaSets
kubectl get replicasets -n solar-facades-prod

# Historial de rollouts
kubectl rollout history deployment/backend -n solar-facades-prod

# Estado de un rollout en curso
kubectl rollout status deployment/backend -n solar-facades-prod

# Pausar un rollout
kubectl rollout pause deployment/backend -n solar-facades-prod

# Reanudar un rollout
kubectl rollout resume deployment/backend -n solar-facades-prod

# Rollback a versión anterior
kubectl rollout undo deployment/backend -n solar-facades-prod

# Rollback a versión específica
kubectl rollout undo deployment/backend --to-revision=2 -n solar-facades-prod
```

### 💾 Verificación de Almacenamiento

```bash
# Ver Persistent Volumes
kubectl get pv

# Ver Persistent Volume Claims
kubectl get pvc -n solar-facades-prod

# Describir un PVC
kubectl describe pvc timescaledb-data-timescaledb-0 -n solar-facades-prod

# Ver uso de disco en un pod
kubectl exec -it <POD_NAME> -n solar-facades-prod -- df -h
```

### 🔐 Verificación de Secrets y ConfigMaps

```bash
# Ver secrets
kubectl get secrets -n solar-facades-prod

# Ver contenido de un secret (base64 encoded)
kubectl get secret solar-facades-secrets -n solar-facades-prod -o yaml

# Decodificar un secret
kubectl get secret solar-facades-secrets -n solar-facades-prod -o jsonpath='{.data.DATABASE_URL}' | base64 -d

# Ver ConfigMaps
kubectl get configmaps -n solar-facades-prod

# Ver contenido de un ConfigMap
kubectl describe configmap solar-facades-config -n solar-facades-prod
```

### 📈 Verificación de HPA (Autoscaling)

```bash
# Ver HPAs
kubectl get hpa -n solar-facades-prod

# Estado detallado de HPA
kubectl describe hpa backend-hpa -n solar-facades-prod

# Ver métricas de pods
kubectl top pods -n solar-facades-prod

# Ver métricas de nodos
kubectl top nodes
```

### 🔄 Operaciones de Restart y Scale

```bash
# Restart de un deployment (rolling restart)
kubectl rollout restart deployment/backend -n solar-facades-prod

# Restart de todos los deployments
kubectl rollout restart deployment -n solar-facades-prod

# Escalar manualmente un deployment
kubectl scale deployment backend --replicas=3 -n solar-facades-prod

# Escalar a 0 (detener sin eliminar)
kubectl scale deployment backend --replicas=0 -n solar-facades-prod
```

### 🧪 Testing y Debugging

```bash
# Ejecutar comando en un pod
kubectl exec <POD_NAME> -n solar-facades-prod -- <comando>

# Ejemplo: verificar conectividad a DB
kubectl exec <BACKEND_POD> -n solar-facades-prod -- curl http://timescaledb-service:5432

# Shell interactivo en un pod
kubectl exec -it <POD_NAME> -n solar-facades-prod -- sh

# Port-forward para acceso local
kubectl port-forward service/backend-service 8000:8000 -n solar-facades-prod
# Accede en: http://localhost:8000

kubectl port-forward service/timescaledb-service 5432:5432 -n solar-facades-prod
# Conecta con: psql -h localhost -U postgres

# Copiar archivos desde/hacia un pod
kubectl cp <POD_NAME>:/path/to/file ./local-file -n solar-facades-prod
kubectl cp ./local-file <POD_NAME>:/path/to/file -n solar-facades-prod
```

### 🌐 Verificación de Red y Firewall

```bash
# Ver reglas de firewall
gcloud compute firewall-rules list --project=bicpv-478621

# Describir regla específica
gcloud compute firewall-rules describe allow-mqtt-nodeport --project=bicpv-478621

# Ver IPs de nodos
kubectl get nodes -o wide

# Test de conectividad externa a MQTT
telnet 34.71.114.102 32015

# Test con nc (netcat)
nc -zv 34.71.114.102 32015
```

### 📊 Logs y Eventos del Cluster

```bash
# Ver eventos recientes del namespace
kubectl get events -n solar-facades-prod --sort-by='.lastTimestamp'

# Ver eventos de un tipo específico
kubectl get events -n solar-facades-prod --field-selector type=Warning

# Ver logs de Cloud Logging (requiere gcloud)
gcloud logging read "resource.type=k8s_pod AND resource.labels.namespace_name=solar-facades-prod" --limit=50 --format=json
```

### 🔬 Troubleshooting Avanzado

```bash
# Verificar estado de nodos
kubectl get nodes
kubectl describe node <NODE_NAME>

# Ver recursos disponibles en el cluster
kubectl describe nodes | grep -A 5 "Allocated resources"

# Ver pods que no están Running
kubectl get pods -n solar-facades-prod --field-selector=status.phase!=Running

# Ver pods con alto restart count
kubectl get pods -n solar-facades-prod --sort-by='.status.containerStatuses[0].restartCount'

# Verificar imágenes de los pods
kubectl get pods -n solar-facades-prod -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.containers[0].image}{"\n"}{end}'

# Verificar readiness y liveness probes
kubectl get pods -n solar-facades-prod -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.status.conditions[?(@.type=="Ready")].status}{"\n"}{end}'
```

---

## 8. Gestión de Secretos y Configuración

### 🔐 Secret Manager (GCP)

```bash
# Listar secretos
gcloud secrets list --project=bicpv-478621

# Ver versiones de un secreto
gcloud secrets versions list db-password --project=bicpv-478621

# Acceder al valor de un secreto
gcloud secrets versions access latest --secret=db-password --project=bicpv-478621

# Crear un nuevo secreto
echo -n "mi-secreto" | gcloud secrets create nuevo-secreto --data-file=- --project=bicpv-478621

# Actualizar un secreto (crea nueva versión)
echo -n "nuevo-valor" | gcloud secrets versions add db-password --data-file=- --project=bicpv-478621

# Dar permisos de lectura a un Service Account
gcloud secrets add-iam-policy-binding db-password \
  --member="serviceAccount:backend-sa@bicpv-478621.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor" \
  --project=bicpv-478621
```

### 🔑 Kubernetes Secrets

```bash
# Crear secret desde literal
kubectl create secret generic mi-secret \
  --from-literal=username=admin \
  --from-literal=password=123456 \
  -n solar-facades-prod

# Crear secret desde archivo
kubectl create secret generic mi-secret \
  --from-file=credentials.json \
  -n solar-facades-prod

# Crear secret desde variables de entorno
kubectl create secret generic solar-facades-secrets \
  --from-literal=DATABASE_URL="postgresql://..." \
  --from-literal=REDIS_URL="redis://..." \
  -n solar-facades-prod \
  --dry-run=client -o yaml | kubectl apply -f -

# Actualizar un secret existente
kubectl delete secret solar-facades-secrets -n solar-facades-prod
kubectl create secret generic solar-facades-secrets \
  --from-literal=DATABASE_URL="nueva-url" \
  -n solar-facades-prod

# Después de actualizar, reiniciar pods
kubectl rollout restart deployment -n solar-facades-prod
```

### 📝 ConfigMaps

```bash
# Ver ConfigMaps
kubectl get configmap solar-facades-config -n solar-facades-prod -o yaml

# Editar ConfigMap
kubectl edit configmap solar-facades-config -n solar-facades-prod

# Aplicar cambios desde archivo
kubectl apply -f k8s/base/configmap.yaml

# Restart después de cambiar ConfigMap
kubectl rollout restart deployment -n solar-facades-prod
```

### 🔄 Workload Identity

Workload Identity permite que los pods accedan a servicios de GCP sin necesidad de service account keys.

```bash
# Verificar que Workload Identity está habilitado
gcloud container clusters describe solar-facades-cluster \
  --region=us-central1 \
  --format="value(workloadIdentityConfig.workloadPool)"

# Vincular KSA (Kubernetes Service Account) con GSA (Google Service Account)
kubectl create serviceaccount backend-ksa -n solar-facades-prod

gcloud iam service-accounts add-iam-policy-binding \
  backend-sa@bicpv-478621.iam.gserviceaccount.com \
  --role=roles/iam.workloadIdentityUser \
  --member="serviceAccount:bicpv-478621.svc.id.goog[solar-facades-prod/backend-ksa]"

kubectl annotate serviceaccount backend-ksa \
  iam.gke.io/gcp-service-account=backend-sa@bicpv-478621.iam.gserviceaccount.com \
  -n solar-facades-prod
```

---

## 9. Escalabilidad y Alta Disponibilidad

### 📈 Horizontal Pod Autoscaler (HPA)

**Backend HPA:**
```yaml
# k8s/base/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: backend-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: backend
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

**Comportamiento:**
- Scale up: Cuando CPU > 70% o Memory > 80%
- Scale down: Después de 5 minutos de carga baja
- Máximo: 10 pods
- Mínimo: 2 pods (alta disponibilidad)

**Monitorear HPA:**
```bash
# Ver estado de HPA
kubectl get hpa -n solar-facades-prod -w

# Ver métricas actuales
kubectl top pods -n solar-facades-prod
```

### 🔄 Rolling Updates

Kubernetes realiza rolling updates automáticamente al actualizar imágenes:

```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 1        # 1 pod adicional durante update
    maxUnavailable: 0  # Nunca tener menos réplicas que las configuradas
```

**Proceso:**
1. Crea 1 pod nuevo con la nueva imagen
2. Espera a que esté Ready (health checks)
3. Elimina 1 pod viejo
4. Repite hasta completar todas las réplicas

### 🛡️ Health Checks

**Liveness Probe:**
```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10
  failureThreshold: 3
```

**Readiness Probe:**
```yaml
readinessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 5
  failureThreshold: 3
```

### 🔁 StatefulSets para Bases de Datos

TimescaleDB usa StatefulSet para garantizar:
- Identidad de red estable (timescaledb-0)
- Almacenamiento persistente vinculado al pod
- Orden en el arranque y shutdown

### 🌐 LoadBalancer con Alta Disponibilidad

Los servicios LoadBalancer de GCP distribuyen tráfico automáticamente:
- Health checks a los pods
- Eliminación automática de pods no saludables
- Distribución de carga round-robin

---

## 10. Troubleshooting

### ❌ Problema: Pods en CrashLoopBackOff

**Síntoma:**
```bash
$ kubectl get pods -n solar-facades-prod
NAME                        READY   STATUS             RESTARTS
backend-xxx-yyy             0/1     CrashLoopBackOff   5
```

**Diagnóstico:**
```bash
# Ver logs del pod
kubectl logs backend-xxx-yyy -n solar-facades-prod

# Ver logs del contenedor anterior (antes del crash)
kubectl logs backend-xxx-yyy --previous -n solar-facades-prod

# Ver eventos del pod
kubectl describe pod backend-xxx-yyy -n solar-facades-prod
```

**Causas comunes:**
1. **Error en código:** Excepción no manejada al iniciar
2. **Falta de dependencias:** Módulo Python no instalado
3. **Configuración incorrecta:** Variable de entorno faltante
4. **No puede conectar a DB:** DATABASE_URL incorrecta o DB no disponible

**Solución:**
```bash
# Si es problema de imagen, rebuild sin cache
docker build --no-cache -t <image> -f <dockerfile> <context>
docker push <image>
kubectl rollout restart deployment/<deployment> -n solar-facades-prod
```

---

### ❌ Problema: ImagePullBackOff

**Síntoma:**
```bash
STATUS: ImagePullBackOff
```

**Diagnóstico:**
```bash
kubectl describe pod <POD_NAME> -n solar-facades-prod | grep -A 10 "Events:"
```

**Causas comunes:**
1. **Imagen no existe:** Typo en el nombre o tag
2. **Permisos:** GKE no tiene acceso a Artifact Registry
3. **Registry incorrecto:** gcr.io vs Artifact Registry

**Solución:**
```bash
# Verificar que la imagen existe
gcloud artifacts docker images list us-central1-docker.pkg.dev/bicpv-478621/solar-facades

# Verificar permisos
gcloud projects get-iam-policy bicpv-478621 | grep artifactregistry

# Corregir nombre de imagen en deployment
kubectl set image deployment/backend backend=us-central1-docker.pkg.dev/bicpv-478621/solar-facades/backend:latest -n solar-facades-prod
```

---

### ❌ Problema: Connection Refused a la Base de Datos

**Síntoma:**
```
ERROR: Connection refused to timescaledb-service:5432
```

**Diagnóstico:**
```bash
# Verificar que TimescaleDB está corriendo
kubectl get pods -l app=timescaledb -n solar-facades-prod

# Verificar el servicio
kubectl get service timescaledb-service -n solar-facades-prod

# Test de conectividad desde otro pod
kubectl run test --image=postgres:15 -it --rm -n solar-facades-prod -- psql -h timescaledb-service -U postgres
```

**Causas comunes:**
1. Pod de TimescaleDB no está Ready
2. Servicio mal configurado
3. DATABASE_URL incorrecta

**Solución:**
```bash
# Restart TimescaleDB
kubectl rollout restart statefulset/timescaledb -n solar-facades-prod

# Verificar DATABASE_URL
kubectl get secret solar-facades-secrets -n solar-facades-prod -o jsonpath='{.data.DATABASE_URL}' | base64 -d
```

---

### ❌ Problema: Password con Caracteres Especiales

**Síntoma:**
```
ValueError: invalid literal for int() with base 10: 'xyz'
```

**Causa:** La contraseña contiene `/`, `=`, `@`, etc. que no están URL-encoded.

**Solución:**
```bash
# URL-encode la contraseña
PASSWORD=$(gcloud secrets versions access latest --secret=db-password --project=bicpv-478621)
ENCODED=$(python3 -c "import urllib.parse; print(urllib.parse.quote_plus('$PASSWORD'))")

# Actualizar secret
kubectl create secret generic solar-facades-secrets \
  --from-literal=DATABASE_URL="postgresql://postgres:${ENCODED}@timescaledb-service:5432/postgres" \
  --from-literal=REDIS_URL="redis://redis-service:6379/0" \
  -n solar-facades-prod \
  --dry-run=client -o yaml | kubectl apply -f -

# Restart pods
kubectl rollout restart deployment -n solar-facades-prod
```

---

### ❌ Problema: Frontend no se conecta al Backend

**Síntoma:** Frontend carga pero no muestra datos, errores CORS en consola del navegador.

**Diagnóstico:**
```bash
# Verificar que el backend está accesible
curl http://34.135.241.88:8000/health

# Ver configuración del frontend
kubectl describe pod <FRONTEND_POD> -n solar-facades-prod | grep VITE_API_URL
```

**Causa:** Frontend compilado con VITE_API_URL incorrecta (localhost en lugar de IP pública).

**Solución:**
```bash
# Rebuild frontend con IP correcta del backend
BACKEND_IP=$(kubectl get service backend-service -n solar-facades-prod -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

docker build --no-cache --build-arg VITE_API_URL=http://${BACKEND_IP}:8000 \
  -t us-central1-docker.pkg.dev/bicpv-478621/solar-facades/frontend:latest \
  -f frontend/Dockerfile.prod ./frontend

docker push us-central1-docker.pkg.dev/bicpv-478621/solar-facades/frontend:latest

kubectl rollout restart deployment/frontend -n solar-facades-prod
```

---

### ❌ Problema: MQTT Connection Timeout

**Síntoma:**
```
[ERROR] Failed to connect to MQTT broker 34.71.114.102:32015 -> timed out
```

**Diagnóstico:**
```bash
# Verificar reglas de firewall
gcloud compute firewall-rules list --filter="name:mqtt" --project=bicpv-478621

# Test de conectividad
nc -zv 34.71.114.102 32015
telnet 34.71.114.102 32015
```

**Causa:** Firewall bloqueando el NodePort.

**Solución:**
```bash
# Obtener NodePort
MQTT_PORT=$(kubectl get service mosquitto-external -n solar-facades-prod -o jsonpath='{.spec.ports[0].nodePort}')

# Crear regla de firewall
gcloud compute firewall-rules create allow-mqtt-nodeport \
  --project=bicpv-478621 \
  --direction=INGRESS \
  --network=solar-facades-cluster-vpc \
  --action=ALLOW \
  --rules=tcp:${MQTT_PORT} \
  --source-ranges=0.0.0.0/0

# Esperar 5-10 segundos para propagación
sleep 10

# Reintentar conexión
python publisher_simulator.py --host 34.71.114.102 --port $MQTT_PORT --freq 5
```

---

### ❌ Problema: Pods Pendientes (Pending)

**Síntoma:**
```bash
STATUS: Pending
```

**Diagnóstico:**
```bash
kubectl describe pod <POD_NAME> -n solar-facades-prod
```

**Causas comunes:**
1. **Recursos insuficientes:** No hay nodos con CPU/RAM disponible
2. **PVC no puede ser bound:** Problema con almacenamiento
3. **Taints y Tolerations:** Pod no puede schedulear en nodos disponibles

**Solución:**
```bash
# Verificar recursos del cluster
kubectl describe nodes | grep -A 5 "Allocated resources"

# Verificar PVCs
kubectl get pvc -n solar-facades-prod

# Si faltan recursos, escalar node pool
gcloud container clusters resize solar-facades-cluster \
  --node-pool=general-pool \
  --num-nodes=3 \
  --region=us-central1 \
  --project=bicpv-478621
```

---

### ❌ Problema: HPA no escala

**Síntoma:** Carga alta pero HPA no crea más pods.

**Diagnóstico:**
```bash
# Ver estado de HPA
kubectl get hpa -n solar-facades-prod
kubectl describe hpa backend-hpa -n solar-facades-prod

# Verificar metrics-server
kubectl get deployment metrics-server -n kube-system
```

**Causa:** Metrics server no instalado o no funcional.

**Solución:**
```bash
# GKE tiene metrics-server por defecto, verificar:
kubectl top nodes
kubectl top pods -n solar-facades-prod

# Si no funciona, esperar unos minutos (puede tardar en inicializar)
```

---

## 11. Mejores Prácticas

### 🛡️ Seguridad

1. **Nunca commitear secretos** en Git
   - Usa Secret Manager o Kubernetes Secrets
   - Añade archivos sensibles a `.gitignore`

2. **Principio de mínimo privilegio**
   - Service Accounts solo con permisos necesarios
   - Usa Workload Identity en lugar de service account keys

3. **Escaneo de imágenes**
   ```bash
   # Escanear imagen antes de deploy
   gcloud artifacts docker images scan us-central1-docker.pkg.dev/bicpv-478621/solar-facades/backend:latest
   ```

4. **Network Policies**
   - Restringir comunicación entre pods
   - Permitir solo tráfico necesario

5. **HTTPS/TLS**
   - Usar Ingress con certificados SSL
   - Configurar Let's Encrypt con cert-manager

### 📊 Observabilidad

1. **Structured Logging**
   ```python
   import logging
   import json
   
   logger.info(json.dumps({
       "timestamp": datetime.now().isoformat(),
       "level": "INFO",
       "message": "Request processed",
       "request_id": request_id,
       "duration_ms": duration
   }))
   ```

2. **Métricas personalizadas**
   - Exportar métricas Prometheus
   - Integrar con Cloud Monitoring

3. **Alertas**
   - Configurar alertas en Cloud Monitoring
   - Notificaciones a Slack/Email

4. **Tracing distribuido**
   - Implementar OpenTelemetry
   - Rastrear requests entre microservicios

### 🚀 Performance

1. **Resource Limits y Requests**
   ```yaml
   resources:
     requests:
       cpu: 200m
       memory: 256Mi
     limits:
       cpu: 500m
       memory: 512Mi
   ```

2. **Caching estratégico**
   - Cache en Redis con TTL apropiado
   - CDN para assets estáticos

3. **Optimización de queries**
   - Índices en TimescaleDB
   - Connection pooling en asyncpg

4. **Compresión**
   - Gzip en Nginx
   - Compresión de responses en API

### 🔄 CI/CD

1. **Versionado semántico**
   ```bash
   # Tagear images con version y SHA
   v1.2.3
   v1.2.3-abc123
   ```

2. **Ambientes separados**
   - dev, staging, production
   - Namespaces diferentes

3. **Rollback rápido**
   ```bash
   # Mantener versiones anteriores
   kubectl rollout undo deployment/backend -n solar-facades-prod
   ```

4. **Tests automáticos**
   - Unit tests en pipeline
   - Integration tests antes de deploy

### 💾 Backup y Disaster Recovery

1. **Backup de TimescaleDB**
   ```bash
   # Ejecutar pg_dump periódicamente
   kubectl exec timescaledb-0 -n solar-facades-prod -- \
     pg_dump -U postgres > backup-$(date +%Y%m%d).sql
   
   # Subir a Cloud Storage
   gsutil cp backup-*.sql gs://bicpv-478621-solar-facades-backups/
   ```

2. **Snapshot de PVs**
   ```bash
   # Crear VolumeSnapshot
   kubectl create -f volume-snapshot.yaml
   ```

3. **Plan de recuperación**
   - Documentar pasos de restore
   - Practicar recuperación periódicamente

### 📈 Escalabilidad

1. **Diseño stateless**
   - Backend sin estado en memoria
   - Sesiones en Redis

2. **Separación de concerns**
   - Backend para API
   - Ingestor para procesamiento asíncrono
   - Alert Monitor para análisis

3. **Throttling y Rate Limiting**
   ```python
   from fastapi_limiter import FastAPILimiter
   
   @app.get("/api/sensors")
   @limiter.limit("100/minute")
   async def get_sensors():
       ...
   ```

4. **Queue para workloads pesados**
   - Cloud Tasks o Pub/Sub
   - Procesamiento asíncrono de reportes

---

## 📚 Recursos Adicionales

### Documentación Oficial

- [Google Kubernetes Engine](https://cloud.google.com/kubernetes-engine/docs)
- [Cloud Build](https://cloud.google.com/build/docs)
- [Artifact Registry](https://cloud.google.com/artifact-registry/docs)
- [Terraform GCP Provider](https://registry.terraform.io/providers/hashicorp/google/latest/docs)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [TimescaleDB Documentation](https://docs.timescale.com/)

### Herramientas Útiles

- [k9s](https://k9scli.io/) - Terminal UI para Kubernetes
- [kubectx + kubens](https://github.com/ahmetb/kubectx) - Cambio rápido de contextos
- [stern](https://github.com/stern/stern) - Multi-pod log tailing
- [Lens](https://k8slens.dev/) - IDE para Kubernetes

---

## 📝 Changelog

| Versión | Fecha | Cambios |
|---------|-------|---------|
| 1.0.0 | 2025-11-09 | Despliegue inicial en GKE |
| 1.1.0 | 2025-11-09 | Configuración CI/CD con Cloud Build |
| 1.2.0 | 2025-11-09 | Exposición pública de MQTT broker |

---

## 👥 Contacto y Soporte

Para preguntas o issues relacionados con el despliegue, contacta al equipo de DevOps.

**Repositorio:** [Alkran93/Project-BICPV](https://github.com/Alkran93/Project-BICPV)

---

**Última actualización:** 9 de Noviembre, 2025
