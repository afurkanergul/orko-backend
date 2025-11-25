# backend/app/db/helpers/file_ingest.py

from sqlalchemy.orm import Session
from backend.app.db.models import FileRecord
from backend.app.db.session import get_engine
from sqlalchemy import select
from datetime import datetime
import json

# 🧩 small helper for staging embeddings later
def enqueue_for_embedding(file_id: int, provider: str, name: str):
    """Simulated queue add — prints for now, real version will push to Redis later."""
    print(f"🧠 Enqueued for embedding → id={file_id} | provider={provider} | name={name}")


def upsert_file_record(session: Session, file_data: dict):
    """
    Insert a new FileRecord if it doesn't exist.
    Otherwise, skip or update timestamp.
    """
    stmt = select(FileRecord).where(FileRecord.remote_id == file_data["remote_id"])
    result = session.execute(stmt).scalar_one_or_none()

    if result:
        # Optional: update modified time if newer
        if file_data.get("modified_at") and file_data["modified_at"] != result.modified_at:
            result.modified_at = file_data["modified_at"]
            session.commit()
            print(f"🔄 Updated modified_at for {result.name}")
        return result.id

    # Insert new record
    new_file = FileRecord(
        provider=file_data["provider"],
        remote_id=file_data["remote_id"],
        name=file_data["name"],
        owner=file_data.get("owner"),
        modified_at=file_data.get("modified_at", datetime.utcnow())
    )
    session.add(new_file)
    session.commit()

    print(f"✅ Added new file: {new_file.name}")
    enqueue_for_embedding(new_file.id, new_file.provider, new_file.name)
    return new_file.id


def ingest_files_bulk(file_list: list[dict]):
    """Accepts a list of Drive/SharePoint files and inserts them all."""
    engine = get_engine()
    with Session(engine) as session:
        for f in file_list:
            try:
                upsert_file_record(session, f)
            except Exception as e:
                print(f"⚠️ Skipped file {f.get('name')} → {e}")
