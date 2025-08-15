import os
from typing import Optional
from fastapi import UploadFile
from app.utils.file_handler import save_file
from app.services.extractor import extract_and_clean

async def process_upload(file: Optional[UploadFile], raw_text: Optional[str] = None):
    """
    Saves file if provided, extracts text if file is given.
    If raw_text is given, uses that instead.
    Returns (source_name, text).
    """
    if file:
        file_bytes = await file.read()
        path = save_file(file_bytes, file.filename)
        ext = os.path.splitext(file.filename)[-1].replace(".", "")
        text = extract_and_clean(path, ext)
        return file.filename, text
    elif raw_text:
        return "raw_text", raw_text
    else:
        raise ValueError("Provide either file or raw_text")
