# backend/app/integrations/files/parsers/docx_parser.py
from docx import Document

def read_docx(path: str) -> str:
    """
    Reads paragraphs from a DOCX file and joins them into one string.
    Empty paragraphs are skipped.
    """
    try:
        doc = Document(path)
        paras = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
        return "\n".join(paras)
    except Exception as e:
        print(f"[ERROR] Failed to read DOCX: {path} | {e}")
        return ""
