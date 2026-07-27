"""
Temporary in-memory storage for chunks and documents.
TODO: Replace with proper database (SQLite/Qdrant) in production.
"""
from datetime import datetime
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

# In-memory storage (lost on server restart)
DOCUMENT_STORE: Dict[str, dict] = {}
CHUNK_STORE: Dict[str, List[dict]] = {}
IMAGE_STORE: Dict[str, List[dict]] = {}  # New: store image metadata by document_id


def store_document(
    document_id: str,
    document_data: dict,
    chunks: List[dict],
    images: Optional[List[dict]] = None
) -> None:
    """Store document, chunks, and image metadata in memory."""
    DOCUMENT_STORE[document_id] = {
        **document_data,
        "document_id": document_id,
        "ingested_at": datetime.now().isoformat(),
        "chunk_count": len(chunks),
        "image_count": len(images) if images else 0
    }
    
    CHUNK_STORE[document_id] = chunks
    
    if images:
        IMAGE_STORE[document_id] = images
    
    logger.info(
        f"Stored document {document_id} with {len(chunks)} chunks "
        f"and {len(images) if images else 0} images"
    )


def get_document(document_id: str) -> Optional[dict]:
    """Retrieve document metadata."""
    return DOCUMENT_STORE.get(document_id)


def get_all_documents() -> List[dict]:
    """Retrieve all stored documents."""
    return list(DOCUMENT_STORE.values())


def get_chunks(document_id: str) -> Optional[List[dict]]:
    """Retrieve all chunks for a document."""
    return CHUNK_STORE.get(document_id)


def get_chunk(document_id: str, chunk_index: int) -> Optional[dict]:
    """Retrieve a specific chunk."""
    chunks = CHUNK_STORE.get(document_id)
    if chunks and 0 <= chunk_index < len(chunks):
        return chunks[chunk_index]
    return None


def delete_document(document_id: str) -> bool:
    """Delete document, chunks, and image metadata."""
    if document_id in DOCUMENT_STORE:
        del DOCUMENT_STORE[document_id]
        if document_id in CHUNK_STORE:
            del CHUNK_STORE[document_id]
        if document_id in IMAGE_STORE:
            del IMAGE_STORE[document_id]
        logger.info(f"Deleted document {document_id}")
        return True
    return False


def get_stats() -> dict:
    """Get storage statistics."""
    total_docs = len(DOCUMENT_STORE)
    total_chunks = sum(len(chunks) for chunks in CHUNK_STORE.values())
    
    return {
        "total_documents": total_docs,
        "total_chunks": total_chunks,
        "documents": list(DOCUMENT_STORE.keys())
    }


def clear_all() -> None:
    """Clear all stored data (use with caution!)."""
    DOCUMENT_STORE.clear()
    CHUNK_STORE.clear()
    IMAGE_STORE.clear()
    logger.warning("Cleared all stored documents, chunks, and images")


def get_images(document_id: str) -> Optional[List[dict]]:
    """Retrieve all image metadata for a document."""
    return IMAGE_STORE.get(document_id)


def get_image(document_id: str, image_index: int) -> Optional[dict]:
    """Retrieve specific image metadata by index."""
    images = IMAGE_STORE.get(document_id)
    if images and 0 <= image_index < len(images):
        return images[image_index]
    return None
