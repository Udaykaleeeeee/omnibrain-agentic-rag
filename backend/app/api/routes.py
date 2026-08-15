import logging
import uuid
from pathlib import Path
from typing import Optional, List, Union, Dict, Any
import time
from fastapi import APIRouter, UploadFile, File, HTTPException, Form, BackgroundTasks
from pydantic import BaseModel, Field

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
    delete_document,
    get_images,
    get_image
)
from ..ingestion.image_storage import delete_document_images
from ..vector_db import RetrievalService, QdrantService
from ..agents.graph import graph
from ..agents.llm import get_llm

logger = logging.getLogger(__name__)

router = APIRouter()
retrieval_service = RetrievalService()
qdrant_service = QdrantService()
processing_status = {}

class IngestResponse(BaseModel):
    document_id: str
    filename: str
    source_format: str
    total_pages: int
    ocr_pages_used: int
    chunks_created: int
    images_extracted: Optional[int] = 0
    metadata: Optional[Dict[str, Any]] = None
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
    document_id: Optional[str] = Form(
    None,
    description="Optional. Leave empty to auto-generate a unique document ID."
),
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
            images_extracted=result.get("images_extracted", 0),
            metadata=result.get("metadata"),
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


@router.get("/documents/{document_id}/images")
def get_document_images(document_id: str):
    """Get all extracted images metadata for a specific document."""
    images = get_images(document_id)

    if images is None:
        raise HTTPException(
            status_code=404,
            detail=f"Document {document_id} not found"
        )

    return {
        "document_id": document_id,
        "total_images": len(images),
        "images": images
    }


@router.get("/documents/{document_id}/images/{image_index}")
def get_specific_image(document_id: str, image_index: int):
    """Get specific image metadata by index."""
    image = get_image(document_id, image_index)

    if image is None:
        raise HTTPException(
            status_code=404,
            detail=f"Image {image_index} not found for document {document_id}"
        )

    return image


@router.delete("/documents/{document_id}")
def delete_document_endpoint(document_id: str):
    """Delete a document and all its chunks and images."""
    success = delete_document(document_id)
    qdrant_service.delete_document(document_id)

    deleted_images = delete_document_images(document_id)

    if not success:
        raise HTTPException(
            status_code=404,
            detail=f"Document {document_id} not found"
        )

    return {
        "message": f"Document {document_id} deleted successfully",
        "images_deleted": deleted_images
    }


@router.get("/stats")
def get_storage_stats():
    """Get storage statistics."""
    stats = get_stats()
    stats["vector_count"] = qdrant_service.count_vectors()
    return stats

class ProcessingResponse(BaseModel):
    document_id: str
    status: str
    progress: int
    current_step: str


def process_document(document_id: str):

    processing_status[document_id] = {
        "status": "processing",
        "progress": 10,
        "current_step": "Initializing"
    }

    time.sleep(2)

    processing_status[document_id] = {
        "status": "processing",
        "progress": 40,
        "current_step": "Extracting text"
    }

    time.sleep(2)

    processing_status[document_id] = {
        "status": "processing",
        "progress": 70,
        "current_step": "Generating embeddings"
    }

    time.sleep(2)

    processing_status[document_id] = {
        "status": "completed",
        "progress": 100,
        "current_step": "Completed"
    }

class SearchRequest(BaseModel):
    query: str
    top_k: Optional[int] = 5
    score_threshold: Optional[float] = None
    document_id: Optional[Union[str, List[str]]] = None
    filename: Optional[str] = None
    source_format: Optional[str] = None
    page_number: Optional[Union[int, List[int]]] = None
    is_ocr: Optional[bool] = None
    enable_hybrid: Optional[bool] = True


