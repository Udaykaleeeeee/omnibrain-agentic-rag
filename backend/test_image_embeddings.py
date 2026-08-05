"""
Test script for image embeddings functionality.
Run with: python test_image_embeddings.py
"""
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.models.image_embeddings import ImageEmbeddingModel
from PIL import Image
import io

def test_image_embedding_model():
    """Test the ImageEmbeddingModel class."""
    print("\n" + "="*60)
    print("Testing Image Embedding Model")
    print("="*60)
    
    try:
        # Initialize model
        print("\n1. Loading CLIP model...")
        model = ImageEmbeddingModel()
        print(f"   ✓ Model loaded: {model.model_name}")
        print(f"   ✓ Embedding dimension: {model.get_embedding_dimension()}")
        
        # Create test images
        print("\n2. Creating test images...")
        test_images = [
            Image.new('RGB', (224, 224), color='red'),
            Image.new('RGB', (224, 224), color='blue'),
            Image.new('RGB', (224, 224), color='green'),
        ]
        print(f"   ✓ Created {len(test_images)} test images")
        
        # Convert one to bytes to test different input types
        img_bytes = io.BytesIO()
        test_images[0].save(img_bytes, format='PNG')
        test_images_mixed = [img_bytes.getvalue(), test_images[1], test_images[2]]
        
        # Generate embeddings
        print("\n3. Generating embeddings...")
        embeddings = model.encode(test_images_mixed)
        print(f"   ✓ Generated {len(embeddings)} embeddings")
        print(f"   ✓ Each embedding has {len(embeddings[0])} dimensions")
        
        # Verify embeddings
        print("\n4. Verifying embeddings...")
        for idx, emb in enumerate(embeddings):
            print(f"   Image {idx+1}: {emb[:5]}... (showing first 5 values)")
        
        print("\n" + "="*60)
        print("✓ ALL TESTS PASSED")
        print("="*60 + "\n")
        return True
        
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_pipeline_integration():
    """Test that pipeline can initialize with image embeddings."""
    print("\n" + "="*60)
    print("Testing Pipeline Integration")
    print("="*60)
    
    try:
        from app.ingestion.pipeline import IngestionPipeline
        
        print("\n1. Initializing pipeline with image embeddings enabled...")
        pipeline = IngestionPipeline(enable_image_embeddings=True)
        print(f"   ✓ Pipeline initialized")
        print(f"   ✓ Image embeddings enabled: {pipeline.enable_image_embeddings}")
        print(f"   ✓ Image embedding model: {pipeline.image_embedding_model is not None}")
        
        print("\n2. Initializing pipeline with image embeddings disabled...")
        pipeline_no_img = IngestionPipeline(enable_image_embeddings=False)
        print(f"   ✓ Pipeline initialized")
        print(f"   ✓ Image embeddings enabled: {pipeline_no_img.enable_image_embeddings}")
        print(f"   ✓ Image embedding model: {pipeline_no_img.image_embedding_model is not None}")
        
        print("\n" + "="*60)
        print("✓ PIPELINE INTEGRATION TESTS PASSED")
        print("="*60 + "\n")
        return True
        
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n" + "="*60)
    print("IMAGE EMBEDDINGS TEST SUITE")
    print("="*60)
    
    success = True
    
    # Test 1: Image Embedding Model
    if not test_image_embedding_model():
        success = False
    
    # Test 2: Pipeline Integration
    if not test_pipeline_integration():
        success = False
    
    # Summary
    print("\n" + "="*60)
    if success:
        print("✓✓✓ ALL TESTS PASSED ✓✓✓")
    else:
        print("✗✗✗ SOME TESTS FAILED ✗✗✗")
    print("="*60 + "\n")
    
    sys.exit(0 if success else 1)
