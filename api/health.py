"""Health check endpoint for Vercel deployment."""
from http.server import BaseHTTPRequestHandler
import json
import os

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        """Handle OPTIONS preflight request."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        return

    def do_GET(self):
        """Health check endpoint."""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {
            "status": "healthy",
            "service": "etl-dashboard",
            "platform": "vercel",
            "python_path": os.environ.get("PYTHONPATH", "not_set"),
            "upload_folder": os.environ.get("UPLOAD_FOLDER", "not_set")
        }
        
        self.wfile.write(json.dumps(response).encode())
        return