import logging
import uuid
from pathlib import Path
from typing import Optional, List, Union, Dict, Any

from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from pydantic import BaseModel
from ..agents.llm import get_llm

from ..ingestion import (
    ingest_document,
    is_supported_format,
    get_supported_extensions,
)

from ..ingestion.storage import (
    get_all_documents,
    get_document,
    get_chunks,
    get_chunk,
    get_stats,
    delete_document,
    get_images,
    get_image,
)

from ..ingestion.image_storage import delete_document_images

from ..vector_db import (
    RetrievalService,
    QdrantService,
    ImageRetrievalService,
)

from ..agents.graph import graph

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================================
# SERVICES
# ============================================================

retrieval_service = RetrievalService()

qdrant_service = QdrantService()

image_retrieval_service = ImageRetrievalService(
    vector_db=qdrant_service
)


# ============================================================
# INGEST RESPONSE
# ============================================================

class IngestResponse(BaseModel):
    document_id: str
    filename: str
    source_format: str
    total_pages: int
    ocr_pages_used: int
    chunks_created: int

    images_extracted: Optional[int] = 0
    embeddings_created: Optional[int] = 0
    image_embeddings_created: Optional[int] = 0

    metadata: Optional[Dict[str, Any]] = None

    status: str
    message: Optional[str] = None


# ============================================================
# BASIC TEST
# ============================================================

@router.get("/test")
def test():
    return {
        "message": "API Routes Working!"
    }


# ============================================================
# SUPPORTED FORMATS
# ============================================================

@router.get("/ingest/formats")
def get_supported_formats():
    """
    Get list of supported document formats.
    """

    return {
        "supported_extensions": get_supported_extensions(),
        "description": "Supported file formats for document ingestion",
    }


# ============================================================
# DOCUMENT INGESTION
# ============================================================

@router.post(
    "/ingest",
    response_model=IngestResponse
)
async def ingest_document_endpoint(
    file: UploadFile = File(...),

    document_id: Optional[str] = Form(None),

    ocr_fallback: bool = Form(True),

    ocr_images: bool = Form(True),

    remove_headers_footers: bool = Form(True),

    skip_empty_pages: bool = Form(True),
):
    """
    Upload and ingest a document.

    Supported:
    - PDF
    - DOCX
    - TXT
    """

    # --------------------------------------------------------
    # Generate document ID
    # --------------------------------------------------------

    if not document_id:
        document_id = str(uuid.uuid4())

    # --------------------------------------------------------
    # Validate file
    # --------------------------------------------------------

    if not is_supported_format(
        file.filename,
        file.content_type
    ):
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Unsupported file format",
                "filename": file.filename,
                "content_type": file.content_type,
                "supported_formats": get_supported_extensions(),
            },
        )

    # --------------------------------------------------------
    # Temporary upload directory
    # --------------------------------------------------------

    upload_dir = Path("temp_uploads")

    upload_dir.mkdir(
        exist_ok=True
    )

    temp_file_path = (
        upload_dir
        / f"{document_id}_{file.filename}"
    )

    try:

        # ----------------------------------------------------
        # Save uploaded file
        # ----------------------------------------------------

        with open(
            temp_file_path,
            "wb"
        ) as f:

            content = await file.read()

            f.write(content)

        logger.info(
            f"Processing document: "
            f"{file.filename} ({document_id})"
        )

        # ----------------------------------------------------
        # Run ingestion pipeline
        # ----------------------------------------------------

        result = ingest_document(
            file_path=str(temp_file_path),

            filename=file.filename,

            document_id=document_id,

            mime_type=file.content_type,

            ocr_fallback=ocr_fallback,

            ocr_images=ocr_images,

            remove_headers_footers=remove_headers_footers,

            skip_empty_pages=skip_empty_pages,
        )

        logger.info(
            f"Successfully ingested "
            f"{file.filename}: "
            f"{result['total_pages']} pages, "
            f"{result['ocr_pages_used']} OCR pages"
        )

        # ----------------------------------------------------
        # Response
        # ----------------------------------------------------

        return IngestResponse(

            document_id=result["document_id"],

            filename=result["filename"],

            source_format=result["source_format"],

            total_pages=result["total_pages"],

            ocr_pages_used=result["ocr_pages_used"],

            chunks_created=result["chunks_created"],

            images_extracted=result.get(
                "images_extracted",
                0
            ),

            embeddings_created=result.get(
                "embeddings_created",
                0
            ),

            image_embeddings_created=result.get(
                "image_embeddings_created",
                0
            ),

            metadata=result.get(
                "metadata"
            ),

            status=result["status"],

            message=(
                f"Successfully ingested "
                f"{file.filename}"
            ),
        )

    except ValueError as e:

        logger.error(
            f"Validation error: {e}"
        )

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except FileNotFoundError as e:

        logger.error(
            f"File not found: {e}"
        )

        raise HTTPException(
            status_code=404,
            detail=str(e)
        )

    except Exception as e:

        logger.error(
            f"Ingestion failed: {e}",
            exc_info=True
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Document ingestion failed: "
                f"{str(e)}"
            ),
        )

    finally:

        # ----------------------------------------------------
        # Delete temporary file
        # ----------------------------------------------------

        try:

            if temp_file_path.exists():

                temp_file_path.unlink()

        except Exception as e:

            logger.warning(
                f"Failed to cleanup temp file: {e}"
            )


