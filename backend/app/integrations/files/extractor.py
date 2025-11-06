# backend/app/integrations/files/extractor.py
"""
ORKO AI — File Extraction & Embedding Orchestrator
---------------------------------------------------
Reads a file, cleans its contents, generates embeddings,
and stores them in the vector database.
"""

import os
import traceback

# --- Import file readers ---
from app.integrations.files.parsers.pdf_parser import read_pdf
from app.integrations.files.parsers.docx_parser import read_docx
from app.integrations.files.parsers.txt_parser import read_txt
from app.integrations.files.parsers.fallback import read_with_textract

# --- Import cleaning helpers ---
from app.integrations.files.cleaning import clean_text, chunk_text

# --- Import vector brain functions (from Step 2) ---
from app.db.vector_client import get_embedding, upsert_vector

# ✅ Add logging helper
from app.db.helpers.logs import log_ingest


def extract_and_embed(
    file_path: str,
    provider: str = "local",
    remote_id: str = "",
    name: str = "",
    org_id: int = 1,
) -> dict:
    """
    1. Detects file type and extracts text.
    2. Cleans and chunks the text.
    3. Embeds each chunk and upserts to vector DB.
    """
    result = {"ok": False, "chunks": 0, "error": None}
    try:
        # ✅ Log start
        log_ingest("extractor", f"Starting extraction for {os.path.basename(file_path)}")

        # --- Step 1: Choose parser by extension ---
        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".pdf":
            raw_text = read_pdf(file_path)
        elif ext == ".docx":
            raw_text = read_docx(file_path)
        elif ext == ".txt":
            raw_text = read_txt(file_path)
        else:
            raw_text = read_with_textract(file_path)

        if not raw_text or not raw_text.strip():
            result["error"] = "Empty or unreadable content"
            log_ingest("extractor", f"Empty or unreadable file: {file_path}", level="warn")
            return result

        # --- Step 2: Clean + chunk text ---
        cleaned = clean_text(raw_text)
        chunks = chunk_text(cleaned)
        if not chunks:
            result["error"] = "No valid chunks after cleaning"
            log_ingest("extractor", f"No valid chunks for {file_path}", level="warn")
            return result

        # --- Step 3: Embed & upsert each chunk ---
        for i, chunk in enumerate(chunks):
            try:
                emb = get_embedding(chunk)
                vector_id = f"{remote_id or os.path.basename(file_path)}:{i}"
                meta = {
                    "provider": provider,
                    "remote_id": remote_id,
                    "name": name or os.path.basename(file_path),
                    "org_id": org_id,
                    "chunk_index": i,
                    "source": "file",
                }
                upsert_vector(vector_id, emb, meta)
            except Exception as e_chunk:
                log_ingest(
                    "extractor",
                    f"Embedding failed for {file_path} chunk {i}: {e_chunk}",
                    level="error",
                )
                print(f"[ERROR] Embedding failed for chunk {i}: {e_chunk}")

        result.update({"ok": True, "chunks": len(chunks)})

        # ✅ Log success
        log_ingest(
            "extractor", f"Extracted & embedded {len(chunks)} chunks from {file_path}"
        )

        print(f"✅ Extracted & embedded {len(chunks)} chunks from {file_path}")
        return result

    except Exception as e:
        tb = traceback.format_exc()
        print(f"[FATAL] Extraction failed for {file_path}:\n{tb}")
        result["error"] = str(e)
        # ✅ Log fatal error
        log_ingest("extractor", f"Fatal extraction error for {file_path}: {e}", level="error")
        return result


# --- Optional local test runner ---
if __name__ == "__main__":
    # You can test quickly with a small text file
    test_path = "samples/test.txt"   # update path if needed
    summary = extract_and_embed(
        file_path=test_path,
        provider="local",
        remote_id="demo123",
        name="Test Doc"
    )
    print(summary)
