# backend/app/services/parsing/guardrail_generator.py

from __future__ import annotations

from pathlib import Path
from backend.app.services.parsing.pattern_miner import PatternMiner

OUTPUT_PATH = Path("backend/docs/guardrail_suggestions_v2.json")


class GuardrailGenerator:
    """
    Converts error patterns into actionable guardrail improvements.
    """

    def __init__(self):
        self.miner = PatternMiner()

    def generate(self):
        summary = self.miner.summarize()

        suggestions = {
            "domain_rules": [],
            "action_rules": [],
            "parameter_rules": [],
            "phrasing_rules": [],
        }

        # Domain confusion -> domain rule expansions
        for exp_dom, pred_map in summary["domain_confusion"].items():
            for pred_dom, count in pred_map.items():
                if exp_dom != pred_dom and count >= 2:
                    suggestions["domain_rules"].append({
                        "reason": "frequent domain confusion",
                        "expected_domain": exp_dom,
                        "wrong_predicted_domain": pred_dom,
                        "suggestion": f"Add few-shot examples emphasizing {exp_dom} vs {pred_dom}",
                        "count": count
                    })

        # Action confusion
        for exp_act, pred_map in summary["action_confusion"].items():
            for pred_act, count in pred_map.items():
                if exp_act != pred_act and count >= 2:
                    suggestions["action_rules"].append({
                        "expected_action": exp_act,
                        "wrong_predicted_action": pred_act,
                        "count": count,
                        "suggestion": f"Provide disambiguation between '{exp_act}' and '{pred_act}' in few-shots."
                    })

        # Missing parameters
        for param, count in summary["missing_parameters"].items():
            if count >= 2:
                suggestions["parameter_rules"].append({
                    "parameter": param,
                    "count": count,
                    "suggestion": f"Add parameter presence hints for '{param}' in prompt rules."
                })

        # Phrasing patterns
        for token, count in summary["frequent_phrasing_tokens"].items():
            if count >= 4:
                suggestions["phrasing_rules"].append({
                    "token": token,
                    "count": count,
                    "suggestion": f"Consider few-shot examples involving '{token}'."
                })

        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        with OUTPUT_PATH.open("w", encoding="utf-8") as f:
            import json
            json.dump(suggestions, f, indent=2)

        return suggestions
