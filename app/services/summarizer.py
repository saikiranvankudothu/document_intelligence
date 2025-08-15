# app/services/summarizer.py
from typing import Optional, List
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
import torch
from app.config import BASE_DIR
import os

# Choose a default summarization model. You can change to a local path for your fine-tuned model.
# Examples: "google/flan-t5-base", "facebook/bart-large-cnn", or local path "models/flan-t5-finetuned"
SUMMARIZER_MODEL = os.environ.get("SUMMARIZER_MODEL", "google/flan-t5-base")
DEVICE = 0 if torch.cuda.is_available() else -1

_tokenizer = None
_model = None
_pipeline = None

def get_summarizer():
    global _tokenizer, _model, _pipeline
    if _pipeline is None:
        # use transformers pipeline for summarization (seq2seq)
        _pipeline = pipeline("summarization", model=SUMMARIZER_MODEL, device=DEVICE, truncation=True)
    return _pipeline

def summarize_text(text: str, max_length: int = 150, min_length: int = 30) -> str:
    """
    Summarize a single text chunk. If the text is long, we chunk it outside or let transformers handle.
    """
    summarizer = get_summarizer()
    # pipeline will handle long text according to model; for very large docs consider manual chunking
    out = summarizer(text, max_length=max_length, min_length=min_length, do_sample=False, clean_up_tokenization_spaces=True)
    return out[0]["summary_text"]

def summarize_sections(sections: List[dict], per_section_max: int = 120) -> List[dict]:
    """
    sections: list of {title, level, content}
    returns list of {title, summary}
    """
    summarizer = get_summarizer()
    results = []
    for s in sections:
        content = s.get("content", "") or ""
        if not content.strip():
            results.append({"title": s.get("title"), "summary": ""})
            continue
        # If content is very long, you may want to split into chunks to avoid truncation.
        summary = summarize_text(content, max_length=per_section_max, min_length=30)
        results.append({"title": s.get("title"), "summary": summary})
    return results
