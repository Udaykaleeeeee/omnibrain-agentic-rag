"""Document ingestion pipeline orchestration."""
import logging
from pathlib import Path
from typing import Optional

from .router import parse_document, is_supported_format
from .models import ParsedDocument
from .preprocessing import (
    preprocess_text,
    detect_repeated_headers_footers,
    is_empty_or_garbage
)

logger = logging.getLogger(__name__)


class IngestionPipeline:
    """Orchestrates document ingestion workflow."""
    
    def __init__(
        self,
        ocr_fallback: bool = True,
        ocr_images: bool = True,
        remove_headers_footers: bool = True,
        skip_empty_pages: bool = True
    ):
        self.ocr_fallback = ocr_fallback
        self.ocr_images = ocr_images
        self.remove_headers_footers = remove_headers_footers
        self.skip_empty_pages = skip_empty_pages
    
    def validate_file(self, file_path: str) -> None:
        """Validate file exists and is supported format."""
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if not is_supported_format(file_path):
            raise ValueError(f"Unsupported format: {path.suffix}")
    
    def parse_and_preprocess(
        self,
        file_path: str,
        filename: str,
        mime_type: Optional[str] = None
    ) -> ParsedDocument:
        """Parse and preprocess document."""
        doc = parse_document(
            file_path=file_path,
            filename=filename,
            mime_type=mime_type,
            ocr_fallback=self.ocr_fallback,
            ocr_images=self.ocr_images
        )
        
        logger.info(f"Parsed {doc.source_format.upper()}: {doc.total_pages} pages, {doc.ocr_pages_used} OCR")
        
        repeated_patterns = []
        if self.remove_headers_footers and len(doc.pages) > 2:
            page_texts = [page.text for page in doc.pages]
            repeated_patterns = detect_repeated_headers_footers(page_texts)
            if repeated_patterns:
                logger.info(f"Detected {len(repeated_patterns)} repeated patterns")
        
        preprocessed_pages = []
        skipped_pages = 0
        
        for page in doc.pages:
            cleaned_text = preprocess_text(page.text, repeated_patterns)
            
            if self.skip_empty_pages and is_empty_or_garbage(cleaned_text):
                logger.debug(f"Skipping empty page {page.page_number}")
                skipped_pages += 1
                continue
            
            page.text = cleaned_text
            
            for image in page.images:
                if image.ocr_text:
                    image.ocr_text = preprocess_text(image.ocr_text, repeated_patterns)
            
            preprocessed_pages.append(page)
        
        if skipped_pages > 0:
            logger.info(f"Skipped {skipped_pages} empty pages")
        
        doc.pages = preprocessed_pages
        doc.total_pages = len(preprocessed_pages)
        
        return doc
    
    def ingest_document(
        self,
        file_path: str,
        filename: str,
        document_id: str,
        mime_type: Optional[str] = None
    ) -> dict:
        """Complete ingestion workflow."""
        self.validate_file(file_path)
        doc = self.parse_and_preprocess(file_path, filename, mime_type)
        
        chunks = []  # TODO: Chunking
        embeddings = []  # TODO: Embedding
        # TODO: Vector DB upsert
        
        return {
            "document_id": document_id,
            "filename": filename,
            "source_format": doc.source_format,
            "total_pages": doc.total_pages,
            "ocr_pages_used": doc.ocr_pages_used,
            "chunks_created": len(chunks),
            "metadata": doc.metadata,
            "status": "success"
        }


def ingest_document(
    file_path: str,
    filename: str,
    document_id: str,
    mime_type: Optional[str] = None,
    **kwargs
) -> dict:
    """Main entry point for document ingestion."""
    pipeline = IngestionPipeline(**kwargs)
    return pipeline.ingest_document(file_path, filename, document_id, mime_type)
