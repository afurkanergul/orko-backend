# backend/app/services/parsing/run_parser_eval.py
# ORKO Unified Parser Evaluation Runner (v1 → v7)

from __future__ import annotations
import argparse
import json

from backend.app.services.parsing.eval_unified import (
    UnifiedParserEvaluator,
    export_errors,
)
from backend.app.services.parsing.parser_metrics_writer import ParserMetricsWriter


# Default accuracy threshold for commercial-grade operation
TARGET_ACCURACY = 0.90


def run(version: str = "v7") -> None:
    """
    Runs ORKO's unified evaluator (v1 → v7).
    Prints human-friendly output and writes parser_metrics row.
    """

    evaluator = UnifiedParserEvaluator()

    print("--------------------------------------------------")
    print(f"     ORKO Parser Evaluation — version {version}     ")
    print("--------------------------------------------------")

    results, summary = evaluator.run(version=version)

    # save to DB
    writer = ParserMetricsWriter()
    metric = writer.save(summary)

    # error export (JSONL)
    export_errors(results)

    # ==========================================================
    # Console Reporting
    # ==========================================================
    print(f"Run ID:         {metric.run_id}")
    print(f"Engine Version: {metric.engine_version}")
    print(f"Total:          {metric.total}")
    print(f"Correct:        {metric.correct}")
    print(f"Accuracy:       {metric.accuracy:.4f}")
    print("--------------------------------------------------")

    # Per-domain accuracy
    print("Per-Domain Accuracy:")
    for dom, acc in (summary.get("per_domain_accuracy") or {}).items():
        print(f"  - {dom:20s}: {acc:.4f}")

    print("--------------------------------------------------")
    # v2/v3 error buckets
    print("Error Buckets:")
    for etype, count in (summary.get("error_buckets") or {}).items():
        print(f"  - {etype:20s}: {count}")

    print("--------------------------------------------------")
    # Confusion matrix
    print("Confusion Matrix:")
    confusion = summary.get("confusion_matrix") or {}
    for gold, predicted_map in confusion.items():
        print(f"  {gold}:")
        for predicted, ct in predicted_map.items():
            print(f"      -> predicted {predicted:20s}: {ct}")

    print("--------------------------------------------------")
    print("Per-Domain PRF:")
    prf = summary.get("per_domain_prf") or {}
    for dom, stats in prf.items():
        print(f"  {dom}")
        print(f"      precision={stats['precision']:.4f}")
        print(f"      recall   ={stats['recall']:.4f}")
        print(f"      f1       ={stats['f1']:.4f}")
        print(f"      TP={stats['tp']} FP={stats['fp']} FN={stats['fn']}")

    print("--------------------------------------------------")
    print("Action-Level PRF:")
    act_prf = summary.get("per_action_prf") or {}
    for act, stats in act_prf.items():
        print(f"  {act}")
        print(f"      precision={stats['precision']:.4f}")
        print(f"      recall   ={stats['recall']:.4f}")
        print(f"      f1       ={stats['f1']:.4f}")
        print(f"      TP={stats['tp']} FP={stats['fp']} FN={stats['fn']}")

    print("--------------------------------------------------")
    print("Errors exported to: backend/tests/eval/results/parser_eval_errors_unified.jsonl")
    print("--------------------------------------------------")

    # Threshold / CI consistency
    acc = summary.get("accuracy", 0.0)
    if acc < TARGET_ACCURACY:
        print(f"WARNING: Accuracy below target ({acc:.4f} < {TARGET_ACCURACY})")
    else:
        print(f"OK: Accuracy meets threshold ({acc:.4f} ≥ {TARGET_ACCURACY})")

    print("--------------------------------------------------")
    print("Unified Parser Evaluation Completed.")
    print("--------------------------------------------------")


def cli():
    """
    CLI interface for:
        python -m backend.app.services.parsing.run_parser_eval --version v7

    Versions allowed: v1, v2, v3, v4, v5, v6, v7
    """
    parser = argparse.ArgumentParser(description="Run ORKO Unified Parser Evaluator")
    parser.add_argument(
        "--version",
        "-v",
        type=str,
        default="v7",
        help="Evaluation mode: v1, v2, v3, v4, v5, v6, v7",
    )

    args = parser.parse_args()
    run(version=args.version)


if __name__ == "__main__":
    cli()
