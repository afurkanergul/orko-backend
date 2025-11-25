import json
from pathlib import Path

ERRORS_FILE = Path("backend/tests/eval/results/parser_eval_errors_unified.jsonl")
OUTPUT_FILE = Path("backend/tests/eval/results/failure_categories.json")

def categorize_failure(e):
    if e["predicted_domain"] != e["expected_domain"]:
        return "domain_failure"

    if e["predicted_action"] != e["expected_action"]:
        return "action_failure"

    if not e.get("parsed", {}).get("action"):
        return "no_action_detected"

    expected_params = e["expected_parameters"] or {}
    predicted_params = e["parsed"].get("parameters", {}) or {}

    if expected_params and not predicted_params:
        return "parameters_missing"

    if predicted_params and predicted_params != expected_params:
        return "parameters_wrong"

    return "other"

def run():
    results = {}

    with ERRORS_FILE.open() as f:
        for line in f:
            e = json.loads(line)
            c = categorize_failure(e)
            results.setdefault(c, 0)
            results[c] += 1

    OUTPUT_FILE.write_text(json.dumps(results, indent=2))
    print("Failure categories written to:", OUTPUT_FILE)

if __name__ == "__main__":
    run()
