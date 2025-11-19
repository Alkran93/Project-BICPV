# GitHub Actions CI/CD Workflow

Este repositorio incluye un workflow completo de CI/CD que se ejecuta automáticamente con cada push a `main`.

## 🚀 Workflow Overview

**Archivo:** `.github/workflows/deploy.yml`

### Trigger
- ✅ Push a rama `main`
- ✅ Pull Request a rama `main`

### Pipeline Steps

1. **📦 Checkout** - Descarga el código del repositorio
2. **🔐 Auth GCP** - Autenticación con Google Cloud
3. **☁️ Setup SDK** - Configuración de Cloud SDK
4. **🐳 Docker Config** - Configuración de Docker para Artifact Registry
5. **🔨 Build Images** - Construcción de todas las imágenes:
   - Backend (FastAPI)
   - Frontend (React + Vite + Nginx)
   - Ingestor (MQTT → TimescaleDB)
   - Alert Monitor (Monitoreo de anomalías)
6. **📤 Push Images** - Subida a `us-central1-docker.pkg.dev/bicpv-478621/solar-facades/`
7. **🔑 GKE Credentials** - Obtención de credenciales del cluster
8. **🚀 Deploy** - Despliegue en Kubernetes con `kubectl rollout restart`
9. **✅ Verify** - Verificación del estado de pods y servicios

## 📊 Arquitectura del Deployment

```
GitHub Push → GitHub Actions → Build Images → Push to Artifact Registry
                                                        ↓
                                              GKE Cluster (us-central1)
                                                        ↓
                                      ┌─────────────────┴─────────────────┐
                                      │     solar-facades-prod namespace   │
                                      ├────────────────────────────────────┤
                                      │  • Backend (FastAPI)               │
                                      │  • Frontend (Nginx)                │
                                      │  • Ingestor (MQTT)                 │
                                      │  • Alert Monitor                   │
                                      │  • TimescaleDB                     │
                                      │  • Redis                           │
                                      │  • Mosquitto (MQTT)                │
                                      └────────────────────────────────────┘
```

## 🔧 Configuración Inicial

### 1. Crear Service Account en GCP

```bash
# Crear service account
gcloud iam service-accounts create github-actions-cicd \
  --display-name="GitHub Actions CI/CD" \
  --project=bicpv-478621

# Asignar roles necesarios
gcloud projects add-iam-policy-binding bicpv-478621 \
  --member="serviceAccount:github-actions-cicd@bicpv-478621.iam.gserviceaccount.com" \
  --role="roles/container.developer"

gcloud projects add-iam-policy-binding bicpv-478621 \
  --member="serviceAccount:github-actions-cicd@bicpv-478621.iam.gserviceaccount.com" \
  --role="roles/artifactregistry.writer"

gcloud projects add-iam-policy-binding bicpv-478621 \
  --member="serviceAccount:github-actions-cicd@bicpv-478621.iam.gserviceaccount.com" \
  --role="roles/storage.admin"

# Crear clave JSON
gcloud iam service-accounts keys create github-actions-key.json \
  --iam-account=github-actions-cicd@bicpv-478621.iam.gserviceaccount.com
```

### 2. Configurar Secreto en GitHub

**Opción A: Usando el script automatizado**

```bash
./setup-github-actions.sh
```

**Opción B: Manualmente con gh CLI**

```bash
# Autenticar
gh auth login

# Configurar secreto
gh secret set GCP_SA_KEY < github-actions-key.json

# Verificar
gh secret list
```

**Opción C: Interfaz web de GitHub**

1. Ve a: `https://github.com/Alkran93/Project-BICPV/settings/secrets/actions`
2. Click en "New repository secret"
3. Nombre: `GCP_SA_KEY`
4. Valor: Contenido completo de `github-actions-key.json`
5. Click "Add secret"

## 🧪 Probar el Workflow

```bash
# Hacer un cambio pequeño
echo "# Test CI/CD" >> README.md

# Commit y push
git add .
git commit -m "ci: test automated deployment pipeline"
git push origin main
```

Luego ve a: https://github.com/Alkran93/Project-BICPV/actions

## 📝 Logs y Monitoreo

### Ver logs del workflow en GitHub Actions

