from __future__ import annotations

from typing import Dict, Any, Mapping
from backend.app.services.telemetry.telemetry_collector import TelemetryCollector


class SlotFillingEngine:
    """
    Unified Slot Filling Engine (v1 → v7)
    -------------------------------------
    Capabilities:
      - v1: Required + defaults
      - v2: Priority: intent > context > defaults
      - v3: Ambiguity detection (intent vs context differ)
      - v4: Missing-parameter detection
      - v5: Domain-aware default expansion
      - v6: Telemetry logging (Step 7)
      - v7: Confidence scoring + structural validation
    """

    # ---------------------------------------------------------
    # v5 — Domain-aware default expansions (extensible)
    # ---------------------------------------------------------
    DOMAIN_DEFAULTS = {
        "finance": {"currency": "USD"},
        "logistics": {"unit": "tons", "region": "global"},
        "hr": {"employment_type": "full_time"},
        "it_ops": {"env": "production"},
    }

    # ---------------------------------------------------------
    # MAIN PUBLIC METHOD (v7)
    # ---------------------------------------------------------
    def fill(
        self,
        workflow_template: Dict[str, Any],
        parsed_intent: Dict[str, Any],
        context: Mapping[str, Any] = None,
    ) -> Dict[str, Any]:
        context = context or {}
        parameters = parsed_intent.get("parameters", {})
        domain = parsed_intent.get("domain")

        required = workflow_template.get("required_parameters", [])
        defaults = workflow_template.get("defaults", {})

        # Domain defaults
        domain_defaults = self.DOMAIN_DEFAULTS.get(domain, {})

        filled = {}
        missing = []
        ambiguous = {}

        # all keys we need to consider
        all_keys = set(required) | set(parameters) | set(defaults) | set(domain_defaults)

        # -----------------------------------------------------
        # SLOT FILLING PRIORITY (v2)
        #     intent > context > domain defaults > template defaults
        # -----------------------------------------------------
        for key in all_keys:
            iv = parameters.get(key)
            cv = context.get(key)
            ddv = domain_defaults.get(key)
            dv = defaults.get(key)

            # ------------ v3: Ambiguity detection ------------
            if iv is not None and cv is not None and iv != cv:
                ambiguous[key] = {"intent": iv, "context": cv}
                filled[key] = iv  # choose intent
            else:
                filled[key] = (
                    iv
                    if iv is not None
                    else cv
                    if cv is not None
                    else ddv
                    if ddv is not None
                    else dv
                )

            # ------------ v4: Missing slot detection ------------
            if key in required and filled.get(key) is None:
                missing.append(key)

        # -----------------------------------------------------
        # v7 — Confidence Score
        #   completeness of required params * no ambiguity penalty
        # -----------------------------------------------------
        total_required = len(required) or 1
        completeness = 1.0 - (len(missing) / total_required)
        ambiguity_penalty = 1.0 - min(len(ambiguous) * 0.1, 0.5)
        confidence = max(0.0, min(1.0, round(completeness * ambiguity_penalty, 3)))

        final_payload = {
            "parameters": filled,
            "missing": missing,
            "ambiguous": ambiguous,
            "confidence": confidence,
        }

        # -----------------------------------------------------
        # v6 — Telemetry (Step 7)
        # -----------------------------------------------------
        TelemetryCollector.record(
            "slot_filling",
            {
                "parameters": filled,
                "missing": missing,
                "ambiguous": ambiguous,
                "domain": domain,
                "confidence": confidence,
            },
        )

        # Return unified slot-filled structure
        return final_payload
