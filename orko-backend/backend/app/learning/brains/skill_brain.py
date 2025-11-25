from backend.app.learning.types.interfaces import Brain


class SkillBrain(Brain):
    def __init__(self):
        # Internal state for this brain
        self.state = {"skills_learned": 0}

        # Adaptive meta-learning state
        self.meta = {
            "cumulative_learning": 0.0,
            "confidence_level": 0.0,
            "memory_factor": 1.0
        }

    def load_state(self):
        """
        Return the current internal state.
        """
        return self.state

    def update(self, data):
        """
        Update state using new processed data.
        For now, increment skills_learned by 'skills'.
        """
        self.state["skills_learned"] += data.get("skills", 0)
        return self.state

    def collect_insights(self):
        """
        Generate insights for the Learning Engine to include
        in its journal entry.
        """
        return {
            "brain": "skill",
            "skills_learned": self.state["skills_learned"]
        }

    # ------------------------------------------------------------
    # Sub-step 2 — Part C: reinforcement heuristic
    # ------------------------------------------------------------
    def analyze(self):
        s = self.state["skills_learned"]

        if s == 0:
            return {"insight": "No skills triggered yet."}

        if s < 3:
            return {"insight": "Some skills executed — early reinforcement."}

        if s < 10:
            return {"insight": "Skill execution is increasing steadily."}

        return {"insight": "High-skill activity — automation strength rising."}

    # ------------------------------------------------------------
    # Sub-step 2 — Part C: scoring
    # ------------------------------------------------------------
    def score(self):
        s = self.state["skills_learned"]

        if s == 0:
            return {"confidence": 0.0, "weight": 0}

        if s < 3:
            return {"confidence": 0.3, "weight": s}

        if s < 10:
            return {"confidence": 0.6, "weight": s * 1.2}

        return {"confidence": 0.85, "weight": s * 1.6}

    # ------------------------------------------------------------
    # Sub-step 3 — Part C: adaptive learning update
    # ------------------------------------------------------------
    def apply_learning(self, strength: float):
        if strength >= 0.5:
            self.meta["cumulative_learning"] += strength * 1.2

            self.meta["confidence_level"] = min(
                1.0,
                self.meta["confidence_level"] + (strength * 0.12)
            )

            self.meta["memory_factor"] = min(
                2.0,
                self.meta["memory_factor"] + (strength * 0.06)
            )

        elif strength < 0.25:
            self.meta["confidence_level"] = max(
                0.0,
                self.meta["confidence_level"] - 0.06
            )

            self.meta["memory_factor"] = max(
                0.5,
                self.meta["memory_factor"] - 0.025
            )

    # ------------------------------------------------------------
    # Sub-step 2 — Part C: long-term decay
    # ------------------------------------------------------------
    def decay_long_term(self):
        """
        Slow natural decay affecting long-term skill reinforcement.
        """
        self.meta["cumulative_learning"] = max(
            0.0,
            self.meta["cumulative_learning"] * 0.975
        )

        self.meta["memory_factor"] = max(
            0.5,
            self.meta["memory_factor"] * 0.994
        )

        self.meta["confidence_level"] = min(
            1.0,
            self.meta["confidence_level"] * 0.994
        )

    def save_state(self):
        """
        Persist internal state.
        (Placeholder — real persistence added later.)
        """
        pass
