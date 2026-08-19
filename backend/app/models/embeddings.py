"""
Lightweight Text Embedding Model for OmniBrain.

Uses Qdrant FastEmbed with BAAI/bge-small-en-v1.5.
FastEmbed uses ONNX instead of the heavier
SentenceTransformers/PyTorch stack.
"""

import logging
from typing import List

logger = logging.getLogger(__name__)


class TextEmbeddingModel:
    """
    Lightweight wrapper around FastEmbed.

    The model is lazy-loaded only when encode()
    is called for the first time.
    """

    def __init__(
        self,
        model_name: str = "BAAI/bge-small-en-v1.5",
        embedding_dimension: int = 384,
    ):
        self.model_name = model_name
        self.embedding_dimension = embedding_dimension

        self.model = None
        self._model_loaded = False

        logger.info(
            "TextEmbeddingModel initialized. "
            "FastEmbed will load only when required."
        )

    def _ensure_model_loaded(self):
        """
        Lazy-load FastEmbed model.
        """

        if self._model_loaded:
            return

        logger.info(
            f"Loading FastEmbed model on demand: "
            f"{self.model_name}"
        )

        try:
            from fastembed import TextEmbedding

            self.model = TextEmbedding(
                model_name=self.model_name,
                lazy_load=True,
            )

            self._model_loaded = True

            logger.info(
                f"FastEmbed model ready: "
                f"{self.model_name}"
            )

        except Exception as e:
            logger.error(
                f"Failed to initialize FastEmbed: {e}",
                exc_info=True,
            )

            raise RuntimeError(
                f"Unable to initialize text embedding model: {e}"
            ) from e

    def get_embedding_dimension(self) -> int:
        """
        BGE-small-en-v1.5 uses 384-dimensional vectors.
        """

        return self.embedding_dimension

    def encode(
        self,
        texts: List[str],
    ) -> List[List[float]]:
        """
        Generate text embeddings.
        """

        if isinstance(texts, str):
            texts = [texts]

        if not texts:
            return []

        if not isinstance(texts, (list, tuple)):
            raise TypeError(
                "texts must be a string, list, or tuple."
            )

        if not all(
            isinstance(text, str)
            for text in texts
        ):
            raise TypeError(
                "All text inputs must be strings."
            )

        self._ensure_model_loaded()

        try:
            embeddings = list(
                self.model.embed(
                    list(texts),
                    batch_size=4,
                    parallel=None,
                )
            )

            vectors = []

            for embedding in embeddings:
                vector = embedding.tolist()

                # Normalize vector
                norm = sum(
                    value * value
                    for value in vector
                ) ** 0.5

                if norm > 0:
                    vector = [
                        value / norm
                        for value in vector
                    ]

                vectors.append(vector)

            return vectors

        except Exception as e:
            logger.error(
                f"Text embedding generation failed: {e}",
                exc_info=True,
            )

            raise RuntimeError(
                f"Failed to generate text embeddings: {e}"
            ) from e


if __name__ == "__main__":

    model = TextEmbeddingModel()

    sample = [
        "Artificial Intelligence is transforming industries.",
        "Large Language Models are changing software development.",
    ]

    vectors = model.encode(sample)

    print("Number of embeddings:", len(vectors))
    print("Embedding dimension:", len(vectors[0]))