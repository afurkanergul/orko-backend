from typing import Protocol, Any, Dict

from backend.app.learning.journal.learning_journal import LearningJournalEntry


class Brain(Protocol):
    def load_state(self) -> Dict[str, Any]:
        ...
    def update(self, data: Dict[str, Any]) -> Dict[str, Any]:
        ...
    def save_state(self) -> None:
        ...


class LearningEngine(Protocol):
    def run_cycle(self) -> None:
        """
        Executes one full learning cycle.
        """
        ...

    def generate_journal_entry(self) -> LearningJournalEntry:
        """
        Creates a structured LearningJournalEntry summarizing
        what ORKO learned this cycle.
        """
        ...
