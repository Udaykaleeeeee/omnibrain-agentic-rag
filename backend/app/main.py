from fastapi import FastAPI
from backend.app.api.routes import router

print("MAIN.PY LOADED")

app = FastAPI(
    title="OmniBrain",
    description="Agentic Multi-Modal RAG Orchestrator",
    version="1.0.0"
)

# Include all API routes
app.include_router(router)


@app.get("/")
def home():
    return {
        "message": "Welcome to OmniBrain"
    }


@app.get("/health")
def health():
    return {
        "status": "Backend Running"
    }