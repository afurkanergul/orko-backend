import uuid
from typing import Any, Dict

from sqlalchemy import inspect

from backend.app.db.session import SessionLocal
from backend.app.models.parser_metric import ParserMetric


class ParserMetricsWriter:
    """
    UNIFIED Writer (v1 → v7)

    - Detects available DB columns dynamically
    - Writes only what exists (avoids UndefinedColumn errors)
    - Supports all parser summary versions:
        v1: accuracy, total, correct, per_domain_accuracy
        v2: error buckets, confusion matrix
        v3: per_domain_prf
        v4–v7 reserved for future extensions
    """

    def __init__(self) -> None:
        # Introspect database columns once
        self.model_columns = self._load_model_columns()

    def _load_model_columns(self):
        """Fetch actual DB columns to avoid inserting into non-existent fields."""
        try:
            mapper = inspect(ParserMetric)
            return set(mapper.columns.keys())
        except Exception:
            return set()

    def _safe_field(self, field: str, value: Any) -> Dict[str, Any]:
        """
        Returns {field: value} only if that field exists in DB.
        Prevents psycopg2.errors.UndefinedColumn crashes.
        """
        return {field: value} if field in self.model_columns else {}

    def save(self, summary: Dict[str, Any], run_id: str | None = None) -> ParserMetric:
        db = SessionLocal()

        try:
            run_id = run_id or str(uuid.uuid4())

            # Mandatory fields — always included
            data = {
                "id": str(uuid.uuid4()),
                "run_id": run_id,
                "total": summary.get("total"),
                "correct": summary.get("correct"),
                "accuracy": summary.get("accuracy"),
            }

            # Optional fields — included only if DB table has them
            optional_fields = {
                "per_domain_accuracy": summary.get("per_domain_accuracy"),
                "per_action": summary.get("per_action"),
                "engine_version": summary.get("version"),
                "error_buckets": summary.get("error_buckets"),
                "confusion_matrix": summary.get("confusion_matrix"),
                "per_domain_prf": summary.get("per_domain_prf"),
            }

            for field, value in optional_fields.items():
                data.update(self._safe_field(field, value))

            # Create and store
            metric = ParserMetric(**data)

            db.add(metric)
            db.commit()
            db.refresh(metric)

            return metric

        finally:
            db.close()
