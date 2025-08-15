# app/routes/nlp_routes.py
from fastapi import APIRouter, File, UploadFile, Body, Query,HTTPException
from typing import Optional, List
from app.utils.file_handler import save_file
from app.services.extractor import extract_and_clean
from app.services.structure import detect_sections, sections_to_json
from app.services.summarizer import summarize_text, summarize_sections
from app.services.embeddings_store import add_texts, search, clear_store
from app.services.qa import retrieve_and_answer
from app.utils.file_processor import process_upload
from app.db.database import SessionLocal
from app.db.models import Document
import os

router = APIRouter(prefix="/nlp", tags=["NLP"])

@router.post("/summarize/document")
async def summarize_document(file: UploadFile = File(None), raw_text: Optional[str] = Body(default=None),
                             max_length: int = 200):
    try:
        _, text = await process_upload(file, raw_text)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    summary = summarize_text(text, max_length=max_length, min_length=30)
    return {"summary": summary}

@router.post("/summarize/sections")
async def summarize_document_sections(file: UploadFile = File(None),
                                      raw_text: Optional[str] = Body(default=None),
                                      per_section_max: int = 120):
    """
    Summarize each detected heading/section.
    """
    if file is None and not raw_text:
        return {"error": "Provide file or raw_text"}
    if file:
        fb = await file.read()
        path = save_file(fb, file.filename)
        ext = os.path.splitext(file.filename)[-1].replace(".", "")
        text = extract_and_clean(path, ext)
    else:
        text = raw_text

    nodes = detect_sections(text)
    # convert nodes to dicts for summarizer
    def node_to_dict(n):
        return {"title": n.title, "level": n.level, "content": n.content}
    nodes_list = [node_to_dict(n) for n in nodes]
    summaries = summarize_sections(nodes_list, per_section_max)
    return {"section_summaries": summaries}

@router.post("/embeddings/add")
async def embeddings_add(file: UploadFile = File(None), raw_text: Optional[str] = Body(default=None),
                         doc_id: Optional[int] = None):
    """
    Extract text and split into passage chunks, create embeddings and add to FAISS.
    """
    if file is None and not raw_text:
        return {"error": "Provide file or raw_text"}
    if file:
        fb = await file.read()
        path = save_file(fb, file.filename)
        ext = os.path.splitext(file.filename)[-1].replace(".", "")
        text = extract_and_clean(path, ext)
        source = file.filename
    else:
        text = raw_text
        source = "raw_text"

    # simple chunking by paragraphs or sentences (adjust chunk size as required)
    paras = [p.strip() for p in text.split("\n\n") if p.strip()]
    texts = []
    metas = []
    for i, p in enumerate(paras):
        texts.append(p)
        metas.append({"source": source, "chunk_id": i, "text": p, "doc_id": doc_id})
    ids = add_texts(texts, metas)
    return {"added_ids": ids, "num_added": len(ids)}

@router.post("/qa")
def qa_endpoint(question: str = Body(...), doc_id: Optional[int] = Body(None), top_k: int = Query(5)):
    """
    Ask a question — optionally restrict search to one document's embeddings.
    """
    # Optional: filter embeddings by doc_id before retrieval
    results = retrieve_and_answer(question, top_k=top_k)
    if doc_id is not None:
        results["sources"] = [src for src in results["sources"] if src["metadata"].get("doc_id") == doc_id]
    return results


@router.post("/embeddings/clear")
async def embeddings_clear():
    clear_store()
    return {"cleared": True}

@router.get("/summary/{doc_id}")
def get_summary(doc_id: int):
    db = SessionLocal()
    try:
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        if not doc.text:
            raise HTTPException(status_code=400, detail="Document has no text")

        text = doc.text.strip()
        max_chunk_size = 1500  # chars per chunk for summarization
        if len(text) > max_chunk_size:
            chunks = [text[i:i+max_chunk_size] for i in range(0, len(text), max_chunk_size)]
            summaries = [summarize_text(c, max_length=500, min_length=50) for c in chunks]
            summary = " ".join(summaries)
        else:
            summary = summarize_text(text, max_length=500, min_length=50)

        return {"summary": summary}
    finally:
        db.close()


from app.services.visualization import hierarchy_to_mermaid
from app.services.structure import detect_sections, sections_to_json

@router.get("/visualization/{doc_id}")
def get_flowchart(doc_id: int):
    db = SessionLocal()
    try:
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        if not doc.text:
            raise HTTPException(status_code=400, detail="Document has no text")
        nodes = detect_sections(doc.text)
        hierarchy = {"title": doc.filename, "sections": sections_to_json(nodes)}
        mermaid_code = hierarchy_to_mermaid(hierarchy)
        return {"mermaid": mermaid_code}
    finally:
        db.close()

from fastapi import status
from app.services.embeddings_store import _metadata, save_index, _init_index
import faiss

@router.delete("/documents/{doc_id}", status_code=status.HTTP_200_OK)
def delete_document(doc_id: int):
    db = SessionLocal()
    try:
        # Get document
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")

        # Remove file from uploads folder
        if doc.original_path and os.path.exists(doc.original_path):
            os.remove(doc.original_path)

        # Remove embeddings related to this doc_id
        _init_index(384)  # Assuming MiniLM 384-dim; adjust if needed
        ids_to_remove = [idx for idx, md in _metadata.items() if md.get("doc_id") == doc_id]
        if ids_to_remove:
            # Create a mask for vectors to keep
            total_ids = list(range(len(_metadata)))
            keep_ids = [i for i in total_ids if i not in ids_to_remove]
            if keep_ids:
                new_index = faiss.IndexFlatIP(_index.d)
                new_metadata = {}
                vectors = faiss.vector_to_array(_index.xb).reshape(-1, _index.d)
                for new_id, old_id in enumerate(keep_ids):
                    new_index.add(vectors[old_id:old_id+1])
                    new_metadata[new_id] = _metadata[old_id]
                _index.reset()
                _index.add(new_index.reconstruct_n(0, len(keep_ids)))
                _metadata.clear()
                _metadata.update(new_metadata)
                save_index()
            else:
                # No embeddings remain → clear store
                from app.services.embeddings_store import clear_store
                clear_store()

        # Delete document from DB
        db.delete(doc)
        db.commit()

        return {"deleted": True, "doc_id": doc_id}
    finally:
        db.close()
