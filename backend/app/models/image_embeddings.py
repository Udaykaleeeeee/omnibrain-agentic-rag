"""
Image Embedding Model

Generates image and text embeddings using OpenCLIP.

Heavy OpenCLIP/PyTorch dependencies are lazy-loaded.
Image embeddings can also be disabled on low-memory
cloud deployments using:

DISABLE_IMAGE_EMBEDDINGS=true
"""

import io
import logging
import os

from PIL import Image


logger = logging.getLogger(__name__)


class ImageEmbeddingModel:
    """
    Generate image and text embeddings using OpenCLIP.

    Supports:
    - image file paths
    - PIL Images
    - image bytes
    - list/tuple of images
    - text queries for image similarity retrieval
    """

    def __init__(
        self,
        model_name="ViT-B-32",
        pretrained="laion2b_s34b_b79k",
        embedding_dimension=512,
    ):
        self.model_name = model_name
        self.pretrained = pretrained
        self.embedding_dimension = embedding_dimension

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

    # ========================================================
    # CHECK IF IMAGE EMBEDDINGS ARE DISABLED
    # ========================================================

    def _disabled(self):
        return (
            os.getenv(
                "DISABLE_IMAGE_EMBEDDINGS",
                "false",
            ).lower()
            == "true"
        )

    # ========================================================
    # LAZY MODEL LOADING
    # ========================================================

    def _ensure_model_loaded(self):
        """
        Load PyTorch and OpenCLIP only when required.
        """

        if self._disabled():
            logger.warning(
                "Image embeddings are disabled "
                "for low-memory deployment."
            )
            return

        if self._model_loaded:
            return

        logger.info(
            "Loading OpenCLIP model on demand..."
        )

        try:
            import torch
            import open_clip

            self.torch = torch
            self.open_clip = open_clip

            self.device = (
                "cuda"
                if self.torch.cuda.is_available()
                else "cpu"
            )

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

            if (
                hasattr(self.model, "visual")
                and hasattr(
                    self.model.visual,
                    "output_dim",
                )
            ):
                self.embedding_dimension = (
                    self.model.visual.output_dim
                )

            self._model_loaded = True

            logger.info(
                f"OpenCLIP model loaded successfully: "
                f"{self.model_name}"
            )

        except Exception as e:
            logger.error(
                f"Failed to load OpenCLIP model: {e}",
                exc_info=True,
            )

            raise RuntimeError(
                f"Unable to load OpenCLIP model: {e}"
            ) from e

    # ========================================================
    # EMBEDDING DIMENSION
    # ========================================================

    def get_embedding_dimension(self):
        return self.embedding_dimension

    # ========================================================
    # LOAD IMAGE
    # ========================================================

    def _load_image(self, image):
        """
        Convert supported inputs into a PIL Image.
        """

        if isinstance(image, Image.Image):
            return image.convert("RGB")

        if isinstance(image, bytes):
            try:
                return Image.open(
                    io.BytesIO(image)
                ).convert("RGB")

            except Exception as e:
                raise ValueError(
                    f"Invalid image bytes: {e}"
                ) from e

        if isinstance(
            image,
            (str, os.PathLike),
        ):
            image_path = os.fspath(image)

            if not os.path.exists(image_path):
                raise FileNotFoundError(
                    f"Image file '{image_path}' not found."
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

        raise TypeError(
            "Unsupported image input type. "
            "Expected file path, PIL Image, "
            "or image bytes."
        )

    # ========================================================
    # SINGLE IMAGE EMBEDDING
    # ========================================================

    def _encode_single(self, image):
        """
        Generate embedding for one image.
        """

        self._ensure_model_loaded()

        if self._disabled():
            return None

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

    # ========================================================
    # IMAGE ENCODE
    # ========================================================

    def encode(self, images):
        """
        Generate image embeddings.
        """

        # IMPORTANT FOR RENDER FREE
        if self._disabled():

            logger.warning(
                "Image embedding generation skipped "
                "because DISABLE_IMAGE_EMBEDDINGS=true."
            )

            return []

        if isinstance(
            images,
            (
                str,
                os.PathLike,
                bytes,
                Image.Image,
            ),
        ):
            vector = self._encode_single(images)

            return (
                [vector]
                if vector is not None
                else []
            )

        if isinstance(
            images,
            (list, tuple),
        ):
            vectors = []

            for image in images:
                vector = self._encode_single(image)

                if vector is not None:
                    vectors.append(vector)

            return vectors

        raise TypeError(
            "images must be a file path, "
            "PIL Image, bytes, list, or tuple."
        )

    # ========================================================
    # TEXT ENCODE FOR IMAGE SEARCH
    # ========================================================

    def encode_text(self, texts):
        """
        Generate OpenCLIP text embeddings
        for image similarity retrieval.
        """

        # IMPORTANT FOR RENDER FREE
        if self._disabled():

            logger.warning(
                "Image search embedding skipped "
                "because DISABLE_IMAGE_EMBEDDINGS=true."
            )

            return []

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

        self._ensure_model_loaded()

        try:
            tokenizer = (
                self.open_clip.get_tokenizer(
                    self.model_name
                )
            )

            tokens = tokenizer(
                list(texts)
            ).to(self.device)

            with self.torch.no_grad():

                embeddings = (
                    self.model.encode_text(
                        tokens
                    )
                )

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


if __name__ == "__main__":

    model = ImageEmbeddingModel()

    print(
        "Configured image embedding dimension:",
        model.get_embedding_dimension(),
    )