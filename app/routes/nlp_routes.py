# app/routes/nlp_routes.py
from fastapi import APIRouter, File, UploadFile, Body, Query
from typing import Optional, List
from app.utils.file_handler import save_file
from app.services.extractor import extract_and_clean
from app.services.structure import detect_sections, sections_to_json
from app.services.summarizer import summarize_text, summarize_sections
from app.services.embeddings_store import add_texts, search, clear_store
from app.services.qa import retrieve_and_answer
import os

router = APIRouter(prefix="/nlp", tags=["NLP"])

@router.post("/summarize/document")
async def summarize_document(file: UploadFile = File(None), raw_text: Optional[str] = Body(default=None),
                             max_length: int = 200):
    """
    Summarize an entire document.
    Provide either file OR raw_text.
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
async def qa_endpoint(question: str = Body(...), top_k: int = Query(5)):
    """
    Ask a question — uses FAISS retrieval + generator to produce an answer.
    """
    out = retrieve_and_answer(question, top_k=top_k)
    return out

@router.post("/embeddings/clear")
async def embeddings_clear():
    clear_store()
    return {"cleared": True}
