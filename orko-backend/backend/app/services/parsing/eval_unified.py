# backend/app/services/parsing/eval_unified.py
# ORKO Unified Parser Evaluator (v1 → v7)

from __future__ import annotations

import json
import yaml
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple

from backend.app.services.parsing.parser_engine import ParserEngine


# =====================================================================
# Paths
# =====================================================================

# Main eval dataset (multi-industry)
DATASET_PATH = Path("backend/tests/eval/parser_eval_set.yml").resolve()

# Unified error export path
ERRORS_OUTPUT = Path(
    "backend/tests/eval/results/parser_eval_errors_unified.jsonl"
).resolve()


# =====================================================================
# Data Models
# =====================================================================

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
    predicted_domain: str | None
    predicted_action: str | None
    domain_correct: bool
    action_correct: bool
    parameters_match: bool
    error_type: str | None
    raw_parsed: Dict[str, Any]


# =====================================================================
# Unified Evaluator
# =====================================================================

class UnifiedParserEvaluator:
    """
    ORKO Unified Evaluator (v1 → v7)

    Provides a single entrypoint that computes:

      - v1: global accuracy
      - v2: per-domain accuracy + confusion matrix
      - v3: enriched error buckets
      - v4: per-domain precision/recall/F1
      - v5: per-action precision/recall/F1
      - v6: guardrail-aware error categories (hook)
      - v7: full evaluation summary for dashboards & observability
    """

    def __init__(self) -> None:
        self.engine = ParserEngine()

    # ---------------------------------------------------------
    # Dataset loader
    # ---------------------------------------------------------
    def _load_items(self) -> List[EvalItem]:
        if not DATASET_PATH.exists():
            raise FileNotFoundError(f"Eval dataset not found: {DATASET_PATH}")

        with DATASET_PATH.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        items: List[EvalItem] = []
        for entry in data.get("commands", []):
            expected = entry.get("expected", {}) or {}
            items.append(
                EvalItem(
                    id=entry["id"],
                    command=entry["command"],
                    expected_domain=expected.get("domain"),
                    expected_action=expected.get("action"),
                    expected_parameters=expected.get("parameters", {}) or {},
                )
            )
        return items

    # ---------------------------------------------------------
    # Matching helpers
    # ---------------------------------------------------------
    @staticmethod
    def _parameters_match(expected: Dict[str, Any], predicted: Dict[str, Any]) -> bool:
        for k, v in expected.items():
            if predicted.get(k) != v:
                return False
        return True

    @staticmethod
    def _classify_error(
        domain_ok: bool,
        action_ok: bool,
        params_ok: bool,
    ) -> str | None:
        """
        v2/v3 style error types.
        """
        if domain_ok and action_ok and params_ok:
            return None
        if not domain_ok:
            return "domain_mismatch"
        if not action_ok:
            return "action_mismatch"
        if not params_ok:
            return "parameters_mismatch"
        return "unknown"

    # ---------------------------------------------------------
    # Main evaluation entrypoint
    # ---------------------------------------------------------
    def run(self, version: str = "v7") -> Tuple[List[EvalResult], Dict[str, Any]]:
        """
        Run full evaluation pipeline.

        `version` is mainly for tagging in metrics; this method
        always computes the full set of statistics.
        """
        items = self._load_items()
        results: List[EvalResult] = []

        total = len(items)
        correct = 0

        # v1/v2 accumulators
        per_domain_counts: Dict[str, Dict[str, int]] = {}
        confusion_matrix: Dict[str, Dict[str, int]] = {}
        error_buckets: Dict[str, int] = {}

        # v3/v4/v5 accumulators
        domain_tp: Dict[str, int] = {}
        domain_fp: Dict[str, int] = {}
        domain_fn: Dict[str, int] = {}

        action_tp: Dict[str, int] = {}
        action_fp: Dict[str, int] = {}
        action_fn: Dict[str, int] = {}

        for item in items:
            parsed = self.engine.parse_command(item.command, context={})

            pred_domain = parsed.get("domain")
            pred_action = parsed.get("action")
            pred_params = parsed.get("parameters", {}) or {}

            domain_ok = (pred_domain == item.expected_domain)
            action_ok = (pred_action == item.expected_action)
            params_ok = self._parameters_match(item.expected_parameters, pred_params)

            error_type = self._classify_error(domain_ok, action_ok, params_ok)

            # v1 correctness
            if error_type is None:
                correct += 1

            # v2/v3 error buckets
            if error_type is not None:
                error_buckets[error_type] = error_buckets.get(error_type, 0) + 1

            # v2 per-domain counts
            dom_stats = per_domain_counts.setdefault(
                item.expected_domain, {"total": 0, "correct": 0}
            )
            dom_stats["total"] += 1
            if error_type is None:
                dom_stats["correct"] += 1

            # v2 confusion matrix (domain-level)
            exp_dom = item.expected_domain or "unknown"
            pred_dom_key = pred_domain or "none"
            row = confusion_matrix.setdefault(exp_dom, {})
            row[pred_dom_key] = row.get(pred_dom_key, 0) + 1

            # v4 domain PRF
            if item.expected_domain:
                if pred_domain == item.expected_domain:
                    domain_tp[item.expected_domain] = domain_tp.get(item.expected_domain, 0) + 1
                else:
                    domain_fn[item.expected_domain] = domain_fn.get(item.expected_domain, 0) + 1
                    if pred_domain:
                        domain_fp[pred_domain] = domain_fp.get(pred_domain, 0) + 1

            # v5 action PRF
            exp_act = item.expected_action
            pred_act = pred_action
            if exp_act:
                if pred_act == exp_act:
                    action_tp[exp_act] = action_tp.get(exp_act, 0) + 1
                else:
                    action_fn[exp_act] = action_fn.get(exp_act, 0) + 1
                    if pred_act:
                        action_fp[pred_act] = action_fp.get(pred_act, 0) + 1

            # Add result object
            results.append(
                EvalResult(
                    id=item.id,
                    command=item.command,
                    expected_domain=item.expected_domain,
                    expected_action=item.expected_action,
                    predicted_domain=pred_domain,
                    predicted_action=pred_action,
                    domain_correct=domain_ok,
                    action_correct=action_ok,
                    parameters_match=params_ok,
                    error_type=error_type,
                    raw_parsed=parsed,
                )
            )

        # ---------------------------------------------------------
        # v2 — per-domain accuracy
        # ---------------------------------------------------------
        per_domain_accuracy: Dict[str, float] = {}
        for dom, stats in per_domain_counts.items():
            total_dom = stats["total"]
            per_domain_accuracy[dom] = (
                stats["correct"] / total_dom if total_dom > 0 else 0.0
            )

        # ---------------------------------------------------------
        # v4 — per-domain PRF
        # ---------------------------------------------------------
        per_domain_prf: Dict[str, Dict[str, Any]] = {}
        all_domains = set(domain_tp) | set(domain_fp) | set(domain_fn)

        for dom in all_domains:
            tp = domain_tp.get(dom, 0)
            fp = domain_fp.get(dom, 0)
            fn = domain_fn.get(dom, 0)

            precision = tp / (tp + fp) if (tp + fp) else 0.0
            recall = tp / (tp + fn) if (tp + fn) else 0.0
            f1 = (
                2 * precision * recall / (precision + recall)
                if (precision + recall)
                else 0.0
            )

            per_domain_prf[dom] = {
                "precision": precision,
                "recall": recall,
                "f1": f1,
                "tp": tp,
                "fp": fp,
                "fn": fn,
            }

        # ---------------------------------------------------------
        # v5 — per-action PRF
        # ---------------------------------------------------------
        per_action_prf: Dict[str, Dict[str, Any]] = {}
        all_actions = set(action_tp) | set(action_fp) | set(action_fn)

        for act in all_actions:
            tp = action_tp.get(act, 0)
            fp = action_fp.get(act, 0)
            fn = action_fn.get(act, 0)

            precision = tp / (tp + fp) if (tp + fp) else 0.0
            recall = tp / (tp + fn) if (tp + fn) else 0.0
            f1 = (
                2 * precision * recall / (precision + recall)
                if (precision + recall)
                else 0.0
            )

            per_action_prf[act] = {
                "precision": precision,
                "recall": recall,
                "f1": f1,
                "tp": tp,
                "fp": fp,
                "fn": fn,
            }

        # ---------------------------------------------------------
        # Final summary bundle (v7)
        # ---------------------------------------------------------
        accuracy = correct / total if total else 0.0

        summary: Dict[str, Any] = {
            "version": version,
            "total": total,
            "correct": correct,
            "accuracy": accuracy,
            "per_domain_accuracy": per_domain_accuracy,
            "error_buckets": error_buckets,
            "confusion_matrix": confusion_matrix,
            "per_domain_prf": per_domain_prf,
            "per_action_prf": per_action_prf,
        }

        return results, summary


# =====================================================================
# Unified Error Export
# =====================================================================

def export_errors(results: List[EvalResult]) -> None:
    """
    Write mis-parsed commands to a unified JSONL file
    for downstream pattern mining (Step 6.5+Step 7).
    """
    ERRORS_OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    with ERRORS_OUTPUT.open("w", encoding="utf-8") as f:
        for r in results:
            if r.error_type is None:
                continue

            row = {
                "id": r.id,
                "command": r.command,
                "expected_domain": r.expected_domain,
                "expected_action": r.expected_action,
                "predicted_domain": r.predicted_domain,
                "predicted_action": r.predicted_action,
                "error_type": r.error_type,
                "raw_parsed": r.raw_parsed,
            }
            f.write(json.dumps(row) + "\n")
