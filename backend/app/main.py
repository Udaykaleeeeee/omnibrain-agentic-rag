from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.app.api.routes import router
from backend.app.agents.graph import graph


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="OmniBrain",
    description="Multi-format document ingestion with OCR and Agentic RAG",
    version="1.0.0",
)


# ============================================================
# CORS CONFIGURATION
# ============================================================

app.add_middleware(
    CORSMiddleware,

    # Local React/Vite development
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],

    # Allow deployed Vercel frontend
    allow_origin_regex=r"https://.*\.vercel\.app",

    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# API ROUTES
# ============================================================

app.include_router(
    router,
    tags=["ingestion"],
)


# ============================================================
# BASIC ENDPOINTS
# ============================================================

@app.get("/")
def home():
    return {
        "message": "OmniBrain API Running"
    }


@app.get("/health")
def health():
    return {
        "status": "Running"
    }


# ============================================================
# AGENT REQUEST
# ============================================================

class AgentRequest(BaseModel):
    query: str


# ============================================================
# LANGGRAPH AGENT ENDPOINT
# ============================================================

@app.post("/agent")
def run_agent(request: AgentRequest):
    """
    Execute the LangGraph workflow.
    """

    state = {
        "query": request.query,
        "response": None,
        "documents": [],
        "images": [],
        "citations": [],
        "next_agent": None,
    }

    result = graph.invoke(state)

    return {
        "query": result.get("query", request.query),
        "response": result.get("response"),
        "agent": result.get("next_agent"),
        "citations": result.get("citations", []),
    }


# NOTE:
# POST /query is already implemented in backend.app.api.routes.
# Do not define another /query endpoint here.