from fastapi import FastAPI
<<<<<<< HEAD
from app.api.routes import router
=======
from backend.app.api.routes import router

print("MAIN.PY LOADED")
>>>>>>> 26cbca42c9a13492e185627e84f30848cb191f6a

app = FastAPI(
    title="OmniBrain",
    description="Agentic Multi-Modal RAG Orchestrator",
    version="1.0.0"
)

<<<<<<< HEAD
# Include ingestion routes
app.include_router(router, tags=["ingestion"])
=======
# Include all API routes
app.include_router(router)

>>>>>>> 26cbca42c9a13492e185627e84f30848cb191f6a

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