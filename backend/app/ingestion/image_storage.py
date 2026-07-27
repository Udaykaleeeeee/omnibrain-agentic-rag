"""
Image storage utilities for extracted document images.
Saves images to disk with proper naming and metadata tracking.
"""
import logging
from pathlib import Path
from typing import Optional
import hashlib

logger = logging.getLogger(__name__)

# Default storage directory for extracted images
DEFAULT_IMAGE_DIR = Path("backend/uploads/images")


def ensure_image_directory(base_dir: Optional[Path] = None) -> Path:
    """Ensure image storage directory exists."""
    image_dir = base_dir or DEFAULT_IMAGE_DIR
    image_dir.mkdir(parents=True, exist_ok=True)
    return image_dir


def generate_image_filename(
    document_id: str,
    page_number: int,
    image_index: int,
    image_format: str
) -> str:
    """Generate standardized filename for extracted image."""
    # Sanitize format
    fmt = image_format.lower().replace('.', '')
    if fmt == 'jpg':
        fmt = 'jpeg'
    
    # Format: {doc_id}_p{page}_img{index}.{ext}
    return f"{document_id}_p{page_number:04d}_img{image_index:03d}.{fmt}"


def save_image(
    image_bytes: bytes,
    document_id: str,
    page_number: int,
    image_index: int,
    image_format: str,
    base_dir: Optional[Path] = None
) -> str:
    """
    Save image bytes to disk and return the relative path.
    
    Returns:
        str: Relative path to saved image (e.g., "images/doc123_p0001_img000.png")
    """
    try:
        image_dir = ensure_image_directory(base_dir)
        
        filename = generate_image_filename(
            document_id, page_number, image_index, image_format
        )
        
        file_path = image_dir / filename
        
        with open(file_path, 'wb') as f:
            f.write(image_bytes)
        
        # Return relative path from uploads directory
        relative_path = f"images/{filename}"
        logger.info(f"Saved image: {relative_path}")
        
        return relative_path
    
    except Exception as e:
        logger.error(f"Failed to save image: {e}")
        raise


def calculate_image_hash(image_bytes: bytes) -> str:
    """Calculate SHA256 hash of image for deduplication."""
    return hashlib.sha256(image_bytes).hexdigest()


def delete_document_images(document_id: str, base_dir: Optional[Path] = None) -> int:
    """
    Delete all images associated with a document.
    
    Returns:
        int: Number of images deleted
    """
    try:
        image_dir = base_dir or DEFAULT_IMAGE_DIR
        
        if not image_dir.exists():
            return 0
        
        # Find all images for this document
        pattern = f"{document_id}_p*.png"
        deleted_count = 0
        
        for img_file in image_dir.glob(f"{document_id}_p*"):
            try:
                img_file.unlink()
                deleted_count += 1
            except Exception as e:
                logger.warning(f"Failed to delete {img_file}: {e}")
        
        logger.info(f"Deleted {deleted_count} images for document {document_id}")
        return deleted_count
    
    except Exception as e:
        logger.error(f"Error deleting images for document {document_id}: {e}")
        return 0
