"""
Search Agent for OmniBrain.
"""

from .llm import get_llm
from .prompts import SEARCH_AGENT_PROMPT
from .state import AgentState
from ..services.retrieval_service import retrieve


def search_agent(state: AgentState) -> AgentState:
    """
    Handles text-based user queries using Gemini.
    """

    model = get_llm()

    # Retrieve relevant document chunks
    retrieved_chunks = retrieve(state["query"])

    # Preserve citation metadata
    state["citations"] = [
        {
            "document": chunk["document"],
            "page": chunk["page"],
            "chunk": chunk["chunk"],
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