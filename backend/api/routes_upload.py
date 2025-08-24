"""Upload API routes for file handling."""

import uuid
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from backend.core.config import settings
from backend.core.logging import logger
from backend.models.schemas import UploadResponse, ErrorResponse
from backend.services.excel_reader import ExcelReader

router = APIRouter()


@router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """
    Upload an Excel workbook and return file info with sheet names.
    
    Args:
        file: Uploaded Excel file
        
    Returns:
        UploadResponse with file_id, filename, sheet_names, etc.
    """
    try:
        # Validate file type
        if not file.filename.lower().endswith(('.xlsx', '.xls')):
            raise HTTPException(
                status_code=400,
                detail="Only Excel files (.xlsx, .xls) are supported"
            )
        
        # Check file size
        file_content = await file.read()
        file_size = len(file_content)
        
        if file_size > settings.max_upload_bytes:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size: {settings.max_upload_size}"
            )
        
        if file_size == 0:
            raise HTTPException(
                status_code=400,
                detail="Empty file uploaded"
            )
        
        # Generate unique file ID
        file_id = str(uuid.uuid4())
        
        # Save file to uploads directory
        upload_path = settings.upload_folder_path / f"{file_id}.xlsx"
        
        with open(upload_path, "wb") as f:
            f.write(file_content)
        
        logger.info("File uploaded successfully", 
                   file_id=file_id,
                   filename=file.filename,
                   size_bytes=file_size)
        
        # Read sheet names using ExcelReader
        try:
            excel_reader = ExcelReader(upload_path)
            sheet_names = excel_reader.get_sheet_names()
            excel_reader.close()
            
        except Exception as e:
            # Clean up uploaded file if Excel reading fails
            if upload_path.exists():
                upload_path.unlink()
            
            logger.error("Failed to read Excel file", 
                        file_id=file_id, error=str(e))
            
            raise HTTPException(
                status_code=400,
                detail=f"Invalid Excel file: {str(e)}"
            )
        
        # Validate minimum requirements
        if len(sheet_names) < 2:
            # Clean up uploaded file
            if upload_path.exists():
                upload_path.unlink()
            
            raise HTTPException(
                status_code=400,
                detail="Excel file must contain at least 2 sheets"
            )
        
        logger.info("Excel file processed successfully",
                   file_id=file_id,
                   sheet_count=len(sheet_names),
                   sheets=sheet_names)
        
        return UploadResponse(
            file_id=file_id,
            filename=file.filename,
            sheet_names=sheet_names,
            file_size=file_size,
            upload_time=datetime.now()
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
        
    except Exception as e:
        logger.error("Unexpected error during file upload", error=str(e))
        
        raise HTTPException(
            status_code=500,
            detail="Internal server error during file upload"
        )


@router.delete("/upload/{file_id}")
async def delete_uploaded_file(file_id: str):
    """
    Delete an uploaded file.
    
    Args:
        file_id: ID of the file to delete
        
    Returns:
        Success message
    """
    try:
        # Validate file_id format
        try:
            uuid.UUID(file_id)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid file ID format"
            )
        
        # Find and delete file
        upload_path = settings.upload_folder_path / f"{file_id}.xlsx"
        
        if not upload_path.exists():
            raise HTTPException(
                status_code=404,
                detail="File not found"
            )
        
        upload_path.unlink()
        
        logger.info("File deleted successfully", file_id=file_id)
        
        return {"message": "File deleted successfully", "file_id": file_id}
        
    except HTTPException:
        raise
        
    except Exception as e:
        logger.error("Error deleting file", file_id=file_id, error=str(e))
        
        raise HTTPException(
            status_code=500,
            detail="Internal server error during file deletion"
        )


@router.get("/upload/{file_id}/info")
async def get_file_info(file_id: str):
    """
    Get information about an uploaded file.
    
    Args:
        file_id: ID of the uploaded file
        
    Returns:
        File information including sheet names
    """
    try:
        # Validate file_id format
        try:
            uuid.UUID(file_id)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid file ID format"
            )
        
        # Check if file exists
        upload_path = settings.upload_folder_path / f"{file_id}.xlsx"
        
        if not upload_path.exists():
            raise HTTPException(
                status_code=404,
                detail="File not found"
            )
        
        # Get file info
        file_stat = upload_path.stat()
        
        # Read sheet names
        excel_reader = ExcelReader(upload_path)
        sheet_names = excel_reader.get_sheet_names()
        excel_reader.close()
        
        return {
            "file_id": file_id,
            "file_size": file_stat.st_size,
            "upload_time": datetime.fromtimestamp(file_stat.st_ctime),
            "sheet_names": sheet_names,
            "sheet_count": len(sheet_names)
        }
        
    except HTTPException:
        raise
        
    except Exception as e:
        logger.error("Error getting file info", file_id=file_id, error=str(e))
        
        raise HTTPException(
            status_code=500,
            detail="Internal server error getting file info"
        )
