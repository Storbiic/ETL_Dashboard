#!/usr/bin/env python3
"""Simplified development server runner for ETL Dashboard."""

import os
import sys
import subprocess
import time
from pathlib import Path

def check_packages():
    """Check if essential packages are available."""
    try:
        import fastapi
        import flask
        import pandas
        import numpy
        import openpyxl
        print("✅ All essential packages are available!")
        return True
    except ImportError as e:
        print(f"❌ Missing package: {e}")
        return False

def run_backend():
    """Run the FastAPI backend server."""
    print("🚀 Starting FastAPI backend...")
    
    cmd = [
        sys.executable, '-m', 'uvicorn',
        'backend.main:app',
        '--reload',
        '--host', '127.0.0.1',
        '--port', '8000'
    ]
    
    return subprocess.Popen(cmd)

def run_frontend():
    """Run the Flask frontend server."""
    print("🌐 Starting Flask frontend...")
    
    env = os.environ.copy()
    env['FLASK_APP'] = 'frontend.app'
    env['FLASK_DEBUG'] = 'true'
    
    cmd = [
        sys.executable, '-m', 'flask', 'run',
        '--host', '127.0.0.1',
        '--port', '5000'
    ]
    
    return subprocess.Popen(cmd, env=env)

def main():
    """Main function to run both servers."""
    print("🔧 ETL Dashboard - Simple Start")
    print("=" * 35)
    
    # Check packages
    if not check_packages():
        print("\n❌ Some packages are missing. Please install them first:")
        print("pip install fastapi uvicorn flask pandas numpy openpyxl python-dotenv")
        return
    
    # Ensure data directories exist
    Path('data/uploads').mkdir(parents=True, exist_ok=True)
    Path('data/processed').mkdir(parents=True, exist_ok=True)
    
    # Start backend only first
    print("\n🚀 Starting backend server...")
    backend_process = run_backend()
    
    print("\n✅ Backend started!")
    print("🔌 Backend API: http://127.0.0.1:8000")
    print("📚 API Docs: http://127.0.0.1:8000/docs")
    print("\n🛑 Press Ctrl+C to stop")
    
    try:
        backend_process.wait()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        backend_process.terminate()
        backend_process.wait()
        print("✅ Server stopped")

if __name__ == '__main__':
    main()
