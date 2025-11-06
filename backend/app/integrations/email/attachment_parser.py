# backend/app/integrations/email/attachment_parser.py
# 🧠 ORKO Email Attachment Parser
# Extracts text from attachments and stages them for vector embedding.

import os
import datetime
import textract
from docx import Document
from PyPDF2 import PdfReader
from sqlalchemy import text

# ✅ Correct import path for your backend
from backend.app.db.session import engine


def extract_text_from_attachment(file_path: str) -> str:
    """
    Read and extract text from .txt, .pdf, .docx, or .xlsx files.
    Returns clean plain-text string.
    """
    if not os.path.exists(file_path):
        print(f"⚠️ File not found: {file_path}")
        return ""

    ext = os.path.splitext(file_path)[1].lower()
    text_content = ""

    try:
        if ext == ".txt":
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                text_content = f.read()

        elif ext == ".pdf":
            reader = PdfReader(file_path)
            pages = [p.extract_text() or "" for p in reader.pages]
            text_content = "\n".join(pages)

        elif ext == ".docx":
            doc = Document(file_path)
            text_content = "\n".join(p.text for p in doc.paragraphs)

        elif ext in [".xlsx", ".xls"]:
            # textract can handle Excel and other binary document formats
            text_content = textract.process(file_path).decode("utf-8", errors="ignore")

        else:
            print(f"⚠️ Unsupported file type: {ext}")
            return ""

    except Exception as e:
        print(f"⚠️ Error reading {file_path}: {e}")

    # 🧹 Clean unwanted control characters
    text_content = text_content.replace("\x00", "")
    return text_content.strip()


def log_stage_marker(filename, message_id=None):
    """
    Print a small console log showing what file has been staged for embedding.
    """
    timestamp = datetime.datetime.now().isoformat(timespec="seconds")
    print(f"🧩 [{timestamp}] Staged for embedding → File: {filename} | MessageID: {message_id}")


import re

def stage_for_embedding(filename, extracted_text, message_id=None):
    """
    Store extracted text temporarily in the database for embedding.
    Cleans text from any binary or non-printable characters that can break SQL.
    """
    try:
        # 🧹 1️⃣ Clean unwanted bytes and invisible characters
        if extracted_text:
            # Remove null bytes and non-printable Unicode ranges
            clean_text = re.sub(r"[\x00-\x1F\x7F-\x9F]", "", extracted_text)
        else:
            clean_text = ""

        with engine.connect() as conn:
            # ✅ Ensure table exists
            conn.execute(
                text("""
                    CREATE TABLE IF NOT EXISTS embedding_queue (
                        id SERIAL PRIMARY KEY,
                        message_id INTEGER,
                        filename TEXT,
                        text_content TEXT,
                        staged_at TIMESTAMP DEFAULT NOW()
                    )
                """)
            )

            # ✅ Insert clean text
            conn.execute(
                text("""
                    INSERT INTO embedding_queue (message_id, filename, text_content)
                    VALUES (:message_id, :filename, :text_content)
                """),
                {
                    "message_id": message_id,
                    "filename": filename,
                    "text_content": clean_text
                }
            )

            conn.commit()

        log_stage_marker(filename, message_id)

    except Exception as e:
        print(f"⚠️ Failed to stage {filename}: {e}")
