<<<<<<< HEAD
import logging
import uuid
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from ..ingestion import ingest_document, is_supported_format, get_supported_extensions

logger = logging.getLogger(__name__)
=======
from fastapi import APIRouter, UploadFile, File
import os
import shutil

print("=================================")
print("ROUTES.PY LOADED")
print(__file__)
print("=================================")
>>>>>>> 26cbca42c9a13492e185627e84f30848cb191f6a

router = APIRouter()


<<<<<<< HEAD
# Response models
class IngestResponse(BaseModel):
    document_id: str
    filename: str
    source_format: str
    total_pages: int
    ocr_pages_used: int
    chunks_created: int
    status: str
    message: Optional[str] = None


@router.get("/test")
def test():
    return {
        "message": "API Routes Working!"
    }


@router.get("/ingest/formats")
def get_supported_formats():
    """Get list of supported document formats."""
    return {
        "supported_extensions": get_supported_extensions(),
        "description": "Supported file formats for document ingestion"
    }


@router.post("/ingest", response_model=IngestResponse)
async def ingest_document_endpoint(
    file: UploadFile = File(...),
    document_id: Optional[str] = Form(None),
    ocr_fallback: bool = Form(True),
    ocr_images: bool = Form(True),
    remove_headers_footers: bool = Form(True),
    skip_empty_pages: bool = Form(True)
):
    """Upload and ingest a document (PDF, DOCX, or TXT)."""
    # Generate document ID if not provided
    if not document_id:
        document_id = str(uuid.uuid4())
    
    # Validate file format
    if not is_supported_format(file.filename, file.content_type):
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Unsupported file format",
                "filename": file.filename,
                "content_type": file.content_type,
                "supported_formats": get_supported_extensions()
            }
        )
    
    # Create temporary directory for uploads
    upload_dir = Path("temp_uploads")
    upload_dir.mkdir(exist_ok=True)
    
    # Save uploaded file temporarily
    temp_file_path = upload_dir / f"{document_id}_{file.filename}"
    
    try:
        # Save file
        with open(temp_file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        logger.info(f"Processing document: {file.filename} ({document_id})")
        
        # Ingest document
        result = ingest_document(
            file_path=str(temp_file_path),
            filename=file.filename,
            document_id=document_id,
            mime_type=file.content_type,
            ocr_fallback=ocr_fallback,
            ocr_images=ocr_images,
            remove_headers_footers=remove_headers_footers,
            skip_empty_pages=skip_empty_pages
        )
        
        logger.info(
            f"Successfully ingested {file.filename}: "
            f"{result['total_pages']} pages, {result['ocr_pages_used']} OCR pages"
        )
        
        # Build response
        return IngestResponse(
            document_id=result["document_id"],
            filename=result["filename"],
            source_format=result["source_format"],
            total_pages=result["total_pages"],
            ocr_pages_used=result["ocr_pages_used"],
            chunks_created=result["chunks_created"],
            status=result["status"],
            message=f"Successfully ingested {file.filename}"
        )
    
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    
    except Exception as e:
        logger.error(f"Ingestion failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Document ingestion failed: {str(e)}"
        )
    
    finally:
        # Cleanup temporary file
        try:
            if temp_file_path.exists():
                temp_file_path.unlink()
        except Exception as e:
            logger.warning(f"Failed to cleanup temp file: {e}")
=======
@router.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload a PDF file and save it inside backend/uploads
    """

    # Check whether the uploaded file is PDF
    if not file.filename.lower().endswith(".pdf"):
        return {
            "success": False,
            "message": "Only PDF files are allowed."
        }

    upload_folder = "backend/uploads"

    # Create uploads folder if it doesn't exist
    os.makedirs(upload_folder, exist_ok=True)

    file_path = os.path.join(upload_folder, file.filename)

    # Save the file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "success": True,
        "message": "PDF uploaded successfully.",
        "filename": file.filename
    }
>>>>>>> 26cbca42c9a13492e185627e84f30848cb191f6a
