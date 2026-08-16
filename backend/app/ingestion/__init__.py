"""
Document ingestion module for OmniBrain RAG system.

Supports parsing, preprocessing, and ingestion of PDF, DOCX, and TXT files.
Includes OCR support for scanned documents and images.
"""

from .models import ParsedDocument, ParsedPage, PageImage
from .router import parse_document, is_supported_format, get_supported_extensions
from .preprocessing import preprocess_text
from .pipeline import IngestionPipeline, ingest_document

__all__ = [
    "ParsedDocument",
    "ParsedPage",
    "PageImage",
    "parse_document",
    "is_supported_format",
    "get_supported_extensions",
    "ingest_document",
    "IngestionPipeline",
    "preprocess_text",
]