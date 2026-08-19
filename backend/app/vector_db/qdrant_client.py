"""
Qdrant Vector Database Service
Handles storing and retrieving text and image embeddings with metadata filtering.
"""

import logging
import uuid
import os
from typing import List, Dict, Any, Optional, Union

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    MatchAny,
    Range,
)

logger = logging.getLogger(__name__)


class QdrantService:
    """
    Handles all interactions with the Qdrant Vector Database.
    Supports text and image vector storage, top-k retrieval, metadata filtering,
    and similarity score thresholding.
    """

    def __init__(
        self,
        collection_name: str = "omnibrain_documents",
        image_collection_name: str = "omnibrain_images",
        host: str = "localhost",
        port: int = 6333,
        vector_size: int = 384,
        image_vector_size: int = 512,
        prefer_grpc: bool = False,
        location: Optional[str] = None,
        url: Optional[str] = None,
        api_key: Optional[str] = None,
    ):
        self.collection_name = collection_name
        self.image_collection_name = image_collection_name
        self.vector_size = vector_size
        self.image_vector_size = image_vector_size

        # Read Qdrant Cloud credentials from environment variables
        qdrant_url = url or os.getenv("QDRANT_URL")
        qdrant_api_key = api_key or os.getenv("QDRANT_API_KEY")

        # Local Qdrant settings
        qdrant_host = os.getenv("QDRANT_HOST", host)
        qdrant_port = int(os.getenv("QDRANT_PORT", str(port)))

        # --------------------------------------------------------
        # In-memory Qdrant
        # --------------------------------------------------------
        if location:
            self.client = QdrantClient(location=location)
            logger.info(
                f"Initialized QdrantClient with location='{location}'"
            )

        # --------------------------------------------------------
        # Qdrant Cloud
        # --------------------------------------------------------
        elif qdrant_url:
            if not qdrant_api_key:
                raise ValueError(
                    "QDRANT_API_KEY is required when QDRANT_URL is configured."
                )

            try:
                self.client = QdrantClient(
                    url=qdrant_url,
                    api_key=qdrant_api_key,
                    prefer_grpc=prefer_grpc,
                    timeout=10.0,
                )

                # Test cloud connection
                self.client.get_collections()

                logger.info(
                    "Successfully connected to Qdrant Cloud."
                )

            except Exception as e:
                logger.error(
                    f"Could not connect to Qdrant Cloud: {e}"
                )
                raise

        # --------------------------------------------------------
        # Local Docker Qdrant
        # --------------------------------------------------------
        else:
            try:
                self.client = QdrantClient(
                    host=qdrant_host,
                    port=qdrant_port,
                    prefer_grpc=prefer_grpc,
                    timeout=5.0,
                )

                # Test local connection
                self.client.get_collections()

                logger.info(
                    f"Connected to local Qdrant at "
                    f"{qdrant_host}:{qdrant_port}"
                )

            except Exception as e:
                logger.warning(
                    f"Could not connect to local Qdrant at "
                    f"{qdrant_host}:{qdrant_port} ({e}). "
                    f"Falling back to in-memory Qdrant instance."
                )

                self.client = QdrantClient(
                    location=":memory:"
                )

        self.create_collection()
        self.create_image_collection()

    def create_collection(self):
        """
        Creates the text document collection if it doesn't already exist.
        """
        try:
            collections = self.client.get_collections().collections
            collection_names = [c.name for c in collections]

            if self.collection_name not in collection_names:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.vector_size,
                        distance=Distance.COSINE,
                    ),
                )
                logger.info(
                    f"Collection '{self.collection_name}' created successfully."
                )
            else:
                logger.info(
                    f"Collection '{self.collection_name}' already exists."
                )
        except Exception as e:
            logger.error(f"Failed to create collection '{self.collection_name}': {e}")

    def create_image_collection(self):
        """
        Creates the image vector collection if it doesn't already exist.
        """
        try:
            collections = self.client.get_collections().collections
            collection_names = [c.name for c in collections]

            if self.image_collection_name not in collection_names:
                self.client.create_collection(
                    collection_name=self.image_collection_name,
                    vectors_config=VectorParams(
                        size=self.image_vector_size,
                        distance=Distance.COSINE,
                    ),
                )
                logger.info(
                    f"Image collection '{self.image_collection_name}' created successfully."
                )
            else:
                logger.info(
                    f"Image collection '{self.image_collection_name}' already exists."
                )
        except Exception as e:
            logger.error(f"Failed to create image collection '{self.image_collection_name}': {e}")

    def upsert_vectors(
        self,
        document_id: str,
        chunks: list,
        embeddings: list,
    ):
        """
        Store embeddings and metadata inside Qdrant.
        """
        if not chunks or not embeddings:
            logger.warning("Empty chunks or embeddings passed to upsert_vectors.")
            return

        points = []

        for index, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            chunk_index = chunk.get("chunk_index", index)
            text_content = chunk.get("text", "")
            page_num = chunk.get("page_number", 1)
            fname = chunk.get("filename", "")
            src_fmt = chunk.get("source_format", "")
            ocr_flag = chunk.get("is_ocr", False)

            point = PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload={
                    "document_id": document_id,
                    "chunk_index": chunk_index,
                    "text": text_content,
                    "page_number": page_num,
                    "filename": fname,
                    "source_format": src_fmt,
                    "is_ocr": ocr_flag,
                },
            )
            points.append(point)

        self.client.upsert(
            collection_name=self.collection_name,
            points=points,
        )

        logger.info(
            f"Inserted {len(points)} vectors into Qdrant collection '{self.collection_name}'."
        )

    def upsert_image_vectors(
        self,
        document_id: str,
        image_metadata: List[Dict[str, Any]],
        embeddings: List[List[float]],
    ):
        """
        Store image embeddings and metadata inside Qdrant.
        """
        if not image_metadata or not embeddings:
            logger.warning("Empty image metadata or embeddings passed to upsert_image_vectors.")
            return

        points = []

        for meta, embedding in zip(image_metadata, embeddings):
            point = PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload={
                    "document_id": document_id,
                    "image_path": meta.get("image_path", ""),
                    "page_number": meta.get("page_number", 1),
                    "image_index": meta.get("image_index", 0),
                    "filename": meta.get("filename", ""),
                    "format": meta.get("format", ""),
                    "width": meta.get("width"),
                    "height": meta.get("height"),
                    "ocr_text": meta.get("ocr_text", ""),
                },
            )
            points.append(point)

        self.client.upsert(
            collection_name=self.image_collection_name,
            points=points,
        )

        logger.info(
            f"Inserted {len(points)} image vectors into Qdrant image collection."
        )

    def _build_filter(
        self,
        document_ids: Optional[Union[str, List[str]]] = None,
        filename: Optional[str] = None,
        source_format: Optional[str] = None,
        is_ocr: Optional[bool] = None,
        page_number: Optional[Union[int, List[int]]] = None,
        extra_filters: Optional[Dict[str, Any]] = None,
    ) -> Optional[Filter]:
        """
        Build Qdrant Filter object from key payload constraints.
        """
        must_conditions = []

        if document_ids:
            if isinstance(document_ids, str):
                must_conditions.append(
                    FieldCondition(
                        key="document_id",
                        match=MatchValue(value=document_ids),
                    )
                )
            elif isinstance(document_ids, list) and len(document_ids) > 0:
                must_conditions.append(
                    FieldCondition(
                        key="document_id",
                        match=MatchAny(any=document_ids),
                    )
                )

        if filename:
            must_conditions.append(
                FieldCondition(
                    key="filename",
                    match=MatchValue(value=filename),
                )
            )

        if source_format:
            must_conditions.append(
                FieldCondition(
                    key="source_format",
                    match=MatchValue(value=source_format.lower()),
                )
            )

        if is_ocr is not None:
            must_conditions.append(
                FieldCondition(
                    key="is_ocr",
                    match=MatchValue(value=is_ocr),
                )
            )

        if page_number is not None:
            if isinstance(page_number, int):
                must_conditions.append(
                    FieldCondition(
                        key="page_number",
                        match=MatchValue(value=page_number),
                    )
                )
            elif isinstance(page_number, list) and len(page_number) > 0:
                must_conditions.append(
                    FieldCondition(
                        key="page_number",
                        match=MatchAny(any=page_number),
                    )
                )

        if extra_filters:
            for key, val in extra_filters.items():
                if isinstance(val, list):
                    must_conditions.append(
                        FieldCondition(
                            key=key,
                            match=MatchAny(any=val),
                        )
                    )
                else:
                    must_conditions.append(
                        FieldCondition(
                            key=key,
                            match=MatchValue(value=val),
                        )
                    )

        if not must_conditions:
            return None

        return Filter(must=must_conditions)

    def search(
        self,
        query_embedding: Optional[List[float]] = None,
        limit: int = 5,
        score_threshold: Optional[float] = None,
        document_ids: Optional[Union[str, List[str]]] = None,
        filename: Optional[str] = None,
        source_format: Optional[str] = None,
        is_ocr: Optional[bool] = None,
        page_number: Optional[Union[int, List[int]]] = None,
        filter_dict: Optional[Dict[str, Any]] = None,
        query_filter: Optional[Filter] = None,
        query_vector: Optional[List[float]] = None,
    ) -> List[Any]:
        """
        Search for similar vectors with top-k limit, metadata filtering, and score threshold.
        """
        vector_to_search = query_embedding if query_embedding is not None else query_vector
        if vector_to_search is None:
            raise ValueError("Must provide either query_embedding or query_vector to QdrantService.search()")

        if query_filter is None:
            query_filter = self._build_filter(
                document_ids=document_ids,
                filename=filename,
                source_format=source_format,
                is_ocr=is_ocr,
                page_number=page_number,
                extra_filters=filter_dict,
            )

        if hasattr(self.client, "search"):
            return self.client.search(
                collection_name=self.collection_name,
                query_vector=vector_to_search,
                limit=limit,
                query_filter=query_filter,
                score_threshold=score_threshold,
            )
        elif hasattr(self.client, "query_points"):
            res = self.client.query_points(
                collection_name=self.collection_name,
                query=vector_to_search,
                limit=limit,
                query_filter=query_filter,
                score_threshold=score_threshold,
            )
            return res.points
        else:
            raise RuntimeError("QdrantClient object has neither 'search' nor 'query_points' method.")

    def search_images(
        self,
        query_embedding: List[float],
        limit: int = 5,
        score_threshold: Optional[float] = None,
        document_id: Optional[str] = None,
    ) -> List[Any]:
        """
        Search for similar image vectors.
        """
        query_filter = None
        if document_id:
            query_filter = Filter(
                must=[
                    FieldCondition(
                        key="document_id",
                        match=MatchValue(value=document_id),
                    )
                ]
            )

        if hasattr(self.client, "search"):
            return self.client.search(
                collection_name=self.image_collection_name,
                query_vector=query_embedding,
                limit=limit,
                query_filter=query_filter,
                score_threshold=score_threshold,
            )
        elif hasattr(self.client, "query_points"):
            res = self.client.query_points(
                collection_name=self.image_collection_name,
                query=query_embedding,
                limit=limit,
                query_filter=query_filter,
                score_threshold=score_threshold,
            )
            return res.points
        else:
            return []

    def delete_document(self, document_id: str) -> bool:
        """
        Delete all points associated with a document_id from text and image collections.
        """
        try:
            doc_filter = Filter(
                must=[
                    FieldCondition(
                        key="document_id",
                        match=MatchValue(value=document_id),
                    )
                ]
            )
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=doc_filter,
            )
            try:
                self.client.delete(
                    collection_name=self.image_collection_name,
                    points_selector=doc_filter,
                )
            except Exception:
                pass
            logger.info(f"Deleted document '{document_id}' points from Qdrant.")
            return True
        except Exception as e:
            logger.error(f"Failed to delete document '{document_id}' points: {e}")
            return False

    def count_vectors(self, collection_name: Optional[str] = None) -> int:
        """
        Get total point count in a collection.
        """
        target = collection_name or self.collection_name
        try:
            info = self.client.get_collection(collection_name=target)
            return info.points_count or 0
        except Exception as e:
            logger.error(f"Error getting vector count for {target}: {e}")
            return 0
