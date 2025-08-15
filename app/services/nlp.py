import re
from collections import Counter
from typing import List

_SENT_SPLIT = re.compile(r'(?<=[\.!?])\s+(?=[A-Z0-9])|[\r\n]{2,}')

def split_sentences(text: str) -> List[str]:
    chunks = [c.strip() for c in _SENT_SPLIT.split(text) if c.strip()]
    return chunks

_WORD_RE = re.compile(r"[A-Za-z][A-Za-z\-']+")

def top_keywords(texts: List[str], k: int = 8) -> List[str]:
    # very light keywording: term frequency minus stop-ish words
    stop = set(("""
    the of and to a in for is on with that as by be are from this it an or at
    we you your our their they he she i was were been than then over under into
    """).split())
    cnt = Counter()
    for t in texts:
        for w in _WORD_RE.findall(t.lower()):
            if w not in stop and len(w) > 2:
                cnt[w] += 1
    return [w for w, _ in cnt.most_common(k)]
