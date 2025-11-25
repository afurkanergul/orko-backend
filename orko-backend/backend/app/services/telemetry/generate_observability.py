from __future__ import annotations

import argparse
import json
import statistics
import time
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Tuple

from backend.app.services.parsing.eval_v2 import ParserEvaluatorV2
from backend.app.services.parsing.domain_weakness_detector import detect_weak_domains


# ------------------------------------------------------------
# Paths
# ------------------------------------------------------------
TELEMETRY_PATH = Path("backend/logs/telemetry")
RESULTS_DIR = Path("backend/tests/eval/results")

OBS_V1_MD = RESULTS_DIR / "observability_report_v1.md"
OBS_V1_JSON = RESULTS_DIR / "observability_report_v1.json"

OBS_V2_MD = RESULTS_DIR / "observability_report_v2.md"
OBS_V2_JSON = RESULTS_DIR / "observability_report_v2.json"

OBS_V3_MD = RESULTS_DIR / "observability_report_v3.md"
OBS_V4_HTML = RESULTS_DIR / "observability_report_v4.html"
OBS_V5_JSON = RESULTS_DIR / "observability_grafana_v5.json"
OBS_V6_JSON = RESULTS_DIR / "observability_anomalies_v6.json"
OBS_V7_MD = RESULTS_DIR / "observability_suggestions_v7.md"


# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------

def load_events(name: str) -> List[Dict[str, Any]]:
    path = TELEMETRY_PATH / f"{name}.jsonl"
    if not path.exists():
        return []
    out: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            out.append(json.loads(line))
    return out


def compute_latency(samples: List[float]) -> Dict[str, float]:
    if not samples:
        return {"p50": 0.0, "p95": 0.0, "p99": 0.0, "avg": 0.0, "max": 0.0}

    values = sorted(samples)

    def pct(p: float) -> float:
        if not values:
            return 0.0
        k = int(round((p / 100.0) * (len(values) - 1)))
        return float(values[k])

    return {
        "p50": pct(50),
        "p95": pct(95),
        "p99": pct(99),
        "avg": float(statistics.mean(values)),
        "max": float(max(values)),
    }


def build_common_stats() -> Dict[str, Any]:
    """
    Core aggregation: telemetry + evaluator v2.
    All versions (v1–v7) build on this.
    """
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    parser_ev = load_events("parser")
    trigger_ev = load_events("trigger")
    workflow_ev = load_events("workflow")

    parser_total = len(parser_ev)
    trigger_total = len(trigger_ev)
    workflow_total = len(workflow_ev)

    # Domain & action traffic
    domain_counts: Dict[str, int] = defaultdict(int)
    action_counts: Dict[str, int] = defaultdict(int)
    guardrail_flags: Dict[str, int] = defaultdict(int)

    for e in parser_ev:
        dom = e.get("domain") or "unknown"
        act = e.get("action") or "unknown"
        domain_counts[dom] += 1
        action_counts[act] += 1

        ctx = e.get("context") or {}
        flags = ctx.get("guardrail_flags") or []
        for f in flags:
            guardrail_flags[str(f)] += 1

    # Workflow errors
    workflow_errors = 0
    workflow_latencies: List[float] = []

    for w in workflow_ev:
        if w.get("error"):
            workflow_errors += 1
        result = w.get("result") or {}
        if isinstance(result, dict):
            dur = result.get("duration_ms")
            if isinstance(dur, (int, float)):
                workflow_latencies.append(float(dur))

    latency_stats = compute_latency(workflow_latencies)

    # Evaluator v2 → PRF + weak domains
    evaluator = ParserEvaluatorV2()
    _, summary = evaluator.run()
    weak_domains = detect_weak_domains(summary)

    stats: Dict[str, Any] = {
        "timestamp": time.time(),
        "traffic": {
            "parser_events": parser_total,
            "trigger_events": trigger_total,
            "workflow_events": workflow_total,
            "domains": dict(domain_counts),
            "actions": dict(action_counts),
        },
        "latency": latency_stats,
        "errors": {
            "workflow_errors": workflow_errors,
        },
        "guardrails": dict(guardrail_flags),
        "weak_domains": weak_domains,
        "prf_metrics": summary.get("per_domain_prf") or {},
        "per_domain_accuracy": summary.get("per_domain_accuracy") or {},
        "accuracy": summary.get("accuracy", 0.0),
        "total_commands": summary.get("total", 0),
    }
    return stats


