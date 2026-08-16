"""
Search Agent for OmniBrain.
"""

from .llm import get_llm
from .prompts import SEARCH_AGENT_PROMPT
from .state import AgentState
from ..vector_db.retrieval import RetrievalService


def search_agent(state: AgentState) -> AgentState:
    """
    Handles text-based user queries using Gemini.
    """

    model = get_llm()

    # Retrieve relevant document chunks using Member 3's Retrieval Service
    retrieval_service = RetrievalService()

    retrieval_result = retrieval_service.retrieve(
        query=state["query"],
        top_k=5
    )

    # Store citations
    state["citations"] = retrieval_result["citations"]

    # Build context for Gemini
    context = retrieval_result["rag_context"]

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