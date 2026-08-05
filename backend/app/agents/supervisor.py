"""
Supervisor Agent for OmniBrain.
"""

from .state import AgentState


VISION_KEYWORDS = {
    "image",
    "photo",
    "picture",
    "diagram",
    "chart",
    "graph",
    "figure",
    "visual",
    "scan",
    "table",
    "plot",
    "screenshot",
}


def supervisor(state: AgentState) -> AgentState:
    """
    Decide which agent should handle the request.

    SEARCH -> Text/document questions
    VISION -> Image/chart/table/visual questions
    """

    query = state["query"].lower()

    if any(keyword in query for keyword in VISION_KEYWORDS):
        state["next_agent"] = "VISION"
    else:
        state["next_agent"] = "SEARCH"

    return state