# ETL Dashboard

A FastAPI + Flask application for auditable ETL processing of Excel workbooks, producing Power BI-ready outputs.

## Features

- **Upload & Preview**: Upload Excel workbooks and preview sheet contents
- **Data Profiling**: Analyze data quality, types, and statistics
- **ETL Processing**: Clean and transform MasterBOM and Status sheets
- **Multiple Outputs**: CSV, Parquet, and SQLite formats
- **Power BI Ready**: Includes connectors, measures, and data dictionary

## Quick Start

### Prerequisites

- Python 3.11+
- pip or conda

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd BI_ETL_DASH
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Create data directories:
```bash
mkdir -p data/uploads data/processed
```

### Running the Application

#### Option 1: Development Script (Recommended)
```bash
python run_dev.py
```
This starts both backend and frontend servers with auto-reload enabled.

#### Option 2: Two Separate Processes

Terminal 1 - FastAPI Backend:
```bash
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

Terminal 2 - Flask Frontend:
```bash
FLASK_APP=frontend.app flask run --host 127.0.0.1 --port 5000
```

#### Option 3: Docker Compose
```bash
docker-compose up --build
```

### Access the Application

- Frontend: http://localhost:5000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Usage

1. **Upload**: Select an Excel workbook (.xlsx)
2. **Select Sheets**: Choose exactly two sheets (MasterBOM and Status)
3. **Preview**: Review sample data from selected sheets
4. **Profile**: Analyze data quality and statistics
5. **Transform**: Run ETL process and download results

## Outputs

The ETL process generates:

- `masterbom_clean.csv/parquet` - Cleaned MasterBOM data
- `status_clean.csv/parquet` - Cleaned Status data
- `plant_item_status.csv/parquet` - Normalized long table
- `fact_parts.csv/parquet` - Part facts for analytics
- `dim_dates.csv/parquet` - Date dimension
- `etl.sqlite` - All tables in SQLite format

## Power BI Integration

See `powerbi/` directory for:
- Power Query M scripts
- DAX measures
- Data dictionary

## Testing

Run all tests:
```bash
pytest tests/ -v
```

Run specific test categories:
```bash
# Unit tests only
pytest tests/test_cleaning.py tests/test_profiler.py -v

# Integration tests
pytest tests/test_api_integration.py -v -m integration

# Skip slow tests
pytest tests/ -v -m "not slow"
```

## Development

Format and lint code:
```bash
black .
ruff check .
```

Run development server with auto-reload:
```bash
python run_dev.py
```

## Project Structure

```
etl-dashboard/
├── backend/           # FastAPI application
├── frontend/          # Flask application  
├── data/             # Upload and processed data
├── powerbi/          # Power BI integration files
├── tests/            # Test suite
└── requirements.txt  # Dependencies
```