```bash
# Listar workflows recientes
gh run list --limit 5

# Ver detalles de un run específico
gh run view <run-id>

# Ver logs de un run
gh run view <run-id> --log
```

### Ver estado del deployment en GKE

```bash
# Ver pods
kubectl get pods -n solar-facades-prod

# Ver deployments
kubectl get deployments -n solar-facades-prod

# Ver servicios
kubectl get svc -n solar-facades-prod

# Ver logs de un pod específico
kubectl logs <pod-name> -n solar-facades-prod --tail=100 -f
```

## 🔄 Rollback

Si un deployment falla, puedes hacer rollback:

```bash
# Rollback backend
kubectl rollout undo deployment/backend -n solar-facades-prod

# Rollback frontend
kubectl rollout undo deployment/frontend -n solar-facades-prod

# Ver historial de rollouts
kubectl rollout history deployment/backend -n solar-facades-prod
```

## 🛡️ Seguridad

### ⚠️ IMPORTANTE

- ❌ **NUNCA** hagas commit de `github-actions-key.json`
- ✅ El archivo está en `.gitignore`
- ✅ Solo GitHub Actions tiene acceso a `GCP_SA_KEY`
- ✅ La clave está encriptada en GitHub Secrets

### Revocar una clave comprometida

```bash
# Listar claves
gcloud iam service-accounts keys list \
  --iam-account=github-actions-cicd@bicpv-478621.iam.gserviceaccount.com

# Eliminar clave específica
gcloud iam service-accounts keys delete <key-id> \
  --iam-account=github-actions-cicd@bicpv-478621.iam.gserviceaccount.com

# Crear nueva clave
gcloud iam service-accounts keys create github-actions-key-new.json \
  --iam-account=github-actions-cicd@bicpv-478621.iam.gserviceaccount.com

# Actualizar secreto en GitHub
gh secret set GCP_SA_KEY < github-actions-key-new.json
```

## 📈 Optimizaciones

### Build Cache

El workflow usa cache de Docker layers para builds más rápidos. Si necesitas limpiar el cache:

```bash
# En GitHub Actions, puedes agregar:
docker builder prune -f
```

### Parallel Builds

Las imágenes se construyen secuencialmente. Para builds paralelos, modifica el workflow para usar `strategy.matrix`.

## 🐛 Troubleshooting

### Error: "Permission denied"

**Solución:** Verifica que el Service Account tenga los roles correctos:

```bash
gcloud projects get-iam-policy bicpv-478621 \
  --flatten="bindings[].members" \
  --filter="bindings.members:github-actions-cicd@bicpv-478621.iam.gserviceaccount.com"
```

### Error: "Image not found"

**Solución:** Verifica que Artifact Registry existe y el nombre es correcto:

```bash
gcloud artifacts repositories list --project=bicpv-478621
```

### Error: "Deployment timeout"

**Solución:** Aumenta el timeout en el workflow o verifica los pods:

```bash
kubectl describe pod <pod-name> -n solar-facades-prod
kubectl logs <pod-name> -n solar-facades-prod
```

## 📚 Recursos

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Google Cloud Authentication](https://github.com/google-github-actions/auth)
- [GKE Credentials](https://github.com/google-github-actions/get-gke-credentials)
- [Kubernetes Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)

## 🎯 Best Practices

1. ✅ **Siempre testea localmente primero** antes de push
2. ✅ **Usa semantic commits** (feat:, fix:, ci:, docs:)
3. ✅ **Revisa los logs del workflow** después de cada deployment
4. ✅ **Monitorea los pods** después del deployment
5. ✅ **Mantén backups** de las configuraciones críticas
6. ✅ **Documenta cambios** en el workflow

## 📞 Soporte

Si encuentras problemas, revisa:

1. 📖 Este README
2. 📄 `GITHUB_ACTIONS_SETUP.md` - Guía detallada de configuración
3. 📄 `DESPLIEGUE.md` - Documentación completa del proyecto
4. 🔧 Logs del workflow en GitHub Actions
5. 🐳 Logs de pods en GKE

---

**Última actualización:** 19 de noviembre de 2025  
**Versión del Workflow:** 1.0  
**Cluster:** `solar-facades-cluster` (us-central1)  
**Namespace:** `solar-facades-prod`
