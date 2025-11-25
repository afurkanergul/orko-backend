from fastapi import APIRouter, Request
from backend.app.schemas.telemetry import WebVitalMetric, ApiLatencyMetric
from backend.app.db.helpers.logs import log_ingest

router = APIRouter(prefix="/api/telemetry", tags=["Telemetry"])

@router.post("/web-vitals")
async def collect_web_vitals(metric: WebVitalMetric, request: Request):
    message = (
        f"path={metric.path} "
        f"name={metric.name} "
        f"value={metric.value:.2f} "
        f"label={metric.label or ''} "
        f"id={metric.id or ''}"
    )
    log_ingest("web_vitals", message)
    return {"ok": True}

@router.post("/api-latency")
async def collect_api_latency(metric: ApiLatencyMetric, request: Request):
    message = (
        f"path={metric.path} "
        f"endpoint={metric.endpoint} "
        f"duration_ms={metric.duration_ms:.1f} "
        f"success={metric.success}"
    )
    log_ingest("api_metrics", message)
    return {"ok": True}
