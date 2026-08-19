"""
Image Embedding Model

Generates image and text embeddings using OpenCLIP.

Important:
The heavy OpenCLIP and PyTorch libraries are lazy-loaded.
This helps reduce memory usage during FastAPI startup,
especially on low-memory deployment environments.
"""

import io
import logging
import os

from PIL import Image


# ------------------------------------------------------------
# Logging
# ------------------------------------------------------------

logger = logging.getLogger(__name__)


# ------------------------------------------------------------
# IMAGE EMBEDDING MODEL
# ------------------------------------------------------------

class ImageEmbeddingModel:
    """
    Generate image and text embeddings using OpenCLIP.

    Supports:
    - image file paths
    - PIL Images
    - image bytes
    - lists/tuples of images
    - text queries for image similarity retrieval

    OpenCLIP and PyTorch are loaded only when an embedding
    operation is actually requested.
    """

    def __init__(
        self,
        model_name="ViT-B-32",
        pretrained="laion2b_s34b_b79k",
        embedding_dimension=512,
    ):
        # ----------------------------------------------------
        # Model configuration
        # ----------------------------------------------------

        self.model_name = model_name
        self.pretrained = pretrained
        self.embedding_dimension = embedding_dimension

        # ----------------------------------------------------
        # Lazy-loaded objects
        # ----------------------------------------------------

        self.model = None
        self.preprocess = None
        self.device = None

        self.torch = None
        self.open_clip = None

        self._model_loaded = False

        logger.info(
            "ImageEmbeddingModel initialized. "
            "OpenCLIP will load only when required."
        )

    # --------------------------------------------------------
    # LAZY MODEL LOADING
    # --------------------------------------------------------

    def _ensure_model_loaded(self):
        """
        Load PyTorch and OpenCLIP only when image/text
        embedding functionality is actually used.
        """

        if self._model_loaded:
            return

        logger.info(
            "Loading OpenCLIP model on demand..."
        )

        try:
            # Heavy imports happen only here
            import torch
            import open_clip

            self.torch = torch
            self.open_clip = open_clip

            # ----------------------------------------------
            # Device
            # ----------------------------------------------

            self.device = (
                "cuda"
                if self.torch.cuda.is_available()
                else "cpu"
            )

            # ----------------------------------------------
            # Load model and preprocessing pipeline
            # ----------------------------------------------

            (
                self.model,
                _,
                self.preprocess,
            ) = self.open_clip.create_model_and_transforms(
                self.model_name,
                pretrained=self.pretrained,
            )

            self.model.to(self.device)
            self.model.eval()

            # ----------------------------------------------
            # Update embedding dimension if available
            # ----------------------------------------------

            if hasattr(self.model, "visual"):
                if hasattr(
                    self.model.visual,
                    "output_dim",
                ):
                    self.embedding_dimension = (
                        self.model.visual.output_dim
                    )

            self._model_loaded = True

            logger.info(
                f"OpenCLIP model loaded successfully: "
                f"{self.model_name} on {self.device}"
            )

        except Exception as e:
            logger.error(
                f"Failed to load OpenCLIP model: {e}",
                exc_info=True,
            )

            raise RuntimeError(
                f"Unable to load OpenCLIP model: {e}"
            ) from e

    # --------------------------------------------------------
    # EMBEDDING DIMENSION
    # --------------------------------------------------------

    def get_embedding_dimension(self):
        """
        Return image embedding dimension.

        ViT-B-32 uses 512-dimensional vectors.
        Returning the configured dimension avoids loading
        the entire model just to obtain this value.
        """

        return self.embedding_dimension

    # --------------------------------------------------------
    # IMAGE LOADING
    # --------------------------------------------------------

    def _load_image(self, image):
        """
        Convert supported image input types into a PIL image.

        Supported:
        - PIL.Image.Image
        - raw bytes
        - file path
        """

        # ----------------------------------------------------
        # PIL Image
        # ----------------------------------------------------

        if isinstance(image, Image.Image):
            return image.convert("RGB")

        # ----------------------------------------------------
        # Raw bytes
        # ----------------------------------------------------

        if isinstance(image, bytes):
            try:
                return Image.open(
                    io.BytesIO(image)
                ).convert("RGB")

            except Exception as e:
                raise ValueError(
                    f"Invalid image bytes: {e}"
                ) from e

        # ----------------------------------------------------
        # File path
        # ----------------------------------------------------

        if isinstance(
            image,
            (str, os.PathLike),
        ):
            image_path = os.fspath(image)

            if not os.path.exists(image_path):
                raise FileNotFoundError(
                    f"Image file "
                    f"'{image_path}' not found."
                )

            try:
                return Image.open(
                    image_path
                ).convert("RGB")

            except Exception as e:
                raise ValueError(
                    f"Could not open image "
                    f"'{image_path}': {e}"
                ) from e

        # ----------------------------------------------------
        # Unsupported input
        # ----------------------------------------------------

        raise TypeError(
            "Unsupported image input type: "
            f"{type(image)}. "
            "Expected a file path, PIL Image, "
            "or image bytes."
        )

    # --------------------------------------------------------
    # SINGLE IMAGE EMBEDDING
    # --------------------------------------------------------

    def _encode_single(self, image):
        """
        Generate an embedding for a single image.
        """

        # Load model only when actually needed
        self._ensure_model_loaded()

        try:
            pil_image = self._load_image(image)

            processed_image = (
                self.preprocess(pil_image)
                .unsqueeze(0)
                .to(self.device)
            )

            with self.torch.no_grad():

                embedding = (
                    self.model.encode_image(
                        processed_image
                    )
                )

            # ------------------------------------------------
            # L2 normalization
            # ------------------------------------------------

            embedding = (
                embedding
                / embedding.norm(
                    dim=-1,
                    keepdim=True,
                )
            )

            return (
                embedding
                .cpu()
                .numpy()[0]
                .tolist()
            )

        except Exception as e:
            raise RuntimeError(
                f"Failed to generate "
                f"image embedding: {e}"
            ) from e

    # --------------------------------------------------------
    # IMAGE EMBEDDING API
    # --------------------------------------------------------

    def encode(self, images):
        """
        Generate image embeddings.

        Accepts:
        - one image path
        - one PIL Image
        - one image as bytes
        - list/tuple of images

        Returns:
        - list of embedding vectors
        """

        # ----------------------------------------------------
        # Single image
        # ----------------------------------------------------

        if isinstance(
            images,
            (
                str,
                os.PathLike,
                bytes,
                Image.Image,
            ),
        ):
            return [
                self._encode_single(images)
            ]

        # ----------------------------------------------------
        # Multiple images
        # ----------------------------------------------------

        if isinstance(
            images,
            (list, tuple),
        ):

            return [
                self._encode_single(image)
                for image in images
            ]

        raise TypeError(
            "images must be a file path, "
            "PIL Image, bytes, list, or tuple."
        )

    # --------------------------------------------------------
    # TEXT EMBEDDINGS FOR IMAGE SEARCH
    # --------------------------------------------------------

    def encode_text(self, texts):
        """
        Generate OpenCLIP text embeddings for
        image similarity retrieval.

        The text embeddings use the same vector space
        as the image embeddings.

        Args:
            texts:
                Single string or list/tuple of strings.

        Returns:
            List of normalized embedding vectors.
        """

        # ----------------------------------------------------
        # Normalize input
        # ----------------------------------------------------

        if isinstance(texts, str):
            texts = [texts]

        if not isinstance(
            texts,
            (list, tuple),
        ):
            raise TypeError(
                "texts must be a string, "
                "list, or tuple."
            )

        if not texts:
            return []

        if not all(
            isinstance(text, str)
            for text in texts
        ):
            raise TypeError(
                "All text queries must be strings."
            )

        # Load model only when text-image search is used
        self._ensure_model_loaded()

        try:
            # ------------------------------------------------
            # Tokenizer
            # ------------------------------------------------

            tokenizer = (
                self.open_clip.get_tokenizer(
                    self.model_name
                )
            )

            tokens = tokenizer(
                list(texts)
            ).to(self.device)

            # ------------------------------------------------
            # Generate embeddings
            # ------------------------------------------------

            with self.torch.no_grad():

                embeddings = (
                    self.model.encode_text(
                        tokens
                    )
                )

            # ------------------------------------------------
            # L2 normalization
            # ------------------------------------------------

            embeddings = (
                embeddings
                / embeddings.norm(
                    dim=-1,
                    keepdim=True,
                )
            )

            return (
                embeddings
                .cpu()
                .numpy()
                .tolist()
            )

        except Exception as e:
            raise RuntimeError(
                f"Failed to generate "
                f"text embedding: {e}"
            ) from e


# ------------------------------------------------------------
# LOCAL TEST
# ------------------------------------------------------------

if __name__ == "__main__":

    model = ImageEmbeddingModel()

    logger.info(
        f"Configured embedding dimension: "
        f"{model.get_embedding_dimension()}"
    )

    # Uncomment for local testing:
    #
    # image_path = "sample.jpg"
    #
    # vectors = model.encode(image_path)
    #
    # logger.info(
    #     f"Image embedding dimension: "
    #     f"{len(vectors[0])}"
    # )
    #
    # text_vectors = model.encode_text(
    #     "financial revenue chart"
    # )
    #
    # logger.info(
    #     f"Text embedding dimension: "
    #     f"{len(text_vectors[0])}"
    # )