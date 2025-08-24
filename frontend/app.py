"""Flask frontend application for ETL Dashboard."""

import os
from pathlib import Path

from flask import Flask, render_template, request, jsonify, send_file
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key')

# Configuration
FASTAPI_BASE_URL = f"http://{os.getenv('FASTAPI_HOST', '127.0.0.1')}:{os.getenv('FASTAPI_PORT', '8000')}"
PROCESSED_FOLDER = Path(os.getenv('PROCESSED_FOLDER', '../data/processed'))


@app.route('/')
def index():
    """Main dashboard page with stepper interface."""
    return render_template('index.html', 
                         fastapi_url=FASTAPI_BASE_URL,
                         page_title="ETL Dashboard")


@app.route('/preview')
def preview():
    """Preview page for sheet data."""
    file_id = request.args.get('file_id')
    sheet = request.args.get('sheet')
    
    if not file_id or not sheet:
        return render_template('index.html', 
                             error="Missing file_id or sheet parameter")
    
    return render_template('preview.html',
                         file_id=file_id,
                         sheet=sheet,
                         fastapi_url=FASTAPI_BASE_URL,
                         page_title="Sheet Preview")


@app.route('/profile')
def profile():
    """Profile page for data quality analysis."""
    file_id = request.args.get('file_id')
    master_sheet = request.args.get('master_sheet')
    status_sheet = request.args.get('status_sheet')
    
    if not all([file_id, master_sheet, status_sheet]):
        return render_template('index.html', 
                             error="Missing required parameters")
    
    return render_template('profile.html',
                         file_id=file_id,
                         master_sheet=master_sheet,
                         status_sheet=status_sheet,
                         fastapi_url=FASTAPI_BASE_URL,
                         page_title="Data Profile")


@app.route('/results')
def results():
    """Results page showing ETL outputs."""
    file_id = request.args.get('file_id')
    
    if not file_id:
        return render_template('index.html', 
                             error="Missing file_id parameter")
    
    return render_template('results.html',
                         file_id=file_id,
                         fastapi_url=FASTAPI_BASE_URL,
                         page_title="ETL Results")


@app.route('/download/<filename>')
def download_file(filename):
    """Download processed files."""
    try:
        file_path = PROCESSED_FOLDER / filename
        
        if not file_path.exists():
            return jsonify({"error": "File not found"}), 404
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "frontend": "Flask",
        "fastapi_url": FASTAPI_BASE_URL
    })


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return render_template('index.html', 
                         error="Page not found"), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return render_template('index.html', 
                         error="Internal server error"), 500


# Template filters
@app.template_filter('filesize')
def filesize_filter(size_bytes):
    """Format file size in human readable format."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


@app.template_filter('percentage')
def percentage_filter(value):
    """Format decimal as percentage."""
    try:
        return f"{float(value) * 100:.1f}%"
    except (ValueError, TypeError):
        return "N/A"


@app.route('/api/health')
def api_health():
    """Proxy health check to FastAPI backend."""
    try:
        response = requests.get(f"{FASTAPI_BASE_URL}/api/health")
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/upload', methods=['POST'])
def api_upload():
    """Proxy file upload to FastAPI backend."""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        # Forward the file to FastAPI backend
        files = {'file': (file.filename, file.stream, file.content_type)}
        response = requests.post(f"{FASTAPI_BASE_URL}/api/upload", files=files)

        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/transform', methods=['POST'])
def api_transform():
    """Proxy ETL transform to FastAPI backend with debugging."""
    try:
        # Get JSON data from request
        transform_data = request.get_json()

        print(f"🔧 Transform request received:")
        print(f"   File ID: {transform_data.get('file_id', 'N/A')}")
        print(f"   Master Sheet: {transform_data.get('master_sheet', 'N/A')}")
        print(f"   Status Sheet: {transform_data.get('status_sheet', 'N/A')}")
        print(f"   Options: {transform_data.get('options', {})}")

        # Forward the request to FastAPI backend
        response = requests.post(
            f"{FASTAPI_BASE_URL}/api/transform",
            json=transform_data,
            headers={'Content-Type': 'application/json'}
        )

        print(f"🔧 FastAPI response status: {response.status_code}")

        if response.status_code != 200:
            print(f"❌ Transform error: {response.text}")
        else:
            result = response.json()
            print(f"✅ Transform success: {result.get('success', False)}")
            if result.get('artifacts'):
                print(f"   Artifacts created: {len(result['artifacts'])}")

        return jsonify(response.json()), response.status_code

    except Exception as e:
        print(f"❌ Transform proxy error: {str(e)}")
        return jsonify({'error': str(e)}), 500



@app.route('/test')
def test_page():
    """Test page for debugging frontend-backend communication."""
    return render_template('test.html',
                         fastapi_url=FASTAPI_BASE_URL,
                         page_title="Frontend-Backend Test")


if __name__ == '__main__':
    # Development server
    host = os.getenv('FLASK_HOST', '127.0.0.1')
    port = int(os.getenv('FLASK_PORT', '5000'))
    debug = os.getenv('FLASK_DEBUG', 'true').lower() == 'true'
    
    app.run(host=host, port=port, debug=debug)
