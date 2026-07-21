# 🚀 Quick Start Guide - OmniBrain Ingestion

## Run the Project in 3 Steps

### Step 1: Start the Server

Open VS Code terminal (Ctrl + `) and run:

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

**You should see:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Application startup complete.
```

### Step 2: Open Swagger UI

Open your browser and go to:
```
http://127.0.0.1:8000/docs
```

You'll see the interactive API documentation!

### Step 3: Upload a Document

1. Find **POST /ingest** (green box)
2. Click **"Try it out"**
3. Click **"Choose File"**
4. Select any PDF, DOCX, or TXT file
5. Click **"Execute"**

**Done!** Your document is ingested.

---

## Full Step-by-Step Guide

### Prerequisites

✅ Python 3.10+ installed  
✅ Git repository cloned  
✅ VS Code open with project

### 1. Install Dependencies (First Time Only)

```bash
pip install -r requirements.txt
```

**This installs:**
- fastapi, uvicorn (API framework)
- pymupdf (PDF parsing)
- python-docx (DOCX parsing)
- pytesseract, pillow (OCR)
- And other dependencies

### 2. Install Tesseract (Optional - for OCR)

**If you need OCR for scanned PDFs:**

**Windows:**
- Download: https://github.com/UB-Mannheim/tesseract/wiki
- Install to: `C:\Program Files\Tesseract-OCR`
- Restart VS Code

**Verify:**
```bash
tesseract --version
```

**Skip OCR?** Regular PDFs and DOCX files work without Tesseract.

### 3. Start the Server

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

**What this does:**
- `app.main:app` - Points to FastAPI app
- `--reload` - Auto-restart on code changes
- `--port 8000` - Server port

**Server is ready when you see:**
```
INFO:     Application startup complete.
```

### 4. Test the Server

**Option A: Browser**
```
http://127.0.0.1:8000/health
```
Should show: `{"status":"Running"}`

**Option B: Terminal (new tab)**
```bash
curl http://127.0.0.1:8000/health
```

### 5. Access the API Documentation

Open browser:
```
http://127.0.0.1:8000/docs
```

**You'll see 10 endpoints:**

**Ingestion:**
- POST /ingest

**Retrieval:**
- GET /documents
- GET /documents/{id}
- GET /documents/{id}/chunks
- GET /documents/{id}/chunks/{index}
- GET /stats
- DELETE /documents/{id}

**Info:**
- GET /
- GET /health
- GET /ingest/formats

### 6. Upload Your First Document

**Method 1: Swagger UI (Easiest)**

1. Go to http://127.0.0.1:8000/docs
2. Find **POST /ingest**
3. Click **"Try it out"**
4. Upload a file
5. Click **"Execute"**

**Method 2: Command Line**

```bash
curl -X POST "http://127.0.0.1:8000/ingest" \
  -F "file=@test_files/sample.txt" \
  -F "document_id=my-first-doc"
```

**Method 3: Python**

```python
import requests

with open("test_files/sample.txt", "rb") as f:
    response = requests.post(
        "http://127.0.0.1:8000/ingest",
        files={"file": f},
        data={"document_id": "my-first-doc"}
    )
    print(response.json())
```

### 7. View Your Data

**List all documents:**
```bash
curl http://127.0.0.1:8000/documents
```

**Get document chunks:**
```bash
curl http://127.0.0.1:8000/documents/my-first-doc/chunks
```

**Or use Swagger UI** - easier!

---

## Common Issues & Solutions

### Issue: "pip: command not found"
```bash
# Try:
python -m pip install -r requirements.txt
# Or:
python3 -m pip install -r requirements.txt
```

### Issue: "uvicorn: command not found"
```bash
# Install uvicorn:
pip install uvicorn

# Or run directly:
python -m uvicorn app.main:app --reload --port 8000
```

### Issue: "Port 8000 already in use"
```bash
# Use different port:
uvicorn app.main:app --reload --port 8001

# Then access: http://127.0.0.1:8001/docs
```

### Issue: "ModuleNotFoundError"
```bash
# Make sure you're in backend/ directory:
cd backend

# Then run:
uvicorn app.main:app --reload --port 8000
```

### Issue: Server starts but crashes
```bash
# Check logs for missing dependencies
# Install missing packages:
pip install <package-name>
```

---

## Testing the Features

### Test 1: Upload TXT File
```bash
# Use the sample file
curl -X POST http://127.0.0.1:8000/ingest \
  -F "file=@test_files/sample.txt" \
  -F "document_id=test-txt"

# View chunks
curl http://127.0.0.1:8000/documents/test-txt/chunks
```

### Test 2: Upload PDF (with text)
```bash
# Upload any PDF
curl -X POST http://127.0.0.1:8000/ingest \
  -F "file=@your-document.pdf" \
  -F "document_id=test-pdf"
```

### Test 3: Upload DOCX
```bash
curl -X POST http://127.0.0.1:8000/ingest \
  -F "file=@your-document.docx" \
  -F "document_id=test-docx"
```

### Test 4: Check Storage Stats
```bash
curl http://127.0.0.1:8000/stats
```

---

## Stop the Server

**In the terminal where server is running:**
Press `Ctrl + C`

**You'll see:**
```
INFO:     Shutting down
INFO:     Finished server process
```

---

## Restart the Server

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

**Note:** Data in memory will be lost on restart (temporary storage).

---

## Development Workflow

### Running the Server
```bash
# Terminal 1: Run server
cd backend
uvicorn app.main:app --reload --port 8000
```

### Testing Endpoints
```bash
# Terminal 2: Test with curl
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/documents
```

### Or Use Swagger UI
- Always available at: http://127.0.0.1:8000/docs
- Interactive testing
- See all endpoints
- Try different parameters

---

## Quick Reference

### Start Server
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

### Important URLs
- **API Docs**: http://127.0.0.1:8000/docs
- **Health**: http://127.0.0.1:8000/health
- **Alt Docs**: http://127.0.0.1:8000/redoc

### Common Commands
```bash
# Install dependencies
pip install -r requirements.txt

# Start server
cd backend && uvicorn app.main:app --reload --port 8000

# Test health
curl http://127.0.0.1:8000/health

# Upload file
curl -X POST http://127.0.0.1:8000/ingest -F "file=@file.pdf"

# List documents
curl http://127.0.0.1:8000/documents
```

---

## Next Steps

After running the project:

1. ✅ Upload documents via Swagger UI
2. ✅ Check /documents endpoint
3. ✅ View chunks
4. ✅ Verify OCR (if Tesseract installed)
5. ✅ Test with your own files

---

## Summary

**To run the project:**
```bash
# 1. Install dependencies (first time)
pip install -r requirements.txt

# 2. Start server
cd backend
uvicorn app.main:app --reload --port 8000

# 3. Open browser
http://127.0.0.1:8000/docs

# 4. Upload a document and test!
```

**That's it!** 🚀

Server runs on: **http://127.0.0.1:8000**  
API docs at: **http://127.0.0.1:8000/docs**
