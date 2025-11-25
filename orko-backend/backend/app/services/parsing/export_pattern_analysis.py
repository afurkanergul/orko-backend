# backend/app/services/parsing/export_pattern_analysis.py

from pathlib import Path
import json

from backend.app.services.parsing.pattern_miner import PatternMiner
from backend.app.services.parsing.guardrail_generator import GuardrailGenerator


# Output file location (auto-created if missing)
OUTPUT = Path("backend/tests/eval/results/pattern_analysis_report.md")


def generate_pattern_report():
    """
    ORKO Step 6.5 — Weekly Pattern Analysis Generator
    ---------------------------------------------------
    This script produces:
      - Domain confusion matrix
      - Action confusion matrix
      - Missing parameters frequency
      - Guardrail suggestions
    """

    print("🔎 Running PatternMiner()...")
    miner = PatternMiner()
    summary = miner.summarize()

    print("🛡️ Running GuardrailGenerator()...")
    guards = GuardrailGenerator().generate()

    lines = []
    lines.append("# ORKO Weekly Pattern Analysis Report (Step 6.5)")
    lines.append("")
    lines.append("This report is auto-generated from evaluation logs.")
    lines.append("Use these insights to adjust domain examples, parser prompts, and guardrails.")
    lines.append("")

    # ---------------------------------------------------------
    # DOMAIN CONFUSION MATRIX
    # ---------------------------------------------------------
    lines.append("## Domain Confusion Matrix")
    for expected_domain, pred_map in summary["domain_confusion"].items():
        lines.append(f"### Expected: `{expected_domain}`")
        for predicted_domain, count in pred_map.items():
            lines.append(f"- Predicted `{predicted_domain}` → **{count}** times")
        lines.append("")  # spacing

    # ---------------------------------------------------------
    # ACTION CONFUSION MATRIX
    # ---------------------------------------------------------
    lines.append("## Action Confusion Matrix")
    for expected_action, pred_map in summary["action_confusion"].items():
        lines.append(f"### Expected Action: `{expected_action}`")
        for predicted_action, count in pred_map.items():
            lines.append(f"- Predicted `{predicted_action}` → **{count}** times")
        lines.append("")

    # ---------------------------------------------------------
    # MISSING PARAMETERS
    # ---------------------------------------------------------
    lines.append("## Missing Parameters")
    for param, count in summary["missing_parameters"].items():
        lines.append(f"- `{param}` missing **{count}** times")

    # ---------------------------------------------------------
    # GUARDRAIL SUGGESTIONS
    # ---------------------------------------------------------
    lines.append("\n## Guardrail Suggestions")
    lines.append("Generated from real parser errors.\n")
    lines.append("```json")
    lines.append(json.dumps(guards, indent=2))
    lines.append("```")

    # ---------------------------------------------------------
    # WRITE FILE
    # ---------------------------------------------------------
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print("✅ Pattern analysis report created:")
    print(f"   → {OUTPUT.absolute()}")


if __name__ == "__main__":
    generate_pattern_report()
