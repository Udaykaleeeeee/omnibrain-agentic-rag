from typing import List


class TextChunker:
    """
    Splits large text into smaller overlapping chunks.
    """

    def __init__(self, chunk_size: int = 1000, overlap: int = 200):
        """
        Initialize the chunker.

        Args:
            chunk_size: Maximum characters per chunk
            overlap: Number of overlapping characters
        """

        if overlap >= chunk_size:
            raise ValueError("overlap must be smaller than chunk_size")

        self.chunk_size = chunk_size
        self.overlap = overlap

    def split_text(self, text: str) -> List[str]:
        """
        Split text into overlapping chunks.

        Args:
            text (str): Input text.

        Returns:
            List[str]: List of text chunks.
        """

        if not text.strip():
            return []

        chunks = []

        start = 0
        text_length = len(text)

        while start < text_length:
            end = start + self.chunk_size

            chunk = text[start:end].strip()

            if chunk:
                chunks.append(chunk)

            start += self.chunk_size - self.overlap

        return chunks


if __name__ == "__main__":

    sample_text = (
        "Artificial Intelligence is transforming industries. " * 10
    )

    chunker = TextChunker(chunk_size=100, overlap=20)

    chunks = chunker.split_text(sample_text)

    print(f"Total Chunks: {len(chunks)}")

    for i, chunk in enumerate(chunks, start=1):
        print(f"\nChunk {i}")
        print(chunk)