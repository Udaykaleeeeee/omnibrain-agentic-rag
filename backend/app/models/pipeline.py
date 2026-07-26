from backend.app.ingestion.pdf_loader import PDFLoader
from backend.app.models.chunking import TextChunker
from backend.app.models.embeddings import TextEmbeddingModel
from backend.app.models.image_embeddings import ImageEmbeddingModel
from backend.app.models.image_index import ImageIndex


class IngestionPipeline:
    """
    Multi-modal document ingestion pipeline.
    """

    def __init__(self):
        self.loader = PDFLoader()
        self.chunker = TextChunker()

        self.text_embedding_model = TextEmbeddingModel()
        self.image_embedding_model = ImageEmbeddingModel()

        self.image_index = ImageIndex()

    def process(self, pdf_path: str, image_path: str = None):
        """
        Process PDF and optional image.
        """

        # ---------- TEXT ----------
        text = self.loader.load(pdf_path)

        chunks = self.chunker.split_text(text)

        embeddings = self.text_embedding_model.encode(chunks)

        documents = []

        for i, (chunk, embedding) in enumerate(
                zip(chunks, embeddings), start=1):

            documents.append(
                {
                    "chunk_id": i,
                    "text": chunk,
                    "embedding": embedding,
                    "source": pdf_path
                }
            )

        # ---------- IMAGE ----------

        if image_path:

            image_embedding = self.image_embedding_model.encode(image_path)[0]

            self.image_index.add(
                image_path,
                image_embedding
            )

        return documents, self.image_index.get_all()


if __name__ == "__main__":

    pipeline = IngestionPipeline()

    documents, images = pipeline.process(
        "sample.pdf",
        "sample.jpg"
    )

    print("\n========== TEXT ==========")

    print(f"Total Chunks: {len(documents)}")

    print(
        f"Embedding Dimension: "
        f"{len(documents[0]['embedding'])}"
    )

    print("\n========== IMAGE ==========")

    print(f"Indexed Images: {len(images)}")

    if images:

        print("Image:", images[0]["image_path"])

        print(
            "Image Embedding Dimension:",
            len(images[0]["embedding"])
        )