# ============================================================
# LIST DOCUMENTS
# ============================================================

@router.get("/documents")
def list_documents():
    """
    Get list of all ingested documents.
    """

    documents = get_all_documents()

    return {
        "total": len(documents),
        "documents": documents,
    }


# ============================================================
# DOCUMENT DETAILS
# ============================================================

@router.get("/documents/{document_id}")
def get_document_details(
    document_id: str
):
    """
    Get details for a specific document.
    """

    document = get_document(
        document_id
    )

    if not document:

        raise HTTPException(
            status_code=404,
            detail=(
                f"Document "
                f"{document_id} not found"
            ),
        )

    return document


# ============================================================
# DOCUMENT CHUNKS
# ============================================================

@router.get(
    "/documents/{document_id}/chunks"
)
def get_document_chunks(
    document_id: str
):
    """
    Get all chunks for a document.
    """

    chunks = get_chunks(
        document_id
    )

    if chunks is None:

        raise HTTPException(
            status_code=404,
            detail=(
                f"Document "
                f"{document_id} not found"
            ),
        )

    return {
        "document_id": document_id,

        "total_chunks": len(chunks),

        "chunks": chunks,
    }


# ============================================================
# SPECIFIC CHUNK
# ============================================================

@router.get(
    "/documents/{document_id}/chunks/{chunk_index}"
)
def get_specific_chunk(
    document_id: str,
    chunk_index: int
):
    """
    Get a specific chunk.
    """

    chunk = get_chunk(
        document_id,
        chunk_index
    )

    if chunk is None:

        raise HTTPException(
            status_code=404,
            detail=(
                f"Chunk {chunk_index} "
                f"not found for document "
                f"{document_id}"
            ),
        )

    return chunk


# ============================================================
# DOCUMENT IMAGES
# ============================================================

@router.get(
    "/documents/{document_id}/images"
)
def get_document_images(
    document_id: str
):
    """
    Get all extracted image metadata.
    """

    images = get_images(
        document_id
    )

    if images is None:

        raise HTTPException(
            status_code=404,
            detail=(
                f"Document "
                f"{document_id} not found"
            ),
        )

    return {
        "document_id": document_id,

        "total_images": len(images),

        "images": images,
    }


# ============================================================
# SPECIFIC IMAGE
# ============================================================

@router.get(
    "/documents/{document_id}/images/{image_index}"
)
def get_specific_image(
    document_id: str,
    image_index: int
):
    """
    Get metadata for a specific image.
    """

    image = get_image(
        document_id,
        image_index
    )

    if image is None:

        raise HTTPException(
            status_code=404,
            detail=(
                f"Image {image_index} "
                f"not found for document "
                f"{document_id}"
            ),
        )

    return image


# ============================================================
# DELETE DOCUMENT
# ============================================================

@router.delete(
    "/documents/{document_id}"
)
def delete_document_endpoint(
    document_id: str
):
    """
    Delete document, chunks, images,
    and vector embeddings.
    """

    success = delete_document(
        document_id
    )

    # Delete text + image vectors
    qdrant_service.delete_document(
        document_id
    )

    # Delete physical image files
    deleted_images = (
        delete_document_images(
            document_id
        )
    )

    if not success:

        raise HTTPException(
            status_code=404,
            detail=(
                f"Document "
                f"{document_id} not found"
            ),
        )

    return {
        "message": (
            f"Document "
            f"{document_id} deleted successfully"
        ),

        "images_deleted": deleted_images,
    }


