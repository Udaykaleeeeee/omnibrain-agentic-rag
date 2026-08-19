"""
Text Embedding Model

Generates semantic text embeddings using
BAAI/bge-small-en-v1.5.

The SentenceTransformer model is lazy-loaded so that
FastAPI can start without immediately loading the heavy
PyTorch/Transformers stack.
"""

import logging
from typing import List


logger = logging.getLogger(__name__)


class TextEmbeddingModel:
    """
    Wrapper around SentenceTransformer for generating
    normalized text embeddings.

    The actual model is loaded only when encode()
    is called for the first time.
    """

    def __init__(
        self,
        model_name: str = "BAAI/bge-small-en-v1.5",
        embedding_dimension: int = 384,
    ):
        self.model_name = model_name
        self.embedding_dimension = embedding_dimension

        # Model is NOT loaded during FastAPI startup
        self.model = None
        self._model_loaded = False

        logger.info(
            "TextEmbeddingModel initialized. "
            "BGE model will load only when required."
        )

    # --------------------------------------------------------
    # LAZY MODEL LOADING
    # --------------------------------------------------------

    def _ensure_model_loaded(self):
        """
        Load SentenceTransformer only when embeddings
        are actually requested.
        """

        if self._model_loaded:
            return

        logger.info(
            f"Loading text embedding model on demand: "
            f"{self.model_name}"
        )

        try:
            # Heavy dependency imported only when required
            from sentence_transformers import SentenceTransformer

            self.model = SentenceTransformer(
                self.model_name
            )

            self._model_loaded = True

            logger.info(
                f"Text embedding model loaded successfully: "
                f"{self.model_name}"
            )

        except Exception as e:
            logger.error(
                f"Failed to load text embedding model: {e}",
                exc_info=True,
            )

            raise RuntimeError(
                f"Unable to load text embedding model: {e}"
            ) from e

    # --------------------------------------------------------
    # EMBEDDING DIMENSION
    # --------------------------------------------------------

    def get_embedding_dimension(self) -> int:
        """
        Return configured embedding dimension without
        loading the full model.

        BAAI/bge-small-en-v1.5 produces 384-dimensional
        vectors.
        """

        return self.embedding_dimension

    # --------------------------------------------------------
    # TEXT ENCODING
    # --------------------------------------------------------

    def encode(
        self,
        texts: List[str],
    ) -> List[List[float]]:
        """
        Generate normalized embeddings for text.

        Args:
            texts:
                List of text strings.

        Returns:
            List of embedding vectors.
        """

        if not texts:
            return []

        if isinstance(texts, str):
            texts = [texts]

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

        # Load BGE only when embedding is actually needed
        self._ensure_model_loaded()

        try:
            embeddings = self.model.encode(
                list(texts),
                batch_size=16,
                show_progress_bar=False,
                normalize_embeddings=True,
            )

            return embeddings.tolist()

        except Exception as e:
            logger.error(
                f"Failed to generate text embeddings: {e}",
                exc_info=True,
            )

            raise RuntimeError(
                f"Failed to generate text embeddings: {e}"
            ) from e


# ------------------------------------------------------------
# LOCAL TEST
# ------------------------------------------------------------

if __name__ == "__main__":

    model = TextEmbeddingModel()

    sample = [
        "Artificial Intelligence is transforming industries.",
        "Large Language Models are changing software development.",
    ]

    vectors = model.encode(sample)

    print(
        "Number of embeddings:",
        len(vectors),
    )

    print(
        "Embedding dimension:",
        len(vectors[0]),
    )