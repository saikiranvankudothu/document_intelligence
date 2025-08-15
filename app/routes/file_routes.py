from fastapi import APIRouter, File, UploadFile
from app.utils.file_handler import save_file
from app.services.extractor import extract_and_clean
import os

router = APIRouter()

@router.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    """Upload and save file."""
    file_bytes = await file.read()
    path = save_file(file_bytes, file.filename)
    return {"filename": file.filename, "path": path}

@router.post("/extract/")
async def extract_file(file: UploadFile = File(...)):
    """Upload, save, and extract text from a file."""
    file_bytes = await file.read()
    path = save_file(file_bytes, file.filename)

    ext = os.path.splitext(file.filename)[-1].replace(".", "")
    try:
        text = extract_and_clean(path, ext)
        return {"filename": file.filename, "extracted_text": text}
    except ValueError as e:
        return {"error": str(e)}
