# backend/app/services/parsing/export_domain_performance.py

import json
from pathlib import Path
from backend.app.services.parsing.eval_v2 import ParserEvaluatorV2

OUTPUT_PATH = Path("backend/tests/eval/results/domain_performance_report.md")


def generate_report():
    evaluator = ParserEvaluatorV2()
    results, summary = evaluator.run()

    prf = summary.get("per_domain_prf", {})
    per_domain_acc = summary.get("per_domain_accuracy", {})
    confusion = summary.get("confusion_matrix", {})

    lines = []
    lines.append("# ORKO Domain Performance Report (Step 6.5)")
    lines.append("")
    lines.append(f"**Total commands:** {summary['total']}")
    lines.append(f"**Accuracy:** {summary['accuracy']:.4f}")
    lines.append("")

    lines.append("## Domain Metrics")
    for dom in sorted(prf.keys()):
        metrics = prf[dom]
        lines.append(f"### {dom}")
        lines.append(f"- Accuracy: {per_domain_acc.get(dom, 0):.4f}")
        lines.append(f"- Precision: {metrics['precision']:.4f}")
        lines.append(f"- Recall: {metrics['recall']:.4f}")
        lines.append(f"- F1: {metrics['f1']:.4f}")
        lines.append(f"- TP: {metrics['tp']} | FP: {metrics['fp']} | FN: {metrics['fn']}")
        lines.append("")

    lines.append("## Confusion Matrix (Domains)")
    lines.append("")
    for exp_dom, preds in confusion.items():
        for pred_dom, count in preds.items():
            lines.append(f"- {exp_dom} → {pred_dom}: {count}")

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print("Domain performance report generated at:", OUTPUT_PATH)


if __name__ == "__main__":
    generate_report()
