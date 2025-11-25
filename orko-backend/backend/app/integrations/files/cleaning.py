# backend/app/integrations/files/cleaning.py
"""
ORKO AI — Text Cleaning Module
--------------------------------
Purpose:
    Takes raw extracted text from any parser (PDF, DOCX, TXT, etc.)
    and cleans it for vector embedding:
      - Normalizes characters
      - Removes headers, footers, and signatures
      - Splits long text into neat overlapping chunks

Structure:
    A. normalize_text()         → normalize and trim
    B. remove_headers_and_footers() → strip repeating junk
    C. remove_signatures()      → cut off signatures/disclaimers
    D. chunk_text()             → create embedding-friendly blocks
    E. clean_text()             → main pipeline combining A–C
"""

import re
import unicodedata


# -------------------------------
# Part A — Trim & Normalize
# -------------------------------
def normalize_text(raw: str) -> str:
    """
    Cleans and normalizes raw text from any parser:
    - Removes control characters and weird spacing
    - Normalizes unicode characters (quotes, dashes, etc.)
    - Collapses multiple spaces/newlines
    """
    if not raw:
        return ""

    # Normalize fancy unicode quotes, dashes, etc.
    clean = unicodedata.normalize("NFKC", raw)

    # Remove control / invisible chars
    clean = re.sub(r"[\x00-\x1F\x7F]", " ", clean)

    # Replace multiple spaces/tabs with one space
    clean = re.sub(r"[ \t]+", " ", clean)

    # Collapse more than 2 newlines to exactly 2
    clean = re.sub(r"\n{3,}", "\n\n", clean)

    # Strip leading/trailing spaces
    return clean.strip()


# -------------------------------
# Part B — Remove Headers & Footers
# -------------------------------
def remove_headers_and_footers(text: str) -> str:
    """
    Removes repeated headers/footers or page numbers that appear often.
    """
    if not text:
        return ""

    lines = text.splitlines()
    cleaned = []
    for line in lines:
        line_stripped = line.strip()
        if not line_stripped:
            cleaned.append("")  # keep blank lines
            continue

        # Skip lines that look like page numbers
        if re.match(r"^page\s*\d+(\s*of\s*\d+)?$", line_stripped, re.IGNORECASE):
            continue

        # Skip overly short repeating headers
        if len(line_stripped) < 40 and re.search(r"(confidential|draft|document id)", line_stripped, re.IGNORECASE):
            continue

        cleaned.append(line_stripped)

    return "\n".join(cleaned)


# -------------------------------
# Part C — Remove Signatures & Boilerplate
# -------------------------------
def remove_signatures(text: str) -> str:
    """
    Removes email-style signatures or legal boilerplate near the end.
    """
    if not text:
        return ""

    # Take last 40 lines for quick scan
    lines = text.splitlines()
    tail = "\n".join(lines[-40:])
    markers = [
        "best regards",
        "sincerely",
        "confidentiality notice",
        "do not share",
        "disclaimer",
    ]

    # If any marker appears near end, trim everything after its first occurrence
    for marker in markers:
        idx = tail.lower().find(marker)
        if idx != -1:
            cutoff = len(lines) - (len(tail[:idx].splitlines()))
            return "\n".join(lines[:cutoff]).strip()

    return text


# -------------------------------
# Part D — Chunk Long Text
# -------------------------------
def chunk_text(text: str, chunk_size: int = 3000, overlap: int = 200):
    """
    Splits cleaned text into overlapping chunks.
    Each chunk ends roughly at a sentence boundary.
    """
    if not text:
        return []

    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        if end >= len(text):
            chunks.append(text[start:].strip())
            break

        # Try to end at a period or newline near the end
        next_break = text.rfind(".", start, end)
        if next_break == -1:
            next_break = end
        chunks.append(text[start:next_break + 1].strip())
        start = max(next_break - overlap, next_break + 1)

    return [c for c in chunks if c]


# -------------------------------
# Part E — Glue Everything Together
# -------------------------------
def clean_text(raw: str) -> str:
    """
    Runs all cleaning steps in order and returns final text.
    """
    step1 = normalize_text(raw)
    step2 = remove_headers_and_footers(step1)
    step3 = remove_signatures(step2)
    return step3.strip()
