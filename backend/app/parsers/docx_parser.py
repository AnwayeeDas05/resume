import io
import logging
from typing import Tuple, List
import docx

logger = logging.getLogger("resume_matcher.docx_parser")

def extract_text_from_docx(file_bytes: bytes, filename: str = "document.docx") -> Tuple[str, List[str]]:
    """
    Extracts text from DOCX document bytes using python-docx.
    Inspects paragraphs and tables.
    """
    try:
        file_stream = io.BytesIO(file_bytes)
        doc = docx.Document(file_stream)
    except Exception as e:
        logger.error(f"Failed to parse DOCX {filename}: {e}")
        raise ValueError(f"Corrupted or invalid DOCX document: {str(e)}")

    paragraphs: List[str] = []
    for p in doc.paragraphs:
        txt = p.text.strip()
        if txt:
            paragraphs.append(txt)

    # Also extract text from any tables in the resume
    for table in doc.tables:
        for row in table.rows:
            row_text = [cell.text.strip() for cell in row.cells if cell.text.strip()]
            if row_text:
                paragraphs.append(" | ".join(row_text))

    full_text = "\n".join(paragraphs).strip()
    if not full_text:
        raise ValueError(f"DOCX {filename} contains no extractable text.")

    return full_text, paragraphs

