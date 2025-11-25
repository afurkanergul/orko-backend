# backend/app/services/telemetry/telemetry_collector.py

from __future__ import annotations
import time
from typing import Any, Dict
from pathlib import Path
import json


LOG_PATH = Path("backend/logs/telemetry")
LOG_PATH.mkdir(parents=True, exist_ok=True)


class TelemetryCollector:
    """
    Unified telemetry pipeline: parser → mapper → trigger → workflow.
    Captures metrics, audit events, errors, and timing.
    """

    @staticmethod
    def record(event_type: str, payload: Dict[str, Any]) -> None:
        payload["timestamp"] = time.time()
        event_file = LOG_PATH / f"{event_type}.jsonl"
        with event_file.open("a", encoding="utf-8") as f:
            f.write(json.dumps(payload) + "\n")

    @staticmethod
    def record_parser(parsed: Dict[str, Any], raw: str) -> None:
        TelemetryCollector.record("parser", {
            "raw_command": raw,
            "parsed": parsed,
            "domain": parsed.get("domain"),
            "action": parsed.get("action"),
            "context": parsed.get("context", {}),
        })

    @staticmethod
    def record_trigger(job_id: str, parsed: Dict[str, Any]) -> None:
        TelemetryCollector.record("trigger", {
            "job_id": job_id,
            "domain": parsed.get("domain"),
            "action": parsed.get("action"),
        })

    @staticmethod
    def record_workflow(workflow_name: str, result: Any, error: str | None) -> None:
        TelemetryCollector.record("workflow", {
            "workflow": workflow_name,
            "result": result,
            "error": error,
        })
