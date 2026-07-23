"""
Document ingestion pipeline orchestration.
"""

import logging
from pathlib import Path
from typing import Optional, List

from .router import parse_document, is_supported_format
from .models import ParsedDocument
from .preprocessing import (
    preprocess_text,
    detect_repeated_headers_footers,
    is_empty_or_garbage,
)

from ..models.chunking import TextChunker
from ..models.embeddings import TextEmbeddingModel
from ..vector_db.qdrant_client import QdrantService
from .storage import store_document

logger = logging.getLogger(__name__)


class IngestionPipeline:
    """
    Complete document ingestion workflow.
    """

    def __init__(
        self,
        ocr_fallback: bool = True,
        ocr_images: bool = True,
        remove_headers_footers: bool = True,
        skip_empty_pages: bool = True,
        chunk_size: int = 500,
        chunk_overlap: int = 100,
    ):
        self.ocr_fallback = ocr_fallback
        self.ocr_images = ocr_images
        self.remove_headers_footers = remove_headers_footers
        self.skip_empty_pages = skip_empty_pages

        self.chunker = TextChunker(
            chunk_size=chunk_size,
            overlap=chunk_overlap,
        )

        self.embedding_model = TextEmbeddingModel()

        self.vector_db = QdrantService()
    def validate_file(self, file_path: str) -> None:
          """
          Validate file exists and is supported.
          """

          path = Path(file_path)

          if not path.exists():
             raise FileNotFoundError(f"File not found: {file_path}")

          if not is_supported_format(file_path):
             raise ValueError(f"Unsupported file format: {path.suffix}")


    def parse_and_preprocess(
        self,
        file_path: str,
        filename: str,
        mime_type: Optional[str] = None,
    ) -> ParsedDocument:
        """
        Parse document and preprocess text.
        """

        doc = parse_document(
            file_path=file_path,
            filename=filename,
            mime_type=mime_type,
            ocr_fallback=self.ocr_fallback,
            ocr_images=self.ocr_images,
        )

        logger.info(
            f"Parsed {doc.source_format.upper()} with {doc.total_pages} pages."
        )

        repeated_patterns = []

        if self.remove_headers_footers and len(doc.pages) > 2:
            page_texts = [page.text for page in doc.pages]

            repeated_patterns = detect_repeated_headers_footers(page_texts)

        processed_pages = []

        for page in doc.pages:

            cleaned_text = preprocess_text(
                page.text,
                repeated_patterns,
            )

            if self.skip_empty_pages and is_empty_or_garbage(cleaned_text):
                continue

            page.text = cleaned_text

            processed_pages.append(page)

        doc.pages = processed_pages
        doc.total_pages = len(processed_pages)

        return doc


    def chunk_document(
        self,
        doc: ParsedDocument,
    ) -> List[dict]:
        """
        Split pages into chunks.
        """

        all_chunks = []

        for page in doc.pages:

            if not page.text.strip():
                continue

            page_chunks = self.chunker.split_text(page.text)

            for index, chunk_text in enumerate(page_chunks):

                chunk = {
                    "text": chunk_text,
                    "page_number": page.page_number,
                    "chunk_index": index,
                    "filename": doc.filename,
                    "source_format": doc.source_format,
                    "is_ocr": page.is_ocr,
                }

                all_chunks.append(chunk)

        logger.info(
            f"Created {len(all_chunks)} chunks from {doc.total_pages} pages."
        )

        return all_chunks   
    def ingest_document(
        self,
        file_path: str,
        filename: str,
        document_id: str,
        mime_type: Optional[str] = None,
    ) -> dict:
          """
          Complete ingestion workflow.
          """

        # -------------------------
        # Validate
        # -------------------------
          self.validate_file(file_path)

        # -------------------------
        # Parse document
        # -------------------------
          doc = self.parse_and_preprocess(
            file_path,
            filename,
            mime_type,
        )

        # -------------------------
        # Create chunks
        # -------------------------
          chunks = self.chunk_document(doc)

        # -------------------------
        # Generate embeddings
        # -------------------------
          chunk_texts = [chunk["text"] for chunk in chunks]

          embeddings = (
            self.embedding_model.encode(chunk_texts)
            if chunk_texts
            else []
        )

          logger.info(
            f"Generated {len(embeddings)} embeddings."
        )

        # -------------------------
        # Store metadata temporarily
        # -------------------------
          document_data = {
            "filename": filename,
            "source_format": doc.source_format,
            "total_pages": doc.total_pages,
            "ocr_pages_used": doc.ocr_pages_used,
            "metadata": doc.metadata,
        }

          store_document(
            document_id,
            document_data,
            chunks,
        )

          logger.info(
            f"Stored {len(chunks)} chunks in temporary storage."
        )

        # -------------------------
        # Store vectors in Qdrant
        # -------------------------
          if embeddings:

            self.vector_db.upsert_vectors(
                document_id=document_id,
                chunks=chunks,
                embeddings=embeddings,
            )

            logger.info(
                "Vectors stored successfully in Qdrant."
            )

        # -------------------------
        # Return response
        # -------------------------
          return {
            "document_id": document_id,
            "filename": filename,
            "source_format": doc.source_format,
            "total_pages": doc.total_pages,
            "ocr_pages_used": doc.ocr_pages_used,
            "chunks_created": len(chunks),
            "embeddings_created": len(embeddings),
            "status": "success",
        } 
def ingest_document(
    file_path: str,
    filename: str,
    document_id: str,
    mime_type: Optional[str] = None,
    **kwargs,
) -> dict:
    """
    Main entry point for document ingestion.
    """
    pipeline = IngestionPipeline(**kwargs)

    return pipeline.ingest_document(
        file_path=file_path,
        filename=filename,
        document_id=document_id,
        mime_type=mime_type,
    )    