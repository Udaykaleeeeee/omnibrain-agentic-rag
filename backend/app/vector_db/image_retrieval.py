"""
Image Retrieval Service

Handles text-to-image semantic search using OpenCLIP
and Qdrant image vector collection.
"""

import logging
from typing import Optional, List, Dict, Any

from .qdrant_client import QdrantService
from ..models.image_embeddings import ImageEmbeddingModel

logger = logging.getLogger(__name__)


class ImageRetrievalService:
    """
    Retrieves semantically relevant images from Qdrant
    using OpenCLIP text embeddings.
    """

    def __init__(
        self,
        vector_db: Optional[QdrantService] = None,
        embedding_model: Optional[ImageEmbeddingModel] = None,
    ):
        self._vector_db = vector_db
        self._embedding_model = embedding_model

    @property
    def vector_db(self) -> QdrantService:
        if self._vector_db is None:
            self._vector_db = QdrantService()
        return self._vector_db

    @property
    def embedding_model(self) -> ImageEmbeddingModel:
        if self._embedding_model is None:
            self._embedding_model = ImageEmbeddingModel()
        return self._embedding_model

    def search(
        self,
        query: str,
        top_k: int = 5,
        score_threshold: Optional[float] = None,
        document_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Search images using a natural-language text query.
        """

        if not query or not query.strip():
            logger.warning("Empty image search query received.")

            return {
                "query": query,
                "total_results": 0,
                "images": [],
            }

        # -----------------------------------------
        # Step 1: Generate OpenCLIP text embedding
        # -----------------------------------------

        logger.info(
            f"Generating OpenCLIP text embedding for: '{query}'"
        )

        query_embeddings = self.embedding_model.encode_text(query)

        if not query_embeddings:
            logger.warning(
                "OpenCLIP returned no text embedding."
            )

            return {
                "query": query,
                "total_results": 0,
                "images": [],
            }

        query_embedding = query_embeddings[0]

        # -----------------------------------------
        # Step 2: Search image collection
        # -----------------------------------------

        logger.info(
            f"Searching image collection for top-{top_k} results."
        )

        hits = self.vector_db.search_images(
            query_embedding=query_embedding,
            limit=top_k,
            score_threshold=score_threshold,
            document_id=document_id,
        )

        # -----------------------------------------
        # Step 3: Format results
        # -----------------------------------------

        images: List[Dict[str, Any]] = []

        for rank, hit in enumerate(hits, start=1):

            payload = getattr(hit, "payload", {}) or {}

            score = getattr(hit, "score", None)

            image_result = {
                "rank": rank,
                "point_id": str(getattr(hit, "id", "")),
                "document_id": payload.get("document_id"),
                "document_name": payload.get("filename", ""),
                "filename": payload.get("filename", ""),
                "page_number": payload.get("page_number"),
                "image_index": payload.get("image_index"),
                "image_path": payload.get("image_path"),
                "format": payload.get("format"),
                "width": payload.get("width"),
                "height": payload.get("height"),
                "ocr_text": payload.get("ocr_text", ""),
                "similarity_score": score,
                "score": score,
            }

            images.append(image_result)

        logger.info(
            f"Image search returned {len(images)} results."
        )

        return {
            "query": query,
            "total_results": len(images),
            "images": images,
        }