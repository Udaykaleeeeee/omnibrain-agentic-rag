"""
Search Agent for OmniBrain.
"""

from .llm import get_llm
from .prompts import SEARCH_AGENT_PROMPT
from .state import AgentState
from ..vector_db import RetrievalService


def search_agent(state: AgentState) -> AgentState:
    """
    Handles text-based user queries using Gemini.
    """

    model = get_llm()

    # Retrieve relevant document chunks
    retrieval_service = RetrievalService()
    result = retrieval_service.retrieve(
    query=state["query"],
    top_k=state["top_k"],
    document_id=state["document_id"],
)
    retrieved_chunks = result["chunks"]

    # Preserve citation metadata
    state["citations"] = [
    {
        "document": chunk["document_name"],
        "page": chunk["page_number"],
        "chunk": chunk["chunk_number"],
        "score": chunk["score"],
    }
    for chunk in retrieved_chunks
]

    # Build context from retrieved chunks
    context = (
        "\n\n".join(chunk["text"] for chunk in retrieved_chunks)
        if retrieved_chunks
        else "No relevant context found."
    )

    prompt = f"""
{SEARCH_AGENT_PROMPT}

Retrieved Context:
{context}

User Query:
{state["query"]}
"""

    response = model.generate_content(prompt)

    state["response"] = response.text

    return state