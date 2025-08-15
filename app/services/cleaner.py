import re

def clean_text(text: str) -> str:
    """Basic text cleaning."""
    text = re.sub(r'\s+', ' ', text)       # remove extra spaces
    text = re.sub(r'\n+', '\n', text)      # normalize newlines
    return text.strip()
