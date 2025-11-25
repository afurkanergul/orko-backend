"""
Unified ORKO Performance Engine
Supports versioned performance tests: v1 → v7

Run:
  python -m backend.tests.e2e.performance_test -v v1
  python -m backend.tests.e2e.performance_test -v v2
  python -m backend.tests.e2e.performance_test -v v7
  python -m backend.tests.e2e.performance_test -v all
"""

import argparse
import statistics
import time
from typing import Dict, List, Tuple

from backend.app.services.parsing.parser_engine import ParserEngine
from backend.app.services.workflow.trigger_queue import TriggerQueue
from backend.app.services.workflow.orchestrator import Orchestrator


# ------------------------------------------------------------
# COMBINED COMMAND LIST (Option C)
# Your commands + 50 multi-domain examples
# ------------------------------------------------------------
COMMANDS = [
    # --- Your original commands ---
    "Generate a quarterly cashflow report for EMEA.",
    "Create a daily maintenance checklist for the packaging line.",
    "Restart the payments service in EU cluster.",
    "Create a new support case for customer BlueWave Inc.",
    "Check inventory levels for smart watches in Europe region.",
    "Schedule a follow-up appointment reminder for patient A129.",
    "Create a purchase order for 300 laptops.",
    "Generate monthly claims summary for insurance partners.",

    # --- Multi-domain additions ---
    "Book vessel Maersk Elba arriving next Tuesday.",
    "Create FX hedge ticket for EURUSD notional 5M.",
    "Generate HR onboarding workflow for employee John Doe.",
    "Submit expense claim for $450 hotel stay.",
    "Run predictive maintenance scan for line 7.",
    "Approve procurement order #55632 for spare parts.",
    "Generate risk dashboard for crude oil exposure.",
    "Trigger incident response workflow for server SRV-22.",
    "Sync patient lab results for case 22013.",
    "Create logistics shipment plan for 14 pallets.",
    "Generate legal compliance report for Q4.",
    "Close customer ticket #88271.",
    "Start batch manufacturing for product code CH-221.",
    "Create insurance underwriting checklist for policy AX99.",
    "Generate sales pipeline report for APAC.",
    "Create real-estate due diligence summary for building A24.",
    "Run energy usage forecast for solar plant B12.",
    "Trigger cybersecurity audit workflow.",
    "Create data export for enterprise customer RedPeak.",
    "Update service-level agreement for gold-tier customers.",
    "Check credit risk exposure for portfolio X1.",
    "Generate financial consolidation report for FY2024.",
    "Start ML model training for anomaly detection.",
    "Pull warehouse cycle-count stats.",
    "Generate support sentiment analysis report.",
    "Check doctor availability for oncology department.",
    "Book maintenance crew visit for pump station PS88.",
    "Generate environmental compliance audit.",
    "Scan internal APIs for vulnerabilities.",
    "Trigger reconciliation workflow for payments.",
    "Generate manufacturing OEE report.",
    "Create escalation workflow for stalled shipments.",
]


# ------------------------------------------------------------
# Shared utilities
# ------------------------------------------------------------
def percentile(values: List[float], p: float) -> float:
    if not values:
        return 0.0
    idx = int(round((p / 100.0) * (len(values) - 1)))
    return values[idx]


# ------------------------------------------------------------
# v1 — Parser-only latency
# ------------------------------------------------------------
def run_v1() -> Dict[str, float]:
    parser = ParserEngine()
    samples = []

    for cmd in COMMANDS:
        t0 = time.perf_counter()
        parser.parse_command(cmd, context={})
        t1 = time.perf_counter()
        samples.append((t1 - t0) * 1000)

    samples_sorted = sorted(samples)
    return {
        "p50": percentile(samples_sorted, 50),
        "p95": percentile(samples_sorted, 95),
        "p99": percentile(samples_sorted, 99),
        "avg": statistics.mean(samples_sorted),
        "max": max(samples_sorted),
        "count": len(samples_sorted),
    }


# ------------------------------------------------------------
# v2 — Parser + Trigger Queue latency
# ------------------------------------------------------------
def run_v2() -> Dict[str, float]:
    parser = ParserEngine()
    samples = []

    for cmd in COMMANDS:
        t0 = time.perf_counter()
        parsed = parser.parse_command(cmd, context={})
        t1 = time.perf_counter()
        TriggerQueue.enqueue_trigger({"parsed": parsed, "metadata": {"simulate": True}})
        t2 = time.perf_counter()
        samples.append((t2 - t0) * 1000)

    samples_sorted = sorted(samples)
    return {
        "p50": percentile(samples_sorted, 50),
        "p95": percentile(samples_sorted, 95),
        "p99": percentile(samples_sorted, 99),
        "avg": statistics.mean(samples_sorted),
        "max": max(samples_sorted),
        "count": len(samples_sorted),
    }


