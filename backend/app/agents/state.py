from typing import TypedDict, List, Dict , Optional


class AgentState(TypedDict):
    """
    Shared state used by all LangGraph agents.
    """

    query: str
    response: Optional[str]

    documents: List[str]
    images: List[str]

    # Metadata returned by Retrieval Service
    citations: List[Dict]

    document_id: Optional[str]
    top_k: int


    next_agent: Optional[str]