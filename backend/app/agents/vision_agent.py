"""
Vision Agent for OmniBrain.
Handles image-based queries using Gemini vision capabilities.
"""

from pathlib import Path

from PIL import Image

from .llm import get_llm
from .prompts import VISION_AGENT_PROMPT
from .state import AgentState


IMAGE_BASE_DIR = Path("backend/uploads")


def vision_agent(state: AgentState) -> AgentState:
    """
    Handles image-related queries using Gemini multimodal input.
    """

    model = get_llm()

    images = state.get("images", [])

    if not images:
        state["response"] = "No image was provided for visual analysis."
        return state

    image_path = Path(images[0])

    # Convert relative image paths such as:
    # images/<document_id>_p0001_img000.png
    # into the project's local storage path.
    if not image_path.is_absolute():
        image_path = IMAGE_BASE_DIR / image_path

    if not image_path.exists():
        state["response"] = f"Image not found: {image_path}"
        return state

    image = Image.open(image_path)

    prompt = f"""
{VISION_AGENT_PROMPT}

User Query:
{state["query"]}

Analyze the provided image carefully and answer the user's query
using information visible in the image.
"""

    response = model.generate_content([prompt, image])

    state["response"] = response.text

    return state