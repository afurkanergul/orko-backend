# backend/tests/e2e/test_runner.py

from pathlib import Path
import yaml
import time

from backend.app.services.parsing.parser_engine import ParserEngine
from backend.app.services.workflow.orchestrator import Orchestrator
from backend.app.services.workflow.trigger_queue import TriggerQueue


E2E_PATH = Path(__file__).resolve().parent / "test_scenarios.yml"


def run_e2e_tests():
    with open(E2E_PATH, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    parser = ParserEngine()
    orchestrator = Orchestrator()

    results = []
    metrics = {
        "total": 0,
        "passed_domain": 0,
        "passed_action": 0,
        "runtime_seconds": 0.0,
    }

    start = time.time()

    for sc in data["scenarios"]:
        metrics["total"] += 1

        cmd = sc["command"]
        parsed = parser.parse_command(cmd, context={})

        domain_ok = parsed.get("domain") == sc["expected_domain"]
        action_ok = parsed.get("action") == sc["expected_action"]

        if domain_ok:
            metrics["passed_domain"] += 1
        if action_ok:
            metrics["passed_action"] += 1

        # Map into workflow via orchestrator
        mapped = orchestrator.handle_intent(parsed)
        workflow_name = mapped.get("workflow_name")

        payload = {
            "trigger_id": sc["id"],
            "parsed": parsed,
            "metadata": {"simulate": True},
        }

        job_id = TriggerQueue.enqueue_trigger(payload)

        results.append({
            "id": sc["id"],
            "command": cmd,
            "domain_ok": domain_ok,
            "action_ok": action_ok,
            "workflow": workflow_name,
            "trigger_job_id": job_id,
        })

    metrics["runtime_seconds"] = round(time.time() - start, 4)

    return {"results": results, "metrics": metrics}
