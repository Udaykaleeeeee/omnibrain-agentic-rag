"""
Qdrant Vector Database Service
Handles storing and retrieving embeddings.
"""

import logging

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
)

logger = logging.getLogger(__name__)


class QdrantService:
    """
    Handles all interactions with the Qdrant Vector Database.
    """

    def __init__(
        self,
        collection_name: str = "omnibrain_documents",
        host: str = "localhost",
        port: int = 6333,
        vector_size: int = 384,
    ):

        self.collection_name = collection_name
        self.vector_size = vector_size

        self.client = QdrantClient(
            host=host,
            port=port
        )

        self.create_collection()

    def create_collection(self):
        """
        Creates the collection if it doesn't already exist.
        """

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

    def upsert_vectors(
        self,
        document_id: str,
        chunks: list,
        embeddings: list,
    ):
        """
        Store embeddings and metadata inside Qdrant.
        """

        points = []

        for index, (chunk, embedding) in enumerate(zip(chunks, embeddings)):

            point = PointStruct(
                id=index,
                vector=embedding,
                payload={
                    "document_id": document_id,
                    "chunk_index": index,
                    "text": chunk["text"],
                    "page_number": chunk["page_number"],
                    "filename": chunk["filename"],
                    "source_format": chunk["source_format"],
                    "is_ocr": chunk["is_ocr"],
                },
            )

            points.append(point)

        self.client.upsert(
            collection_name=self.collection_name,
            points=points,
        )

        logger.info(
            f"Inserted {len(points)} vectors into Qdrant."
        )

    def search(
        self,
        query_embedding: list,
        limit: int = 5,
    ):
        """
        Search for similar vectors.
        """

        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=limit,
        )

        return results