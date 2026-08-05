"""
LangGraph workflow for OmniBrain.
"""

from langgraph.graph import StateGraph, END

from .state import AgentState
from .supervisor import supervisor
from .search_agent import search_agent
from .vision_agent import vision_agent


def route(state: AgentState):
    """
    Route to the correct agent.
    """
    if state["next_agent"] == "VISION":
        return "vision"

    return "search"


builder = StateGraph(AgentState)

# Nodes
builder.add_node("supervisor", supervisor)
builder.add_node("search", search_agent)
builder.add_node("vision", vision_agent)

# Entry point
builder.set_entry_point("supervisor")

# Conditional routing
builder.add_conditional_edges(
    "supervisor",
    route,
    {
        "search": "search",
        "vision": "vision",
    },
)

# Finish
builder.add_edge("search", END)
builder.add_edge("vision", END)

graph = builder.compile()