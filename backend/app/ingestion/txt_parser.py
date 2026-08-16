"""Plain text parser with encoding detection."""
import logging
from pathlib import Path
from typing import List

try:
    import chardet
    CHARDET_AVAILABLE = True
except ImportError:
    CHARDET_AVAILABLE = False

from .models import ParsedDocument, ParsedPage

logger = logging.getLogger(__name__)


def detect_encoding(file_path: Path) -> str:
    """Detect text file encoding."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            f.read()
        return 'utf-8'
    except UnicodeDecodeError:
        pass
    
    if CHARDET_AVAILABLE:
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read()
            result = chardet.detect(raw_data)
            detected_encoding = result.get('encoding', 'utf-8')
            logger.info(f"Detected encoding: {detected_encoding}")
            return detected_encoding or 'utf-8'
        except Exception as e:
            logger.warning(f"Encoding detection failed: {e}")
    
    return 'utf-8'


def split_text_into_pages(text: str) -> List[str]:
    """Split text into pages by form-feed or blank lines."""
    if '\f' in text:
        pages = text.split('\f')
        pages = [p.strip() for p in pages if p.strip()]
        if pages:
            return pages
    
    sections = text.split('\n\n\n')
    sections = [s.strip() for s in sections if s.strip()]
    
    if len(sections) > 1:
        return sections
    
    return [text] if text.strip() else []


def parse_txt(file_path: str, filename: str) -> ParsedDocument:
    """Parse plain text file."""
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"TXT file not found: {file_path}")
    
    try:
        encoding = detect_encoding(file_path)
        
        try:
            with open(file_path, 'r', encoding=encoding, errors='replace') as f:
                text = f.read()
        except Exception as e:
            logger.warning(f"Fallback to utf-8: {e}")
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                text = f.read()
        
        page_texts = split_text_into_pages(text)
        
        pages: List[ParsedPage] = []
        for page_num, page_text in enumerate(page_texts):
            parsed_page = ParsedPage(
                page_number=page_num + 1,
                text=page_text,
                images=[],
                is_ocr=False,
                metadata={}
            )
            pages.append(parsed_page)
        
        if not pages:
            pages = [ParsedPage(
                page_number=1,
                text="",
                images=[],
                is_ocr=False,
                metadata={}
            )]
        
        file_stat = file_path.stat()
        metadata = {
            "encoding": encoding,
            "size_bytes": file_stat.st_size,
            "created": str(file_stat.st_ctime),
            "modified": str(file_stat.st_mtime)
        }
        
        return ParsedDocument(
            filename=filename,
            source_format="txt",
            pages=pages,
            total_pages=len(pages),
            ocr_pages_used=0,
            metadata=metadata
        )
    
    except Exception as e:
        logger.error(f"Failed to parse TXT {filename}: {e}")
        raise
