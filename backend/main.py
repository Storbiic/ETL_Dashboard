"""FastAPI main application for ETL Dashboard."""

from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.api import routes_upload, routes_preview, routes_profile, routes_transform
from backend.core.config import settings
from backend.core.logging import logger
from backend.models.schemas import HealthResponse, ErrorResponse


# Create FastAPI application
app = FastAPI(
    title="ETL Dashboard API",
    description="FastAPI backend for Excel ETL processing with Power BI outputs",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors."""
    logger.error("Unhandled exception", error=str(exc), path=str(request.url))
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal server error",
            detail=str(exc) if settings.fastapi_reload else "An unexpected error occurred"
        ).dict()
    )


@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint with basic health check."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now()
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Detailed health check endpoint."""
    # Check if required directories exist
    upload_dir = Path(settings.upload_folder)
    processed_dir = Path(settings.processed_folder)
    
    if not upload_dir.exists():
        raise HTTPException(
            status_code=503,
            detail=f"Upload directory not found: {upload_dir}"
        )
    
    if not processed_dir.exists():
        raise HTTPException(
            status_code=503,
            detail=f"Processed directory not found: {processed_dir}"
        )
    
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now()
    )


# Include API routers
app.include_router(
    routes_upload.router,
    prefix="/api",
    tags=["upload"]
)

app.include_router(
    routes_preview.router,
    prefix="/api",
    tags=["preview"]
)

app.include_router(
    routes_profile.router,
    prefix="/api",
    tags=["profile"]
)

app.include_router(
    routes_transform.router,
    prefix="/api",
    tags=["transform"]
)


@app.on_event("startup")
async def startup_event():
    """Application startup event."""
    logger.info("Starting ETL Dashboard API", version="1.0.0")
    
    # Ensure required directories exist
    settings.upload_folder_path.mkdir(parents=True, exist_ok=True)
    settings.processed_folder_path.mkdir(parents=True, exist_ok=True)
    
    logger.info("ETL Dashboard API started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event."""
    logger.info("Shutting down ETL Dashboard API")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "backend.main:app",
        host=settings.fastapi_host,
        port=settings.fastapi_port,
        reload=settings.fastapi_reload,
        log_level=settings.log_level.lower()
    )
