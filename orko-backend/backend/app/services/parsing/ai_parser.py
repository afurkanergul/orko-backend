from __future__ import annotations

import json
from typing import Any, Dict, List, Optional, Tuple, Set

from openai import OpenAI

from backend.app.services.parsing.domain_registry import DomainRegistry


class AIParser:
    """
    ORKO Parser — SEMI-STRICT, CROSS-DOMAIN MODE

    Key ideas:

    1) Few-shots are CROSS-DOMAIN:
       - We no longer feed the model only examples from a single guessed domain.
       - Instead, we show examples from ALL configured domains.
       - Domain hints are soft only.

    2) We keep "fuzzy" actions + parameters:
       - We do NOT wipe unknown actions.
       - We keep parameters so canonicalizer + heuristics can fix them.

    3) We maintain a semi-strict catalog from domain_examples:
       - allowed_actions[domain] = {actions}
       - allowed_params[(domain, action)] = {param names}
       - default_params[(domain, action)] = canonical example parameter values
         (used to fill missing keys and normalize values).
    """

    def __init__(self, model: str = "gpt-4.1-mini") -> None:
        self.model = model
        self.client = OpenAI()
        self.registry = DomainRegistry()

        # Semi-strict catalogs
        self.allowed_actions: Dict[str, Set[str]] = {}
        self.allowed_params: Dict[Tuple[str, str], Set[str]] = {}
        self.default_params: Dict[Tuple[str, str], Dict[str, Any]] = {}

        self._build_action_catalog()

    # ============================================================
    # Catalog builder (from DomainRegistry examples)
    # ============================================================

    def _build_action_catalog(self) -> None:
        """
        Build:
          - self.allowed_actions[domain] = {action1, action2, ...}
          - self.allowed_params[(domain, action)] = {param1, param2, ...}
          - self.default_params[(domain, action)] = canonical example param values
        based on the "expected" blocks of domain_examples.
        """
        domains = getattr(self.registry, "domains", []) or []

        for domain in domains:
            cfg = self.registry.get_examples(domain) or {}
            examples = cfg.get("examples", []) or []

            actions: Set[str] = set()

            for ex in examples:
                expected = ex.get("expected") or {}
                action = expected.get("action")
                if not action:
                    continue

                actions.add(action)

                params = expected.get("parameters") or {}
                key = (domain, action)

                # Allowed parameter names
                if key not in self.allowed_params:
                    self.allowed_params[key] = set()
                self.allowed_params[key].update(params.keys())

                # Canonical default parameter values (first example wins)
                if key not in self.default_params:
                    # shallow copy is enough (flat dict)
                    self.default_params[key] = dict(params)

            if actions:
                self.allowed_actions[domain] = actions

    def _allowed_actions_text_global(self) -> str:
        """
        Build human-readable list of allowed actions for ALL domains.

        This replaces domain-specific guidance that over-biased the model.
        """
        if not self.allowed_actions:
            return (
                "There is currently no registered canonical action list.\n"
                "You MAY still propose reasonable action names, but:\n"
                "- Prefer simple verbs like 'generate_report', 'create', 'list', etc.\n"
                "- If you are very unsure, set \"action\": null and \"parameters\": {}.\n"
            )

        lines: List[str] = []
        for domain, actions in sorted(self.allowed_actions.items(), key=lambda kv: kv[0]):
            if not actions:
                continue
            actions_list = ", ".join(sorted(actions))
            lines.append(f"- {domain}: {actions_list}")

        return (
            "When choosing an \"action\", prefer one of the known canonical actions\n"
            "for the chosen domain, taken from this overview:\n"
            + "\n".join(lines)
            + "\n\n"
            "You SHOULD NOT invent arbitrary, unrelated action names.\n"
            "However, if a close synonym is clearly appropriate (e.g. 'generate_summary'\n"
            "vs 'generate_tax_summary'), you MAY use the synonym — downstream\n"
            "canonicalization will map it.\n"
            "If none of the canonical actions clearly applies, you MAY propose a simple,\n"
            "reasonable action name or set \"action\": null and \"parameters\": {} AS A LAST RESORT.\n"
        )

    # ============================================================
    # Few-shot builder (CROSS-DOMAIN)
    # ============================================================

    def _build_few_shot_messages(self, domain_hint: Optional[str]) -> List[Dict[str, Any]]:
        """
        Build few-shot messages using EXAMPLES FROM ALL DOMAINS.

        - domain_hint is a soft hint only, mentioned in system text.
        """
        allowed_actions_text = self._allowed_actions_text_global()
        valid_domains = ", ".join(getattr(self.registry, "domains", []) or [])

        hint = (domain_hint or "").strip()
        domains = getattr(self.registry, "domains", []) or []
        hint_normalized = hint if hint in domains else "none"

        system_text = (
            "You are ORKO's deterministic command parser.\n"
            "You MUST output ONLY valid JSON. No explanations, no extra text.\n"
            "\n"
            "Required JSON structure:\n"
            "{\n"
            '  \"domain\": string | null,\n'
            '  \"action\": string | null,\n'
            '  \"parameters\": object,\n'
            '  \"context\": { \"confidence\": number }\n'
            "}\n"
            "\n"
            f"Valid domains: {valid_domains}\n"
            "If user context suggests a domain, it is a soft hint ONLY.\n"
            f"Current soft domain hint (may be \"none\"): {hint_normalized}\n"
            "\n"
            "IMPORTANT:\n"
            "- Choose the domain based on the ACTUAL command text.\n"
            "- You MAY override the soft domain hint if the text clearly belongs\n"
            "  to another domain.\n"
            "\n"
            "DOMAIN / ACTION GUIDANCE (ALL DOMAINS):\n"
            f"{allowed_actions_text}\n"
            "PARAMETER RULES:\n"
            "- \"parameters\" MUST ALWAYS be a JSON object (never null, never a list).\n"
            "- When using a canonical action from the examples, try to match parameter names\n"
            "  from those examples exactly.\n"
            "- NEVER invent parameters that are obviously unrelated to the command.\n"
            "- If you are not sure about parameters, use an empty object: {}.\n"
            "\n"
            "ACTION RULES (VERY IMPORTANT):\n"
            "- You MUST ALMOST ALWAYS output a non-null \"action\" when any reasonable\n"
            "  action can be inferred.\n"
            "- Only use \"action\": null when it is ABSOLUTELY IMPOSSIBLE to infer any\n"
            "  meaningful action.\n"
            "- NEVER omit the \"action\" key.\n"
            "\n"
            "CONFIDENCE RULES:\n"
            "- High certainty (domain + action + parameters): confidence close to 1.0.\n"
            "- Uncertain or guessed: confidence <= 0.5.\n"
            "\n"
            "GLOBAL HARD CONSTRAINTS:\n"
            "- NO natural language explanations.\n"
            "- Return ONLY ONE JSON object as the entire response.\n"
        )

        messages: List[Dict[str, Any]] = [
            {
                "role": "system",
                "content": [
                    {
                        "type": "input_text",
                        "text": system_text,
                    }
                ],
            }
        ]

        # Cross-domain few-shots
        for domain in domains:
            cfg = self.registry.get_examples(domain) or {}
            examples = cfg.get("examples", []) or []

            # If prompt size becomes a problem, slice here: examples = examples[:N]
            for ex in examples:
                cmd = ex.get("command") or ""
                expected = ex.get("expected") or {}

                messages.append(
                    {
                        "role": "user",
                        "content": [{"type": "input_text", "text": cmd}],
                    }
                )
                messages.append(
                    {
                        "role": "assistant",
                        "content": [
                            {
                                "type": "output_text",
                                "text": json.dumps(expected, ensure_ascii=False),
                            }
                        ],
                    }
                )

        return messages

    # ============================================================
    # Post-processing guardrails (SEMI-STRICT)
    # ============================================================

    @staticmethod
    def _norm_value_for_compare(v: Any) -> Any:
        """
        Normalize simple string values for comparison against canonical defaults.
        Handles minor variations like spaces vs underscores, casing, etc.
        """
        if isinstance(v, str):
            return v.strip().lower().replace("_", "").replace(" ", "")
        return v

    def _postprocess_parsed(
        self,
        parsed: Dict[str, Any],
        command: str,
        domain_hint: Optional[str],
    ) -> Dict[str, Any]:
        """
        Enforce domain + action + parameter constraints, but keep enough
        information for canonicalizer + eval to work:

        - We DO NOT force unrecognized actions to null.
        - For known canonical actions we:
            * project parameters onto the canonical key set
            * fill missing keys with defaults from domain_examples
            * normalize values that are near-duplicates of defaults
        """
        # Ensure context is dict
        parsed.setdefault("context", {})
        if not isinstance(parsed["context"], dict):
            parsed["context"] = {"value": parsed["context"]}

        ctx = parsed["context"]
        flags = ctx.get("guardrail_flags") or []
        if not isinstance(flags, list):
            flags = [str(flags)]

        # ---- Domain normalization (light, AI-level; canonicalizer will refine)
        raw_domain = parsed.get("domain") or domain_hint
        registry_domains = set(getattr(self.registry, "domains", []) or [])

        if raw_domain not in registry_domains:
            guessed = self.registry.guess_domain(command)
            domain = guessed if guessed in registry_domains else None
        else:
            domain = raw_domain

        parsed["domain"] = domain

        # ---- Action & parameter normalization (semi-strict with defaults)
        raw_action = parsed.get("action")
        allowed_for_domain = self.allowed_actions.get(domain or "", set())
        params = parsed.get("parameters") or {}
        if not isinstance(params, dict):
            params = {}

        # No action at all: truly unknown
        if not raw_action:
            parsed["action"] = None
            parsed["parameters"] = {}
            if "unknown_action" not in flags:
                flags.append("unknown_action")
        else:
            # Action string exists
            if allowed_for_domain and raw_action in allowed_for_domain:
                # Known canonical action -> strict-ish parameter projection
                allowed_keys = self.allowed_params.get((domain, raw_action), set())
                defaults = self.default_params.get((domain, raw_action), {})

                if not allowed_keys:
                    # No knowledge → keep parameters as-is
                    filtered = params
                else:
                    filtered: Dict[str, Any] = {}
                    for key in allowed_keys:
                        if key in params:
                            v = params[key]
                            # If there is a canonical default, and strings are "equivalent",
                            # normalize to the canonical form from examples.
                            if key in defaults:
                                dv = defaults[key]
                                nv = self._norm_value_for_compare(v)
                                ndv = self._norm_value_for_compare(dv)
                                if nv == ndv or ndv in nv or nv in ndv:
                                    filtered[key] = dv
                                else:
                                    filtered[key] = v
                            else:
                                filtered[key] = v
                        else:
                            # Missing key: backfill from defaults if available
                            if key in defaults:
                                filtered[key] = defaults[key]
                    # filtered now contains exactly the canonical key set (where possible)
                parsed["action"] = raw_action
                parsed["parameters"] = filtered
            else:
                # Unknown / unregistered action:
                #  - Keep it so canonicalizer has something to work with.
                #  - Keep parameters untouched for now.
                parsed["action"] = raw_action
                parsed["parameters"] = params
                if "unregistered_action" not in flags:
                    flags.append("unregistered_action")

        # ---- Confidence normalization
        try:
            conf = float(ctx.get("confidence", 1.0))
        except Exception:
            conf = 1.0
        ctx["confidence"] = max(0.0, min(1.0, conf))

        # Store flags back
        ctx["guardrail_flags"] = flags
        parsed["context"] = ctx
        return parsed

    # ============================================================
    # MAIN PARSE FUNCTION
    # ============================================================

    def parse(
        self,
        command: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Main entrypoint used by ParserEngine.

        FLOW:
        - Read optional domain_hint from context (soft).
        - Build CROSS-DOMAIN few-shot messages (all domains).
        - Call Responses API.
        - Apply semi-strict domain / action / parameter post-processing.
        - ParserEngine will then call canonicalizer() on top of this.
        """
        context = context or {}

        # Soft domain hint
        domain_hint = context.get("domain")
        # Still compute a guessed domain for absolute fallback
        fallback_domain = self.registry.guess_domain(command)

        # Build cross-domain messages with soft hint
        messages = self._build_few_shot_messages(domain_hint=domain_hint)
        messages.append(
            {
                "role": "user",
                "content": [{"type": "input_text", "text": command}],
            }
        )

        # -------------------------------
        # Responses API call
        # -------------------------------
        resp = self.client.responses.create(
            model=self.model,
            input=messages,
        )

        # -------------------------------
        # Extract text from response
        # -------------------------------
        try:
            raw_text = resp.output_text  # newer SDKs
        except Exception:
            try:
                raw_text = resp.output[0].content[0].text  # older shapes
            except Exception:
                raw_text = ""

        # -------------------------------
        # JSON decode (best-effort)
        # -------------------------------
        try:
            parsed = json.loads(raw_text)
        except Exception:
            # Total parse failure: fallback structure
            parsed = {
                "domain": fallback_domain,
                "action": None,
                "parameters": {},
                "context": {
                    "parse_error": True,
                    "raw": raw_text,
                    "confidence": 0.0,
                },
            }

        # Ensure required keys exist
        parsed.setdefault("domain", fallback_domain)
        parsed.setdefault("action", None)
        parsed.setdefault("parameters", {})
        parsed.setdefault("context", {})

        # Merge inbound context into parsed.context
        if not isinstance(parsed["context"], dict):
            parsed["context"] = {"value": parsed["context"]}
        parsed["context"].update(context or {})

        # Apply semi-strict post-processing
        parsed = self._postprocess_parsed(parsed, command, domain_hint)

        return parsed
