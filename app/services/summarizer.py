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
    out = summarizer(text, max_new_tokens=max_length, min_length=min_length, do_sample=False, clean_up_tokenization_spaces=True)
    return out[0]["summary_text"]

def summarize_sections(sections: List[dict], per_section_max: int = 120) -> List[dict]:
    """
    Summarize multiple sections in batches for better performance.
    """
    summarizer = get_summarizer()

    # Prepare inputs
    inputs = []
    titles = []
    for s in sections:
        content = s.get("content", "") or ""
        titles.append(s.get("title"))
        if not content.strip():
            inputs.append(None)  # placeholder for empty
        else:
            inputs.append(content)

    # Filter out None values before sending to model
    batch_texts = [txt for txt in inputs if txt]

    # Run summarizer in a single batch call
    summaries = []
    if batch_texts:
        raw_summaries = summarizer(
            batch_texts,
            max_new_tokens=per_section_max,
            min_length=30,
            do_sample=False,
            clean_up_tokenization_spaces=True
        )
        summaries = [r["summary_text"] for r in raw_summaries]

    # Rebuild final list with correct order
    results = []
    summary_idx = 0
    for i, content in enumerate(inputs):
        if content is None:
            results.append({"title": titles[i], "summary": ""})
        else:
            results.append({"title": titles[i], "summary": summaries[summary_idx]})
            summary_idx += 1

    return results

