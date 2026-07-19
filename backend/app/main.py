from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(
    title="OmniBrain Agentic RAG",
    description="Month 1 Internship Project",
    version="1.0.0"
)

# Include ingestion routes
app.include_router(router, tags=["ingestion"])

@app.get("/")
def home():
    return {
        "message": "Welcome to OmniBrain Agentic RAG"
    }

@app.get("/health")
def health():
    return {
        "status": "Backend is running successfully!"
    }