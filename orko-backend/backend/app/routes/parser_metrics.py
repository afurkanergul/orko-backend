from typing import Any, Dict, Optional, Generator
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.db.session import SessionLocal
from backend.app.models.parser_metric import ParserMetric

router = APIRouter()


# Correct DB session generator
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/parser/metrics/latest")
def get_latest_parser_metrics(
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Return the latest parser evaluation metrics snapshot.
    This endpoint does NOT require authentication because it's used
    for internal monitoring (Grafana, admin dashboards, eval pipelines).
    """
    metric: Optional[ParserMetric] = (
        db.query(ParserMetric)
        .order_by(ParserMetric.created_at.desc())
        .first()
    )

    if not metric:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No parser metrics found."
        )

    return {
        "run_id": metric.run_id,
        "created_at": metric.created_at,
        "total": metric.total,
        "correct": metric.correct,
        "accuracy": metric.accuracy,
        "per_domain_accuracy": metric.per_domain_accuracy,
        "per_action": metric.per_action,
    }
