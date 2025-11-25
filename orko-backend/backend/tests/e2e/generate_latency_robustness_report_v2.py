# backend/tests/e2e/generate_latency_robustness_report_v2.py

import json
from pathlib import Path

from backend.tests.e2e.performance_test import run_latency_benchmark
from backend.tests.e2e.performance_concurrency_test import run_concurrency_test
from backend.tests.e2e.robustness_test import run_robustness_smoke

JSON_OUT = Path("backend/tests/e2e/results/latency_robustness_report_v2.json")
MD_OUT = Path("backend/tests/e2e/results/latency_robustness_report_v2.md")

P95_TARGET_MS = 3000.0  # 3 seconds


def main():
    samples, latency_summary = run_latency_benchmark(runs_per_command=10)
    concurrency_summary = None
    try:
        # Importing asyncio here to avoid forcing event loop at import time
        import asyncio

        concurrency_summary = asyncio.run(run_concurrency_test())
    except Exception:
        concurrency_summary = {"error": "concurrency_test_failed"}

    robustness_results = run_robustness_smoke()

    report = {
        "latency": latency_summary,
        "concurrency": concurrency_summary,
        "robustness": robustness_results,
        "thresholds": {
            "p95_ms_target": P95_TARGET_MS,
        },
    }

    JSON_OUT.parent.mkdir(parents=True, exist_ok=True)
    with JSON_OUT.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    # Build markdown
    lines = []
    lines.append("# ORKO Latency & Robustness Report — v2")
    lines.append("")
    lines.append("## Latency (Single-Command Benchmark)")
    lines.append(f"- Count: {latency_summary['count']}")
    lines.append(f"- p50: {latency_summary['p50_ms']:.2f} ms")
    lines.append(f"- p95: {latency_summary['p95_ms']:.2f} ms")
    lines.append(f"- p99: {latency_summary['p99_ms']:.2f} ms")
    lines.append(f"- avg: {latency_summary['avg_ms']:.2f} ms")
    lines.append(f"- max: {latency_summary['max_ms']:.2f} ms")
    lines.append(f"- Target p95: {P95_TARGET_MS:.2f} ms")
    lines.append("")

    lines.append("## Concurrency (Parallel /trigger Requests)")
    if "error" in concurrency_summary:
        lines.append(f"- ERROR: {concurrency_summary['error']}")
    else:
        lines.append(f"- Requests: {concurrency_summary['requests']}")
        lines.append(f"- p50: {concurrency_summary['p50_ms']:.2f} ms")
        lines.append(f"- p95: {concurrency_summary['p95_ms']:.2f} ms")
        lines.append(f"- p99: {concurrency_summary['p99_ms']:.2f} ms")
        lines.append(f"- max: {concurrency_summary['max_ms']:.2f} ms")
        lines.append(f"- errors: {concurrency_summary['errors']}")
    lines.append("")

    lines.append("## Robustness (Messy/Multilingual Inputs)")
    for cmd, ok in robustness_results.items():
        status = "OK" if ok else "FAIL"
        lines.append(f"- [{status}] {cmd}")

    with MD_OUT.open("w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print("Latency & robustness report written to:")
    print(" -", JSON_OUT)
    print(" -", MD_OUT)


if __name__ == "__main__":
    main()
