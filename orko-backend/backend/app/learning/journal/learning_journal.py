import json
import os
from dataclasses import asdict
from backend.app.learning.types.schemas import LearningJournalEntry

# Journal storage file — lives next to main.py at runtime
JOURNAL_FILE = "learning_journal.json"


# ------------------------------------------------------------
# Sub-step 2 — Part B: safe_load()
# ------------------------------------------------------------
def safe_load():
    """
    Safely load the JSON journal file.
    Returns an empty list if the file does not exist
    or if the JSON is malformed.
    """
    if not os.path.exists(JOURNAL_FILE):
        return []

    try:
        with open(JOURNAL_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []


# ------------------------------------------------------------
# Sub-step 2 — Part C: safe_save(entries)
# ------------------------------------------------------------
def safe_save(entries):
    """
    Safely save a list of journal entries to disk.
    Always writes clean JSON with indentation.
    """
    with open(JOURNAL_FILE, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)


# ------------------------------------------------------------
# Sub-step 3 — Part A: LearningJournal class
# ------------------------------------------------------------
class LearningJournal:
    def __init__(self):
        # Load existing entries immediately
        self.entries = safe_load()

    # --------------------------------------------------------
    # Sub-step 3 — Part B: list_entries()
    # --------------------------------------------------------
    def list_entries(self):
        """
        Return all cached journal entries.
        """
        return self.entries

    # --------------------------------------------------------
    # Sub-step 3 — Part C: append_entry()
    # --------------------------------------------------------
    def append_entry(self, entry: LearningJournalEntry):
        """
        Append a new journal entry (dataclass) and save to disk.
        """
        entry_dict = asdict(entry)

        self.entries.append(entry_dict)
        safe_save(self.entries)

    # --------------------------------------------------------
    # Sub-step 3 — Part D: clear()
    # --------------------------------------------------------
    def clear(self):
        """
        Clear all journal entries.
        """
        self.entries = []
        safe_save(self.entries)

    # --------------------------------------------------------
    # NEW: entry_count() — required for diminishing returns
    # --------------------------------------------------------
    def entry_count(self):
        """
        Return number of total journal entries.
        Used by stability and decay rules in the engine.
        """
        return len(self.entries)
