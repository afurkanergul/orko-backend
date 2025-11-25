import sys, os

# Add project root to PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from backend.app.learning.types.interfaces import Brain, LearningEngine
from backend.app.learning.journal.learning_journal import LearningJournalEntry

print("IMPORT OK")
