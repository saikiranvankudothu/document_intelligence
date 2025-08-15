from fastapi import APIRouter, File, UploadFile, Body
from typing import Optional, Dict, Any
import os

from app.utils.file_handler import save_file
from app.services.extractor import extract_and_clean
from app.services.structure import detect_sections, sections_to_json
from app.services.nlp import split_sentences, top_keywords

# DB
from app.db.database import SessionLocal, engine, Base
from app.db.models import Document, Section

# ML
import numpy as np
from sentence_transformers import SentenceTransformer
import hdbscan
from sklearn.feature_extraction.text import TfidfVectorizer

router = APIRouter(prefix="/structure", tags=["Structure & Topics"])

# Create tables if not exist
Base.metadata.create_all(bind=engine)

# Lazy global model
_model: Optional[SentenceTransformer] = None
def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model

@router.post("/parse")
async def parse_structure(file: UploadFile = File(...), save: bool = False):
    """
    Upload a file, extract text, detect headings/sections, return hierarchy JSON.
    Optional: ?save=true to persist into SQLite.
    """
    file_bytes = await file.read()
    path = save_file(file_bytes, file.filename)
    ext = os.path.splitext(file.filename)[-1].replace(".", "")

    text = extract_and_clean(path, ext)
    nodes = detect_sections(text)
    payload = sections_to_json(nodes)

    if save:
        db = SessionLocal()
        try:
            doc = Document(filename=file.filename, original_path=path, text=text)
            db.add(doc); db.flush()

            def persist(node, parent_id=None):
                s = Section(document_id=doc.id, title=node["title"], level=node["level"],
                            start_line=node["start_line"], end_line=node["end_line"],
                            content=node["content"], parent_id=parent_id)
                db.add(s); db.flush()
                for ch in node["children"]:
                    persist(ch, parent_id=s.id)

            for root in payload:
                persist(root, None)
            db.commit()
            return {"document_id": doc.id, "hierarchy": payload}
        finally:
            db.close()

    return {"hierarchy": payload}

@router.post("/cluster")
async def semantic_clusters(
    file: UploadFile = File(None),
    raw_text: Optional[str] = Body(default=None),
    min_cluster_size: int = 8,
    min_samples: Optional[int] = None
):
    """
    Semantic clustering for non-heading segmentation.
    Provide either a file OR raw_text (string).
    Returns clusters with sentences and keywords.
    """
    if file is None and not raw_text:
        return {"error": "Provide a file or raw_text"}

    if file is not None:
        file_bytes = await file.read()
        path = save_file(file_bytes, file.filename)
        ext = os.path.splitext(file.filename)[-1].replace(".", "")
        text = extract_and_clean(path, ext)
    else:
        text = raw_text

    sents = split_sentences(text)
    if len(sents) < max(10, min_cluster_size):
        return {"warning": "Not enough sentences for clustering", "sentences": sents}

    model = get_model()
    emb = model.encode(sents, batch_size=64, convert_to_numpy=True, normalize_embeddings=True)

    clusterer = hdbscan.HDBSCAN(min_cluster_size=min_cluster_size, min_samples=min_samples or min_cluster_size//2,
                                metric='euclidean', cluster_selection_method='eom')
    labels = clusterer.fit_predict(emb)

    clusters: Dict[int, Dict[str, Any]] = {}
    for i, lab in enumerate(labels):
        if lab == -1:  # noise
            continue
        clusters.setdefault(lab, {"sentences": [], "idx": []})
        clusters[lab]["sentences"].append(sents[i])
        clusters[lab]["idx"].append(i)

    # Simple keywords per cluster via TF-IDF or fallback freq
    results = []
    for cid, data in sorted(clusters.items(), key=lambda kv: kv[0]):
        s_list = data["sentences"]
        if not s_list:
            continue
        try:
            tfidf = TfidfVectorizer(max_features=2000, ngram_range=(1,2), stop_words="english")
            X = tfidf.fit_transform(s_list)
            # top terms by mean tfidf
            scores = np.asarray(X.mean(axis=0)).ravel()
            terms = np.array(tfidf.get_feature_names_out())
            top_idx = np.argsort(-scores)[:8]
            keywords = terms[top_idx].tolist()
        except Exception:
            keywords = top_keywords(s_list, 8)

        results.append({
            "cluster_id": int(cid),
            "size": len(s_list),
            "keywords": keywords,
            "sentences": s_list
        })

    return {
        "num_clusters": len(results),
        "clusters": results
    }
