import os

from dotenv import load_dotenv
import google.generativeai as genai

# Load variables from .env
load_dotenv()

# Read the Gemini API key
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)


def get_llm():
    """
    Returns a configured Gemini model.
    """

    return genai.GenerativeModel("gemini-3-flash-preview")