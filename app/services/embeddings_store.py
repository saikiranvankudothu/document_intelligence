# app/services/embeddings_store.py
import os
import faiss
import numpy as np
import pickle
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer
from app.config import BASE_DIR
import sqlite3
import json

EMB_MODEL = os.environ.get("EMB_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
INDEX_DIR = os.path.join(BASE_DIR, "vectorstore")
os.makedirs(INDEX_DIR, exist_ok=True)
INDEX_PATH = os.path.join(INDEX_DIR, "faiss.index")
META_PATH = os.path.join(INDEX_DIR, "meta.pkl")  # map id -> metadata
DIM_PATH = os.path.join(INDEX_DIR, "dim.json")
# lazy load
_model = None
_index = None
_metadata = None

def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(EMB_MODEL)
    return _model


def save_index():
    global _index, _metadata
    if _index is not None:
        faiss.write_index(_index, INDEX_PATH)
    with open(META_PATH, "wb") as f:
        pickle.dump(_metadata, f)

def add_texts(texts: List[str], metadatas: List[Dict[str, Any]]):
    """
    texts: list of strings
    metadatas: list of dicts (same length) e.g. {"doc_id":123, "section_id":45, "text": "..."}
    """
    model = get_model()
    emb = model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
    dim = emb.shape[1]
    _init_index(dim)

    # ensure index is of correct dim — if not, recreate (simple approach)
    if _index.ntotal == 0:
        # If IndexFlatIP, nothing to check
        pass

    start_id = _index.ntotal
    _index.add(emb)  # adds vectors
    # assign metadata ids: use integer ids starting from 0 to ntotal-1
    for i, md in enumerate(metadatas):
        _metadata[start_id + i] = md
    save_index()
    return list(range(start_id, start_id + len(texts)))

def search(query: str, top_k: int = 5):
    """
    Returns list of (score, metadata) for top_k
    """
    model = get_model()
    q_emb = model.encode([query], convert_to_numpy=True, normalize_embeddings=True)
    _init_index(q_emb.shape[1])
    if _index.ntotal == 0:
        return []
    scores, idxs = _index.search(q_emb, top_k)
    results = []
    for sc, idx in zip(scores[0], idxs[0]):
        if idx < 0:
            continue
        md = _metadata.get(int(idx), {})
        results.append({"score": float(sc), "metadata": md})
    return results

def clear_store():
    global _index, _metadata
    if os.path.exists(INDEX_PATH):
        os.remove(INDEX_PATH)
    if os.path.exists(META_PATH):
        os.remove(META_PATH)
    _index = None
    _metadata = None

def _init_index(dim: int):
    global _index, _metadata
    stored_dim = None
    if os.path.exists(DIM_PATH):
        try:
            import json
            with open(DIM_PATH, "r") as f:
                stored_dim = json.load(f).get("dim")
        except:
            pass

    if _index is None:
        if os.path.exists(INDEX_PATH):
            if stored_dim is not None and stored_dim != dim:
                # dimension mismatch → reset
                print(f"[WARN] FAISS index dim {stored_dim} != model dim {dim}. Recreating index.")
                os.remove(INDEX_PATH)
                os.remove(META_PATH) if os.path.exists(META_PATH) else None
                _index = faiss.IndexFlatIP(dim)
                _metadata = {}
            else:
                _index = faiss.read_index(INDEX_PATH)
        else:
            _index = faiss.IndexFlatIP(dim)

        if os.path.exists(META_PATH):
            with open(META_PATH, "rb") as f:
                _metadata = pickle.load(f)
        else:
            _metadata = {}

    # store current dim
    with open(DIM_PATH, "w") as f:
        import json
        json.dump({"dim": dim}, f)