from typing import List, Dict, Optional

from backend.app.models.image_embeddings import ImageEmbeddingModel


class ImageIndex:
    """
    Simple in-memory image index for storing image embeddings.
    """

    def __init__(self):
        self.index: List[Dict] = []

    def add(self, image_path: str, embedding: List[float]) -> None:
        """
        Store an image embedding.

        Args:
            image_path: Path of the image.
            embedding: Image embedding vector.
        """
        self.index.append(
            {
                "image_path": image_path,
                "embedding": embedding
            }
        )

    def get_all(self) -> List[Dict]:
        """
        Return all indexed images.
        """
        return self.index

    def count(self) -> int:
        """
        Return total number of indexed images.
        """
        return len(self.index)

    def find_by_path(self, image_path: str) -> Optional[Dict]:
        """
        Find an indexed image by its path.

        Args:
            image_path: Image file path.

        Returns:
            Image metadata if found, otherwise None.
        """
        for item in self.index:
            if item["image_path"] == image_path:
                return item
        return None


if __name__ == "__main__":

    # Load OpenCLIP model
    model = ImageEmbeddingModel()

    # Create image index
    index = ImageIndex()

    # Generate embedding for sample image
    embedding = model.encode("sample.jpg")[0]

    # Store image embedding
    index.add("sample.jpg", embedding)

    # Print summary
    print(f"Total Images: {index.count()}")

    result = index.find_by_path("sample.jpg")

    if result:
        print(f"Image: {result['image_path']}")
        print(f"Embedding Dimension: {len(result['embedding'])}")
    else:
        print("Image not found in index.")