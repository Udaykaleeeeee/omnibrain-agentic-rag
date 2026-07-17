from fastapi import FastAPI

app = FastAPI(
    title="OmniBrain Agentic RAG",
    description="Month 1 Internship Project",
    version="1.0.0"
)

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