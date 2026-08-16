"""Document parsing router for PDF, DOCX, and TXT files."""
import logging
import mimetypes
from pathlib import Path
from typing import Optional

from .models import ParsedDocument
from .pdf_parser import parse_pdf
from .docx_parser import parse_docx
from .txt_parser import parse_txt

logger = logging.getLogger(__name__)

SUPPORTED_FORMATS = {
    '.pdf': 'application/pdf',
    '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    '.txt': 'text/plain',
}


def get_file_format(file_path: str, mime_type: Optional[str] = None) -> Optional[str]:
    """Determine file format from extension or MIME type."""
    extension = Path(file_path).suffix.lower()
    
    if extension in SUPPORTED_FORMATS:
        return extension[1:]
    
    if mime_type:
        mime_to_format = {
            'application/pdf': 'pdf',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'docx',
            'text/plain': 'txt',
        }
        return mime_to_format.get(mime_type.lower())
    
    guessed_type, _ = mimetypes.guess_type(file_path)
    if guessed_type:
        mime_to_format = {
            'application/pdf': 'pdf',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'docx',
            'text/plain': 'txt',
        }
        return mime_to_format.get(guessed_type.lower())
    
    return None


def is_supported_format(file_path: str, mime_type: Optional[str] = None) -> bool:
    """Check if file format is supported."""
    return get_file_format(file_path, mime_type) is not None


def parse_document(
    file_path: str,
    filename: str,
    mime_type: Optional[str] = None,
    ocr_fallback: bool = True,
    ocr_images: bool = True
) -> ParsedDocument:
    """Parse document (PDF, DOCX, or TXT) with automatic format detection."""
    file_format = get_file_format(file_path, mime_type)
    
    if not file_format:
        extension = Path(file_path).suffix.lower()
        raise ValueError(
            f"Unsupported file format: {extension}. "
            f"Supported: {', '.join(SUPPORTED_FORMATS.keys())}"
        )
    
    logger.info(f"Parsing {file_format.upper()}: {filename}")
    
    try:
        if file_format == 'pdf':
            return parse_pdf(file_path, filename, ocr_fallback=ocr_fallback)
        elif file_format == 'docx':
            return parse_docx(file_path, filename, ocr_images=ocr_images)
        elif file_format == 'txt':
            return parse_txt(file_path, filename)
        else:
            raise ValueError(f"Format {file_format} not implemented")
    except Exception as e:
        logger.error(f"Failed to parse {filename}: {e}")
        raise


def get_supported_extensions() -> list:
    """Get list of supported extensions."""
    return list(SUPPORTED_FORMATS.keys())


def get_supported_mime_types() -> list:
    """Get list of supported MIME types."""
    return list(SUPPORTED_FORMATS.values())
