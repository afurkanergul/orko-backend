from backend.app.learning.types.interfaces import Brain


class PatternBrain(Brain):
    def __init__(self):
        # Internal state for this brain
        self.state = {"patterns_detected": 0}

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
        For now, increment patterns_detected by 'patterns'.
        """
        self.state["patterns_detected"] += data.get("patterns", 0)
        return self.state

    def collect_insights(self):
        """
        Generate insights for the Learning Engine to include
        in its journal entry.
        """
        return {
            "brain": "pattern",
            "patterns_detected": self.state["patterns_detected"]
        }

    # ------------------------------------------------------------
    # Sub-step 2 — Part B: repetition detection
    # ------------------------------------------------------------
    def analyze(self):
        p = self.state["patterns_detected"]

        if p == 0:
            return {"insight": "No patterns detected."}

        if p == 1:
            return {"insight": "One pattern detected — good start."}

        if p < 5:
            return {"insight": f"{p} repeated patterns found."}

        return {"insight": "Strong pattern activity — ORKO sees correlations."}

    # ------------------------------------------------------------
    # Sub-step 2 — Part B: scoring
    # ------------------------------------------------------------
    def score(self):
        p = self.state["patterns_detected"]

        if p == 0:
            return {"confidence": 0.0, "weight": 0}

        if p == 1:
            return {"confidence": 0.2, "weight": 1}

        if p < 5:
            return {"confidence": 0.4, "weight": p * 1.1}

        return {"confidence": 0.7, "weight": p * 1.4}

    # ------------------------------------------------------------
    # Sub-step 3 — Part B: adaptive learning update
    # ------------------------------------------------------------
    def apply_learning(self, strength: float):
        if strength >= 0.5:  # Growth phase
            self.meta["cumulative_learning"] += strength * 0.8

            self.meta["confidence_level"] = min(
                1.0,
                self.meta["confidence_level"] + (strength * 0.08)
            )

            self.meta["memory_factor"] = min(
                2.0,
                self.meta["memory_factor"] + (strength * 0.04)
            )

        elif strength < 0.25:  # Decay phase
            self.meta["confidence_level"] = max(
                0.0,
                self.meta["confidence_level"] - 0.04
            )

            self.meta["memory_factor"] = max(
                0.5,
                self.meta["memory_factor"] - 0.015
            )

    # ------------------------------------------------------------
    # Sub-step 2 — Part B: long-term decay
    # ------------------------------------------------------------
    def decay_long_term(self):
        """
        Slow natural decay affecting long-term pattern consolidation.
        """
        self.meta["cumulative_learning"] = max(
            0.0,
            self.meta["cumulative_learning"] * 0.985
        )

        self.meta["memory_factor"] = max(
            0.5,
            self.meta["memory_factor"] * 0.997
        )

        self.meta["confidence_level"] = min(
            1.0,
            self.meta["confidence_level"] * 0.997
        )

    def save_state(self):
        """
        Persist internal state.
        (Placeholder — real persistence added later.)
        """
        pass
