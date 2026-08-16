import uuid
from typing import List, Optional

from qdrant_client.models import PointStruct

from backend.app.ingestion.pdf_loader import PDFLoader
from backend.app.models.chunking import TextChunker
from backend.app.models.embeddings import TextEmbeddingModel
from backend.app.models.image_embeddings import ImageEmbeddingModel


class IngestionPipeline:
    """
    Multi-modal document ingestion pipeline.

    Generates:
    - BGE text embeddings
    - OpenCLIP image embeddings
    - Qdrant PointStruct objects
    """

    def __init__(self):

        self.loader = PDFLoader()
        self.chunker = TextChunker()

        self.text_embedding_model = TextEmbeddingModel()
        self.image_embedding_model = ImageEmbeddingModel()

    def process(
        self,
        pdf_path: str,
        image_path: Optional[str] = None
    ) -> List[PointStruct]:
        """
        Process a PDF and optional image.

        Returns:
            List[PointStruct] ready for Qdrant upsert().
        """

        points: List[PointStruct] = []

        # ==========================================================
        # TEXT EMBEDDINGS
        # ==========================================================

        text = self.loader.load(pdf_path)

        chunks = self.chunker.split_text(text)

        embeddings = self.text_embedding_model.encode(chunks)

        for chunk_id, (chunk, embedding) in enumerate(
            zip(chunks, embeddings),
            start=1
        ):

            point = PointStruct(

                id=str(uuid.uuid4()),

                vector=embedding,

                payload={

                    "document_id": pdf_path,

                    "chunk_id": chunk_id,

                    "source": pdf_path,

                    "content": chunk,

                    "modality": "text"

                }

            )

            points.append(point)

        # ==========================================================
        # IMAGE EMBEDDINGS
        # ==========================================================

        if image_path:

            image_embedding = self.image_embedding_model.encode(
                image_path
            )[0]

            image_point = PointStruct(

                id=str(uuid.uuid4()),

                vector=image_embedding,

                payload={

                    "document_id": pdf_path,

                    "image_id": 1,

                    "image_path": image_path,

                    "source": image_path,

                    "modality": "image"

                }

            )

            points.append(image_point)

        return points


if __name__ == "__main__":

    pipeline = IngestionPipeline()

    points = pipeline.process(

        pdf_path="sample.pdf",

        image_path="sample.jpg"

    )

    print("\nGenerated Points:", len(points))

    for point in points:

        print("-" * 60)

        print("ID:", point.id)

        print("Payload:")

        for key, value in point.payload.items():
            print(f"  {key}: {value}")

        print("Embedding Dimension:", len(point.vector))