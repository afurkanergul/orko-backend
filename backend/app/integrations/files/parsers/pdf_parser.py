# backend/app/integrations/files/parsers/pdf_parser.py
from pypdf import PdfReader

def read_pdf(path: str) -> str:
    """
    Opens a PDF file safely and returns all text as one string.
    Skips unreadable pages but continues with others.
    """
    text_parts = []
    try:
        reader = PdfReader(path)
        for i, page in enumerate(reader.pages):
            try:
                text = page.extract_text()
                if text:
                    text_parts.append(text)
            except Exception as e:
                print(f"[WARN] Could not read page {i+1}: {e}")
        return "\n".join(text_parts).strip()
    except Exception as e:
        print(f"[ERROR] Failed to read PDF: {path} | {e}")
        return ""
