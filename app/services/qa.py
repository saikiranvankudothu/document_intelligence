# app/services/qa.py
from typing import List, Dict, Any
from app.services.embeddings_store import search, add_texts
from app.services.summarizer import get_summarizer, summarize_text
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
import torch
import os

# generator model — can be same as summarizer model or another generator model you fine-tuned.
GEN_MODEL = os.environ.get("GEN_MODEL", os.environ.get("SUMMARIZER_MODEL", "google/flan-t5-base"))
DEVICE = 0 if torch.cuda.is_available() else -1

_generator = None

def get_generator():
    global _generator
    if _generator is None:
        _generator = pipeline("text2text-generation", model=GEN_MODEL, device=DEVICE)
    return _generator

def retrieve_and_answer(query: str, top_k: int = 5, max_input_len: int = 1000) -> Dict[str, Any]:
    """
    1) Search FAISS for top_k passages
    2) Build a context string from their texts and metadata
    3) Use generator to answer the query given the context (prompting)
    """
    hits = search(query, top_k=top_k)
    if not hits:
        return {"answer": "", "sources": []}

    # build context
    contexts = []
    sources = []
    for h in hits:
        md = h.get("metadata", {})
        txt = md.get("text") or md.get("content") or ""
        snippets = txt.strip()
        if snippets:
            contexts.append(snippets)
            sources.append({"score": h["score"], "metadata": md})

    # join with separators, and truncate if too long
    context_joined = "\n\n---\n\n".join(contexts)
    if len(context_joined) > max_input_len:
        context_joined = context_joined[:max_input_len]

    prompt = f"Context:\n{context_joined}\n\nQuestion: {query}\nAnswer concisely:"
    gen = get_generator()
    out = gen(prompt, max_length=256, do_sample=False)
    answer = out[0]["generated_text"]
    return {"answer": answer, "sources": sources}
