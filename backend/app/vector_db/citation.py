"""
Citation Generation Engine
Formats vector search results and payload metadata into standardized citations for RAG prompt synthesis.
"""

import logging
from typing import List, Dict, Any, Tuple

logger = logging.getLogger(__name__)


class CitationEngine:
    """
    Formats search hits into structured citations and formatted RAG context prompts.
    """

    @staticmethod
    def format_citation_tag(
        filename: str,
        page_number: int,
        chunk_index: int,
        citation_idx: int = 1,
    ) -> str:
        """
        Generate a inline citation tag string (e.g. [Ref 1: sample.pdf, Page 2, Chunk 0]).
        """
        clean_filename = filename or "document"
        return f"[Ref {citation_idx}: {clean_filename}, Page {page_number}, Chunk {chunk_index}]"

    @classmethod
    def format_hit(cls, hit: Any, index: int = 1) -> Dict[str, Any]:
        """
        Convert a raw Qdrant ScoredPoint / dictionary into a normalized citation object.
        """
        payload = getattr(hit, "payload", {}) if hasattr(hit, "payload") else hit.get("payload", hit)
        score = float(getattr(hit, "score", 0.0)) if hasattr(hit, "score") else float(hit.get("score", 0.0))
        point_id = str(getattr(hit, "id", "")) if hasattr(hit, "id") else str(hit.get("id", ""))

        filename = payload.get("filename", "unknown_doc")
        page_number = payload.get("page_number", 1)
        chunk_index = payload.get("chunk_index", 0)
        document_id = payload.get("document_id", "")
        text = payload.get("text", "")
        source_format = payload.get("source_format", "")

        citation_tag = cls.format_citation_tag(
            filename=filename,
            page_number=page_number,
            chunk_index=chunk_index,
            citation_idx=index,
        )

        return {
            "citation_index": index,
            "citation_tag": citation_tag,
            "point_id": point_id,
            "document_id": document_id,
            "filename": filename,
            "page_number": page_number,
            "chunk_index": chunk_index,
            "source_format": source_format,
            "score": round(score, 4),
            "text": text,
        }

    @classmethod
    def build_rag_context(
        cls,
        hits: List[Any],
        max_context_length: int = 4000,
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Convert search hits into a structured context string and citation list for RAG.
        
        Returns:
            Tuple of (formatted_context_string, citation_objects_list)
        """
        citations = []
        context_blocks = []
        current_length = 0

        for i, hit in enumerate(hits, start=1):
            citation = cls.format_hit(hit, index=i)
            citations.append(citation)

            block = (
                f"--- Citation {citation['citation_tag']} (Score: {citation['score']}) ---\n"
                f"Document: {citation['filename']} | Page: {citation['page_number']} | Chunk: {citation['chunk_index']}\n"
                f"Content:\n{citation['text']}\n"
            )

            if current_length + len(block) > max_context_length and context_blocks:
                break

            context_blocks.append(block)
            current_length += len(block)

        formatted_context = "\n\n".join(context_blocks)
        return formatted_context, citations
