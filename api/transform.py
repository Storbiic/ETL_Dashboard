"""Data transformation endpoint for Vercel deployment."""
from http.server import BaseHTTPRequestHandler
import json
import os
import sys
from pathlib import Path

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
        """Handle data transformation requests."""
        try:
            # Set up CORS
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            
            # Read request data
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            request_data = json.loads(post_data.decode('utf-8'))
            
            file_id = request_data.get('file_id')
            transform_options = request_data.get('options', {})
            
            if not file_id:
                response = {"error": "file_id is required"}
                self.wfile.write(json.dumps(response).encode())
                return
            
            # Create processing directories
            processed_dir = Path('/tmp/processed')
            processed_dir.mkdir(parents=True, exist_ok=True)
            
            # Import backend services
            try:
                from services.pipeline_service import PipelineService
                from services.excel_reader import ExcelReader
            except ImportError as e:
                response = {"error": f"Failed to import backend services: {str(e)}"}
                self.wfile.write(json.dumps(response).encode())
                return
            
            # Find the uploaded file
            upload_dir = Path('/tmp/uploads')
            file_patterns = [f"{file_id}.xlsx", f"{file_id}.xls"]
            file_path = None
            
            for pattern in file_patterns:
                potential_path = upload_dir / pattern
                if potential_path.exists():
                    file_path = potential_path
                    break
            
            if not file_path:
                response = {"error": "File not found"}
                self.wfile.write(json.dumps(response).encode())
                return
            
            # Initialize pipeline service
            pipeline = PipelineService(
                upload_folder='/tmp/uploads',
                processed_folder='/tmp/processed'
            )
            
            # Process the file
            result = pipeline.process_file(
                file_path=str(file_path),
                options=transform_options
            )
            
            # Return the transformation results
            response = {
                "file_id": file_id,
                "status": "success",
                "result": result,
                "processed_files": result.get('files_created', []),
                "message": "Transformation completed successfully"
            }
            
            self.wfile.write(json.dumps(response, default=str).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            response = {"error": f"Transformation failed: {str(e)}"}
            self.wfile.write(json.dumps(response).encode())
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()