# backend/app/services/parsing/export_pattern_analysis.py

"""
Step 6.5 — Pattern Mining Report Generator
------------------------------------------
Analyzes parser_eval_errors_v2.jsonl and produces:

- Frequent domain mismatches
- Frequent action mismatches
- Parameters mismatch frequency
- Confused domain pairs (A→B patterns)
- Recommendation hints for fixing patterns / guardrails
"""

from __future__ import annotations
import json
from pathlib import Path
from collections import defaultdict

ERRORS_PATH = Path("backend/tests/eval/results/parser_eval_errors_v2.jsonl")
REPORT_PATH = Path("backend/tests/eval/results/pattern_analysis_report.md")


def load_errors():
    if not ERRORS_PATH.exists():
        return []
    rows = []
    with ERRORS_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            try:
                rows.append(json.loads(line))
            except Exception:
                pass
    return rows


def generate_pattern_report():
    errors = load_errors()

    domain_confusion = defaultdict(lambda: defaultdict(int))
    action_mismatch = defaultdict(int)
    param_mismatch = defaultdict(int)

    for e in errors:
        exp_dom = e.get("expected_domain")
        pred_dom = e.get("predicted_domain")
        etype = e.get("error_type")

        if etype == "domain_mismatch":
            domain_confusion[exp_dom][pred_dom] += 1

        if etype == "action_mismatch":
            action_mismatch[(e.get("expected_action"), e.get("predicted_action"))] += 1

        if etype == "parameters_mismatch":
            param_mismatch[e.get("expected_action")] += 1

    # Build Report
    lines = []
    lines.append("# ORKO Pattern Analysis Report (Step 6.5)")
    lines.append("")

    lines.append("## 1. Domain Confusion Patterns")
    for exp, preds in domain_confusion.items():
        lines.append(f"### Expected: {exp}")
        for pred, ct in preds.items():
            lines.append(f"- Predicted as **{pred}** → {ct} times")
        lines.append("")

    lines.append("## 2. Action Mismatch Patterns")
    for (exp, pred), ct in action_mismatch.items():
        lines.append(f"- `{exp}` → misclassified as `{pred}` ({ct} times)")

    lines.append("\n## 3. Parameter Error Hotspots")
    for action, ct in param_mismatch.items():
        lines.append(f"- Action `{action}` has {ct} parameter mismatches")

    # Recommendations
    lines.append("\n## 4. Recommendations (Auto-Generated)")
    lines.append("- Add few-shots for frequently confused domain pairs")
    lines.append("- Strengthen domain keywords for top confusion pairs")
    lines.append("- Add guardrail hints where destructive confusion appears")
    lines.append("- Improve parameter schema for high-error actions")

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")

    print("Pattern analysis report generated at:", REPORT_PATH)
