from typing import List

from sentence_transformers import SentenceTransformer


class TextEmbeddingModel:
    """
    Wrapper around SentenceTransformer for generating text embeddings.
    """

    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5"):
        self.model_name = model_name
        print(f"Loading model: {model_name}...")
        self.model = SentenceTransformer(model_name)
        print("Model loaded successfully!")

    def encode(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of text chunks.

        Args:
            texts: List of strings

        Returns:
            List of embedding vectors
        """

        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True
        )

        return embeddings.tolist()
if __name__ == "__main__":

    model = TextEmbeddingModel()

    sample = [
        "Artificial Intelligence is transforming industries.",
        "Large Language Models are changing software development."
    ]

    vectors = model.encode(sample)

    print("Number of embeddings:", len(vectors))
    print("Embedding dimension:", len(vectors[0]))