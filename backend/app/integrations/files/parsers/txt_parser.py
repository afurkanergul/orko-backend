# backend/app/integrations/files/parsers/txt_parser.py
def read_txt(path: str) -> str:
    """
    Reads plain text file content safely with UTF-8 fallback.
    """
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        return content.strip()
    except Exception as e:
        print(f"[ERROR] Failed to read TXT: {path} | {e}")
        return ""
