#!/bin/bash

# Render deployment startup script for ETL Dashboard
set -e

echo "🚀 Starting ETL Dashboard on Render..."
echo "PORT: $PORT"
echo "Environment: $ENV"
echo "Python Path: $PYTHONPATH"

# Ensure data directories exist
mkdir -p /app/data/uploads
mkdir -p /app/data/processed
mkdir -p /app/data/pipeline_output

echo "📁 Data directories created"

# Set permissions
chmod -R 755 /app/data/

# Start backend in background
echo "🔧 Starting backend server on port 8000..."
cd /app && python -m uvicorn backend.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --log-level info \
    --access-log &

BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"

# Wait for backend to be ready
echo "⏳ Waiting for backend to start..."
for i in {1..30}; do
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Backend is ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ Backend failed to start within 30 seconds"
        exit 1
    fi
    sleep 1
done

# Start frontend on the PORT provided by Render
echo "🌐 Starting frontend server on port $PORT..."

# Set Flask configuration for production
export FLASK_APP=frontend.app
export FLASK_ENV=production
export FLASK_DEBUG=false

# Start frontend
cd /app && python -c "
import os
from frontend.app import app, Config

print(f'Frontend starting on port {Config.PORT}')
print(f'Backend URL: {Config.FASTAPI_BASE_URL}')

app.run(
    host='0.0.0.0', 
    port=Config.PORT, 
    debug=Config.DEBUG,
    threaded=True
)
"