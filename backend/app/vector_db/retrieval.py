"""
Retrieval Service & Pipeline
Handles Semantic Search, Top-K Retrieval, Metadata Filtering, Hybrid Search (RRF),
and Citation Generation.
"""

import math
import logging
from typing import List, Dict, Any, Optional, Union

from .qdrant_client import QdrantService
from .citation import CitationEngine
from ..models.embeddings import TextEmbeddingModel

logger = logging.getLogger(__name__)


class RetrievalService:
    """
    High-level Retrieval Service exposing clean search interfaces for downstream RAG and AI Agents.
    """

    def __init__(
        self,
        vector_db: Optional[QdrantService] = None,
        embedding_model: Optional[TextEmbeddingModel] = None,
    ):
        self._vector_db = vector_db
        self._embedding_model = embedding_model

    @property
    def vector_db(self) -> QdrantService:
        if self._vector_db is None:
            self._vector_db = QdrantService()
        return self._vector_db

    @property
    def embedding_model(self) -> TextEmbeddingModel:
        if self._embedding_model is None:
            self._embedding_model = TextEmbeddingModel()
        return self._embedding_model

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        score_threshold: Optional[float] = None,
        document_id: Optional[Union[str, List[str]]] = None,
        filename: Optional[str] = None,
        source_format: Optional[str] = None,
        page_number: Optional[Union[int, List[int]]] = None,
        is_ocr: Optional[bool] = None,
        enable_hybrid: bool = True,
        rrf_k: int = 60,
    ) -> Dict[str, Any]:
        """
        Main retrieval interface requested by Member 6 and RAG pipeline.

        Args:
            query: User search text query.
            top_k: Number of top relevant chunks to retrieve.
            score_threshold: Minimum similarity score cutoff (0.0 to 1.0).
            document_id: Filter by specific document ID or list of IDs.
            filename: Filter by document filename.
            source_format: Filter by file format (e.g. 'pdf', 'docx', 'txt').
            page_number: Filter by specific page number or list of pages.
            is_ocr: Filter by OCR status.
            enable_hybrid: Whether to perform Hybrid Search (Dense + Keyword RRF).
            rrf_k: Reciprocal Rank Fusion constant parameter (default 60).

        Returns:
            Dict containing:
                - query (str)
                - total_results (int)
                - chunks (List[Dict]) with document_name, page_number, chunk_number, similarity_score, etc.
                - rag_context (str) formatted prompt block for LLM
                - citations (List[Dict])
        """
        if not query or not query.strip():
            logger.warning("Empty query passed to RetrievalService.retrieve")
            return {
                "query": query,
                "total_results": 0,
                "chunks": [],
                "rag_context": "",
                "citations": [],
            }

        # Step 1: Generate Query Vector
        logger.info(f"Generating embedding for retrieval query: '{query}'")
        query_vectors = self.embedding_model.encode([query])
        query_embedding = query_vectors[0]

        # Step 2: Dense Vector Search in Qdrant
        # We fetch extra candidates if hybrid search is enabled
        fetch_limit = top_k * 3 if enable_hybrid else top_k

        dense_hits = self.vector_db.search(
            query_embedding=query_embedding,
            limit=fetch_limit,
            score_threshold=score_threshold,
            document_ids=document_id,
            filename=filename,
            source_format=source_format,
            page_number=page_number,
            is_ocr=is_ocr,
        )

        final_hits = dense_hits

        # Step 3: Hybrid Search (Reciprocal Rank Fusion with Keyword Match)
        if enable_hybrid and dense_hits:
            final_hits = self._apply_hybrid_rrf(
                query=query,
                dense_hits=dense_hits,
                top_k=top_k,
                rrf_k=rrf_k,
            )
        else:
            final_hits = dense_hits[:top_k]

        # Step 4: Format Chunks & Citations
        chunks = []
        for index, hit in enumerate(final_hits, start=1):
            formatted_hit = CitationEngine.format_hit(hit, index=index)
            
            chunk_data = {
                "text": formatted_hit["text"],
                "document_name": formatted_hit["filename"],
                "filename": formatted_hit["filename"],
                "page_number": formatted_hit["page_number"],
                "chunk_number": formatted_hit["chunk_index"],
                "chunk_index": formatted_hit["chunk_index"],
                "similarity_score": formatted_hit["score"],
                "score": formatted_hit["score"],
                "document_id": formatted_hit["document_id"],
                "source_format": formatted_hit["source_format"],
                "citation_tag": formatted_hit["citation_tag"],
                "citation_index": formatted_hit["citation_index"],
                "point_id": formatted_hit["point_id"],
            }
            chunks.append(chunk_data)

        rag_context, citations = CitationEngine.build_rag_context(final_hits)

        return {
            "query": query,
            "total_results": len(chunks),
            "chunks": chunks,
            "rag_context": rag_context,
            "citations": citations,
        }

    def _apply_hybrid_rrf(
        self,
        query: str,
        dense_hits: List[Any],
        top_k: int = 5,
        rrf_k: int = 60,
    ) -> List[Any]:
        """
        Combine Dense Vector similarity scores with Lexical Keyword Match scores using Reciprocal Rank Fusion (RRF).
        """
        query_terms = set(query.lower().split())

        # Lexical scoring on candidate hit payloads
        scored_candidates = []
        for hit in dense_hits:
            payload = getattr(hit, "payload", {}) if hasattr(hit, "payload") else hit.get("payload", hit)
            text = payload.get("text", "").lower()

            # Count keyword term occurrences
            keyword_score = sum(1 for term in query_terms if term in text)
            scored_candidates.append((hit, keyword_score))

        # Sort by lexical score for rank assignments
        lexical_sorted = sorted(scored_candidates, key=lambda x: x[1], reverse=True)

        # Build rank lookups
        dense_ranks = {id(hit): rank for rank, hit in enumerate(dense_hits, start=1)}
        lexical_ranks = {id(hit): rank for rank, (hit, _) in enumerate(lexical_sorted, start=1)}

        # Compute RRF score: 1 / (k + r_dense) + 1 / (k + r_lexical)
        rrf_scores = []
        for hit in dense_hits:
            r_dense = dense_ranks[id(hit)]
            r_lex = lexical_ranks[id(hit)]
            score = (1.0 / (rrf_k + r_dense)) + (1.0 / (rrf_k + r_lex))

            # Store updated score back on hit object or tuple wrapper
            if hasattr(hit, "score"):
                # Normalize RRF score to 0..1 scale for display
                hit.score = min(1.0, score * (rrf_k + 1))
            rrf_scores.append((hit, score))

        # Sort candidate hits by combined RRF score
        rrf_sorted = sorted(rrf_scores, key=lambda x: x[1], reverse=True)
        return [hit for hit, _ in rrf_sorted[:top_k]]
