import sys, os

# Add project root to PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

# Import brains
from backend.app.learning.brains.knowledge_brain import KnowledgeBrain
from backend.app.learning.brains.pattern_brain import PatternBrain
from backend.app.learning.brains.skill_brain import SkillBrain

# Import interfaces
from backend.app.learning.types.interfaces import Brain, LearningEngine

# Import journal entry
from backend.app.learning.journal.learning_journal import LearningJournalEntry

# Import engine
from backend.app.learning.engine.engine import OrkoLearningEngine

print("ALL IMPORTS OK")
