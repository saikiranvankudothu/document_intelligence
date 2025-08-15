import os
from ..config import UPLOAD_DIR

def save_file(file, filename: str) -> str:
    """Save uploaded file to local uploads directory."""
    file_path = os.path.join(UPLOAD_DIR, filename)
    with open(file_path, "wb") as buffer:
        buffer.write(file)
    return file_path
