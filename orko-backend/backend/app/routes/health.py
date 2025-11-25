# backend/app/routes/health.py
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from backend.app.db.session import SessionLocal
import traceback

router = APIRouter()

# Helper to check one channel
def check_channel(source: str) -> dict:
    """Reads the latest ingestion_audit record and returns status summary."""
    db: Session = SessionLocal()
    try:
        result = db.execute(
            f"""
            SELECT status, error, updated_at
            FROM ingestion_audit
            WHERE source = :source
            ORDER BY updated_at DESC
            LIMIT 1
            """,
            {"source": source},
        ).fetchone()

        if not result:
            return {"status": "warn", "last_audit": None, "notes": "No records yet"}

        status, error, updated_at = result
        if not updated_at:
            updated_at = datetime.now(timezone.utc)

        age_hours = (datetime.now(timezone.utc) - updated_at).total_seconds() / 3600

        if status == "processed" and age_hours <= 6:
            return {"status": "ok", "last_audit": updated_at.isoformat(), "notes": "Recent success"}
        elif status == "processed" and age_hours <= 24:
            return {"status": "warn", "last_audit": updated_at.isoformat(), "notes": "Stale but ok"}
        elif status == "failed":
            return {"status": "fail", "last_audit": updated_at.isoformat(), "notes": error or "Failed"}
        else:
            return {"status": "warn", "last_audit": updated_at.isoformat(), "notes": "Unknown state"}

    except Exception as e:
        print(f"⚠️ Health check error for {source}: {e}")
        traceback.print_exc()
        return {"status": "fail", "last_audit": None, "notes": str(e)}
    finally:
        db.close()


@router.get("/status/ingestion")
def ingestion_status():
    """Returns health summary for all ingestion channels."""
    services = {
        "telegram": check_channel("telegram"),
        "whatsapp": check_channel("whatsapp"),
        "gmail": check_channel("gmail"),
        "drive": check_channel("drive"),
        "sharepoint": check_channel("sharepoint"),
    }

    total_ok = sum(1 for s in services.values() if s["status"] == "ok")
    total_fail = sum(1 for s in services.values() if s["status"] == "fail")
    total_warn = sum(1 for s in services.values() if s["status"] == "warn")

    overall_ok = total_fail == 0
    return JSONResponse(
        {
            "ok": overall_ok,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "services": services,
            "summary": {"total_ok": total_ok, "total_fail": total_fail, "total_warn": total_warn},
        }
    )
