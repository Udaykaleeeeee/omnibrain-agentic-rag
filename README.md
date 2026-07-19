# OmniBrain Agentic RAG

Multi-agent RAG system with document ingestion.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Optional: Install Tesseract for OCR
sudo apt-get install tesseract-ocr  # Linux
brew install tesseract              # macOS

# Start server
cd backend
uvicorn app.main:app --reload --port 8000
```

Visit: http://localhost:8000/docs

## API Usage

```bash
# Upload document
curl -X POST "http://localhost:8000/ingest" -F "file=@document.pdf"

# Check formats
curl http://localhost:8000/ingest/formats
```

## Python Usage

```python
from backend.app.ingestion import ingest_document

result = ingest_document(
    file_path="document.pdf",
    filename="document.pdf",
    document_id="doc-123"
)

print(f"Pages: {result['total_pages']}")
print(f"OCR pages: {result['ocr_pages_used']}")
```

## Features

- PDF, DOCX, TXT parsing
- OCR for scanned documents
- Text preprocessing
- REST API endpoints

## Endpoints

- `POST /ingest` - Upload document
- `GET /ingest/formats` - List formats
- `GET /docs` - API documentation