"""
Vision Agent for OmniBrain.
"""

from .llm import get_llm
from .prompts import VISION_AGENT_PROMPT
from .state import AgentState


def vision_agent(state: AgentState) -> AgentState:
    """
    Handles image-related queries.
    """

    model = get_llm()

    prompt = f"""
{VISION_AGENT_PROMPT}

User Query:
{state["query"]}

Available Images:
{state["images"]}
"""

    response = model.generate_content(prompt)

    state["response"] = response.text

    return state