from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple

import yaml

from backend.app.services.parsing.parser_engine import ParserEngine

BASE_DIR = Path(__file__).resolve().parent
CONFIG_DIR = BASE_DIR / "config"
EVAL_SET_PATH = CONFIG_DIR / "parser_eval_set.yml"


# ---------------------------------------------------------------------
# DATA CLASSES
# ---------------------------------------------------------------------
@dataclass
class EvalItem:
    id: str
    command: str
    expected_domain: str
    expected_action: str
    expected_parameters: Dict[str, Any]


@dataclass
class EvalResult:
    id: str
    command: str
    expected_domain: str
    expected_action: str
    predicted_domain: str
    predicted_action: str
    domain_correct: bool
    action_correct: bool
    parameters_match: bool
    raw_parsed: Dict[str, Any]


# ---------------------------------------------------------------------
# PARSER EVALUATOR
# ---------------------------------------------------------------------
class ParserEvaluator:
    """
    Runs the labeled evaluation set through ParserEngine and computes metrics.
    Produces:
      • overall accuracy
      • per-domain accuracy
      • per-action precision/recall (approx.)
    """

    def __init__(self) -> None:
        self.engine = ParserEngine()

    # -------------------------------------------------------------
    # Load items from YAML
    # -------------------------------------------------------------
    def _load_eval_items(self) -> List[EvalItem]:
        if not EVAL_SET_PATH.exists():
            raise FileNotFoundError(f"Eval set not found: {EVAL_SET_PATH}")

        with EVAL_SET_PATH.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        items: List[EvalItem] = []
        for entry in data.get("commands", []):
            expected = entry.get("expected", {})
            items.append(
                EvalItem(
                    id=entry["id"],
                    command=entry["command"],
                    expected_domain=expected.get("domain"),
                    expected_action=expected.get("action"),
                    expected_parameters=expected.get("parameters", {}),
                )
            )
        return items

    # -------------------------------------------------------------
    # Parameter matching (subset)
    # -------------------------------------------------------------
    @staticmethod
    def _parameters_match(expected: Dict[str, Any], predicted: Dict[str, Any]) -> bool:
        """
        Simple subset check:
        All expected keys must match exactly in predicted.
        """
        for k, v in expected.items():
            if predicted.get(k) != v:
                return False
        return True

    # -------------------------------------------------------------
    # Run evaluator and compute metrics
    # -------------------------------------------------------------
    def run(self) -> Tuple[List[EvalResult], Dict[str, Any]]:
        items = self._load_eval_items()
        results: List[EvalResult] = []

        correct_count = 0
        domain_stats: Dict[str, Dict[str, int]] = {}

        # Action-level metrics
        action_tp: Dict[str, int] = {}
        action_fp: Dict[str, int] = {}
        action_fn: Dict[str, int] = {}

        for item in items:
            parsed = self.engine.parse_command(item.command, context={})
            pred_domain = parsed.get("domain")
            pred_action = parsed.get("action")
            pred_params = parsed.get("parameters", {})

            domain_correct = (pred_domain == item.expected_domain)
            action_correct = (pred_action == item.expected_action)
            params_match = self._parameters_match(item.expected_parameters, pred_params)

            all_correct = domain_correct and action_correct and params_match
            if all_correct:
                correct_count += 1

            # Per-domain statistics
            stats = domain_stats.setdefault(item.expected_domain, {"total": 0, "correct": 0})
            stats["total"] += 1
            if all_correct:
                stats["correct"] += 1

            # Simplified action-level metrics
            exp_key = f"{item.expected_domain}:{item.expected_action}"
            pred_key = (
                f"{pred_domain}:{pred_action}"
                if pred_domain and pred_action
                else None
            )

            if all_correct:
                action_tp[exp_key] = action_tp.get(exp_key, 0) + 1
            else:
                action_fn[exp_key] = action_fn.get(exp_key, 0) + 1
                if pred_key:
                    action_fp[pred_key] = action_fp.get(pred_key, 0) + 1

            results.append(
                EvalResult(
                    id=item.id,
                    command=item.command,
                    expected_domain=item.expected_domain,
                    expected_action=item.expected_action,
                    predicted_domain=pred_domain,
                    predicted_action=pred_action,
                    domain_correct=domain_correct,
                    action_correct=action_correct,
                    parameters_match=params_match,
                    raw_parsed=parsed,
                )
            )

        total = len(items)
        accuracy = correct_count / total if total else 0.0

        per_domain_accuracy = {
            dom: (
                stat["correct"] / stat["total"]
                if stat["total"] > 0
                else 0.0
            )
            for dom, stat in domain_stats.items()
        }

        per_action_metrics: Dict[str, Dict[str, float]] = {}
        all_actions = set(action_tp) | set(action_fp) | set(action_fn)
        for key in all_actions:
            tp = action_tp.get(key, 0)
            fp = action_fp.get(key, 0)
            fn = action_fn.get(key, 0)
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            per_action_metrics[key] = {
                "precision": precision,
                "recall": recall,
                "tp": tp,
                "fp": fp,
                "fn": fn,
            }

        summary = {
            "total": total,
            "correct": correct_count,
            "accuracy": accuracy,
            "per_domain_accuracy": per_domain_accuracy,
            "per_action": per_action_metrics,
        }

        return results, summary

    # -------------------------------------------------------------
    # JSON export
    # -------------------------------------------------------------
    @staticmethod
    def to_json(results: List[EvalResult], summary: Dict[str, Any]) -> str:
        return json.dumps(
            {
                "summary": summary,
                "results": [
                    {
                        "id": r.id,
                        "command": r.command,
                        "expected_domain": r.expected_domain,
                        "expected_action": r.expected_action,
                        "predicted_domain": r.predicted_domain,
                        "predicted_action": r.predicted_action,
                        "domain_correct": r.domain_correct,
                        "action_correct": r.action_correct,
                        "parameters_match": r.parameters_match,
                        "raw_parsed": r.raw_parsed,
                    }
                    for r in results
                ],
            },
            indent=2,
        )
