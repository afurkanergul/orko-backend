from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
from uuid import uuid4

from backend.app.db.session import SessionLocal
from backend.app.models.parser_log import ParserLog

from backend.app.services.parsing.ai_parser import AIParser
from backend.app.services.parsing.masking import mask_reasoning
from backend.app.services.parsing.canonicalizer import canonicalize

from backend.app.services.parser.intent_mapper import IntentMapper
from backend.app.services.parser.slot_filling import SlotFillingEngine  # kept for compatibility
from backend.app.services.parser.intent_schema import Intent

# Step 7 – Telemetry
from backend.app.services.telemetry.telemetry_collector import TelemetryCollector


# ============================================================
# Directory Setup
# ============================================================
BASE_DIR = Path(__file__).resolve().parent
CONFIG_DIR = BASE_DIR / "config"
PROMPT_TEMPLATES_DIR = BASE_DIR / "prompt_templates"


def _read_file(path: Path) -> str:
    if not path.exists():
        return ""
    with path.open("r", encoding="utf-8") as f:
        return f.read()


def get_prompt_version(domain: str) -> Tuple[int, str]:
    """
    Reads prompt_versions.json and returns (version, updated_at) for a given domain.
    Falls back to version=1 if not found.
    """
    version_file = CONFIG_DIR / "prompt_versions.json"
    if not version_file.exists():
        return 1, ""
    with version_file.open("r", encoding="utf-8") as f:
        all_meta = json.load(f)
    meta = all_meta.get(domain, {})
    return meta.get("version", 1), meta.get("updated_at", "")


# ============================================================
# Guardrails (Non-destructive)
# ============================================================

def load_guardrails() -> Dict[str, Any]:
    """
    Loads guardrails configuration from config/guardrails.json or local fallback.
    """
    primary = CONFIG_DIR / "guardrails.json"
    fallback = BASE_DIR / "guardrails.json"
    path = primary if primary.exists() else fallback
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def apply_guardrails(parsed: Dict[str, Any]) -> Dict[str, Any]:
    """
    Applies simple risk-level tagging based on action verbs.
    - Does NOT mutate action/domain.
    - Only sets risk_level + appends guardrail_flags.
    """
    cfg = load_guardrails()

    allowed = set(cfg.get("allowed_verbs", []))
    risky = set(cfg.get("risky_verbs", []))
    blocked = set(cfg.get("blocked_verbs", []))

    action = (parsed.get("action") or "").lower()
    flags: list[str] = []

    # Preserve any existing flags from upstream (AIParser, etc.)
    parsed.setdefault("context", {})
    existing_flags = parsed["context"].get("guardrail_flags") or []
    if not isinstance(existing_flags, list):
        existing_flags = [str(existing_flags)]

    if action in blocked:
        flags.append("blocked_action")
        parsed["risk_level"] = "blocked"
    elif action in risky:
        flags.append("risky_action")
        parsed["risk_level"] = "high"
    elif action in allowed:
        parsed["risk_level"] = "low"
    else:
        flags.append("unknown_action")
        parsed["risk_level"] = "medium"

    # Merge flags (deduplicated)
    merged_flags = list(dict.fromkeys(existing_flags + flags))
    parsed["context"]["guardrail_flags"] = merged_flags

    return parsed


# ============================================================
# Lightweight Fallback Parser (EXTREME BACKUP ONLY)
# ============================================================


