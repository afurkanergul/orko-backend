# backend/app/integrations/files/parsers/fallback.py
import textract

def read_with_textract(path: str) -> str:
    """
    Fallback reader using textract.
    Works with many file types (PDF, DOC, PPT, etc.).
    """
    try:
        text_bytes = textract.process(path)
        return text_bytes.decode("utf-8", errors="ignore").strip()
    except Exception as e:
        print(f"[ERROR] Textract failed for {path}: {e}")
        return ""
