# backend/tests/e2e/test_failure_cases.py

from backend.app.services.workflow.trigger_queue import TriggerQueue
from backend.app.services.parsing.parser_engine import ParserEngine
from backend.app.services.workflow.orchestrator import Orchestrator


def test_failure_scenarios():
    parser = ParserEngine()
    orchestrator = Orchestrator()

    failure_jobs = []

    # ---------------------------------------------------------
    # 1. ORCHESTRATOR FAILURE (invalid workflow/action)
    # ---------------------------------------------------------
    bad_workflow_payload = {
        "trigger_id": "FAIL-WORKFLOW-001",
        "parsed": {
            "domain": "it_ops",
            "action": "action_does_not_exist",
            "parameters": {},
            "context": {}
        },
        "metadata": {"simulate": True}
    }

    job1 = TriggerQueue.enqueue_trigger(bad_workflow_payload)
    failure_jobs.append(("orchestrator_failure", job1))

    # ---------------------------------------------------------
    # 2. PARSE FAILURE (intentionally invalid command)
    # ---------------------------------------------------------
    invalid_command = "##INVALID@@@"  # guaranteed parse fail
    try:
        parsed = parser.parse_command(invalid_command, context={})
    except Exception:
        # If parse_command raises, we convert it into a payload
        parsed = {
            "domain": None,
            "action": None,
            "parameters": None,
            "error": "forced_parse_error",
        }

    bad_parse_payload = {
        "trigger_id": "FAIL-PARSE-002",
        "parsed": parsed,
        "metadata": {"simulate": True}
    }

    job2 = TriggerQueue.enqueue_trigger(bad_parse_payload)
    failure_jobs.append(("parse_failure", job2))

    # ---------------------------------------------------------
    # 3. MISSING REQUIRED PARAMETERS
    # ---------------------------------------------------------
    missing_param_payload = {
        "trigger_id": "FAIL-MISSING-PARAM-003",
        "parsed": {
            "domain": "it_ops",
            "action": "restart_server",  # requires 'server_name'
            "parameters": {},            # missing parameters → workflow will fail
            "context": {}
        },
        "metadata": {"simulate": True}
    }

    job3 = TriggerQueue.enqueue_trigger(missing_param_payload)
    failure_jobs.append(("missing_parameters", job3))

    return failure_jobs