# ------------------------------------------------------------
# v1 — Minimal Observability (basic stats)
# ------------------------------------------------------------

def generate_v1(stats: Dict[str, Any]) -> None:
    data = {
        "parser_total": stats["traffic"]["parser_events"],
        "trigger_total": stats["traffic"]["trigger_events"],
        "workflow_total": stats["traffic"]["workflow_events"],
        "domains": stats["traffic"]["domains"],
        "actions": stats["traffic"]["actions"],
        "workflow_errors": stats["errors"]["workflow_errors"],
    }

    with OBS_V1_JSON.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    lines: List[str] = []
    lines.append("# ORKO Observability Dashboard v1")
    lines.append("")
    lines.append(f"Total parser events: {data['parser_total']}")
    lines.append(f"Total trigger events: {data['trigger_total']}")
    lines.append(f"Total workflow events: {data['workflow_total']}")
    lines.append(f"Workflow errors: {data['workflow_errors']}")
    lines.append("\n## Domain Counts")
    for k, v in data["domains"].items():
        lines.append(f"- {k}: {v}")

    lines.append("\n## Action Counts")
    for k, v in data["actions"].items():
        lines.append(f"- {k}: {v}")

    with OBS_V1_MD.open("w", encoding="utf-8") as f:
        f.write("\n".join(lines))


# ------------------------------------------------------------
# v2 — Rich stats (what you have now)
# ------------------------------------------------------------

