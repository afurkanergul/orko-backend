from pydantic import BaseModel
from typing import Optional, Literal


class WebVitalMetric(BaseModel):
    metric_type: Literal["web_vital"] = "web_vital"
    name: str
    value: float
    id: Optional[str] = None
    label: Optional[str] = None
    path: str
    timestamp_ms: Optional[int] = None


class ApiLatencyMetric(BaseModel):
    metric_type: Literal["api_latency"] = "api_latency"
    endpoint: str
    duration_ms: float
    path: str
    success: bool = True
    timestamp_ms: Optional[int] = None
