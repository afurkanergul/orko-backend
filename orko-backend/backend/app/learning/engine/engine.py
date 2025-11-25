from datetime import datetime
import uuid

from backend.app.learning.journal.learning_journal import LearningJournal
from backend.app.learning.types.schemas import LearningJournalEntry

from backend.app.learning.brains.knowledge_brain import KnowledgeBrain
from backend.app.learning.brains.pattern_brain import PatternBrain
from backend.app.learning.brains.skill_brain import SkillBrain


class OrkoLearningEngine:
    def __init__(self):
        self.journal = LearningJournal()
        self.knowledge = KnowledgeBrain()
        self.pattern = PatternBrain()
        self.skill = SkillBrain()

    # ------------------------------------------------------------
    # Utility helpers
    # ------------------------------------------------------------
    def normalize(self, value, max_value=50):
        v = min(value, max_value)
        return v / max_value

    def heuristic_signal(self, heuristics):
        signal = 0.0
        for brain, h in heuristics.items():
            text = h.get("insight", "").lower()

            if "high" in text:
                signal += 1
            elif "moderate" in text:
                signal += 0.5
            elif "no" in text:
                signal += 0

        return signal / 3

    # ------------------------------------------------------------
    # Stability Rules
    # ------------------------------------------------------------
    def apply_stability_rules(self):
        # Prevent runaway confidence and memory explosion
        for b in [self.knowledge, self.pattern, self.skill]:
            b.meta["confidence_level"] = min(1.0, max(0.0, b.meta["confidence_level"]))
            b.meta["memory_factor"] = min(2.0, max(0.5, b.meta["memory_factor"]))

    # ------------------------------------------------------------
    # Diminishing Returns
    # ------------------------------------------------------------
    def apply_diminishing_returns(self, strength):
        if self.journal.entry_count() > 25:
            return strength * 0.8
        return strength

    # ------------------------------------------------------------
    # Decay trigger logic
    # ------------------------------------------------------------
    def maybe_apply_long_term_decay(self):
        if self.journal.entry_count() % 5 == 0:
            self.knowledge.decay_long_term()
            self.pattern.decay_long_term()
            self.skill.decay_long_term()
            return self.record_decay_event()
        return None

    def record_decay_event(self):
        entry = LearningJournalEntry(
            id=str(uuid.uuid4()),
            timestamp=datetime.utcnow().isoformat(),
            brain="system",
            summary="Long-term decay applied.",
            metadata={
                "knowledge": self.knowledge.meta,
                "pattern": self.pattern.meta,
                "skill": self.skill.meta
            }
        )
        self.journal.append_entry(entry)
        return entry

    # ------------------------------------------------------------
    # Event mapping
    # ------------------------------------------------------------
    def map_event_type(self, event):
        tag = (event.get("brain") or event.get("tag") or "").lower()

        if tag == "knowledge":
            return {"knowledge": {"docs_added": 1}}
        if tag == "pattern":
            return {"pattern": {"patterns": 1}}
        if tag == "skill":
            return {"skill": {"skills": 1}}

        return {"system": {}}

    # ------------------------------------------------------------
    # Single event processor
    # ------------------------------------------------------------
    def process_event(self, event: dict):
        mapped = self.map_event_type(event)

        if "knowledge" in mapped:
            self.knowledge.update(mapped["knowledge"])
        if "pattern" in mapped:
            self.pattern.update(mapped["pattern"])
        if "skill" in mapped:
            self.skill.update(mapped["skill"])

        entry = LearningJournalEntry(
            id=str(uuid.uuid4()),
            timestamp=datetime.utcnow().isoformat(),
            brain=event.get("brain", "system"),
            summary=event.get("title", "Timeline event processed"),
            metadata={"event": event, "mapped_update": mapped}
        )

        self.journal.append_entry(entry)
        return entry

    # ------------------------------------------------------------
    # Batch processor
    # ------------------------------------------------------------
    def process_events(self, events: list):
        for ev in events:
            self.process_event(ev)

        heuristic_entry = self.record_heuristic_insights()
        score_entry = self.record_scores()
        strength_entry = self.record_learning_strength()

        return {
            "heuristics": heuristic_entry,
            "scores": score_entry,
            "learning_strength": strength_entry
        }

    # ------------------------------------------------------------
    # Insight collection + snapshots
    # ------------------------------------------------------------
    def collect_all_insights(self):
        return {
            "knowledge": self.knowledge.collect_insights(),
            "pattern": self.pattern.collect_insights(),
            "skill": self.skill.collect_insights()
        }

    def generate_journal_entry(self):
        insights = self.collect_all_insights()
        entry = LearningJournalEntry(
            id=str(uuid.uuid4()),
            timestamp=datetime.utcnow().isoformat(),
            brain="system",
            summary="Periodic learning snapshot.",
            metadata=insights
        )
        return entry

    # ------------------------------------------------------------
    # Heuristics
    # ------------------------------------------------------------
    def run_heuristics(self):
        return {
            "knowledge": self.knowledge.analyze(),
            "pattern": self.pattern.analyze(),
            "skill": self.skill.analyze()
        }

    def record_heuristic_insights(self):
        insights = self.run_heuristics()
        entry = LearningJournalEntry(
            id=str(uuid.uuid4()),
            timestamp=datetime.utcnow().isoformat(),
            brain="system",
            summary="Heuristic learning analysis completed.",
            metadata=insights
        )
        self.journal.append_entry(entry)
        return entry

    # ------------------------------------------------------------
    # Scores
    # ------------------------------------------------------------
    def run_scores(self):
        return {
            "knowledge": self.knowledge.score(),
            "pattern": self.pattern.score(),
            "skill": self.skill.score()
        }

    def record_scores(self):
        scores = self.run_scores()
        entry = LearningJournalEntry(
            id=str(uuid.uuid4()),
            timestamp=datetime.utcnow().isoformat(),
            brain="system",
            summary="Learning score evaluation completed.",
            metadata=scores
        )
        self.journal.append_entry(entry)
        return entry

    # ------------------------------------------------------------
    # Learning strength
    # ------------------------------------------------------------
    def compute_learning_strength(self):
        scores = self.run_scores()
        heuristics = self.run_heuristics()

        confidences = [
            scores["knowledge"]["confidence"],
            scores["pattern"]["confidence"],
            scores["skill"]["confidence"]
        ]
        avg_confidence = sum(confidences) / 3

        total_weight = (
            scores["knowledge"]["weight"] +
            scores["pattern"]["weight"] +
            scores["skill"]["weight"]
        )
        normalized_weight = self.normalize(total_weight)

        h_signal = self.heuristic_signal(heuristics)

        strength = (
            (avg_confidence * 0.6) +
            (normalized_weight * 0.3) +
            (h_signal * 0.1)
        )

        return {
            "confidence_avg": avg_confidence,
            "weight_normalized": normalized_weight,
            "heuristic_signal": h_signal,
            "learning_strength": round(strength, 4)
        }

    def record_learning_strength(self):
        strength = self.compute_learning_strength()
        entry = LearningJournalEntry(
            id=str(uuid.uuid4()),
            timestamp=datetime.utcnow().isoformat(),
            brain="system",
            summary="Learning strength evaluation completed.",
            metadata=strength
        )
        self.journal.append_entry(entry)
        return entry

    # ------------------------------------------------------------
    # Learning application to all brains
    # ------------------------------------------------------------
    def apply_learning_to_all(self, strength: float):
        self.knowledge.apply_learning(strength)
        self.pattern.apply_learning(strength)
        self.skill.apply_learning(strength)

    # ------------------------------------------------------------
    # Meta evolution log
    # ------------------------------------------------------------
    def record_meta_evolution(self, strength):
        entry = LearningJournalEntry(
            id=str(uuid.uuid4()),
            timestamp=datetime.utcnow().isoformat(),
            brain="system",
            summary="Brain meta updated based on learning strength.",
            metadata={
                "knowledge": self.knowledge.meta,
                "pattern": self.pattern.meta,
                "skill": self.skill.meta,
                "strength": strength
            }
        )
        self.journal.append_entry(entry)
        return entry

    # ------------------------------------------------------------
    # FULL CYCLE
    # ------------------------------------------------------------
    def run_cycle(self):
        snapshot = self.generate_journal_entry()
        self.journal.append_entry(snapshot)

        heuristics = self.record_heuristic_insights()
        scores = self.record_scores()
        learning_strength = self.record_learning_strength()

        # Extract strength
        strength_value = learning_strength.metadata["learning_strength"]

        # Apply diminishing returns FIRST
        strength_value = self.apply_diminishing_returns(strength_value)

        # Apply learning
        self.apply_learning_to_all(strength_value)

        # Apply stability rules
        self.apply_stability_rules()

        # Long-term decay (every 5 journal entries)
        decay_entry = self.maybe_apply_long_term_decay()

        # Meta evolution log
        meta_entry = self.record_meta_evolution(strength_value)

        return {
            "snapshot": snapshot,
            "heuristics": heuristics,
            "scores": scores,
            "learning_strength": learning_strength,
            "meta": meta_entry,
            "decay": decay_entry
        }
