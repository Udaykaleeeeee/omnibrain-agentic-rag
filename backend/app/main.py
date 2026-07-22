from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(
    title="OmniBrain",
    description="Multi-format document ingestion with OCR",
    version="1.0.0"
)

app.include_router(router, tags=["ingestion"])


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