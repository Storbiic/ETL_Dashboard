# 🔧 GCP Cloud Run Port Configuration - FIXED

## ✅ Changes Made

### 1. Updated Dockerfile.frontend
- **Changed exposed port**: `EXPOSE 3000` → `EXPOSE $PORT`
- **Added PORT environment variable**: `ENV PORT=8080`
- **Updated CMD**: Now uses `${PORT:-8080}` for dynamic port assignment
- **Fixed health check**: Uses `${PORT:-8080}` instead of hardcoded 3000

### 2. Updated frontend/app.py
- **Config class**: Changed default port from 5000 to 8080
- **Development server**: Now prioritizes PORT environment variable
- **Host binding**: Changed from 127.0.0.1 to 0.0.0.0 for container compatibility

## 🚀 Deployment Instructions

### Option 1: PowerShell Deployment (Windows)
```powershell
.\deploy-frontend-gcp.ps1
```

### Option 2: Manual Deployment
```bash
# Build image
docker build -f Dockerfile.frontend -t gcr.io/yazaki-etl-dashboard/frontend-service:latest .

# Push to Google Container Registry
docker push gcr.io/yazaki-etl-dashboard/frontend-service:latest

# Deploy to Cloud Run
gcloud run deploy frontend-service \
  --image gcr.io/yazaki-etl-dashboard/frontend-service:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080 \
  --timeout 900 \
  --memory 2Gi \
  --cpu 2 \
  --max-instances 10 \
  --set-env-vars PORT=8080,FLASK_ENV=production,PYTHONPATH=/app \
  --project yazaki-etl-dashboard
```

## 🔍 Key Fixes for Cloud Run

1. **Port 8080**: Cloud Run requires containers to listen on port 8080
2. **Dynamic PORT**: Container reads PORT environment variable provided by Cloud Run
3. **Host 0.0.0.0**: Container binds to all interfaces for Cloud Run networking
4. **Environment Variables**: Proper configuration for production deployment

## 🧪 Testing

- **Local Test**: Run `python test_gcp_config.py` to verify configuration
- **Docker Test**: Build and test locally with `PORT=8080` environment variable

## 📋 Next Steps

1. Ensure Docker Desktop is running
2. Run the deployment script: `.\deploy-frontend-gcp.ps1`
3. Monitor deployment logs in GCP Console
4. Test the deployed service URL

The previous "container failed to start and listen on port 8080" error should now be resolved!