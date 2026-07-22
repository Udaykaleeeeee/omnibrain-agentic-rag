"""Document ingestion pipeline orchestration."""
import logging
from pathlib import Path
from typing import Optional, List

from .router import parse_document, is_supported_format
from .models import ParsedDocument
from .preprocessing import (
    preprocess_text,
    detect_repeated_headers_footers,
    is_empty_or_garbage
)

try:
    from ..models.chunking import TextChunker
    CHUNKER_AVAILABLE = True
except ImportError:
    CHUNKER_AVAILABLE = False
    TextChunker = None  # type: ignore

logger = logging.getLogger(__name__)


class IngestionPipeline:
    """Orchestrates document ingestion workflow."""
    
    def __init__(
        self,
        ocr_fallback: bool = True,
        ocr_images: bool = True,
        remove_headers_footers: bool = True,
        skip_empty_pages: bool = True,
        chunk_size: int = 500,
        chunk_overlap: int = 100
    ):
        self.ocr_fallback = ocr_fallback
        self.ocr_images = ocr_images
        self.remove_headers_footers = remove_headers_footers
        self.skip_empty_pages = skip_empty_pages
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        if CHUNKER_AVAILABLE:
            self.chunker = TextChunker(chunk_size=chunk_size, overlap=chunk_overlap)
        else:
            self.chunker = None
            logger.warning("Chunking module not available - chunks will not be created")
    
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
    
    def chunk_document(self, doc: ParsedDocument) -> List[dict]:
        """Chunk document pages into smaller text segments."""
        if not self.chunker:
            logger.warning("Chunker not available - skipping chunking")
            return []
        
        all_chunks = []
        
        for page in doc.pages:
            if not page.text.strip():
                continue
            
            page_chunks = self.chunker.split_text(page.text)
            
            for chunk_index, chunk_text in enumerate(page_chunks):
                chunk = {
                    "text": chunk_text,
                    "page_number": page.page_number,
                    "chunk_index": chunk_index,
                    "source_format": doc.source_format,
                    "filename": doc.filename,
                    "is_ocr": page.is_ocr
                }
                all_chunks.append(chunk)
        
        logger.info(f"Created {len(all_chunks)} chunks from {doc.total_pages} pages")
        return all_chunks
    
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
        
        chunks = self.chunk_document(doc)
        
        # Store chunks in memory (temporary storage)
        from .storage import store_document
        
        document_data = {
            "filename": filename,
            "source_format": doc.source_format,
            "total_pages": doc.total_pages,
            "ocr_pages_used": doc.ocr_pages_used,
            "metadata": doc.metadata
        }
        
        store_document(document_id, document_data, chunks)
        logger.info(f"Stored {len(chunks)} chunks for document {document_id}")
        
        # TODO: Embedding generation
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
