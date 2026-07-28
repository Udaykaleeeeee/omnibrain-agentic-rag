from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.api.routes import router

app = FastAPI(
    title="OmniBrain",
    description="Multi-format document ingestion with OCR",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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