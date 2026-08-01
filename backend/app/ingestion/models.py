"""
Data models for document parsing and ingestion.
These models provide a unified interface regardless of source format (PDF, DOCX, TXT).
"""
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class PageImage:
    """Represents an image extracted from a document page."""
    image_bytes: bytes
    page_number: int
    image_index: int  # Index within the page (0-based)
    width: Optional[int] = None
    height: Optional[int] = None
    format: Optional[str] = None  # e.g., 'PNG', 'JPEG'
    ocr_text: Optional[str] = None  # Text extracted via OCR if applicable
    # Image storage metadata
    image_path: Optional[str] = None  # Path where image is saved
    bbox: Optional[dict] = None  # Bounding box {x0, y0, x1, y1} if available
    document_id: Optional[str] = None  # Reference to source document


@dataclass
class ParsedPage:
    """Represents a single page from a parsed document."""
    page_number: int  # 1-indexed
    text: str
    images: List[PageImage] = field(default_factory=list)
    is_ocr: bool = False  # True if text came from OCR rather than native extraction
    metadata: dict = field(default_factory=dict)  # Additional page-level metadata


@dataclass
class ParsedDocument:
    """Unified representation of a parsed document (PDF, DOCX, or TXT)."""
    filename: str
    source_format: str  # 'pdf', 'docx', 'txt'
    pages: List[ParsedPage]
    total_pages: int
    ocr_pages_used: int = 0  # Count of pages where OCR was applied
    metadata: dict = field(default_factory=dict)  # Document-level metadata