class CommandParser:
    """
    Very simple heuristic parser.
    In v7 we use this ONLY when AIParser hard-fails or returns no usable result.
    It must NOT override AIParser in normal operation.
    """

    def __init__(self) -> None:
        self.intent_schema: Dict[str, Any] = self._load_json(
            CONFIG_DIR / "intent_schema.json"
        )
        self.guardrails: Dict[str, Any] = self._load_json(
            CONFIG_DIR / "guardrails.json"
        )

        self.prompt_versions: Dict[str, Any] = self._load_json(
            CONFIG_DIR / "prompt_versions.json"
        )

    def _load_json(self, path: Path, default: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if not path.exists():
            return default or {}
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def _guess_domain(self, text: str, default: str) -> str:
        """
        Heuristic domain guess.
        This is only used when AIParser fails completely.
        It MUST NOT be used to override a valid AIParser domain.
        """
        t = text.lower()

        # Match your 19 domains using simple keyword heuristics
        if any(k in t for k in ["contract", "hedge", "pnl", "hedging", "mt", "shipment"]):
            return "trading"
        if any(k in t for k in ["ship", "vessel", "eta", "load", "port", "truck", "warehouse", "delivery"]):
            return "logistics"
        if any(k in t for k in ["invoice", "cashflow", "pnl", "tax", "budget", "expense"]):
            return "finance"
        if any(k in t for k in ["employee", "onboarding", "vacation", "leave", "hr"]):
            return "hr"
        if any(k in t for k in ["service", "incident", "cluster", "server", "restart", "patch"]):
            return "it_ops"
        if any(k in t for k in ["microservice", "load test", "deploy pipeline", "devops"]):
            return "devops"
        if any(k in t for k in ["ticket", "support case", "escalation"]):
            return "customer_support"
        if any(k in t for k in ["maintenance", "checklist", "operational risk", "incidents"]):
            return "operations"
        if any(k in t for k in ["forecast", "demand", "retention", "churn", "analytics"]):
            return "analytics"
        if any(k in t for k in ["opportunity", "pipeline", "win-loss", "sales"]):
            return "sales"
        if any(k in t for k in ["campaign", "marketing", "engagement", "competitive report"]):
            return "marketing"
        if any(k in t for k in ["purchase order", "suppliers", "vendor", "sourcing"]):
            return "procurement"
        if any(k in t for k in ["machine", "work orders", "plant", "assembly"]):
            return "manufacturing"
        if any(k in t for k in ["nda", "contract", "compliance", "regulation", "legal"]):
            return "legal"
        if any(k in t for k in ["store", "inventory", "stockout", "retail"]):
            return "retail"
        if any(k in t for k in ["grid", "outage", "energy", "renewable"]):
            return "energy"
        if any(k in t for k in ["patient", "claims", "lab results"]):
            return "healthcare_admin"
        if any(k in t for k in ["meeting", "travel request", "okr", "office supplies"]):
            return "general_admin"
        if any(k in t for k in ["knowledge base", "documentation", "specification", "docs"]):
            return "knowledge_work"

        return default

    def _extract_action(self, text: str) -> str:
        """
        SUPER crude verb extractor.
        This is ONLY used when AIParser fails.
        It must never overwrite a valid AIParser action.
        """
        parts = (text or "").strip().split()
        return parts[0].lower() if parts else "unknown"

    def parse(self, raw_text: str, domain: str = "general") -> Dict[str, Any]:
        return self.extract(raw_text, domain)

    def extract(self, raw_text: str, domain: str) -> Dict[str, Any]:
        text = raw_text or ""
        inferred_domain = self._guess_domain(text, domain)
        action = self._extract_action(text)

        return {
            "raw_text": text,
            "intent": "",
            "action": action,
            "parameters": {},
            "domain": inferred_domain,
            "context": {},
        }


# ============================================================
# ParserEngine v7 — AI-First, Fallback-Only-on-Hard-Fail
# ============================================================


class ParserEngine:
    def __init__(self) -> None:
        # Primary brain: AIParser (LLM few-shot, domain examples, etc.)
        self._ai_parser = AIParser()
        # Backup brain: CommandParser (heuristic) — only if AIParser dies
        self._fallback = CommandParser()

    # ---------------------------
    # Intent Guardrails
    # ---------------------------
    def _load_intent_guardrails(self) -> Dict[str, Any]:
        path = CONFIG_DIR / "intent_guardrails.json"
        if not path.exists():
            return {}
        try:
            with path.open("r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def _load_destructive_verbs(self) -> set[str]:
        cfg = self._load_intent_guardrails()
        verbs = cfg.get("destructive_verbs") or cfg.get("unsafe_action_verbs") or []
        return set(verbs)

    # ---------------------------
    # Helper – Decide if we must fallback
    # ---------------------------
    @staticmethod
    def _should_use_fallback(ai_parsed: Dict[str, Any]) -> bool:
        """
        Decide whether AIParser output is unusable and we should fallback
        to heuristic CommandParser.
        """
        if not ai_parsed:
            return True

        ctx = ai_parsed.get("context") or {}
        if isinstance(ctx, dict) and ctx.get("parse_error"):
            return True

        domain = ai_parsed.get("domain")
        action = ai_parsed.get("action")

        # If both are completely missing -> useless
        if (domain is None or domain == "") and (action is None or action == ""):
            return True

        return False

    # ---------------------------
    # MAIN PARSE METHOD
    # ---------------------------
    def parse_command(
        self,
        text: str,
        context: Optional[Dict[str, Any]] = None,
        domain: str = "general",
    ) -> Dict[str, Any]:

        # Make a copy of incoming context and inject domain as a soft hint
        base_context: Dict[str, Any] = dict(context or {})
        if domain and "domain" not in base_context:
            base_context["domain"] = domain

        # 1) Call AIParser (PRIMARY)
        ai_parsed: Dict[str, Any] = {}
        try:
            ai_parsed = self._ai_parser.parse(text, context=base_context) or {}
        except Exception as e:
            print("\n🔥🔥🔥 AIParser FAILED — DEBUG INFO 🔥🔥🔥")
            print("Error:", e)
            print("Command:", text)
            print("--------------------------------------------------\n")
            ai_parsed = {}

        # 2) Decide whether to fallback
        use_fallback = self._should_use_fallback(ai_parsed)

        if use_fallback:
            # --------------------------------------------
            # EXTREME CASE ONLY — heuristic backup
            # --------------------------------------------
            base_parsed = self._fallback.parse(text, domain=domain)

            parsed: Dict[str, Any] = {
                "raw_text": text,
                "intent": "",
                "action": base_parsed.get("action"),
                "parameters": base_parsed.get("parameters") or {},
                "domain": base_parsed.get("domain") or domain,
                "context": base_parsed.get("context") or {},
            }

            # Mark clearly as fallback so we can see in logs
            parsed.setdefault("context", {})
            parsed["context"]["used_fallback_parser"] = True
            parsed["context"].setdefault("confidence", 0.3)
        else:
            # --------------------------------------------
            # Normal case — we trust AIParser output shape
            # --------------------------------------------
            ai_ctx = ai_parsed.get("context") or {}
            if not isinstance(ai_ctx, dict):
                ai_ctx = {"value": ai_ctx}

            # Merge inbound context non-destructively
            merged_ctx: Dict[str, Any] = {}
            merged_ctx.update(ai_ctx)
            merged_ctx.update(base_context or {})

            final_domain = (
                ai_parsed.get("domain")
                or base_context.get("domain")
                or domain
                or "general"
            )
            final_action = ai_parsed.get("action")
            final_params = ai_parsed.get("parameters") or {}

            parsed = {
                "raw_text": text,
                "intent": ai_parsed.get("intent", ""),
                "action": final_action,
                "parameters": final_params,
                "domain": final_domain,
                "context": merged_ctx,
            }

            parsed["context"]["used_fallback_parser"] = False

        # 2.5) Canonicalization step:
        # Normalize fuzzy domain/action/params into strict canonical space.
        parsed = canonicalize(parsed, text)

        # 3) Destructive verbs + risk tiers (do NOT change domain/action)
        destructive_verbs = self._load_destructive_verbs()
        action_lower = (parsed.get("action") or "").lower()

        guardrails_cfg = self._load_intent_guardrails()
        risk_tiers = guardrails_cfg.get("risk_tiers", {}) or {}
        high_risk = set(risk_tiers.get("high_risk", []) or [])
        medium_risk = set(risk_tiers.get("medium_risk", []) or [])

        parsed.setdefault("context", {})

        # Confirmation / admin flags
        if action_lower in destructive_verbs:
            parsed["context"]["requires_confirmation"] = True

        if action_lower in medium_risk:
            parsed["context"]["requires_confirmation"] = True

        if action_lower in high_risk:
            parsed["context"]["requires_confirmation"] = True
            parsed["context"]["requires_admin"] = True

        # 4) Non-destructive guardrails (sets risk_level + flags)
        parsed = apply_guardrails(parsed)

        # 5) Confidence normalization
        try:
            conf = float(parsed["context"].get("confidence", 1.0))
        except Exception:
            conf = 1.0
        parsed["context"]["confidence"] = max(0.0, min(1.0, conf))

        # 6) Prompt version tagging
        domain_for_version = parsed.get("domain") or "general"
        version, updated_at = get_prompt_version(domain_for_version)
        parsed["prompt_version"] = version
        parsed["prompt_version_updated_at"] = updated_at

        # 7) Masked reasoning log (if any)
        reasoning = parsed.get("context", {}).get("reasoning_trace")
        masked = mask_reasoning(reasoning) if reasoning else None

        log = ParserLog(
            id=str(uuid4()),
            user_id=base_context.get("user_id"),
            command=text,
            parsed_output=parsed,
            masked_reasoning=masked,
            domain=parsed.get("domain"),
            action=parsed.get("action"),
        )

        db = SessionLocal()
        try:
            db.add(log)
            db.commit()
        finally:
            db.close()

        # 8) Telemetry
        TelemetryCollector.record_parser(parsed, text)

        return parsed

    # ---------------------------
    # Workflow Mapping
    # ---------------------------
    def map_to_workflow(self, parsed_cmd: Dict[str, Any]) -> Dict[str, Any]:
        mapper = IntentMapper()
        _slot_engine = SlotFillingEngine()  # kept for compatibility / future use

        domain = parsed_cmd.get("domain") or "general"
        action = parsed_cmd.get("action") or "unknown"
        params = parsed_cmd.get("parameters") or {}
        ctx = parsed_cmd.get("context") or {}

        intent = Intent(
            name=f"{domain}.{action}",
            parameters=params,
        )

        mapped = mapper.map(intent, ctx)

        return {
            "workflow_name": mapped["workflow_name"],
            "parameters": mapped["parameters"],
            "missing": mapped.get("missing", []),
            "ambiguous": mapped.get("ambiguous", {}),
        }


def get_default_parser_engine() -> ParserEngine:
    return ParserEngine()
