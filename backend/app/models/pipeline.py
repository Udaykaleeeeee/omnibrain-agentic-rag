from backend.app.ingestion.pdf_loader import PDFLoader
from backend.app.models.chunking import TextChunker
from backend.app.models.embeddings import TextEmbeddingModel


class IngestionPipeline:
    """
    Complete document ingestion pipeline.
    """

    def __init__(self):
        self.loader = PDFLoader()
        self.chunker = TextChunker()
        self.embedding_model = TextEmbeddingModel()

    def process(self, pdf_path: str):
        """
        Load PDF, split into chunks and generate embeddings.
        """

        # Load PDF
        text = self.loader.load(pdf_path)

        # Split into chunks
        chunks = self.chunker.split_text(text)

        # Generate embeddings for all chunks
        embeddings = self.embedding_model.encode(chunks)

        return chunks, embeddings


if __name__ == "__main__":

    pipeline = IngestionPipeline()

    chunks, embeddings = pipeline.process("sample.pdf")

    print(f"\nTotal Chunks: {len(chunks)}")
    print(f"Total Embeddings: {len(embeddings)}")

    if embeddings:
        print(f"Embedding Dimension: {len(embeddings[0])}")

    for i, chunk in enumerate(chunks, start=1):
        print(f"\nChunk {i}")
        print("-" * 40)
        print(chunk)