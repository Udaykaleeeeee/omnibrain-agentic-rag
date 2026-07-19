from typing import List


class TextChunker:
    """
    Splits large text into smaller overlapping chunks.
    """

    def __init__(self, chunk_size: int = 500, overlap: int = 100):
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
