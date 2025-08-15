# app/routes/file_routes.py
from fastapi import APIRouter, File, UploadFile, Query, HTTPException
from app.utils.file_handler import save_file
from app.services.extractor import extract_and_clean
from app.db.database import SessionLocal
from app.db.models import Document
import os

router = APIRouter()

@router.post("/upload/")
async def upload_file(
    file: UploadFile = File(...),
    extract: bool = Query(False, description="If true, extract text"),
    save_to_db: bool = Query(False, description="If true, save doc & text to DB")
):
    """
    Upload a file, optionally extract text and/or save to DB.
    """
    try:
        file_bytes = await file.read()
        path = save_file(file_bytes, file.filename)
        
        text = None
        if extract:
            ext = os.path.splitext(file.filename)[-1].replace(".", "")
            text = extract_and_clean(path, ext)

        doc_id = None
        if save_to_db:
            db = SessionLocal()
            try:
                doc = Document(filename=file.filename, original_path=path, text=text or "")
                db.add(doc)
                db.commit()
                db.refresh(doc)
                doc_id = doc.id
            finally:
                db.close()

        return {
            "filename": file.filename,
            "path": path,
            "doc_id": doc_id,
            "extracted_text": text
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction failed: {e}")

@router.get("/documents")
def list_documents():
    """
    Return a list of all stored documents with id and filename.
    """
    db = SessionLocal()
    try:
        docs = db.query(Document).all()
        return [{"id": d.id, "filename": d.filename} for d in docs]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()