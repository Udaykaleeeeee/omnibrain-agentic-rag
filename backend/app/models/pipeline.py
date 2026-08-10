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
        Load PDF, split into chunks, generate embeddings,
        and return metadata for each chunk.
        """

        # Load PDF
        text = self.loader.load(pdf_path)

        # Split into chunks
        chunks = self.chunker.split_text(text)

        # Generate embeddings
        embeddings = self.embedding_model.encode(chunks)

        # Create metadata
        documents = []

        for i, (chunk, embedding) in enumerate(
            zip(chunks, embeddings), start=1
        ):
            documents.append(
                {
                    "chunk_id": i,
                    "text": chunk,
                    "embedding": embedding,
                    "source": pdf_path
                }
            )

        return documents


if __name__ == "__main__":

    pipeline = IngestionPipeline()

    documents = pipeline.process("sample.pdf")

    print(f"\nTotal Chunks: {len(documents)}")

    if documents:
        print(
            f"Embedding Dimension: "
            f"{len(documents[0]['embedding'])}"
        )

    for doc in documents:

        print(f"\nChunk {doc['chunk_id']}")
        print("-" * 50)
        print(doc["text"])

        print("\nMetadata")
        print(f"Source : {doc['source']}")
        print(f"Chunk ID : {doc['chunk_id']}")