# backend/app/services/parsing/domain_weakness_detector.py

"""
Unified Domain Weakness Detector (v1 → v7)
------------------------------------------

This module replaces the simple v1 detector.

It now computes a multi-version commercial-grade domain weakness analysis,
including:

v1  – Basic threshold checks (F1/Precision/Recall)
v2  – PRF scoring (tp/fp/fn awareness)
v3  – Weighted weakness score
v4  – Drift detection (domain distribution shift)
v5  – Misclassification clustering (confusion-matrix based)
v6  – Severity grading (low / medium / high / critical)
v7  – Actionability scoring + recommended next actions

Output is fully structured and ready for:

- Observability dashboards
- Evaluation reports
- Pattern-mining pipelines
- Auto-prompt upgrade system
- CI regressions
"""


def detect_weak_domains(summary: dict) -> list:
    """
    Unified analyzer for domain weaknesses.

    summary must include:
    - per_domain_prf
    - confusion_matrix (optional)
    - per_domain_accuracy (optional)

    Returns list of domain weakness entries:

    {
        "domain": "finance",
        "precision": 0.72,
        "recall": 0.70,
        "f1": 0.71,
        "tp": 8,
        "fp": 3,
        "fn": 4,
        "severity": "high",
        "weakness_score": 0.84,
        "reasons": [...],
        "recommended_actions": [...]
    }
    """

    prf = summary.get("per_domain_prf", {}) or {}
    confusion = summary.get("confusion_matrix", {}) or {}
    accuracy = summary.get("per_domain_accuracy", {}) or {}

    results = []

    for dom, m in prf.items():
        p = m.get("precision", 0.0)
        r = m.get("recall", 0.0)
        f = m.get("f1", 0.0)
        tp = m.get("tp", 0)
        fp = m.get("fp", 0)
        fn = m.get("fn", 0)

        reasons = []
        severity_score = 0.0

        # ------------------------------------------------------
        # v1 – Basic threshold checks
        # ------------------------------------------------------
        if f < 0.80:
            reasons.append("Low F1 score")
            severity_score += (0.80 - f) * 1.2

        if p < 0.75:
            reasons.append("Low precision")
            severity_score += (0.75 - p) * 1.0

        if r < 0.75:
            reasons.append("Low recall (likely high FN)")
            severity_score += (0.75 - r) * 1.1

        # ------------------------------------------------------
        # v2 – FN-heavy domains (missed domain assignments)
        # ------------------------------------------------------
        if fn > fp:
            severity_score += min((fn - fp) * 0.05, 1.0)
            reasons.append("High false-negative rate")

        # ------------------------------------------------------
        # v3 – Weighted weakness score
        # ------------------------------------------------------
        # Normalize domain strength based on tp / all
        denom = tp + fp + fn
        if denom > 0:
            weakness = (fp + fn) / denom
            severity_score += weakness * 0.6
            if weakness > 0.4:
                reasons.append("Significant misclassification density")

        # ------------------------------------------------------
        # v4 – Drift detection
        # ------------------------------------------------------
        # If a domain suddenly appears much more or much less than typical
        dom_confusion = confusion.get(dom, {})
        total_predictions = sum(dom_confusion.values()) if dom_confusion else 0

        if total_predictions > 0 and tp / total_predictions < 0.4:
            reasons.append("Domain drift detected (low TP ratio)")
            severity_score += 0.7

        # ------------------------------------------------------
        # v5 – Confusion clustering
        # ------------------------------------------------------
        # Identify which domains it is confused with
        confused_with = sorted(
            [(k, v) for k, v in dom_confusion.items() if k != dom],
            key=lambda x: x[1],
            reverse=True,
        )

        # Top confusion domain contributes to severity
        if confused_with:
            top_confused, freq = confused_with[0]
            reasons.append(f"Frequently confused with '{top_confused}'")
            severity_score += min(freq * 0.1, 1.0)

        # ------------------------------------------------------
        # v6 – Severity grading
        # ------------------------------------------------------
        if severity_score >= 2.5:
            severity = "critical"
        elif severity_score >= 1.6:
            severity = "high"
        elif severity_score >= 0.9:
            severity = "medium"
        elif severity_score > 0:
            severity = "low"
        else:
            severity = "healthy"

        # ------------------------------------------------------
        # v7 – Actionability recommendations
        # ------------------------------------------------------
        actions = []

        if severity in ("high", "critical"):
            actions.append("Add 5–10 new training examples for this domain")
            actions.append("Review prompt+guardrail patterns for this domain")

        if fp > fn:
            actions.append("Improve domain boundary classification patterns")
        if fn > fp:
            actions.append("Add slot rules to reduce false negatives")

        if severity == "critical":
            actions.append("Urgent: add explicit few-shot examples for this domain")
            actions.append("Manually inspect confusion_matrix for domain drift")

        # ------------------------------------------------------
        # Build final entry
        # ------------------------------------------------------
        results.append({
            "domain": dom,
            "precision": p,
            "recall": r,
            "f1": f,
            "tp": tp,
            "fp": fp,
            "fn": fn,
            "severity": severity,
            "weakness_score": round(severity_score, 4),
            "reasons": reasons,
            "confused_with": [
                {"domain": cw, "count": ct} for cw, ct in confused_with[:3]
            ],
            "recommended_actions": actions,
        })

    # Sort by severity level: critical → high → medium → low → healthy
    rank = {"critical": 4, "high": 3, "medium": 2, "low": 1, "healthy": 0}
    results.sort(key=lambda x: rank[x["severity"]], reverse=True)

    return results


# Manual test runner
if __name__ == "__main__":
    print("Domain Weakness Detector v7 Test")
