"""Data profiling endpoint for Vercel deployment."""
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
        """Handle data profiling requests."""
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
            sheet_name = request_data.get('sheet_name')
            
            if not file_id:
                response = {"error": "file_id is required"}
                self.wfile.write(json.dumps(response).encode())
                return
            
            # Import backend services
            try:
                from services.excel_reader import ExcelReader
                from services.profiler import DataProfiler
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
            
            # Read the file and generate profile
            reader = ExcelReader(str(file_path))
            
            if sheet_name:
                df = reader.read_sheet(sheet_name)
                profiler = DataProfiler()
                profile_result = profiler.generate_profile(df, sheet_name)
            else:
                # Profile all sheets
                sheets_info = reader.get_sheet_info()
                profile_result = {}
                profiler = DataProfiler()
                
                for sname in sheets_info.keys():
                    df = reader.read_sheet(sname)
                    profile_result[sname] = profiler.generate_profile(df, sname)
            
            response = {
                "file_id": file_id,
                "sheet_name": sheet_name,
                "profile": profile_result,
                "status": "success"
            }
            
            self.wfile.write(json.dumps(response, default=str).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            response = {"error": f"Profiling failed: {str(e)}"}
            self.wfile.write(json.dumps(response).encode())
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()