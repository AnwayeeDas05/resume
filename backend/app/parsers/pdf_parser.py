import fitz  # PyMuPDF
import logging
from typing import Tuple, List

logger = logging.getLogger("resume_matcher.pdf_parser")

def extract_text_from_pdf(file_bytes: bytes, filename: str = "document.pdf") -> Tuple[str, List[str]]:
    """
    Extracts full text and per-page text from a PDF byte stream using PyMuPDF.
    Raises ValueError if the PDF is encrypted, corrupted, or unreadable.
    """
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
    except Exception as e:
        logger.error(f"Failed to open PDF {filename}: {e}")
        raise ValueError(f"Corrupted or invalid PDF file: {str(e)}")

    if doc.is_encrypted:
        try:
            doc.authenticate("")
        except Exception:
            raise ValueError("Encrypted/Password-protected PDF cannot be processed.")

    pages_text: List[str] = []
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text("text")
        if text:
            pages_text.append(text.strip())

    doc.close()

    full_text = "\n\n".join(pages_text).strip()
    if not full_text:
        raise ValueError(f"PDF {filename} contains no extractable text (it may be scanned/image-only).")

    return full_text, pages_text

