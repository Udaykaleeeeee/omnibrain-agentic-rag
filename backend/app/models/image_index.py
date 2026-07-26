from typing import List, Dict

from backend.app.models.image_embeddings import ImageEmbeddingModel


class ImageIndex:
    """
    Simple in-memory image index for storing image embeddings.
    """

    def __init__(self):
        self.index: List[Dict] = []

    def add(self, image_path: str, embedding: List[float]):
        """
        Store an image embedding.
        """
        self.index.append({
            "image_path": image_path,
            "embedding": embedding
        })

    def get_all(self):
        """
        Return all indexed images.
        """
        return self.index

    def count(self):
        """
        Return total number of indexed images.
        """
        return len(self.index)

    def find_by_path(self, image_path: str):
        """
        Find an indexed image by its path.
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

    # Add to index
    index.add("sample.jpg", embedding)

    print("Total Images:", index.count())

    result = index.find_by_path("sample.jpg")

    print("Image:", result["image_path"])
    print("Embedding Dimension:", len(result["embedding"]))