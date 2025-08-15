# app/routes/file_routes.py
from fastapi import APIRouter, File, UploadFile, Query, HTTPException
from app.utils.file_handler import save_file
from app.services.extractor import extract_and_clean
from app.db.database import SessionLocal
from app.db.models import Document
from app.services.embeddings_store import add_texts
import os

router = APIRouter()

@router.post("/upload/")
async def upload_file(
    file: UploadFile = File(...),
    extract: bool = Query(True, description="If true, extract text"),
    save_to_db: bool = Query(True, description="If true, save doc & text to DB"),
    create_embeddings: bool = Query(True, description="If true, create embeddings for QnA")
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

        # 🔹 Create embeddings so QnA works immediately
        if create_embeddings and text:
            paras = [p.strip() for p in text.split("\n\n") if p.strip()]
            texts = []
            metas = []
            for i, p in enumerate(paras):
                texts.append(p)
                metas.append({"source": file.filename, "chunk_id": i, "text": p, "doc_id": doc_id})
            add_texts(texts, metas)

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


from fastapi import status
from app.services.embeddings_store import _metadata, _index, save_index, _init_index, clear_store
import faiss

@router.delete("/documents/{doc_id}", status_code=status.HTTP_200_OK)
def delete_document(doc_id: int):
    db = SessionLocal()
    try:
        # Get the document
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")

        # Remove file from uploads folder
        if doc.original_path and os.path.exists(doc.original_path):
            try:
                os.remove(doc.original_path)
            except Exception as e:
                print(f"Warning: could not remove file {doc.original_path}: {e}")

        # Remove embeddings for this document
        _init_index(384)  # adjust to your embedding dimension
        if _metadata:
            ids_to_keep = []
            vectors_to_keep = []
            for idx in range(_index.ntotal):
                md = _metadata.get(idx)
                if md and md.get("doc_id") != doc_id:
                    ids_to_keep.append(idx)
                    vectors_to_keep.append(_index.reconstruct(idx))

            if vectors_to_keep:
                new_index = faiss.IndexFlatIP(_index.d)
                new_index.add(vectors_to_keep)
                _index.reset()
                _index.add(vectors_to_keep)
                # rebuild metadata
                new_metadata = {}
                for new_id, old_id in enumerate(ids_to_keep):
                    new_metadata[new_id] = _metadata[old_id]
                _metadata.clear()
                _metadata.update(new_metadata)
                save_index()
            else:
                clear_store()

        # Delete from DB (sections will cascade delete)
        db.delete(doc)
        db.commit()

        return {"deleted": True, "doc_id": doc_id}
    finally:
        db.close()
