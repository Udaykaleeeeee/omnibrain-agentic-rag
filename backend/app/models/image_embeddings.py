from PIL import Image
import open_clip
import torch
import os
import logging
import io

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ImageEmbeddingModel:
    """
    Generate image and text embeddings using OpenCLIP.

    Supports:
    - image file paths
    - PIL Images
    - image bytes
    - list/tuple of the above
    - text queries for image similarity retrieval
    """

    def __init__(
        self,
        model_name="ViT-B-32",
        pretrained="laion2b_s34b_b79k",
    ):
        logger.info("Loading OpenCLIP model...")

        self.model_name = model_name
        self.pretrained = pretrained

        self.device = (
            "cuda"
            if torch.cuda.is_available()
            else "cpu"
        )

        self.model, _, self.preprocess = (
            open_clip.create_model_and_transforms(
                model_name,
                pretrained=pretrained,
            )
        )

        self.model.to(self.device)
        self.model.eval()

        logger.info(
            f"OpenCLIP model loaded successfully: "
            f"{self.model_name}"
        )

    def get_embedding_dimension(self):
        """
        Return the dimensionality of the image embedding.
        """
        return self.model.visual.output_dim

    def _load_image(self, image):
        """
        Convert different image input types into a PIL Image.

        Supported:
        - PIL Image
        - bytes
        - file path
        """

        # PIL Image
        if isinstance(image, Image.Image):
            return image.convert("RGB")

        # Image bytes
        if isinstance(image, bytes):
            try:
                return Image.open(
                    io.BytesIO(image)
                ).convert("RGB")
            except Exception as e:
                raise ValueError(
                    f"Invalid image bytes: {e}"
                ) from e

        # File path
        if isinstance(image, (str, os.PathLike)):
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
                    f"Could not open image '{image_path}': {e}"
                ) from e

        raise TypeError(
            "Unsupported image input type: "
            f"{type(image)}. Expected a file path, "
            "PIL Image, or image bytes."
        )

    def _encode_single(self, image):
        """
        Generate an embedding for a single image.
        """

        try:
            pil_image = self._load_image(image)

            processed_image = (
                self.preprocess(pil_image)
                .unsqueeze(0)
                .to(self.device)
            )

            with torch.no_grad():
                embedding = self.model.encode_image(
                    processed_image
                )

            # L2 normalize embedding
            embedding = embedding / embedding.norm(
                dim=-1,
                keepdim=True,
            )

            return embedding.cpu().numpy()[0].tolist()

        except Exception as e:
            raise RuntimeError(
                f"Failed to generate image embedding: {e}"
            ) from e

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

        # Single image
        if isinstance(
            images,
            (str, os.PathLike, bytes, Image.Image),
        ):
            return [
                self._encode_single(images)
            ]

        # Multiple images
        if isinstance(images, (list, tuple)):
            return [
                self._encode_single(image)
                for image in images
            ]

        raise TypeError(
            "images must be a file path, PIL Image, "
            "bytes, list, or tuple."
        )

    def encode_text(self, texts):
        """
        Generate OpenCLIP text embeddings for image similarity retrieval.

        The generated text embeddings are normalized and share
        the same embedding space as the image embeddings.

        Args:
            texts:
                A single text query or a list/tuple of text queries.

        Returns:
            List of normalized text embedding vectors.
        """

        # Convert single text query into a list
        if isinstance(texts, str):
            texts = [texts]

        if not isinstance(texts, (list, tuple)):
            raise TypeError(
                "texts must be a string, list, or tuple."
            )

        if not texts:
            return []

        # Validate that all inputs are strings
        if not all(isinstance(text, str) for text in texts):
            raise TypeError(
                "All text queries must be strings."
            )

        try:
            # OpenCLIP tokenizer
            tokenizer = open_clip.get_tokenizer(
                self.model_name
            )

            # Tokenize text queries
            tokens = tokenizer(
                list(texts)
            ).to(self.device)

            # Generate text embeddings
            with torch.no_grad():
                embeddings = self.model.encode_text(
                    tokens
                )

            # L2 normalize embeddings
            embeddings = embeddings / embeddings.norm(
                dim=-1,
                keepdim=True,
            )

            return embeddings.cpu().numpy().tolist()

        except Exception as e:
            raise RuntimeError(
                f"Failed to generate text embedding: {e}"
            ) from e


if __name__ == "__main__":
    model = ImageEmbeddingModel()

    # Test image embedding
    image_path = "sample.jpg"

    vectors = model.encode(image_path)

    logger.info(
        f"Model: {model.model_name}"
    )

    logger.info(
        f"Image embedding dimension: {len(vectors[0])}"
    )

    # Test text embedding
    text_vectors = model.encode_text(
        "financial revenue chart"
    )

    logger.info(
        f"Text embedding dimension: {len(text_vectors[0])}"
    )