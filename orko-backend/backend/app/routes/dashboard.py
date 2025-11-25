# backend/app/routes/dashboard.py
from fastapi import APIRouter
from datetime import datetime
from backend.app.schemas.dashboard import (
    DashboardResponse,
    DashboardMetrics,
    JournalResponse,
    JournalEntry,
)

router = APIRouter(prefix="/api", tags=["dashboard"])

@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard():
    metrics = DashboardMetrics(
        knowledge_docs_indexed=7,
        pattern_automations_suggested=3,
        skill_accuracy_pct=95.6
    )
    return {"metrics": metrics, "as_of": datetime.utcnow()}

@router.get("/journal", response_model=JournalResponse)
async def get_journal():
    entries = [
        JournalEntry(
            id="demo-1",
            timestamp=datetime.utcnow(),
            title="Auto-learning loop completed",
            summary="ORKO Pattern Brain learned a new automation rule",
            tags=["learning","automation"],
            source="system",
            confidence=0.94,
            pinned=True
        ),
        JournalEntry(
            id="demo-2",
            timestamp=datetime.utcnow(),
            title="Drive connector synced",
            summary="New files indexed from Google Drive and SharePoint",
            tags=["drive","sync"],
            source="files",
            confidence=0.87,
            pinned=False
        ),
    ]
    return {"items": entries, "page":1, "page_size":20, "total":len(entries)}
