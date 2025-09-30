#!/bin/bash
# GCP Cloud Run Deployment Script for ETL Dashboard Frontend

# Configuration
PROJECT_ID="yazaki-etl-dashboard"
SERVICE_NAME="frontend-service"
REGION="us-central1"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo "🚀 Deploying ETL Dashboard Frontend to GCP Cloud Run..."

# Build the Docker image
echo "📦 Building Docker image..."
docker build -f Dockerfile.frontend -t ${IMAGE_NAME}:latest .

# Push to Google Container Registry
echo "📤 Pushing image to Google Container Registry..."
docker push ${IMAGE_NAME}:latest

# Deploy to Cloud Run
echo "🌐 Deploying to Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
  --image ${IMAGE_NAME}:latest \
  --platform managed \
  --region ${REGION} \
  --allow-unauthenticated \
  --port 8080 \
  --timeout 900 \
  --memory 2Gi \
  --cpu 2 \
  --max-instances 10 \
  --set-env-vars PORT=8080,FLASK_ENV=production,PYTHONPATH=/app \
  --project ${PROJECT_ID}

# Get the service URL
echo "✅ Deployment complete!"
echo "🔗 Service URL:"
gcloud run services describe ${SERVICE_NAME} --region=${REGION} --format='value(status.url)' --project ${PROJECT_ID}

echo ""
echo "🔍 You can monitor logs at:"
echo "https://console.cloud.google.com/logs/viewer?project=${PROJECT_ID}&resource=cloud_run_revision/service_name/${SERVICE_NAME}"