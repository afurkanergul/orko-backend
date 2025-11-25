from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Mapping, Optional, Dict

from .intent_schema import Intent
from backend.app.services.telemetry.telemetry_collector import TelemetryCollector


# Local mapping file
MAPPING_FILE = Path(__file__).with_name("intent_to_workflow.json")


class IntentMappingError(Exception):
    pass


class IntentMapper:
    """
    Unified Intent Mapper (v1 → v7)
    --------------------------------
    Features included:

    v1 – Basic intent → workflow mapping
    v2 – Slot filling (intent > context > defaults)
    v3 – Guardrail-aware mapping (blocked / high risk → safe workflows)
    v4 – Action canonicalization
    v5 – Multi-domain routing (domain + action → workflow)
    v6 – Telemetry (record mapping events)
    v7 – Mapping confidence + routing versions map_v1..map_v7
    """

    def __init__(self, mapping_path: Optional[Path] = None):
        self.path = mapping_path or MAPPING_FILE
        self.mapping: Dict[str, Any] = self._load()
        self.logger = logging.getLogger(__name__)

    # -----------------------------------------------------
    # Load mapping file
    # -----------------------------------------------------
    def _load(self) -> dict:
        if not self.path.exists():
            raise FileNotFoundError(f"Mapping file missing at {self.path}")
        return json.loads(self.path.read_text())

    # -----------------------------------------------------
    # Main router entrypoint
    # -----------------------------------------------------
    def map(self, intent: Intent, context: Mapping[str, Any] = None) -> dict:
        """
        The public method. Executes the latest version (v7).
        """
        return self.map_v7(intent, context or {})

    # -----------------------------------------------------
    # v1 — Basic mapping
    # -----------------------------------------------------
    def map_v1(self, intent: Intent) -> dict:
        cfg = self.mapping.get(intent.name)
        if not cfg:
            raise IntentMappingError(f"No mapping for intent: {intent.name}")
        return {"workflow_name": cfg["workflow_name"], "parameters": {}}

    # -----------------------------------------------------
    # v2 — Slot-filling logic
    # -----------------------------------------------------
    def _slot_fill(self, cfg: dict, intent: Intent, context: Mapping[str, Any]):
        required = cfg.get("required_params", [])
        defaults = cfg.get("defaults", {})
        intent_params = intent.parameters or {}

        filled = {}
        missing = []
        ambiguous = {}

        keys = set(required) | set(intent_params) | set(defaults)

        for key in keys:
            iv = intent_params.get(key)
            cv = context.get(key)
            dv = defaults.get(key)

            if iv is not None and cv is not None and iv != cv:
                ambiguous[key] = {"intent": iv, "context": cv}
                filled[key] = iv
                self.logger.warning(
                    f"Ambiguity: '{key}' intent={iv}, context={cv} — choosing intent."
                )
            else:
                filled[key] = iv if iv is not None else cv if cv is not None else dv

            if key in required and filled.get(key) is None:
                missing.append(key)

        return filled, missing, ambiguous

    # -----------------------------------------------------
    # v3 — Guardrail-aware routing
    # -----------------------------------------------------
    def _guardrail_routing(self, intent: Intent, cfg: dict):
        risk = intent.context.get("risk_level")
        needs_admin = intent.context.get("requires_admin")

        if risk == "blocked":
            return "blocked_action_workflow"
        if needs_admin:
            return cfg.get("admin_workflow") or cfg["workflow_name"]
        if risk == "high":
            return cfg.get("elevated_workflow") or cfg["workflow_name"]

        return cfg["workflow_name"]

    # -----------------------------------------------------
    # v4 — Canonicalize action names
    # -----------------------------------------------------
    def _canonicalize_action(self, intent: Intent):
        act = (intent.action or "").strip().lower()
        canon = {
            "create": "create",
            "make": "create",
            "add": "create",
            "remove": "delete",
            "delete": "delete",
            "update": "update",
            "modify": "update",
        }
        return canon.get(act, act)

    # -----------------------------------------------------
    # v5 — Multi-domain routing resolver
    # -----------------------------------------------------
    def _resolve_intent_key(self, intent: Intent):
        """
        Allows keys such as:
            "finance.create_report"
            "hr.create_employee"
            "general.summary"
        """
        action = self._canonicalize_action(intent)
        dom = intent.domain or "general"

        composite_key = f"{dom}.{intent.name}"
        fallback_key = intent.name

        if composite_key in self.mapping:
            return composite_key
        if fallback_key in self.mapping:
            return fallback_key

        raise IntentMappingError(f"No mapping entry for: {intent.name}")

    # -----------------------------------------------------
    # v6 – Telemetry hook
    # -----------------------------------------------------
    def _record_telemetry(self, intent: Intent, workflow_name: str, params: dict):
        TelemetryCollector.record(
            "intent_mapping",
            {
                "intent": intent.name,
                "domain": intent.domain,
                "workflow_name": workflow_name,
                "parameters": params,
                "risk": intent.context.get("risk_level"),
            },
        )

    # -----------------------------------------------------
    # v7 — Unified mapping (final)
    # -----------------------------------------------------
    def map_v7(self, intent: Intent, context: Mapping[str, Any]) -> dict:
        intent_key = self._resolve_intent_key(intent)
        cfg = self.mapping[intent_key]

        # 1️⃣ Slot fill
        params, missing, ambiguous = self._slot_fill(cfg, intent, context)

        # 2️⃣ Guardrail-aware workflow selection
        workflow_name = self._guardrail_routing(intent, cfg)

        # 3️⃣ Compute mapping confidence score
        completeness = 1.0 - (len(missing) / max(len(cfg.get("required_params", [])), 1))
        confidence = round(max(0.0, min(1.0, completeness * 0.9)), 3)

        result = {
            "workflow_name": workflow_name,
            "parameters": params,
            "missing": missing,
            "ambiguous": ambiguous,
            "confidence": confidence,
            "version": "v7",
        }

        # 4️⃣ Telemetry
        self._record_telemetry(intent, workflow_name, params)

        return result
