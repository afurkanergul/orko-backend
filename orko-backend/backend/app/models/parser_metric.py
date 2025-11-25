# backend/app/models/parser_metric.py

from datetime import datetime
from sqlalchemy import Column, DateTime, Float, JSON, String
from backend.app.db.base import Base


class ParserMetric(Base):
    """
    Unified parser metrics model (v1 → v7)

    This model is intentionally conservative on columns so that:
      - Older DB schemas (created before Step 6.5) still work
      - Newer evaluators (v2–v7) can serialize richer blobs into JSON fields

    Version mapping (how data is stored):

      v1 (Step 6):
        - total, correct, accuracy
        - per_domain_accuracy

      v2 (Step 6.5):
        - error_buckets
        - confusion_matrix

      v3–v4:
        - per_domain_prf (precision/recall/F1 + tp/fp/fn per domain)

      v5+:
        - per_action (optional action-level metrics, can store PRF or counts)
        - Additional metrics can be nested inside existing JSON blobs to
          avoid schema churn.
    """

    __tablename__ = "parser_metrics"

    # Primary key (UUID string)
    id = Column(String, primary_key=True, index=True)

    # Logical run identifier for grouping runs (CI runs, nightly evals, etc.)
    run_id = Column(String, index=True)

    # Timestamp of when this metric row was created
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # ============================
    # v1 (Step 6) Core Metrics
    # ============================
    total = Column(Float)
    correct = Column(Float)
    accuracy = Column(Float)

    # Domain-level accuracy percentages
    # Example: { "trading": 0.92, "finance": 0.88, ... }
    per_domain_accuracy = Column(JSON)

    # Action-level classification metrics (optional, multi-version)
    # Example (v5+): { "create_contract": {...}, "restart_service": {...} }
    per_action = Column(JSON)

    # ============================
    # v2 (Step 6.5) Advanced Metrics
    # ============================

    # The parser/engine version used for this evaluation run
    # Example: "v1", "v2", "v7"
    engine_version = Column(String, nullable=True)

    # Error buckets (e.g., domain_mismatch, action_mismatch, parameters_mismatch)
    # Example: { "domain_mismatch": 5, "action_mismatch": 3, "parameters_mismatch": 2 }
    error_buckets = Column(JSON, nullable=True)

    # Domain-level confusion matrix (expected → predicted → count)
    # Example: { "trading": { "finance": 1, "trading": 9 }, "finance": { ... } }
    confusion_matrix = Column(JSON, nullable=True)

    # Domain-level Precision/Recall/F1 + tp/fp/fn counts
    # {
    #   "finance": { "precision":0.91, "recall":0.87, "f1":0.89, "tp":20, "fp":3, "fn":1 },
    #   "trading": { ... }
    # }
    per_domain_prf = Column(JSON, nullable=True)
