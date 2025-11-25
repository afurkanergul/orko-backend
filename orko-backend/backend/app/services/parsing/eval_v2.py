# backend/app/services/parsing/eval_unified.py
# ORKO Unified Parser Evaluator (v1 → v7)

from __future__ import annotations

import json
import yaml
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple
from statistics import mean

from backend.app.services.parsing.parser_engine import ParserEngine


# =====================================================================
# Dataset Paths
# =====================================================================
DATASET_PATH = Path("backend/tests/eval/parser_eval_set.yml").resolve()
ERRORS_OUTPUT = Path("backend/tests/eval/results/parser_eval_errors_unified.jsonl").resolve()


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
# Unified Evaluator Engine
# =====================================================================

class UnifiedParserEvaluator:
    """
    ORKO Unified Evaluator (v1 → v7)
    Includes:
        - v1  Accuracy
        - v2  Per-domain PRF + confusion matrix
        - v3  Expanded error buckets
        - v4  Action PRF
        - v5  Semantic scoring hook (optional future)
        - v6  Guardrail scoring
        - v7  Full evaluation bundle export
    """

    def __init__(self) -> None:
        self.engine = ParserEngine()

    # ---------------------------------------------------------
    # Load dataset
    # ---------------------------------------------------------
    def _load_items(self) -> List[EvalItem]:
        if not DATASET_PATH.exists():
            raise FileNotFoundError(f"Dataset not found: {DATASET_PATH}")

        with DATASET_PATH.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        items: List[EvalItem] = []
        for entry in data.get("commands", []):
            exp = entry.get("expected", {})
            items.append(
                EvalItem(
                    id=entry["id"],
                    command=entry["command"],
                    expected_domain=exp.get("domain"),
                    expected_action=exp.get("action"),
                    expected_parameters=exp.get("parameters", {}),
                )
            )
        return items

    # ---------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------
    @staticmethod
    def _parameters_match(expected: Dict[str, Any], predicted: Dict[str, Any]) -> bool:
        for k, v in expected.items():
            if predicted.get(k) != v:
                return False
        return True

    @staticmethod
    def _classify_error(domain_ok: bool, action_ok: bool, params_ok: bool) -> str | None:
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
    # Main Run
    # ---------------------------------------------------------
    def run(self, version: str = "v7") -> Tuple[List[EvalResult], Dict[str, Any]]:
        items = self._load_items()
        results: List[EvalResult] = []

        total = len(items)
        correct = 0

        # v1/v2 metrics
        per_domain_counts: Dict[str, Dict[str, int]] = {}
        confusion_matrix: Dict[str, Dict[str, int]] = {}
        error_buckets: Dict[str, int] = {}

        # v3 expanded error types
        action_fp: Dict[str, int] = {}
        action_fn: Dict[str, int] = {}
        action_tp: Dict[str, int] = {}

        for item in items:
            parsed = self.engine.parse_command(item.command, context={})
            pred_domain = parsed.get("domain")
            pred_action = parsed.get("action")
            pred_params = parsed.get("parameters", {}) or {}

            domain_ok = (pred_domain == item.expected_domain)
            action_ok = (pred_action == item.expected_action)
            params_ok = self._parameters_match(item.expected_parameters, pred_params)

            error = self._classify_error(domain_ok, action_ok, params_ok)

            if error is None:
                correct += 1
                # Track action TP
                action_tp[pred_action] = action_tp.get(pred_action, 0) + 1
            else:
                error_buckets[error] = error_buckets.get(error, 0) + 1

                # Action FP/FN
                action_fn[item.expected_action] = action_fn.get(item.expected_action, 0) + 1
                action_fp[pred_action] = action_fp.get(pred_action, 0) + 1

            # Per-domain accuracy tracking
            dom_stats = per_domain_counts.setdefault(item.expected_domain, {"correct": 0, "total": 0})
            dom_stats["total"] += 1
            if error is None:
                dom_stats["correct"] += 1

            # Confusion matrix
            exp_dom = item.expected_domain or "unknown"
            pred_dom = pred_domain or "none"
            row = confusion_matrix.setdefault(exp_dom, {})
            row[pred_dom] = row.get(pred_dom, 0) + 1

            # Result object
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
                    error_type=error,
                    raw_parsed=parsed,
                )
            )

        # ---------------------------------------------------------
        # v2 — Per-domain accuracy
        # ---------------------------------------------------------
        per_domain_accuracy = {
            dom: (v["correct"] / v["total"] if v["total"] else 0.0)
            for dom, v in per_domain_counts.items()
        }

        # ---------------------------------------------------------
        # v2/v3 — Domain PRF
        # ---------------------------------------------------------
        dom_tp: Dict[str, int] = {}
        dom_fp: Dict[str, int] = {}
        dom_fn: Dict[str, int] = {}

        for r in results:
            exp = r.expected_domain
            pred = r.predicted_domain

            if exp == pred:
                dom_tp[exp] = dom_tp.get(exp, 0) + 1
            else:
                dom_fn[exp] = dom_fn.get(exp, 0) + 1
                dom_fp[pred] = dom_fp.get(pred, 0) + 1

        per_domain_prf: Dict[str, Any] = {}
        all_doms = set(dom_tp) | set(dom_fp) | set(dom_fn)

        for dom in all_doms:
            tp = dom_tp.get(dom, 0)
            fp = dom_fp.get(dom, 0)
            fn = dom_fn.get(dom, 0)

            prec = tp / (tp + fp) if (tp + fp) else 0.0
            rec = tp / (tp + fn) if (tp + fn) else 0.0
            f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0

            per_domain_prf[dom] = {
                "precision": prec,
                "recall": rec,
                "f1": f1,
                "tp": tp,
                "fp": fp,
                "fn": fn,
            }

        # ---------------------------------------------------------
        # v4 — action-level PRF
        # ---------------------------------------------------------
        action_prf = {}
        all_actions = set(action_tp) | set(action_fp) | set(action_fn)

        for act in all_actions:
            tp = action_tp.get(act, 0)
            fp = action_fp.get(act, 0)
            fn = action_fn.get(act, 0)

            prec = tp / (tp + fp) if (tp + fp) else 0.0
            rec = tp / (tp + fn) if (tp + fn) else 0.0
            f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0

            action_prf[act] = {
                "precision": prec,
                "recall": rec,
                "f1": f1,
                "tp": tp,
                "fp": fp,
                "fn": fn,
            }

        # ---------------------------------------------------------
        # Final unified summary
        # ---------------------------------------------------------
        summary = {
            "version": version,
            "total": total,
            "correct": correct,
            "accuracy": correct / total if total else 0.0,
            "per_domain_accuracy": per_domain_accuracy,
            "error_buckets": error_buckets,
            "confusion_matrix": confusion_matrix,
            "per_domain_prf": per_domain_prf,
            "per_action_prf": action_prf,
        }

        return results, summary


# =====================================================================
# Error Export (Unified)
# =====================================================================
def export_errors(results: List[EvalResult]) -> None:
    ERRORS_OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    with ERRORS_OUTPUT.open("w", encoding="utf-8") as f:
        for r in results:
            if r.error_type is None:
                continue

            f.write(json.dumps({
                "id": r.id,
                "command": r.command,
                "expected_domain": r.expected_domain,
                "expected_action": r.expected_action,
                "predicted_domain": r.predicted_domain,
                "predicted_action": r.predicted_action,
                "error_type": r.error_type,
                "raw_parsed": r.raw_parsed,
            }) + "\n")
