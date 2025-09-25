"""File upload endpoint for Vercel deployment."""
from http.server import BaseHTTPRequestHandler
import json
import os
import sys
import tempfile
import uuid
from pathlib import Path
import cgi
import io

# Add backend to path
sys.path.insert(0, '/var/task/backend')

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        """Handle OPTIONS preflight request."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        return

    def do_POST(self):
        """Handle file upload."""
        try:
            # Set up CORS
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            
            # Parse multipart form data
            content_type = self.headers.get('Content-Type', '')
            if not content_type.startswith('multipart/form-data'):
                response = {"error": "Content-Type must be multipart/form-data"}
                self.wfile.write(json.dumps(response).encode())
                return
            
            # Get content length
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                response = {"error": "No file data received"}
                self.wfile.write(json.dumps(response).encode())
                return
            
            # Read the posted data
            post_data = self.rfile.read(content_length)
            
            # Parse the form data
            fp = io.BytesIO(post_data)
            form = cgi.FieldStorage(
                fp=fp,
                headers=self.headers,
                environ={'REQUEST_METHOD': 'POST'}
            )
            
            # Get the uploaded file
            file_field = form['file']
            if not file_field.filename:
                response = {"error": "No file selected"}
                self.wfile.write(json.dumps(response).encode())
                return
            
            # Validate file type
            allowed_extensions = ['xlsx', 'xls']
            file_ext = file_field.filename.split('.')[-1].lower()
            if file_ext not in allowed_extensions:
                response = {"error": f"File type {file_ext} not allowed. Use: {', '.join(allowed_extensions)}"}
                self.wfile.write(json.dumps(response).encode())
                return
            
            # Create upload directory
            upload_dir = Path('/tmp/uploads')
            upload_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate unique filename
            file_id = str(uuid.uuid4())
            filename = f"{file_id}.{file_ext}"
            file_path = upload_dir / filename
            
            # Save the file
            with open(file_path, 'wb') as f:
                f.write(file_field.file.read())
            
            response = {
                "message": "File uploaded successfully",
                "filename": file_field.filename,
                "file_id": file_id,
                "file_path": str(file_path),
                "file_size": file_path.stat().st_size
            }
            
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            response = {"error": f"Upload failed: {str(e)}"}
            self.wfile.write(json.dumps(response).encode())
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()