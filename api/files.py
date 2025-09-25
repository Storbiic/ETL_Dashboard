"""File download and management endpoint for Vercel deployment."""
from http.server import BaseHTTPRequestHandler
import json
import os
import sys
from pathlib import Path
import mimetypes
import urllib.parse

# Add backend to path
sys.path.insert(0, '/var/task/backend')

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        """Handle OPTIONS preflight request."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        return

    def do_GET(self):
        """Handle file download requests."""
        try:
            # Parse the request path
            path_parts = self.path.split('/')
            if len(path_parts) < 3:
                self.send_error(404, "File not found")
                return
            
            # Extract filename from path (e.g., /api/files/filename.csv)
            filename = urllib.parse.unquote(path_parts[-1])
            
            # Look for file in processed directory
            processed_dir = Path('/tmp/processed')
            file_path = processed_dir / filename
            
            if not file_path.exists():
                # Also check uploads directory
                upload_dir = Path('/tmp/uploads')
                file_path = upload_dir / filename
                
                if not file_path.exists():
                    self.send_error(404, f"File {filename} not found")
                    return
            
            # Get MIME type
            mime_type, _ = mimetypes.guess_type(str(file_path))
            if not mime_type:
                mime_type = 'application/octet-stream'
            
            # Send file
            self.send_response(200)
            self.send_header('Content-Type', mime_type)
            self.send_header('Content-Disposition', f'attachment; filename="{filename}"')
            self.send_header('Content-Length', str(file_path.stat().st_size))
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            # Read and send file in chunks
            with open(file_path, 'rb') as f:
                while True:
                    chunk = f.read(8192)  # 8KB chunks
                    if not chunk:
                        break
                    self.wfile.write(chunk)
                    
        except Exception as e:
            self.send_error(500, f"File download failed: {str(e)}")
    
    def do_POST(self):
        """List available files."""
        try:
            # Set up CORS
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            
            # List files in processed directory
            processed_dir = Path('/tmp/processed')
            upload_dir = Path('/tmp/uploads')
            
            files_info = {
                "processed_files": [],
                "uploaded_files": []
            }
            
            # Get processed files
            if processed_dir.exists():
                for file_path in processed_dir.iterdir():
                    if file_path.is_file():
                        files_info["processed_files"].append({
                            "name": file_path.name,
                            "size": file_path.stat().st_size,
                            "modified": file_path.stat().st_mtime,
                            "download_url": f"/api/files/{file_path.name}"
                        })
            
            # Get uploaded files
            if upload_dir.exists():
                for file_path in upload_dir.iterdir():
                    if file_path.is_file():
                        files_info["uploaded_files"].append({
                            "name": file_path.name,
                            "size": file_path.stat().st_size,
                            "modified": file_path.stat().st_mtime,
                            "download_url": f"/api/files/{file_path.name}"
                        })
            
            self.wfile.write(json.dumps(files_info, default=str).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            response = {"error": f"File listing failed: {str(e)}"}
            self.wfile.write(json.dumps(response).encode())
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()