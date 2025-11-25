# backend/app/schemas/dashboard.py
from pydantic import BaseModel, Field
from typing import List
from datetime import datetime

# ----- Dashboard -----
class DashboardMetrics(BaseModel):
    knowledge_docs_indexed: int = Field(0, ge=0, description="Total documents successfully indexed")
    pattern_automations_suggested: int = Field(0, ge=0, description="Number of suggested automations")
    skill_accuracy_pct: float = Field(0, ge=0, le=100, description="Overall skill accuracy percent")

class DashboardResponse(BaseModel):
    metrics: DashboardMetrics
    as_of: datetime

# ----- Journal -----
class JournalEntry(BaseModel):
    id: str
    timestamp: datetime
    title: str
    summary: str
    tags: List[str] = []
    source: str
    confidence: float = Field(0.0, ge=0, le=1)
    pinned: bool = False

class JournalResponse(BaseModel):
    items: List[JournalEntry]
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
    total: int = Field(0, ge=0)
