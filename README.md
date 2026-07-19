🚀 Development Milestones
✅ Milestone 1 – Backend Foundation & PDF Upload
Completed
Initialized the FastAPI backend application.
Designed the backend project structure.
Configured main.py and API routing using APIRouter.
Implemented the POST /upload-pdf endpoint.
Added PDF file validation (only .pdf files are accepted).
Created automatic backend/uploads/ directory creation.
Successfully stored uploaded PDF files.
Tested all APIs using Swagger UI (/docs).
Verified backend functionality and completed Git workflow (feature branch → commit → PR → merge).

Status: ✅ Completed & Merged

✅ Milestone 2 – Chunking & Embedding Module
Completed
Implemented configurable text chunking with overlapping chunks.
Added text embedding generation using BAAI BGE Small (BAAI/bge-small-en-v1.5).
Added image embedding generation using OpenCLIP (ViT-B-32).
Created the initial embedding pipeline structure.
Installed and verified required dependencies.
Reviewed, tested, and integrated the embedding module.

Status: ✅ Completed & Merged

🚧 Milestone 3 – PDF Ingestion Pipeline
Planned
Read uploaded PDF documents.
Extract text from PDFs.
Clean and preprocess extracted text.
Connect extraction with the chunking module.
Prepare chunks for embedding generation.

Status: ⏳ In Progress

🚧 Milestone 4 – Vector Database Integration
Planned
Generate embeddings for document chunks.
Store embeddings in FAISS/Qdrant.
Store document metadata.
Implement semantic similarity search.

Status: ⏳ Pending

🚧 Milestone 5 – Multi-Modal Retrieval
Planned
Retrieve relevant text chunks.
Retrieve image embeddings.
Build context generation pipeline.
Support hybrid retrieval.

Status: ⏳ Pending

🚧 Milestone 6 – Agentic AI Orchestrator
Planned
Implement LangGraph Supervisor Agent.
Integrate Search Agent.
Integrate Vision Agent.
Integrate SQL Agent.
Enable multi-agent task routing.

Status: ⏳ Pending

🚧 Milestone 7 – Evaluation & Guardrails
Planned
Add response validation.
Detect hallucinations.
Integrate NeMo Guardrails.
Add Langfuse monitoring.
Improve response reliability.

Status: ⏳ Pending

🚧 Milestone 8 – Deployment & Documentation
Planned
End-to-end testing.
API documentation.
Docker support.
Deployment.
Final project documentation.

Status: ⏳ Pending
