from backend.app.learning.types.interfaces import Brain


class KnowledgeBrain(Brain):
    def __init__(self):
        # Internal state for this brain
        self.state = {"docs_indexed": 0}

        # Adaptive meta-learning state
        self.meta = {
            "cumulative_learning": 0.0,
            "confidence_level": 0.0,
            "memory_factor": 1.0
        }

    def load_state(self):
        """
        Return the current internal state.
        (Later this may load from disk or Redis.)
        """
        return self.state

    def update(self, data):
        """
        Update state using new incoming data.
        For now, increment docs_indexed by docs_added.
        """
        self.state["docs_indexed"] += data.get("docs_added", 0)
        return self.state

    def collect_insights(self):
        """
        Produce insights that will be included in learning snapshots.
        """
        return {
            "brain": "knowledge",
            "docs_indexed": self.state["docs_indexed"]
        }

    # ------------------------------------------------------------
    # Sub-step 2 — Part A: document spike detection
    # ------------------------------------------------------------
    def analyze(self):
        docs = self.state["docs_indexed"]

        if docs == 0:
            return {"insight": "No documents processed yet."}

        if docs < 5:
            return {"insight": "Small document activity."}

        if docs < 20:
            return {"insight": "Moderate document ingestion."}

        return {"insight": "High document ingestion — ORKO is learning a lot."}

    # ------------------------------------------------------------
    # Sub-step 2 — Part A: scoring
    # ------------------------------------------------------------
    def score(self):
        docs = self.state["docs_indexed"]

        if docs == 0:
            return {"confidence": 0.0, "weight": 0}

        if docs < 5:
            return {"confidence": 0.25, "weight": docs}

        if docs < 20:
            return {"confidence": 0.5, "weight": docs * 1.2}

        return {"confidence": 0.75, "weight": docs * 1.5}

    # ------------------------------------------------------------
    # Sub-step 3 — Part A: apply_learning() adaptive update
    # ------------------------------------------------------------
    def apply_learning(self, strength: float):
        # Growth mode
        if strength >= 0.5:
            self.meta["cumulative_learning"] += strength

            self.meta["confidence_level"] = min(
                1.0,
                self.meta["confidence_level"] + (strength * 0.1)
            )

            self.meta["memory_factor"] = min(
                2.0,
                self.meta["memory_factor"] + (strength * 0.05)
            )

        # Decay mode
        elif strength < 0.25:
            self.meta["confidence_level"] = max(
                0.0,
                self.meta["confidence_level"] - 0.05
            )

            self.meta["memory_factor"] = max(
                0.5,
                self.meta["memory_factor"] - 0.02
            )

    # ------------------------------------------------------------
    # Sub-step 2 — Part A: long-term decay
    # ------------------------------------------------------------
    def decay_long_term(self):
        """
        Organic long-term decay:
        - cumulative learning fades slowly
        - memory factor slightly decreases
        - confidence gently recalibrates
        """
        self.meta["cumulative_learning"] = max(
            0.0, self.meta["cumulative_learning"] * 0.98
        )

        self.meta["memory_factor"] = max(
            0.5, self.meta["memory_factor"] * 0.995
        )

        self.meta["confidence_level"] = min(
            1.0, self.meta["confidence_level"] * 0.995
        )

    def save_state(self):
        """
        Persist the brain's internal state.
        (Placeholder – real persistence added later.)
        """
        pass
