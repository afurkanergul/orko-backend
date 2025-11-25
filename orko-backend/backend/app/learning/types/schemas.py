from dataclasses import dataclass
from typing import Any, Dict

@dataclass
class LearningJournalEntry:
    """
    A structured learning journal entry produced by the Learning Engine.
    (Updated to match engine.py fields exactly.)
    """
    id: str
    timestamp: str
    brain: str
    summary: str
    metadata: Dict[str, Any]
