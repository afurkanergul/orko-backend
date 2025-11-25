from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Any

import yaml

from backend.app.services.parsing.parser_engine import ParserEngine


BASE_DIR = Path(__file__).resolve().parent
CONFIG_DIR = BASE_DIR / "config"
EVAL_COMMANDS_PATH = CONFIG_DIR / "ai_eval_commands.yml"
REPORT_PATH = CONFIG_DIR / "ai_eval_report.json"


class AIParserEvaluator:
    """
    Multi-domain evaluator for ORKO AIParser + ParserEngine.
    Runs 20+ commands across industries and logs:
      - coverage ratio
      - ambiguous results
      - full parsed output for inspection

    Produces ai_eval_report.json as required in Step 6 Day 6.
    """

    def __init__(self):
        self.engine = ParserEngine()

    # ---------------------------------------------------------
    # Load test commands from YAML
    # ---------------------------------------------------------
    def _load_commands(self) -> List[str]:
        if not EVAL_COMMANDS_PATH.exists():
            return []

        with EVAL_COMMANDS_PATH.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        return data.get("commands", [])

    # ---------------------------------------------------------
    # Run evaluation over all commands
    # ---------------------------------------------------------
    def run(self) -> Dict[str, Any]:
        commands = self._load_commands()
        total = len(commands)

        if total == 0:
            return {
                "total": 0,
                "covered": 0,
                "coverage": 0.0,
                "results": [],
                "ambiguous": [],
            }

        results: List[Dict[str, Any]] = []
        ambiguous: List[Dict[str, Any]] = []
        covered = 0

        for cmd in commands:
            parsed = self.engine.parse_command(cmd, context={})

            domain = parsed.get("domain")
            action = parsed.get("action")

            # Coverage = domain + action identified
            ok = bool(domain) and bool(action)

            if ok:
                covered += 1
            else:
                ambiguous.append({
                    "command": cmd,
                    "parsed": parsed,
                })

            results.append({
                "command": cmd,
                "parsed": parsed,
                "ok": ok,
            })

        coverage = covered / total if total else 0.0

        report = {
            "total": total,
            "covered": covered,
            "coverage": coverage,
            "results": results,
            "ambiguous": ambiguous,
        }

        # Write report to JSON
        with REPORT_PATH.open("w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        return report


# -------------------------------------------------------------
# Optional CLI execution
# -------------------------------------------------------------
if __name__ == "__main__":
    evaluator = AIParserEvaluator()
    out = evaluator.run()
    print(json.dumps(out, indent=2))
