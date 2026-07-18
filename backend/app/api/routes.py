from fastapi import APIRouter, UploadFile, File
import os
import shutil

print("=================================")
print("ROUTES.PY LOADED")
print(__file__)
print("=================================")

router = APIRouter()


@router.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload a PDF file and save it inside backend/uploads
    """

    # Check whether the uploaded file is PDF
    if not file.filename.lower().endswith(".pdf"):
        return {
            "success": False,
            "message": "Only PDF files are allowed."
        }

    upload_folder = "backend/uploads"

    # Create uploads folder if it doesn't exist
    os.makedirs(upload_folder, exist_ok=True)

    file_path = os.path.join(upload_folder, file.filename)

    # Save the file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "success": True,
        "message": "PDF uploaded successfully.",
        "filename": file.filename
    }