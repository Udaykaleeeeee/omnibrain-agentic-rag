"""
Document ingestion pipeline orchestration.
"""
 
import logging
from pathlib import Path
from typing import Optional, List, Tuple
 
from .router import parse_document, is_supported_format
from .models import ParsedDocument
from .preprocessing import (
    preprocess_text,
    detect_repeated_headers_footers,
    is_empty_or_garbage,
    detect_language,
)
from .image_storage import save_image, DEFAULT_IMAGE_DIR
 
from ..models.chunking import TextChunker
from ..models.embeddings import TextEmbeddingModel
from ..models.image_embeddings import ImageEmbeddingModel
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
        enable_image_embeddings: bool = True,
    ):
        self.ocr_fallback = ocr_fallback
        self.ocr_images = ocr_images
        self.remove_headers_footers = remove_headers_footers
        self.skip_empty_pages = skip_empty_pages
        self.enable_image_embeddings = enable_image_embeddings
 
        self.chunker = TextChunker(
            chunk_size=chunk_size,
            overlap=chunk_overlap,
        )
 
        self.embedding_model = TextEmbeddingModel()
 
        # Initialize image embedding model if enabled
        self.image_embedding_model = None
        if self.enable_image_embeddings:
            try:
                self.image_embedding_model = ImageEmbeddingModel()
                logger.info("Image embedding model initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize image embedding model: {e}")
                logger.warning("Image embeddings will be disabled for this pipeline")
                self.enable_image_embeddings = False
 
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
 
        # Detect document language from combined text
        all_text = "\n".join([p.text for p in doc.pages if p.text])
        detected_lang = detect_language(all_text)
        if detected_lang:
            doc.metadata["detected_language"] = detected_lang
 
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
 
    def process_images(
        self,
        doc: ParsedDocument,
        document_id: str,
    ) -> Tuple[List[dict], List[Optional[List[float]]]]:
        """
        Extract, save, catalog, and embed images from document.
 
        Returns:
            Tuple of (image_metadata, image_embeddings)
        """
        image_metadata = []
        image_embeddings = []
 
        for page in doc.pages:
            for img in page.images:
                try:
                    # Save image to disk
                    image_path = save_image(
                        image_bytes=img.image_bytes,
                        document_id=document_id,
                        page_number=img.page_number,
                        image_index=img.image_index,
                        image_format=img.format or "png"
                    )
 
                    # Build metadata record
                    img_meta = {
                        "document_id": document_id,
                        "page_number": img.page_number,
                        "image_index": img.image_index,
                        "image_path": image_path,
                        "width": img.width,
                        "height": img.height,
                        "format": img.format,
                        "ocr_text": img.ocr_text,
                        "bbox": None,
                        "filename": doc.filename,
                    }
 
                    image_metadata.append(img_meta)
 
                    # Generate embedding for this image using its actual saved file path
                    if self.enable_image_embeddings and self.image_embedding_model:
                        try:
                            full_image_path = str(DEFAULT_IMAGE_DIR / Path(image_path).name)
                            embedding = self.image_embedding_model.encode(full_image_path)
                            # encode() returns a list containing one embedding, e.g. [[...]]
                            image_embeddings.append(embedding[0])
                        except Exception as e:
                            logger.error(
                                f"Failed to embed image {img.image_index} "
                                f"on page {img.page_number}: {e}"
                            )
                            image_embeddings.append(None)
 
                except Exception as e:
                    logger.error(
                        f"Failed to process image {img.image_index} "
                        f"on page {img.page_number}: {e}"
                    )
 
        logger.info(f"Processed {len(image_metadata)} images from document")
        logger.info(
            f"Generated {sum(1 for e in image_embeddings if e is not None)} image embeddings"
        )
 
        return image_metadata, image_embeddings
 
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
        # Process, save, and embed images
        # -------------------------
        images, image_embeddings = self.process_images(doc, document_id)
 
        # -------------------------
        # Generate text embeddings
        # -------------------------
        chunk_texts = [chunk["text"] for chunk in chunks]
 
        embeddings = (
            self.embedding_model.encode(chunk_texts)
            if chunk_texts
            else []
        )
 
        logger.info(
            f"Generated {len(embeddings)} text embeddings."
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
            images,
        )
 
        logger.info(
            f"Stored {len(chunks)} chunks and {len(images)} images in temporary storage."
        )
 
        # -------------------------
        # Store text vectors in Qdrant
        # -------------------------
        if embeddings:
            self.vector_db.upsert_vectors(
                document_id=document_id,
                chunks=chunks,
                embeddings=embeddings,
            )
 
            logger.info(
                "Text vectors stored successfully in Qdrant."
            )
 
        # -------------------------
        # Store image vectors in Qdrant
        # -------------------------
        valid_image_pairs = [
            (meta, emb) for meta, emb in zip(images, image_embeddings)
            if emb is not None
        ]
 
        if valid_image_pairs:
            try:
                valid_metadata = [pair[0] for pair in valid_image_pairs]
                valid_embeddings = [pair[1] for pair in valid_image_pairs]
 
                self.vector_db.upsert_image_vectors(
                    document_id=document_id,
                    image_metadata=valid_metadata,
                    embeddings=valid_embeddings,
                )
                logger.info(
                    f"Stored {len(valid_embeddings)} image vectors in Qdrant."
                )
            except Exception as e:
                logger.error(f"Failed to store image vectors in Qdrant: {e}")
                logger.warning("Continuing without image vector storage")
 
        # -------------------------
        # Return response
        # -------------------------
        images_embedded_count = sum(1 for e in image_embeddings if e is not None)
 
        return {
            "document_id": document_id,
            "filename": filename,
            "source_format": doc.source_format,
            "total_pages": doc.total_pages,
            "ocr_pages_used": doc.ocr_pages_used,
            "chunks_created": len(chunks),
            "images_extracted": len(images),
            "embeddings_created": len(embeddings),
            "image_embeddings_created": images_embedded_count,
            "metadata": doc.metadata,
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