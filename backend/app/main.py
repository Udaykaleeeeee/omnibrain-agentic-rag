from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.app.api.routes import router
from backend.app.agents.graph import graph


app = FastAPI(
    title="OmniBrain",
    description="Multi-format document ingestion with OCR and Agentic RAG",
    version="1.0.0"
)


# -----------------------------
# CORS Configuration
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------
# API Routes
# -----------------------------
app.include_router(router, tags=["ingestion"])


class QueryRequest(BaseModel):
    query: str


# -----------------------------
# Basic Endpoints
# -----------------------------
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


# -----------------------------
# LangGraph Agent Endpoint
# -----------------------------
@app.post("/agent")
def run_agent(request: QueryRequest):
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
        "query": result["query"],
        "response": result["response"],
        "agent": result["next_agent"],
        "citations": result["citations"],
    }


# -----------------------------
# Frontend Query Endpoint
# -----------------------------
@app.post("/query")
def query(request: QueryRequest):
    """
    Frontend endpoint.
    Uses the LangGraph workflow.
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
        "answer": result["response"],
        "citations": result["citations"],
    }