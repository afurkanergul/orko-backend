# backend/tests/e2e/performance_concurrency_test.py

import asyncio
import time
from typing import Any, Dict, List

import httpx


TEST_COMMANDS = [
    "Generate a quarterly cashflow report for EMEA.",
    "Create a daily maintenance checklist for the packaging line.",
    "Restart the payments service in EU cluster.",
    "Check inventory levels for smart watches in Europe region.",
    "Schedule patch update for core banking system.",
]


async def _send_trigger(
    client: httpx.AsyncClient,
    base_url: str,
    command: str,
) -> Dict[str, Any]:
    t0 = time.perf_counter()
    resp = await client.post(
        f"{base_url}/trigger",
        json={
            "command": command,
            "org_id": "perf-org",
            "source": "perf-test",
            "channel": "cli",
            "request_id": f"req-{int(t0*1000)}",
        },
        timeout=10.0,
    )
    t1 = time.perf_counter()

    return {
        "status_code": resp.status_code,
        "latency_ms": (t1 - t0) * 1000.0,
    }


async def run_concurrency_test(
    base_url: str = "http://localhost:8000/api",
    concurrent_requests: int = 50,
) -> Dict[str, Any]:
    results: List[Dict[str, Any]] = []

    async with httpx.AsyncClient() as client:
        tasks = []
        for i in range(concurrent_requests):
            cmd = TEST_COMMANDS[i % len(TEST_COMMANDS)]
            tasks.append(_send_trigger(client, base_url, cmd))
        results = await asyncio.gather(*tasks)

    latencies = [r["latency_ms"] for r in results]
    latencies_sorted = sorted(latencies)

    def percentile(values: List[float], p: float) -> float:
        if not values:
            return 0.0
        k = int(round((p / 100.0) * (len(values) - 1)))
        return values[k]

    summary = {
        "requests": concurrent_requests,
        "p50_ms": percentile(latencies_sorted, 50),
        "p95_ms": percentile(latencies_sorted, 95),
        "p99_ms": percentile(latencies_sorted, 99),
        "max_ms": max(latencies) if latencies else 0.0,
        "errors": sum(1 for r in results if r["status_code"] >= 500),
    }
    return summary


if __name__ == "__main__":
    # Simple CLI runner
    summary = asyncio.run(run_concurrency_test())
    print("Concurrency Test Summary:", summary)