# ============================================================
# STORAGE STATS
# ============================================================

@router.get("/stats")
def get_storage_stats():
    """
    Get storage statistics.
    """

    stats = get_stats()

    stats["vector_count"] = (
        qdrant_service.count_vectors()
    )

    stats["image_vector_count"] = (
        qdrant_service.count_vectors(
            qdrant_service.image_collection_name
        )
    )

    return stats


# ============================================================
# TEXT SEARCH REQUEST
# ============================================================

class SearchRequest(BaseModel):

    query: str

    top_k: Optional[int] = 5

    score_threshold: Optional[float] = None

    document_id: Optional[
        Union[str, List[str]]
    ] = None

    filename: Optional[str] = None

    source_format: Optional[str] = None

    page_number: Optional[
        Union[int, List[int]]
    ] = None

    is_ocr: Optional[bool] = None

    enable_hybrid: Optional[bool] = True


# ============================================================
# TEXT SEMANTIC SEARCH
# ============================================================

@router.post("/search")
async def search_documents(
    request: SearchRequest
):
    """
    Semantic text search.

    Searches document text chunks
    using embeddings + Qdrant.
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

        logger.error(
            f"Search failed: {e}",
            exc_info=True
        )

        raise HTTPException(
            status_code=500,
            detail=(
                f"Search failed: {str(e)}"
            ),
        )


# ============================================================
# IMAGE SEARCH REQUEST
# ============================================================

class ImageSearchRequest(BaseModel):

    query: str

    top_k: Optional[int] = 5

    score_threshold: Optional[float] = None

    document_id: Optional[str] = None


# ============================================================
# IMAGE SEMANTIC SEARCH
# ============================================================

@router.post("/search/images")
async def search_images(
    request: ImageSearchRequest
):
    """
    Search document images using natural language.

    Example:

        {
            "query": "financial revenue chart",
            "top_k": 5
        }

    OpenCLIP converts the text query into a
    512-dimensional embedding.

    Qdrant searches the image vector collection.

    Returns the most semantically relevant images.
    """

    try:

        # ----------------------------------------------------
        # Validate query
        # ----------------------------------------------------

        if not request.query.strip():

            raise HTTPException(
                status_code=400,
                detail="Image search query cannot be empty",
            )

        # ----------------------------------------------------
        # Search images
        # ----------------------------------------------------

        results = image_retrieval_service.search(

            query=request.query,

            top_k=request.top_k or 5,

            score_threshold=request.score_threshold,

            document_id=request.document_id,
        )

        return results

    except HTTPException:

        raise

    except Exception as e:

        logger.error(
            f"Image search failed: {e}",
            exc_info=True
        )

        raise HTTPException(
            status_code=500,
            detail=(
                f"Image search failed: {str(e)}"
            ),
        )


# ============================================================
# QUERY REQUEST
# ============================================================

class QueryRequest(BaseModel):

    question: str

    document_id: Optional[str] = None

    top_k: Optional[int] = 5


# ============================================================
# QUERY RESPONSE
# ============================================================

class QueryResponse(BaseModel):

    question: str

    answer: str

    sources: list = []

    rag_context: Optional[str] = None


# ============================================================
# RAG QUERY
# ============================================================

@router.post(
    "/query",
    response_model=QueryResponse
)
async def query_documents(
    request: QueryRequest
):
    """
    Ask a question and generate an AI answer
    using the LangGraph workflow.
    """

    try:
        state = {
            "query": request.question,
            "response": None,
            "documents": [],
            "images": [],
            "citations": [],
            "next_agent": None,
        }

        result = graph.invoke(state)

        return QueryResponse(
            question=request.question,
            answer=result.get("response") or "No answer generated.",
            sources=result.get("citations", []),
        )

    except Exception as e:
        logger.error(
            f"Query endpoint failed: {e}",
            exc_info=True
        )

        return QueryResponse(
            question=request.question,
            answer=f"Error executing query: {str(e)}",
            sources=[],
        )


# ============================================================
# MEMO REQUEST
# ============================================================

class MemoRequest(BaseModel):

    document_id: str

    focus_area: Optional[str] = None


# ============================================================
# MEMO RESPONSE
# ============================================================

class MemoResponse(BaseModel):

    document_id: str

    memo: str

    status: str


# ============================================================
# GENERATE MEMO
# ============================================================

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