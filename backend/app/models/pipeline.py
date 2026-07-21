from backend.app.ingestion.pdf_loader import PDFLoader
from backend.app.models.chunking import TextChunker


class IngestionPipeline:
    """
    Complete document ingestion pipeline.
    """

    def __init__(self):
        self.loader = PDFLoader()
        self.chunker = TextChunker()

    def process(self, pdf_path: str):
        """
        Load PDF and split it into chunks.
        """

        text = self.loader.load(pdf_path)

        chunks = self.chunker.split_text(text)

        return chunks


if __name__ == "__main__":

    pipeline = IngestionPipeline()

    chunks = pipeline.process("sample.pdf")

    print(f"Total Chunks: {len(chunks)}")

    for i, chunk in enumerate(chunks, start=1):
        print(f"\nChunk {i}")
        print("-" * 40)
        print(chunk)