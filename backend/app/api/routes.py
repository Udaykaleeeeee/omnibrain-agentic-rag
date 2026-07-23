import logging
import uuid
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from pydantic import BaseModel

from ..ingestion import (
    ingest_document, 
    is_supported_format, 
    get_supported_extensions
)
from ..ingestion.storage import (
    get_all_documents,
    get_document,
    get_chunks,
    get_chunk,
    get_stats,
    delete_document
)

logger = logging.getLogger(__name__)

router = APIRouter()


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
    if not document_id:
        document_id = str(uuid.uuid4())
    
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
    
    upload_dir = Path("temp_uploads")
    upload_dir.mkdir(exist_ok=True)
    
    temp_file_path = upload_dir / f"{document_id}_{file.filename}"
    
    try:
        with open(temp_file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        logger.info(f"Processing document: {file.filename} ({document_id})")
        
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
        try:
            if temp_file_path.exists():
                temp_file_path.unlink()
        except Exception as e:
            logger.warning(f"Failed to cleanup temp file: {e}")



@router.get("/documents")
def list_documents():
    """Get list of all ingested documents."""
    documents = get_all_documents()
    return {
        "total": len(documents),
        "documents": documents
    }


@router.get("/documents/{document_id}")
def get_document_details(document_id: str):
    """Get details for a specific document."""
    document = get_document(document_id)
    
    if not document:
        raise HTTPException(
            status_code=404,
            detail=f"Document {document_id} not found"
        )
    
    return document


@router.get("/documents/{document_id}/chunks")
def get_document_chunks(document_id: str):
    """Get all chunks for a specific document."""
    chunks = get_chunks(document_id)
    
    if chunks is None:
        raise HTTPException(
            status_code=404,
            detail=f"Document {document_id} not found"
        )
    
    return {
        "document_id": document_id,
        "total_chunks": len(chunks),
        "chunks": chunks
    }


@router.get("/documents/{document_id}/chunks/{chunk_index}")
def get_specific_chunk(document_id: str, chunk_index: int):
    """Get a specific chunk by index."""
    chunk = get_chunk(document_id, chunk_index)
    
    if chunk is None:
        raise HTTPException(
            status_code=404,
            detail=f"Chunk {chunk_index} not found for document {document_id}"
        )
    
    return chunk


@router.delete("/documents/{document_id}")
def delete_document_endpoint(document_id: str):
    """Delete a document and all its chunks."""
    success = delete_document(document_id)
    
    if not success:
        raise HTTPException(
            status_code=404,
            detail=f"Document {document_id} not found"
        )
    
    return {
        "message": f"Document {document_id} deleted successfully"
    }


@router.get("/stats")
def get_storage_stats():
    """Get storage statistics."""
    return get_stats()
