# backend/app/services/workflow/orchestrator.py

from __future__ import annotations

import time
import asyncio
from typing import Any, Dict, Optional, List, Callable

from backend.app.db.session import SessionLocal
from backend.app.db import models

from backend.app.services.workflow.dlq_helpers import record_dlq_failure
from backend.app.services.workflow.audit_logger import AuditLogger

# Step 7 — Telemetry
from backend.app.services.telemetry.telemetry_collector import TelemetryCollector


# A workflow step: callable(context) → Any (sync or async)
WorkflowStep = Callable[[Dict[str, Any]], Any]

# Unified Orchestrator versioning (v1 → v7 superset)
WORKFLOW_ENGINE_VERSION = "v7"


class Orchestrator:
    """
    ORKO Orchestrator (Unified v7)
    ----------------------------------
    This version merges all features you built:
    - sync + async workflow steps
    - simulate mode
    - DLQ failure pipeline
    - telemetry hooks (parser → trigger → workflow)
    - audit logging
    - latency metrics (WorkflowMetrics table)
    - structured return payload
    - safe context merging
    - workflow engine version tag

    All changes are backward-compatible.
    """

    def __init__(self) -> None:
        self.audit = AuditLogger()

    # ------------------------------------------------------------------
    # PUBLIC API (called by TriggerQueue)
    # ------------------------------------------------------------------
    async def run(
        self,
        workflow_steps: List[WorkflowStep],
        context: Optional[Dict[str, Any]] = None,
        scenario: str = "engine_run",
        workflow_name: Optional[str] = None,
        user_id: Optional[str] = None,
        simulate: bool = False,
    ) -> Dict[str, Any]:
        """
        Executes a workflow end-to-end.

        simulate=True → no steps, no DB writes, no DLQ, no audit logs.

        Returns a structured dict used by TriggerQueue and Telemetry.
        """

        context = context.copy() if context else {}

        # ===============================================================
        # SIMULATE MODE (no side-effects)
        # ===============================================================
        if simulate:
            result_payload = {
                "mode": "simulate",
                "workflow_engine_version": WORKFLOW_ENGINE_VERSION,
                "workflow_name": workflow_name,
                "parameters": context,
                "user_id": user_id,
                "scenario": scenario,
            }

            TelemetryCollector.record_workflow(
                workflow_name=workflow_name or "",
                result=result_payload,
                error=None,
            )

            return result_payload

        # ===============================================================
        # REAL EXECUTION MODE
        # ===============================================================
        start_time = time.monotonic()
        success = False
        error_message: Optional[str] = None

        try:
            # ----------------------------------------------------------
            # Execute workflow steps
            # ----------------------------------------------------------
            for step in workflow_steps:
                if not callable(step):
                    raise ValueError("Workflow step is not callable")

                if asyncio.iscoroutinefunction(step):
                    await step(context)
                else:
                    step(context)

            success = True

        except Exception as exc:
            error_message = str(exc)
            context["error"] = error_message
            success = False

            # ----------------------------------------------------------
            # DLQ handling (real mode only)
            # ----------------------------------------------------------
            record_dlq_failure(
                scenario=scenario,
                error_message=error_message,
                context=context,
            )

        finally:
            # ----------------------------------------------------------
            # Latency metrics (real mode)
            # ----------------------------------------------------------
            end_time = time.monotonic()
            duration_ms = (end_time - start_time) * 1000.0

            self._record_single_run_metric(
                duration_ms=duration_ms,
                success=success,
                scenario=scenario,
            )

            # ----------------------------------------------------------
            # Audit logging (real mode)
            # ----------------------------------------------------------
            if workflow_name and user_id:
                self.audit.log(
                    workflow_name=workflow_name,
                    parameters=context,
                    result={
                        "success": success,
                        "duration_ms": duration_ms,
                        "context": context,
                    },
                    user_id=user_id,
                )

        # ===============================================================
        # Final structured result payload
        # ===============================================================
        result_payload: Dict[str, Any] = {
            "success": success,
            "duration_ms": duration_ms,
            "context": context,
            "workflow_name": workflow_name,
            "scenario": scenario,
            "mode": "execute",
            "workflow_engine_version": WORKFLOW_ENGINE_VERSION,
        }

        # ---------------------------------------------------------------
        # Telemetry (records success/error)
        # ---------------------------------------------------------------
        TelemetryCollector.record_workflow(
            workflow_name=workflow_name or "",
            result=result_payload,
            error=None if success else error_message,
        )

        return result_payload

    # ------------------------------------------------------------------
    # INTERNAL — Write WorkflowMetrics row
    # ------------------------------------------------------------------
    def _record_single_run_metric(
        self,
        duration_ms: float,
        success: bool,
        scenario: str = "engine_run",
    ) -> None:
        """
        Writes a single WorkflowMetrics row for latency analytics.

        Non-breaking:
        - does not overwrite batches
        - does not aggregate here (dashboard does aggregation)
        """
        db = SessionLocal()
        try:
            row = models.WorkflowMetrics(
                scenario=scenario,
                total_runs=1,
                success_count=1 if success else 0,
                failure_count=0 if success else 1,
                p50_latency_ms=duration_ms,   # single-run latency
                p95_latency_ms=None,          # aggregated later
                notes="single run metric from orchestrator v7",
            )
            db.add(row)
            db.commit()
        finally:
            db.close()
