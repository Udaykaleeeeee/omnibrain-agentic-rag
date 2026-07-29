from fastapi import FastAPI
from pydantic import BaseModel

from backend.app.agents.graph import graph

app = FastAPI()


class QueryRequest(BaseModel):
    query: str


@app.get("/")
def home():
    return {"message": "OmniBrain API Running"}


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
@app.post("/query")
def query(request: QueryRequest):
    """
    Frontend endpoint.
    Uses the same LangGraph workflow as /agent.
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