# ------------------------------------------------------------
# v3 — Parser + Orchestrator simulation
# ------------------------------------------------------------
def run_v3() -> Dict[str, float]:
    parser = ParserEngine()
    orch = Orchestrator()
    samples = []

    for cmd in COMMANDS:
        t0 = time.perf_counter()
        parsed = parser.parse_command(cmd, context={})
        orch.run([], parsed, simulate=True)  # simulate mode
        t1 = time.perf_counter()
        samples.append((t1 - t0) * 1000)

    samples_sorted = sorted(samples)
    return {
        "p50": percentile(samples_sorted, 50),
        "p95": percentile(samples_sorted, 95),
        "p99": percentile(samples_sorted, 99),
        "avg": statistics.mean(samples_sorted),
        "max": max(samples_sorted),
        "count": len(samples_sorted),
    }


# ------------------------------------------------------------
# v4 — Domain traffic simulation (just counts)
# ------------------------------------------------------------
def run_v4():
    parser = ParserEngine()
    domain_counts = {}

    for cmd in COMMANDS:
        parsed = parser.parse_command(cmd, context={})
        dom = parsed.get("domain", "unknown")
        domain_counts[dom] = domain_counts.get(dom, 0) + 1

    return domain_counts


# ------------------------------------------------------------
# v5 — Stress test (10 rapid cycles)
# ------------------------------------------------------------
def run_v5():
    parser = ParserEngine()
    samples = []

    for _ in range(10):
        for cmd in COMMANDS:
            t0 = time.perf_counter()
            parser.parse_command(cmd, context={})
            t1 = time.perf_counter()
            samples.append((t1 - t0) * 1000)

    return {
        "runs": len(samples),
        "avg": statistics.mean(samples),
        "max": max(samples),
    }


# ------------------------------------------------------------
# v6 — Extended statistics
# ------------------------------------------------------------
def run_v6():
    parser = ParserEngine()
    samples = []

    for cmd in COMMANDS:
        t0 = time.perf_counter()
        parser.parse_command(cmd, context={})
        t1 = time.perf_counter()
        samples.append({"cmd": cmd, "lat_ms": (t1 - t0) * 1000})

    sorted_samples = sorted(samples, key=lambda x: x["lat_ms"], reverse=True)
    values = [s["lat_ms"] for s in samples]

    return {
        "std_dev": statistics.stdev(values) if len(values) > 2 else 0.0,
        "slowest_5": sorted_samples[:5],
        "avg": statistics.mean(values),
        "max": max(values),
        "p99": percentile(sorted(values), 99),
    }


# ------------------------------------------------------------
# v7 — Full commercial-grade performance suite
# ------------------------------------------------------------
def run_v7():
    parser = ParserEngine()
    samples = []

    for cmd in COMMANDS:
        t0 = time.perf_counter()
        parser.parse_command(cmd, context={})
        t1 = time.perf_counter()
        samples.append((t1 - t0) * 1000)

    values = sorted(samples)

    return {
        "p50": percentile(values, 50),
        "p90": percentile(values, 90),
        "p95": percentile(values, 95),
        "p99": percentile(values, 99),
        "p999": percentile(values, 99.9),
        "avg": statistics.mean(values),
        "max": max(values),
        "slow_path_detected": percentile(values, 95) > 3000,
    }


# ------------------------------------------------------------
# CLI
# ------------------------------------------------------------
def cli():
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--version", required=True, choices=["v1","v2","v3","v4","v5","v6","v7","all"])
    args = parser.parse_args()

    if args.version == "v1":
        print(run_v1())
    elif args.version == "v2":
        print(run_v2())
    elif args.version == "v3":
        print(run_v3())
    elif args.version == "v4":
        print(run_v4())
    elif args.version == "v5":
        print(run_v5())
    elif args.version == "v6":
        print(run_v6())
    elif args.version == "v7":
        print(run_v7())
    elif args.version == "all":
        print({
            "v1": run_v1(),
            "v2": run_v2(),
            "v3": run_v3(),
            "v4": run_v4(),
            "v5": run_v5(),
            "v6": run_v6(),
            "v7": run_v7(),
        })


if __name__ == "__main__":
    cli()
