"""File preview endpoint for Vercel deployment - Simplified version."""
from http.server import BaseHTTPRequestHandler
import json
from pathlib import Path

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

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
        """Handle file preview requests."""
        try:
            # Set up CORS
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            # Get request data
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                response = {"error": "No data received"}
                self.wfile.write(json.dumps(response).encode('utf-8'))
                return
            
            post_data = self.rfile.read(content_length)
            try:
                request_data = json.loads(post_data.decode('utf-8'))
            except json.JSONDecodeError:
                response = {"error": "Invalid JSON data"}
                self.wfile.write(json.dumps(response).encode('utf-8'))
                return
            
            file_id = request_data.get('file_id')
            sheet_name = request_data.get('sheet_name')
            
            if not file_id or not sheet_name:
                response = {"error": "file_id and sheet_name are required"}
                self.wfile.write(json.dumps(response).encode('utf-8'))
                return
            
            if not PANDAS_AVAILABLE:
                response = {"error": "Excel processing not available - pandas not installed"}
                self.wfile.write(json.dumps(response).encode('utf-8'))
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
                self.wfile.write(json.dumps(response).encode('utf-8'))
                return
            
            # Read the Excel sheet (first 10 rows for preview)
            try:
                df = pd.read_excel(file_path, sheet_name=sheet_name, nrows=10)
                
                # Convert to JSON-serializable format
                preview_data = []
                for _, row in df.iterrows():
                    row_data = {}
                    for col in df.columns:
                        value = row[col]
                        if pd.isna(value):
                            value = None
                        elif hasattr(value, 'isoformat'):  # datetime
                            value = value.isoformat()
                        else:
                            value = str(value)
                        row_data[str(col)] = value
                    preview_data.append(row_data)
                
                response = {
                    "message": "Sheet preview loaded successfully",
                    "sheet_name": sheet_name,
                    "columns": [str(col) for col in df.columns.tolist()],
                    "data": preview_data,
                    "total_columns": len(df.columns),
                    "preview_rows": len(preview_data)
                }
                
            except Exception as e:
                response = {"error": f"Failed to read sheet '{sheet_name}': {str(e)}"}
            
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {"error": f"Preview failed: {str(e)}"}
            self.wfile.write(json.dumps(response).encode('utf-8'))