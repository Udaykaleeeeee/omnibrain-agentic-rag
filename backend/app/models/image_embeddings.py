from PIL import Image
import open_clip
import torch
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ImageEmbeddingModel:
    """
    Generate image embeddings using OpenCLIP.
    """

    def __init__(self, model_name="ViT-B-32", pretrained="laion2b_s34b_b79k"):
        logger.info("Loading OpenCLIP model...")

        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        self.model, _, self.preprocess = open_clip.create_model_and_transforms(
            model_name,
            pretrained=pretrained
        )

        self.model.to(self.device)
        self.model.eval()

        logger.info("OpenCLIP model loaded successfully!")

    def encode(self, image_path):
        """
        Generate embedding from an image.
        """

        if not os.path.exists(image_path):
            raise FileNotFoundError(
                f"Image file '{image_path}' not found."
            )

        try:
            image = self.preprocess(
                Image.open(image_path)
            ).unsqueeze(0).to(self.device)

            with torch.no_grad():
                embedding = self.model.encode_image(image)

            embedding = embedding / embedding.norm(dim=-1, keepdim=True)

            return embedding.cpu().numpy().tolist()

        except Exception as e:
            raise RuntimeError(
                f"Failed to generate image embedding: {e}"
            )


if __name__ == "__main__":

    model = ImageEmbeddingModel()

    image_path = "sample.jpg"

    vector = model.encode(image_path)

    logger.info(f"Embedding dimension: {len(vector[0])}")