"""
Unit tests for QdrantService, CitationEngine, and RetrievalService (Member 3 - Vector DB & Retrieval)
"""

from backend.app.vector_db.qdrant_client import QdrantService
from backend.app.vector_db.citation import CitationEngine
from backend.app.vector_db.retrieval import RetrievalService
from backend.app.models.embeddings import TextEmbeddingModel



def test_qdrant_service_in_memory():
    """Test QdrantService in-memory initialization and vector upsert/search."""
    qdrant = QdrantService(location=":memory:")
    assert qdrant.client is not None
    assert qdrant.count_vectors() == 0

    # Create dummy chunks and embeddings
    document_id = "doc-123-abc"
    chunks = [
        {
            "text": "Artificial Intelligence and Machine Learning transform software.",
            "page_number": 1,
            "chunk_index": 0,
            "filename": "ai_report.pdf",
            "source_format": "pdf",
            "is_ocr": False,
        },
        {
            "text": "Vector databases like Qdrant provide fast similarity retrieval.",
            "page_number": 2,
            "chunk_index": 1,
            "filename": "ai_report.pdf",
            "source_format": "pdf",
            "is_ocr": False,
        },
    ]

    # Generate real embeddings (dim 384)
    model = TextEmbeddingModel()
    embeddings = model.encode([c["text"] for c in chunks])

    # Upsert
    qdrant.upsert_vectors(document_id, chunks, embeddings)
    assert qdrant.count_vectors() == 2

    # Search
    query_vector = model.encode(["Qdrant vector similarity"])[0]
    hits = qdrant.search(query_vector=query_vector, limit=2)
    assert len(hits) > 0
    assert hits[0].payload["filename"] == "ai_report.pdf"


def test_citation_engine():
    """Test CitationEngine tag and RAG context building."""
    hit_payload = {
        "filename": "sample_doc.pdf",
        "page_number": 3,
        "chunk_index": 2,
        "document_id": "doc-999",
        "text": "This chunk describes semantic retrieval performance.",
        "source_format": "pdf",
    }
    dummy_hit = {"payload": hit_payload, "score": 0.9123}

    formatted = CitationEngine.format_hit(dummy_hit, index=1)
    assert formatted["citation_index"] == 1
    assert formatted["filename"] == "sample_doc.pdf"
    assert formatted["page_number"] == 3
    assert formatted["chunk_index"] == 2
    assert formatted["score"] == 0.9123
    assert "[Ref 1: sample_doc.pdf, Page 3, Chunk 2]" in formatted["citation_tag"]

    rag_context, citations = CitationEngine.build_rag_context([dummy_hit])
    assert "Citation [Ref 1: sample_doc.pdf, Page 3, Chunk 2]" in rag_context
    assert len(citations) == 1


def test_retrieval_service_clean_interface():
    """Test RetrievalService retrieve() clean interface requested by Member 6."""
    qdrant = QdrantService(location=":memory:")
    embed_model = TextEmbeddingModel()
    retrieval = RetrievalService(vector_db=qdrant, embedding_model=embed_model)

    doc_id = "doc-finance-2026"
    chunks = [
        {
            "text": "The quarterly revenue grew by 25% year over year.",
            "page_number": 4,
            "chunk_index": 0,
            "filename": "financial_report.pdf",
            "source_format": "pdf",
            "is_ocr": False,
        },
        {
            "text": "Operational costs decreased due to automation and cloud optimization.",
            "page_number": 5,
            "chunk_index": 1,
            "filename": "financial_report.pdf",
            "source_format": "pdf",
            "is_ocr": False,
        },
    ]
    embeddings = embed_model.encode([c["text"] for c in chunks])
    qdrant.upsert_vectors(doc_id, chunks, embeddings)

    # Execute retrieve()
    response = retrieval.retrieve(query="quarterly revenue growth", top_k=2)

    assert response["query"] == "quarterly revenue growth"
    assert response["total_results"] == 2
    assert len(response["chunks"]) == 2

    top_chunk = response["chunks"][0]
    # Verify exact metadata fields requested by Member 6
    assert "document_name" in top_chunk
    assert top_chunk["document_name"] == "financial_report.pdf"
    assert "page_number" in top_chunk
    assert top_chunk["page_number"] in [4, 5]
    assert "chunk_number" in top_chunk
    assert "similarity_score" in top_chunk
    assert isinstance(top_chunk["similarity_score"], float)
    assert top_chunk["similarity_score"] > 0.0

    # Verify RAG context and citations
    assert "rag_context" in response
    assert len(response["citations"]) == 2
    logger.info("Retrieval Service clean interface test passed successfully!")


def test_retrieval_service_metadata_filtering():
    """Test metadata filtering in RetrievalService."""
    qdrant = QdrantService(location=":memory:")
    embed_model = TextEmbeddingModel()
    retrieval = RetrievalService(vector_db=qdrant, embedding_model=embed_model)

    # Ingest chunks from two different files
    chunks1 = [
        {
            "text": "Deep learning architectures for vision tasks.",
            "page_number": 1,
            "chunk_index": 0,
            "filename": "vision.pdf",
            "source_format": "pdf",
            "is_ocr": False,
        }
    ]
    chunks2 = [
        {
            "text": "Deep learning architectures for text generation.",
            "page_number": 1,
            "chunk_index": 0,
            "filename": "nlp.docx",
            "source_format": "docx",
            "is_ocr": False,
        }
    ]

    qdrant.upsert_vectors("doc-1", chunks1, embed_model.encode([chunks1[0]["text"]]))
    qdrant.upsert_vectors("doc-2", chunks2, embed_model.encode([chunks2[0]["text"]]))

    # Search with document_id filter
    res = retrieval.retrieve(query="deep learning architectures", document_id="doc-1")
    assert res["total_results"] == 1
    assert res["chunks"][0]["document_id"] == "doc-1"
    assert res["chunks"][0]["filename"] == "vision.pdf"

    # Search with source_format filter
    res_docx = retrieval.retrieve(query="deep learning architectures", source_format="docx")
    assert res_docx["total_results"] == 1
    assert res_docx["chunks"][0]["filename"] == "nlp.docx"


if __name__ == "__main__":
    print("Running Vector DB & Retrieval Pipeline Tests...")
    test_qdrant_service_in_memory()
    print("✓ test_qdrant_service_in_memory passed")
    test_citation_engine()
    print("✓ test_citation_engine passed")
    test_retrieval_service_clean_interface()
    print("✓ test_retrieval_service_clean_interface passed")
    test_retrieval_service_metadata_filtering()
    print("✓ test_retrieval_service_metadata_filtering passed")
    print("\nAll 4 tests completed successfully!")

