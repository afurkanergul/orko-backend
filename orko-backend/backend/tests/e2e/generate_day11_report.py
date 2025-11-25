# backend/tests/e2e/generate_day11_report.py

import json
import os

from backend.tests.e2e.test_runner import run_e2e_tests
from backend.tests.e2e.performance_test import measure_latency


OUTPUT_PATH = "backend/tests/e2e/results/day11_report.json"


def main():
    # Run full E2E pipeline tests
    e2e_results = run_e2e_tests()

    # Single latency probe (full benchmark is separate)
    latency_metrics = measure_latency("Generate a quarterly cashflow report.")

    report = {
        "e2e_results": e2e_results,
        "latency_metrics": latency_metrics,
    }

    # Ensure directory exists
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"Day 11 QA report generated → {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