def generate_v2(stats: Dict[str, Any]) -> None:
    with OBS_V2_JSON.open("w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)

    lines: List[str] = []
    lines.append("# ORKO Observability Dashboard v2")
    lines.append("")
    lines.append("## 1. Traffic Overview")
    lines.append(f"- Parser events: **{stats['traffic']['parser_events']}**")
    lines.append(f"- Trigger events: **{stats['traffic']['trigger_events']}**")
    lines.append(f"- Workflow events: **{stats['traffic']['workflow_events']}**")

    lines.append("\n### Domain Traffic")
    for dom, cnt in stats["traffic"]["domains"].items():
        lines.append(f"- {dom}: {cnt}")

    lines.append("\n### Action Frequency")
    for act, cnt in stats["traffic"]["actions"].items():
        lines.append(f"- {act}: {cnt}")

    lat = stats["latency"]
    lines.append("\n## 2. Latency (Workflow Execution)")
    lines.append(f"- p50: {lat['p50']:.2f} ms")
    lines.append(f"- p95: {lat['p95']:.2f} ms")
    lines.append(f"- p99: {lat['p99']:.2f} ms")
    lines.append(f"- avg: {lat['avg']:.2f} ms")
    lines.append(f"- max: {lat['max']:.2f} ms")

    lines.append("\n## 3. Errors")
    lines.append(f"- Workflow errors: **{stats['errors']['workflow_errors']}**")

    lines.append("\n## 4. Guardrail Flags (Safety Usage)")
    if stats["guardrails"]:
        for f, cnt in stats["guardrails"].items():
            lines.append(f"- {f}: {cnt}")
    else:
        lines.append("- (no guardrail flags recorded)")

    lines.append("\n## 5. Weak Domains (from Evaluator v2)")
    weak = stats["weak_domains"] or []
    if weak:
        for entry in weak:
            lines.append(
                f"- {entry['domain']} "
                f"(F1={entry['f1']:.2f}, P={entry['precision']:.2f}, R={entry['recall']:.2f})"
            )
    else:
        lines.append("- None — all domains healthy.")

    lines.append("\n## 6. Per-Domain PRF")
    prf = stats["prf_metrics"] or {}
    acc = stats["per_domain_accuracy"] or {}
    for dom, m in prf.items():
        lines.append(f"### {dom}")
        lines.append(f"- Accuracy: {acc.get(dom, 0.0):.2f}")
        lines.append(f"- Precision: {m['precision']:.2f}")
        lines.append(f"- Recall: {m['recall']:.2f}")
        lines.append(f"- F1: {m['f1']:.2f}")
        lines.append(f"- TP={m['tp']}, FP={m['fp']}, FN={m['fn']}")

    with OBS_V2_MD.open("w", encoding="utf-8") as f:
        f.write("\n".join(lines))


# ------------------------------------------------------------
# v3 — ASCII charts (pretty markdown)
# ------------------------------------------------------------

def _ascii_bar(value: int, max_value: int, width: int = 40) -> str:
    if max_value <= 0:
        return ""
    length = int(round((value / max_value) * width))
    return "#" * max(length, 1)


def generate_v3(stats: Dict[str, Any]) -> None:
    domains = stats["traffic"]["domains"] or {}
    actions = stats["traffic"]["actions"] or {}

    max_dom = max(domains.values()) if domains else 1
    max_act = max(actions.values()) if actions else 1

    lines: List[str] = []
    lines.append("# ORKO Observability Dashboard v3 — ASCII Charts")
    lines.append("")

    lines.append("## Domain Traffic (Histogram)")
    for dom, cnt in domains.items():
        bar = _ascii_bar(cnt, max_dom)
        lines.append(f"- {dom:20s} | {bar} ({cnt})")

    lines.append("\n## Action Frequency (Histogram)")
    for act, cnt in actions.items():
        bar = _ascii_bar(cnt, max_act)
        lines.append(f"- {act:20s} | {bar} ({cnt})")

    with OBS_V3_MD.open("w", encoding="utf-8") as f:
        f.write("\n".join(lines))


# ------------------------------------------------------------
# v4 — HTML dashboard
# ------------------------------------------------------------

def generate_v4(stats: Dict[str, Any]) -> None:
    doms = stats["traffic"]["domains"] or {}
    acts = stats["traffic"]["actions"] or {}
    lat = stats["latency"] or {}
    weak = stats["weak_domains"] or []
    prf = stats["prf_metrics"] or {}

    html = [
        "<!DOCTYPE html>",
        "<html>",
        "<head>",
        "<meta charset='utf-8' />",
        "<title>ORKO Observability Dashboard v4</title>",
        "<style>",
        "body { font-family: Arial, sans-serif; padding: 20px; }",
        "h1, h2, h3 { color: #222; }",
        "table { border-collapse: collapse; margin-bottom: 20px; }",
        "th, td { border: 1px solid #ccc; padding: 6px 10px; }",
        "th { background: #f2f2f2; }",
        "</style>",
        "</head>",
        "<body>",
        "<h1>ORKO Observability Dashboard v4</h1>",
        f"<p>Generated at: {time.ctime(stats['timestamp'])}</p>",
        "<h2>Traffic Overview</h2>",
        "<ul>",
        f"<li>Parser events: <b>{stats['traffic']['parser_events']}</b></li>",
        f"<li>Trigger events: <b>{stats['traffic']['trigger_events']}</b></li>",
        f"<li>Workflow events: <b>{stats['traffic']['workflow_events']}</b></li>",
        "</ul>",
        "<h2>Domain Traffic</h2>",
        "<table><tr><th>Domain</th><th>Count</th></tr>",
    ]
    for d, c in doms.items():
        html.append(f"<tr><td>{d}</td><td>{c}</td></tr>")
    html.append("</table>")

    html.append("<h2>Action Frequency</h2>")
    html.append("<table><tr><th>Action</th><th>Count</th></tr>")
    for a, c in acts.items():
        html.append(f"<tr><td>{a}</td><td>{c}</td></tr>")
    html.append("</table>")

    html.append("<h2>Latency (ms)</h2>")
    html.append("<ul>")
    html.append(f"<li>p50: {lat.get('p50', 0):.2f}</li>")
    html.append(f"<li>p95: {lat.get('p95', 0):.2f}</li>")
    html.append(f"<li>p99: {lat.get('p99', 0):.2f}</li>")
    html.append(f"<li>avg: {lat.get('avg', 0):.2f}</li>")
    html.append(f"<li>max: {lat.get('max', 0):.2f}</li>")
    html.append("</ul>")

    html.append("<h2>Weak Domains</h2>")
    if weak:
        html.append("<table><tr><th>Domain</th><th>Precision</th><th>Recall</th><th>F1</th></tr>")
        for w in weak:
            html.append(
                f"<tr><td>{w['domain']}</td>"
                f"<td>{w['precision']:.2f}</td>"
                f"<td>{w['recall']:.2f}</td>"
                f"<td>{w['f1']:.2f}</td></tr>"
            )
        html.append("</table>")
    else:
        html.append("<p>No weak domains detected.</p>")

    html.append("<h2>Per-Domain PRF</h2>")
    html.append("<table><tr><th>Domain</th><th>Precision</th><th>Recall</th><th>F1</th></tr>")
    for dom, m in prf.items():
        html.append(
            f"<tr><td>{dom}</td>"
            f"<td>{m['precision']:.2f}</td>"
            f"<td>{m['recall']:.2f}</td>"
            f"<td>{m['f1']:.2f}</td></tr>"
        )
    html.append("</table>")

    html.append("</body></html>")

    with OBS_V4_HTML.open("w", encoding="utf-8") as f:
        f.write("\n".join(html))


# ------------------------------------------------------------
# v5 — Grafana / BI-friendly JSON
# ------------------------------------------------------------

def generate_v5(stats: Dict[str, Any]) -> None:
    doms = stats["traffic"]["domains"] or {}
    prf = stats["prf_metrics"] or {}
    acc = stats["per_domain_accuracy"] or {}

    domains_list = []
    for dom, count in doms.items():
        metrics = prf.get(dom, {})
        domains_list.append(
            {
                "domain": dom,
                "count": count,
                "accuracy": acc.get(dom, 0.0),
                "precision": metrics.get("precision", 0.0),
                "recall": metrics.get("recall", 0.0),
                "f1": metrics.get("f1", 0.0),
            }
        )

    grafana_payload = {
        "timestamp": stats["timestamp"],
        "latency": stats["latency"],
        "workflow_errors": stats["errors"]["workflow_errors"],
        "domains": domains_list,
        "overall_accuracy": stats["accuracy"],
        "total_commands": stats["total_commands"],
    }

    with OBS_V5_JSON.open("w", encoding="utf-8") as f:
        json.dump(grafana_payload, f, indent=2)


# ------------------------------------------------------------
# v6 — Simple anomaly detection
# ------------------------------------------------------------

def generate_v6(stats: Dict[str, Any]) -> None:
    anomalies: List[Dict[str, Any]] = []

    wf_events = stats["traffic"]["workflow_events"]
    wf_errors = stats["errors"]["workflow_errors"]
    if wf_events > 0:
        err_rate = wf_errors / wf_events
        if err_rate > 0.10:
            anomalies.append(
                {
                    "type": "high_error_rate",
                    "message": f"Workflow error rate is {err_rate:.2%}, above 10%.",
                    "workflow_events": wf_events,
                    "workflow_errors": wf_errors,
                }
            )

    prf = stats["prf_metrics"] or {}
    for dom, m in prf.items():
        if m["f1"] < 0.75:
            anomalies.append(
                {
                    "type": "low_f1_domain",
                    "domain": dom,
                    "f1": m["f1"],
                    "precision": m["precision"],
                    "recall": m["recall"],
                    "message": f"Domain {dom} has low F1 ({m['f1']:.2f}).",
                }
            )

    payload = {
        "timestamp": stats["timestamp"],
        "anomalies": anomalies,
    }

    with OBS_V6_JSON.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


# ------------------------------------------------------------
# v7 — Improvement suggestions (human-readable)
# ------------------------------------------------------------

def generate_v7(stats: Dict[str, Any]) -> None:
    lines: List[str] = []
    lines.append("# ORKO Observability Suggestions v7")
    lines.append("")
    lines.append(f"Generated at: {time.ctime(stats['timestamp'])}")
    lines.append("")
    lines.append("## 1. Domain-level Suggestions")

    weak = stats["weak_domains"] or []
    if not weak:
        lines.append("- All domains meet current F1 thresholds. Continue monitoring.")
    else:
        for w in weak:
            dom = w["domain"]
            f1 = w["f1"]
            lines.append(f"### Domain: {dom}")
            lines.append(f"- F1: {f1:.2f}")
            lines.append("- Suggested actions:")
            lines.append("  - Add more labeled examples for this domain.")
            lines.append("  - Inspect error JSONL (parser_eval_errors_v2.jsonl) for recurring patterns.")
            lines.append("  - Tighten or expand guardrails / prompts for this domain.")
            lines.append("")

    lines.append("## 2. Guardrail & Safety Suggestions")
    if stats["guardrails"]:
        lines.append("- Guardrail flags are being triggered. Review the most common flags:")
        for flag, cnt in stats["guardrails"].items():
            lines.append(f"  - {flag}: {cnt}")
        lines.append("- Suggested:")
        lines.append("  - For frequent `blocked_action` flags, check if users need safe alternatives.")
        lines.append("  - For `risky_action` flags, ensure confirmation flows are clear in the UI.")
    else:
        lines.append("- No guardrail flags recorded. Ensure destructive actions are still properly tested.")

    wf_events = stats["traffic"]["workflow_events"]
    wf_errors = stats["errors"]["workflow_errors"]
    lines.append("\n## 3. Reliability Suggestions")
    if wf_events > 0:
        err_rate = wf_errors / wf_events
        lines.append(f"- Current workflow error rate: {err_rate:.2%}")
        if err_rate > 0.10:
            lines.append("- Suggested:")
            lines.append("  - Inspect workflow DLQ entries and fix fragile steps.")
            lines.append("  - Add retries / idempotency to external calls.")
            lines.append("  - Add tests for most failing workflows.")
        else:
            lines.append("- Error rate is within acceptable bounds. Keep monitoring.")
    else:
        lines.append("- No workflow executions recorded. Run more end-to-end flows to gather data.")

    with OBS_V7_MD.open("w", encoding="utf-8") as f:
        f.write("\n".join(lines))


# ------------------------------------------------------------
# CLI entrypoint
# ------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="ORKO Unified Observability Generator (v1–v7)"
    )
    parser.add_argument(
        "--version",
        "-v",
        choices=["v1", "v2", "v3", "v4", "v5", "v6", "v7", "all"],
        default="v2",
        help="Which observability version to generate (default: v2).",
    )
    args = parser.parse_args()

    stats = build_common_stats()

    if args.version in ("v1", "all"):
        generate_v1(stats)
    if args.version in ("v2", "all"):
        generate_v2(stats)
    if args.version in ("v3", "all"):
        generate_v3(stats)
    if args.version in ("v4", "all"):
        generate_v4(stats)
    if args.version in ("v5", "all"):
        generate_v5(stats)
    if args.version in ("v6", "all"):
        generate_v6(stats)
    if args.version in ("v7", "all"):
        generate_v7(stats)

    if args.version == "all":
        print("Observability v1–v7 dashboards generated.")
    else:
        print(f"Observability {args.version} dashboard generated.")


if __name__ == "__main__":
    main()
