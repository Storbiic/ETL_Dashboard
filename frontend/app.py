"""Flask frontend application for ETL Dashboard."""

import os
from pathlib import Path

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request, send_file

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-key")


# Configuration for different deployment environments
class Config:
    # For Docker, internal communication uses service name
    FASTAPI_BASE_URL = f"http://{os.getenv('FASTAPI_HOST', '127.0.0.1')}:{os.getenv('FASTAPI_PORT', '8000')}"
    # For browser, always use localhost (Docker port mapping)
    FASTAPI_BROWSER_URL = f"http://localhost:{os.getenv('FASTAPI_PORT', '8000')}"

    PORT = int(os.getenv("PORT", 5000))
    DEBUG = os.getenv("FLASK_DEBUG", "false").lower() == "true"


# Apply configuration
FASTAPI_BASE_URL = Config.FASTAPI_BASE_URL
FASTAPI_BROWSER_URL = Config.FASTAPI_BROWSER_URL

# Get the project root directory (parent of frontend directory)
PROJECT_ROOT = Path(__file__).parent.parent
PROCESSED_FOLDER = PROJECT_ROOT / os.getenv("PROCESSED_FOLDER", "data/processed")
PIPELINE_OUTPUT_FOLDER = PROJECT_ROOT / os.getenv(
    "PIPELINE_OUTPUT_FOLDER", "data/pipeline_output"
)


@app.route("/")
def index():
    """Main dashboard page with stepper interface."""
    return render_template(
        "index.html", fastapi_url=FASTAPI_BROWSER_URL, page_title="ETL Dashboard"
    )


@app.route("/preview")
def preview():
    """Preview page for sheet data."""
    file_id = request.args.get("file_id")
    sheet = request.args.get("sheet")

    if not file_id or not sheet:
        return render_template("index.html", error="Missing file_id or sheet parameter")

    return render_template(
        "preview.html",
        file_id=file_id,
        sheet=sheet,
        fastapi_url=FASTAPI_BROWSER_URL,
        page_title="Sheet Preview",
    )


@app.route("/profile")
def profile():
    """Profile page for data quality analysis."""
    file_id = request.args.get("file_id")
    master_sheet = request.args.get("master_sheet")
    status_sheet = request.args.get("status_sheet")

    if not all([file_id, master_sheet, status_sheet]):
        return render_template("index.html", error="Missing required parameters")

    return render_template(
        "profile.html",
        file_id=file_id,
        master_sheet=master_sheet,
        status_sheet=status_sheet,
        fastapi_url=FASTAPI_BROWSER_URL,
        page_title="Data Profile",
    )


@app.route("/results")
def results():
    """Results page showing ETL outputs."""
    file_id = request.args.get("file_id")

    if not file_id:
        return render_template("index.html", error="Missing file_id parameter")

    return render_template(
        "results.html",
        file_id=file_id,
        fastapi_url=FASTAPI_BROWSER_URL,
        page_title="ETL Results",
    )


@app.route("/logs")
def logs():
    """Logs page for monitoring system activity."""
    return render_template(
        "logs.html", fastapi_url=FASTAPI_BROWSER_URL, page_title="System Logs"
    )


@app.route("/api/logs/backend")
def get_backend_logs():
    """Get recent backend logs via API proxy."""
    try:
        response = requests.get(f"{FASTAPI_BASE_URL}/api/logs/recent", timeout=10)
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to fetch backend logs: {str(e)}"}), 500


@app.route("/api/progress/status")
def get_progress_status():
    """Get current ETL progress status via API proxy."""
    try:
        response = requests.get(f"{FASTAPI_BASE_URL}/api/progress/status", timeout=10)
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to fetch progress status: {str(e)}"}), 500


# Pipeline status endpoint removed - manual ETL only


