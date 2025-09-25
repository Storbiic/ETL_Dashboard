# 🔧 Local Development Setup Guide

## Quick Start (2 Commands)

### Option 1: Automatic Setup
```bash
python run_local_dev.py
```
This will:
- Install dependencies automatically
- Start backend on http://localhost:8000
- Start frontend on http://localhost:8080
- Auto-open browser to http://localhost:8080/index-local.html

### Option 2: Manual Setup (if automatic fails)

#### Terminal 1 - Backend
```bash
# Install dependencies
pip install -r requirements-local.txt

# Start FastAPI backend
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

#### Terminal 2 - Frontend
```bash
# Start simple HTTP server
python -m http.server 8080

# Then open: http://localhost:8080/index-local.html
```

## 🎯 Local Development URLs

- **Frontend (Modern UI)**: http://localhost:8080/index-local.html
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🎨 UI Consistency

The local development now uses the **exact same UI** as Vercel:
- ✅ Modern Tailwind CSS styling
- ✅ Interactive step indicators
- ✅ File upload interface
- ✅ Progress tracking
- ✅ Responsive design
- ✅ Same color scheme and layout

## 🔄 Key Differences

| Feature | Local Development | Vercel Production |
|---------|------------------|-------------------|
| **Backend URL** | http://localhost:8000 | https://your-app.vercel.app/api |
| **Frontend** | index-local.html | api/index.py |
| **Resources** | CDN (same as Vercel) | CDN |
| **Auto-reload** | ✅ Backend only | ❌ Deploy needed |
| **File storage** | Local ./data folders | /tmp (temporary) |

## 🚀 Development Workflow

1. **Start servers**: `python run_local_dev.py`
2. **Make changes**: Edit backend code - auto-reloads
3. **Test locally**: Upload files, test ETL process
4. **Deploy**: `vercel --prod` when ready

## 🎯 What's Now Consistent

✅ **Visual Design**: Identical UI/UX between local and Vercel  
✅ **User Experience**: Same workflow and interactions  
✅ **API Endpoints**: Same endpoint structure  
✅ **Functionality**: File upload, processing, download  
✅ **Responsive Layout**: Works on all screen sizes  

## 🔧 Troubleshooting

### Backend Issues
```bash
# Check if backend is running
curl http://localhost:8000/health

# View backend logs
# Check the terminal running uvicorn
```

### Frontend Issues
```bash
# Check if frontend server is running
curl http://localhost:8080/index-local.html

# Verify file exists
ls index-local.html
```

### Port Conflicts
```bash
# Check what's using port 8000
netstat -an | findstr :8000

# Check what's using port 8080
netstat -an | findstr :8080
```

## 📁 File Structure for Local Dev

```
ETL_Dashboard/
├── index-local.html          # Local development UI (matches Vercel)
├── run_local_dev.py         # Automatic dev server startup
├── requirements-local.txt    # Full dependencies for local dev
├── requirements.txt         # Minimal deps for Vercel
├── backend/                 # FastAPI backend code
├── frontend/               # Original Flask templates (optional)
├── api/                    # Vercel serverless functions
└── data/                  # Local file storage
    ├── uploads/           # Uploaded files
    ├── processed/         # Processed outputs
    └── pipeline_output/   # ETL results
```

Your local development environment now provides the **exact same experience** as the Vercel deployment! 🎉