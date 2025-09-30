# GCP Cloud Run Deployment Commands and Instructions

## 🚀 **Complete Deployment Scripts Created**

### **📁 Available Scripts:**

1. **`deploy-gcp.ps1`** - Complete frontend + backend deployment (PowerShell)
2. **`deploy-gcp.sh`** - Complete frontend + backend deployment (Bash)
3. **`deploy-frontend-only.ps1`** - Frontend only deployment
4. **`deploy-backend-only.ps1`** - Backend only deployment

---

## 🛠️ **Usage Instructions**

### **Option 1: Deploy Both Services (Recommended)**
```powershell
# PowerShell (Windows)
.\deploy-gcp.ps1
```

```bash
# Bash (Linux/Mac)
chmod +x deploy-gcp.sh
./deploy-gcp.sh
```

### **Option 2: Deploy Services Individually**

**Deploy Backend First:**
```powershell
.\deploy-backend-only.ps1
```

**Deploy Frontend (uses backend URL automatically):**
```powershell
.\deploy-frontend-only.ps1
```

**Deploy Frontend with specific backend URL:**
```powershell
.\deploy-frontend-only.ps1 -BackendUrl "https://your-backend-url.run.app"
```

### **Option 3: Skip Build (if images already pushed)**
```powershell
# Skip building, just deploy existing images
.\deploy-frontend-only.ps1 -SkipBuild
.\deploy-backend-only.ps1 -SkipBuild
```

---

## 🔧 **Manual Commands (if scripts don't work)**

### **1. Setup Authentication:**
```bash
gcloud auth login
gcloud config set project yazaki-etl-dashboard
gcloud auth configure-docker europe-west3-docker.pkg.dev
```

### **2. Build and Push Images:**
```bash
# Backend
docker build -f Dockerfile.backend -t europe-west3-docker.pkg.dev/yazaki-etl-dashboard/etl-dashboard/backend-service:latest .
docker push europe-west3-docker.pkg.dev/yazaki-etl-dashboard/etl-dashboard/backend-service:latest

# Frontend
docker build -f Dockerfile.frontend -t europe-west3-docker.pkg.dev/yazaki-etl-dashboard/etl-dashboard/frontend-service:latest .
docker push europe-west3-docker.pkg.dev/yazaki-etl-dashboard/etl-dashboard/frontend-service:latest
```

### **3. Deploy Services:**
```bash
# Deploy Backend
gcloud run deploy backend-service \
    --image europe-west3-docker.pkg.dev/yazaki-etl-dashboard/etl-dashboard/backend-service:latest \
    --platform managed \
    --region europe-west3 \
    --allow-unauthenticated \
    --port 8000 \
    --memory 2Gi \
    --timeout 900

# Get Backend URL
BACKEND_URL=$(gcloud run services describe backend-service --region=europe-west3 --format='value(status.url)')

# Deploy Frontend with Backend URL
gcloud run deploy frontend-service \
    --image europe-west3-docker.pkg.dev/yazaki-etl-dashboard/etl-dashboard/frontend-service:latest \
    --platform managed \
    --region europe-west3 \
    --allow-unauthenticated \
    --port 8080 \
    --memory 2Gi \
    --timeout 900 \
    --set-env-vars "PORT=8080,FLASK_ENV=production,PYTHONPATH=/app,FASTAPI_HOST=${BACKEND_URL},FASTAPI_PORT=443"
```

---

## 🧪 **Testing After Deployment**

### **Get Service URLs:**
```bash
# Frontend URL
gcloud run services describe frontend-service --region=europe-west3 --format='value(status.url)'

# Backend URL
gcloud run services describe backend-service --region=europe-west3 --format='value(status.url)'
```

### **Test Endpoints:**
```bash
# Test Backend Health
curl https://your-backend-url.run.app/health

# Test Frontend
curl https://your-frontend-url.run.app/

# Test Backend API Docs
open https://your-backend-url.run.app/docs
```

---

## 🔍 **Monitoring and Logs**

### **View Logs:**
```bash
# Frontend logs
gcloud logs read "resource.type=cloud_run_revision AND resource.labels.service_name=frontend-service" --project=yazaki-etl-dashboard --limit=50

# Backend logs
gcloud logs read "resource.type=cloud_run_revision AND resource.labels.service_name=backend-service" --project=yazaki-etl-dashboard --limit=50
```

### **Web Console Links:**
- **Frontend Logs:** https://console.cloud.google.com/logs/viewer?project=yazaki-etl-dashboard&resource=cloud_run_revision/service_name/frontend-service
- **Backend Logs:** https://console.cloud.google.com/logs/viewer?project=yazaki-etl-dashboard&resource=cloud_run_revision/service_name/backend-service

---

## 🚨 **Troubleshooting**

### **Common Issues:**

1. **Authentication Error:**
   ```bash
   gcloud auth login
   gcloud auth configure-docker europe-west3-docker.pkg.dev
   ```

2. **Port Issues:**
   - Frontend: Ensure PORT=8080 is set
   - Backend: Ensure port 8000 is exposed

3. **Service Communication:**
   - Ensure frontend has correct FASTAPI_HOST environment variable
   - Check that backend URL is accessible

4. **Build Timeouts:**
   - Increase build timeout: `--timeout 1800`
   - Use cloud build instead of local build

---

## ✅ **Quick Start**

**Run this single command to deploy everything:**
```powershell
.\deploy-gcp.ps1
```

This will:
1. ✅ Authenticate with GCP
2. ✅ Build both images
3. ✅ Push to Artifact Registry
4. ✅ Deploy backend service
5. ✅ Deploy frontend service with correct backend URL
6. ✅ Test both services
7. ✅ Display service URLs