@app.route("/api/powerbi/templates")
def get_powerbi_templates():
    """Get available PowerBI templates via API proxy."""
    try:
        response = requests.get(f"{FASTAPI_BASE_URL}/api/powerbi/templates", timeout=10)

        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return (
                jsonify(
                    {
                        "templates": [],
                        "count": 0,
                        "error": f"Backend returned status {response.status_code}",
                        "details": response.text,
                    }
                ),
                response.status_code,
            )

    except requests.exceptions.RequestException as e:
        return (
            jsonify(
                {
                    "templates": [],
                    "count": 0,
                    "error": f"Failed to fetch PowerBI templates: {str(e)}",
                }
            ),
            500,
        )
    except Exception as e:
        return (
            jsonify(
                {"templates": [], "count": 0, "error": f"Unexpected error: {str(e)}"}
            ),
            500,
        )


@app.route("/download/<filename>")
def download_file(filename):
    """Download processed files."""
    try:
        # Use processed folder only
        file_path = PROCESSED_FOLDER / filename

        if not file_path.exists():
            return jsonify({"error": f"File not found: {filename}"}), 404

        return send_file(file_path, as_attachment=True, download_name=filename)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/download/bulk/<file_id>")
def download_bulk_files(file_id):
    """Download all files for a specific processing session as a ZIP."""
    import tempfile
    import zipfile
    from datetime import datetime

    try:
        # Create a temporary ZIP file
        temp_dir = tempfile.mkdtemp()
        zip_filename = (
            f"etl_results_{file_id[:8]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        )
        zip_path = Path(temp_dir) / zip_filename

        # Find all files related to this processing session
        files_to_zip = []

        # Check processed folder only
        if PROCESSED_FOLDER.exists():
            for file_path in PROCESSED_FOLDER.iterdir():
                if file_path.is_file():
                    files_to_zip.append((file_path, file_path.name))

        if not files_to_zip:
            return jsonify({"error": "No files found to download"}), 404

        # Create ZIP file
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for file_path, archive_name in files_to_zip:
                zipf.write(file_path, archive_name)

        return send_file(
            zip_path,
            as_attachment=True,
            download_name=zip_filename,
            mimetype="application/zip",
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/download/powerbi/<file_id>")
def download_powerbi_package(file_id):
    """Download organized Power BI package with Parquet files and DAX measures."""
    import tempfile
    import zipfile
    from datetime import datetime

    try:
        # Import DAX generator with error handling
        try:
            from backend.services.dax_generator import DAXGenerator
        except ImportError as e:
            print(f"Warning: Could not import DAXGenerator: {e}")
            # Continue without DAX file
            DAXGenerator = None

        # Get Parquet files from processed folder
        parquet_files = []

        if PROCESSED_FOLDER.exists():
            print(f"Checking processed folder: {PROCESSED_FOLDER}")
            for file_path in PROCESSED_FOLDER.iterdir():
                if file_path.is_file() and file_path.suffix.lower() == ".parquet":
                    parquet_files.append(file_path)
                    print(f"Found parquet file: {file_path.name}")

        if not parquet_files:
            print(f"No parquet files found in {PROCESSED_FOLDER}")
            return (
                jsonify({"error": "No Parquet files found for Power BI package"}),
                404,
            )

        print(f"Found {len(parquet_files)} parquet files")

        # Create temporary ZIP file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp_file:
            with zipfile.ZipFile(tmp_file.name, "w", zipfile.ZIP_DEFLATED) as zipf:
                # Add Parquet files to DATA_BI folder
                for file_path in parquet_files:
                    zipf.write(file_path, f"DATA_BI/{file_path.name}")
                    print(f"Added to zip: DATA_BI/{file_path.name}")

                # Try to add DAX measures file if DAXGenerator is available
                if DAXGenerator:
                    try:
                        with tempfile.TemporaryDirectory() as temp_dir:
                            dax_generator = DAXGenerator()
                            dax_file_path = dax_generator.generate_dax_file(temp_dir)
                            zipf.write(
                                dax_file_path, "DATA_BI/ETL_Dashboard_Measures.dax"
                            )
                            print("Added DAX measures file to zip")
                    except Exception as dax_error:
                        print(f"Warning: Could not generate DAX file: {dax_error}")
                        # Continue without DAX file
                else:
                    print("Skipping DAX file generation (DAXGenerator not available)")

            # Generate download filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            download_filename = f"DATA_BI_{timestamp}.zip"

            print(f"Sending zip file: {download_filename}")
            return send_file(
                tmp_file.name,
                as_attachment=True,
                download_name=download_filename,
                mimetype="application/zip",
            )

    except Exception as e:
        print(f"Error in download_powerbi_package: {str(e)}")
        import traceback

        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/download/csv/<file_id>")
def download_csv_package(file_id):
    """Download organized CSV package."""
    import tempfile
    import zipfile
    from datetime import datetime

    try:
        # Get CSV files from processed folder
        csv_files = []

        if PROCESSED_FOLDER.exists():
            for file_path in PROCESSED_FOLDER.iterdir():
                if file_path.is_file() and file_path.suffix.lower() == ".csv":
                    csv_files.append(file_path)

        if not csv_files:
            return jsonify({"error": "No CSV files found for CSV package"}), 404

        # Create temporary ZIP file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp_file:
            with zipfile.ZipFile(tmp_file.name, "w", zipfile.ZIP_DEFLATED) as zipf:
                # Add CSV files to DATA_CSV folder
                for file_path in csv_files:
                    zipf.write(file_path, f"DATA_CSV/{file_path.name}")

            # Generate download filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            download_filename = f"DATA_CSV_{timestamp}.zip"

            return send_file(
                tmp_file.name,
                as_attachment=True,
                download_name=download_filename,
                mimetype="application/zip",
            )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/download/dax/<file_id>")
def download_dax_measures(file_id):
    """Download DAX measures file."""
    import tempfile
    from datetime import datetime

    from backend.services.dax_generator import DAXGenerator

    try:
        # Generate DAX measures file
        with tempfile.TemporaryDirectory() as temp_dir:
            dax_generator = DAXGenerator()
            dax_file_path = dax_generator.generate_dax_file(temp_dir)

            # Generate download filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            download_filename = f"ETL_Dashboard_Measures_{timestamp}.dax"

            return send_file(
                dax_file_path,
                as_attachment=True,
                download_name=download_filename,
                mimetype="text/plain",
            )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/open-folder/<folder_type>")
def open_local_folder(folder_type):
    """Open local folder in file explorer."""
    import platform
    import subprocess

    try:
        if folder_type == "pipeline":
            folder_path = PIPELINE_OUTPUT_FOLDER
        elif folder_type == "processed":
            folder_path = PROCESSED_FOLDER
        else:
            return jsonify({"error": "Invalid folder type"}), 400

        if not folder_path.exists():
            folder_path.mkdir(parents=True, exist_ok=True)

        # Open folder based on operating system
        system = platform.system()
        if system == "Windows":
            subprocess.run(["explorer", str(folder_path.absolute())], check=True)
        elif system == "Darwin":  # macOS
            subprocess.run(["open", str(folder_path.absolute())], check=True)
        elif system == "Linux":
            subprocess.run(["xdg-open", str(folder_path.absolute())], check=True)
        else:
            return jsonify({"error": f"Unsupported operating system: {system}"}), 400

        return jsonify(
            {
                "success": True,
                "message": f"Opened {folder_type} folder",
                "path": str(folder_path.absolute()),
            }
        )

    except subprocess.CalledProcessError as e:
        return jsonify({"error": f"Failed to open folder: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/files/list")
def list_available_files():
    """List all available files for download."""
    try:
        files = []

        # Pipeline output folder removed - using processed folder only

        # Check processed folder
        if PROCESSED_FOLDER.exists():
            for file_path in PROCESSED_FOLDER.iterdir():
                if file_path.is_file():
                    stat = file_path.stat()
                    files.append(
                        {
                            "name": file_path.name,
                            "path": f"processed/{file_path.name}",
                            "size_bytes": stat.st_size,
                            "size_human": format_file_size(stat.st_size),
                            "modified": stat.st_mtime,
                            "type": "processed",
                            "download_url": f"/download/{file_path.name}",
                        }
                    )

        # Sort by modification time (newest first)
        files.sort(key=lambda f: f["modified"], reverse=True)

        return jsonify(
            {
                "files": files,
                "count": len(files),
                "pipeline_folder": str(PIPELINE_OUTPUT_FOLDER.absolute()),
                "processed_folder": str(PROCESSED_FOLDER.absolute()),
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def format_file_size(size_bytes):
    """Format file size in human readable format."""
    if size_bytes == 0:
        return "0 B"

    size_names = ["B", "KB", "MB", "GB"]
    import math

    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_names[i]}"


@app.route("/health")
def health():
    """Health check endpoint."""
    return jsonify(
        {
            "status": "healthy",
            "frontend": "Flask",
            "fastapi_url": FASTAPI_BASE_URL,
            "pipeline_folder": str(PIPELINE_OUTPUT_FOLDER.absolute()),
            "processed_folder": str(PROCESSED_FOLDER.absolute()),
        }
    )


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return render_template("index.html", error="Page not found"), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return render_template("index.html", error="Internal server error"), 500


# Template filters
@app.template_filter("filesize")
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


@app.template_filter("percentage")
def percentage_filter(value):
    """Format decimal as percentage."""
    try:
        return f"{float(value) * 100:.1f}%"
    except (ValueError, TypeError):
        return "N/A"


@app.route("/api/health")
def api_health():
    """Proxy health check to FastAPI backend."""
    try:
        response = requests.get(f"{FASTAPI_BASE_URL}/api/health")
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/upload", methods=["POST"])
def api_upload():
    """Proxy file upload to FastAPI backend."""
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400

        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No file selected"}), 400

        # Read the file content to avoid stream issues
        file_content = file.read()
        file.seek(0)  # Reset stream position

        # Forward the file to FastAPI backend
        files = {"file": (file.filename, file_content, file.content_type)}
        response = requests.post(
            f"{FASTAPI_BASE_URL}/api/upload", files=files, timeout=30
        )

        if response.status_code == 200:
            return jsonify(response.json()), response.status_code
        else:
            return (
                jsonify({"error": f"Backend error: {response.text}"}),
                response.status_code,
            )

    except requests.exceptions.Timeout:
        return jsonify({"error": "Upload timeout - file may be too large"}), 408
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Network error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Upload failed: {str(e)}"}), 500


@app.route("/api/transform", methods=["POST"])
def api_transform():
    """Proxy ETL transform to FastAPI backend with debugging."""
    try:
        # Get JSON data from request
        transform_data = request.get_json()

        print("🔧 Transform request received:")
        print(f"   File ID: {transform_data.get('file_id', 'N/A')}")
        print(f"   Master Sheet: {transform_data.get('master_sheet', 'N/A')}")
        print(f"   Status Sheet: {transform_data.get('status_sheet', 'N/A')}")
        print(f"   Options: {transform_data.get('options', {})}")

        # Forward the request to FastAPI backend
        response = requests.post(
            f"{FASTAPI_BASE_URL}/api/transform",
            json=transform_data,
            headers={"Content-Type": "application/json"},
        )

        print(f"🔧 FastAPI response status: {response.status_code}")

        if response.status_code != 200:
            print(f"❌ Transform error: {response.text}")
        else:
            result = response.json()
            print(f"✅ Transform success: {result.get('success', False)}")
            if result.get("artifacts"):
                print(f"   Artifacts created: {len(result['artifacts'])}")

        return jsonify(response.json()), response.status_code

    except Exception as e:
        print(f"❌ Transform proxy error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/test")
def test_page():
    """Test page for debugging frontend-backend communication."""
    return render_template(
        "test.html", fastapi_url=FASTAPI_BASE_URL, page_title="Frontend-Backend Test"
    )


if __name__ == "__main__":
    # Development server
    host = os.getenv("FLASK_HOST", "127.0.0.1")
    port = int(os.getenv("FLASK_PORT", "5000"))
    debug = os.getenv("FLASK_DEBUG", "true").lower() == "true"

    app.run(host=host, port=port, debug=debug)
