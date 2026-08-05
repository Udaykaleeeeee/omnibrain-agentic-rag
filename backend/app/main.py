from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.app.api.routes import router
from backend.app.agents.graph import graph

app = FastAPI(
    title="OmniBrain",
    description="Multi-format document ingestion with OCR",
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


@app.get("/")
def home():
    return {
        "message": "Welcome to OmniBrain"
    }


@app.get("/health")
def health():
    return {
        "status": "Running"
    }


@app.post("/agent")
def run_agent(request: QueryRequest):
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