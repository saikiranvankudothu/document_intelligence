import fitz  # PyMuPDF
import docx
import pytesseract
from PIL import Image
from app.services.cleaner import clean_text
from concurrent.futures import ProcessPoolExecutor

def extract_text_pdf(path: str) -> str:
    """Extract text from a normal PDF."""
    text = ""
    with fitz.open(path) as pdf:
        for page in pdf:
            text += page.get_text()
    return text

def ocr_scanned_pdf(path: str, max_workers: int = 4) -> str:
    """Run OCR on scanned PDFs with multiprocessing."""
    with fitz.open(path) as pdf:
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            texts = list(executor.map(_ocr_page_image, pdf))
    return "\n".join(texts)

def extract_text_docx(path: str) -> str:
    """Extract text from DOCX files."""
    doc = docx.Document(path)
    return "\n".join([p.text for p in doc.paragraphs])

def extract_text_txt(path: str) -> str:
    """Read plain text files."""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def extract_and_clean(path: str, ext: str, enable_ocr: bool = True) -> str:
    ext = ext.lower()
    if ext == "pdf":
        text = extract_text_pdf(path)
        if enable_ocr and not text.strip():  # Only OCR if empty
            text = ocr_scanned_pdf(path)
    elif ext == "docx":
        text = extract_text_docx(path)
    elif ext == "txt":
        text = extract_text_txt(path)
    else:
        raise ValueError("Unsupported file type")
    return clean_text(text)


def _ocr_page_image(page):
    pix = page.get_pixmap()
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    return pytesseract.image_to_string(img)