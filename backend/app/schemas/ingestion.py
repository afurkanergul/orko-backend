from typing import List, Optional, Any
from pydantic import BaseModel, Field

class IngestMessage(BaseModel):
    source: str = Field(..., description="telegram | whatsapp | gmail | outlook | drive | sharepoint")
    sender: str
    timestamp: str  # ISO 8601 format
    content: Optional[str] = None
    attachments: List[Any] = []
    org_id: Optional[int] = None
    channel_msg_id: Optional[str] = None

    def to_dict(self) -> dict:
        """Return a JSON-safe dict, skipping None fields."""
        return self.model_dump(exclude_none=True)
