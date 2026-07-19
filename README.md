# OmniBrain Document Ingestion

Multi-format document ingestion module with OCR support for RAG systems.

## Features

- **Multi-format parsing**: PDF, DOCX, TXT
- **OCR integration**: Tesseract for scanned documents and images
- **Text preprocessing**: Normalization, dehyphenation, header/footer removal
- **REST API**: FastAPI endpoints for document upload
- **Unified output**: Consistent ParsedDocument structure across all formats

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Install Tesseract OCR (optional, for scanned documents)
sudo apt-get install tesseract-ocr  # Linux
brew install tesseract              # macOS

# Start server
cd backend
uvicorn app.main:app --reload --port 8000
```

## API Endpoints

**Upload Document**
```bash
curl -X POST "http://localhost:8000/ingest" \
  -F "file=@document.pdf" \
  -F "ocr_fallback=true"
```

**Get Supported Formats**
```bash
curl http://localhost:8000/ingest/formats
```

**API Documentation**: http://localhost:8000/docs

## Python Usage

```python
from backend.app.ingestion import ingest_document

result = ingest_document(
    file_path="document.pdf",
    filename="document.pdf",
    document_id="doc-123",
    ocr_fallback=True
)

print(f"Pages: {result['total_pages']}")
print(f"OCR used: {result['ocr_pages_used']}")
print(f"Chunks: {result['chunks_created']}")
```

## Architecture

```
backend/app/ingestion/
├── models.py          # Data structures (ParsedDocument, ParsedPage, PageImage)
├── router.py          # Format detection and parser routing
├── pdf_parser.py      # PDF parsing with PyMuPDF
├── docx_parser.py     # DOCX parsing with python-docx
├── txt_parser.py      # TXT parsing with encoding detection
├── ocr.py             # Tesseract OCR integration
├── preprocessing.py   # Text cleaning and normalization
└── pipeline.py        # Main orchestration
```

## Document Flow

1. **Upload** → Document uploaded via REST API
2. **Route** → Format detected, appropriate parser selected
3. **Parse** → Text and images extracted
4. **OCR** → Applied to scanned pages/images if needed
5. **Preprocess** → Text cleaned and normalized
6. **Output** → Structured ParsedDocument returned

## Supported Formats

- **PDF**: Text extraction + OCR for scanned pages
- **DOCX**: Paragraph and image extraction with pseudo-page creation
- **TXT**: Plain text with encoding auto-detection

## Requirements

- Python 3.8+
- FastAPI
- PyMuPDF (fitz)
- python-docx
- pytesseract
- Pillow
- Tesseract OCR (system package)