@router.post("/search")
async def search_documents(request: SearchRequest):
    """
    Semantic search & retrieval endpoint.
    Returns top-k chunks, payload metadata, similarity scores, and formatted citations.
    """
    try:
        results = retrieval_service.retrieve(
            query=request.query,
            top_k=request.top_k,
            score_threshold=request.score_threshold,
            document_id=request.document_id,
            filename=request.filename,
            source_format=request.source_format,
            page_number=request.page_number,
            is_ocr=request.is_ocr,
            enable_hybrid=request.enable_hybrid,
        )
        return results
    except Exception as e:
        logger.error(f"Search failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.post("/processing/{document_id}", response_model=ProcessingResponse)
async def start_processing(
    document_id: str,
    background_tasks: BackgroundTasks
):
    document = get_document(document_id)

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    background_tasks.add_task(process_document, document_id)

    return ProcessingResponse(
        document_id=document_id,
        status="processing",
        progress=0,
        current_step="Starting"
    )


@router.get("/processing/{document_id}", response_model=ProcessingResponse)
async def get_processing_status(document_id: str):

    if document_id not in processing_status:
        raise HTTPException(
            status_code=404,
            detail="Processing status not found"
        )

    status = processing_status[document_id]

    return ProcessingResponse(
        document_id=document_id,
        status=status["status"],
        progress=status["progress"],
        current_step=status["current_step"]
    )


class QueryRequest(BaseModel):
    question: str = Field(..., description="Question to ask")
    document_id: Optional[str] = Field(None, description="Specific document to search in")
    top_k: Optional[int] = Field(5, description="Number of top matching chunks to retrieve")


class QueryResponse(BaseModel):
    question: str = Field(..., description="The original question")
    answer: str = Field(..., description="AI generated answer")
    sources: list = Field(default=[], description="List of source documents used")
    rag_context: Optional[str] = Field(None, description="Retrieved context used for the answer")


@router.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """Ask a question through the LangGraph workflow."""

    if not request.question or not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    try:
        state = {
            "query": request.question,
            "response": None,
            "documents": [],
            "images": [],
            "document_id": request.document_id,
            "top_k": request.top_k or 5,
            "citations": [],
            "next_agent": None,
        }

        result = graph.invoke(state)

        return QueryResponse(
            question=request.question,
            answer=result.get("response") or "No answer generated.",
            sources=result.get("citations", []),
            rag_context=None,
        )

    except Exception as e:
        logger.error(f"Query endpoint failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Query endpoint failed: {str(e)}",
        )


class MemoRequest(BaseModel):
    document_id: str = Field(..., description="ID of the document to generate memo for")
    focus_area: Optional[str] = Field(None, description="Specific area to focus on in the memo")


class MemoResponse(BaseModel):
    document_id: str = Field(..., description="ID of the document")
    memo: str = Field(..., description="Generated memo content")
    status: str = Field(..., description="Status of memo generation")


@router.post("/generate-memo", response_model=MemoResponse)
async def generate_memo(request: MemoRequest):
    if not request.document_id or request.document_id.strip() == "":
        raise HTTPException(status_code=400, detail="Document ID cannot be empty")

    try:
        retrieval_result = retrieval_service.retrieve(
            query=request.focus_area or "Provide a comprehensive summary of the document.",
            top_k=10,
            document_id=request.document_id,
            enable_hybrid=False,
        )

        chunks = retrieval_result.get("chunks", [])

        if not chunks:
            raise HTTPException(
                    status_code=404,
                    detail=f"No chunks found for document {request.document_id}"
                )

        context = "\n\n".join(
                chunk.get("text", "")
                for chunk in chunks
                if chunk.get("text")
            )

        focus = request.focus_area or "Provide a comprehensive summary of the document."

        prompt = f"""
Generate a concise but useful memo based only on the document context below.

Focus:
{focus}

Document Context:
{context}
"""

        model = get_llm()
        response = model.generate_content(prompt)

        return MemoResponse(
            document_id=request.document_id,
            memo=response.text,
            status="completed"
        )

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Memo generation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Memo generation failed: {str(e)}"
        )