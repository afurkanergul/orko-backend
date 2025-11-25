# backend/app/services/workflow/trigger_queue_loadtest.py

import time
from typing import Any, Dict, List

from backend.app.services.workflow.trigger_queue import TriggerQueue


def generate_dummy_payload(i: int) -> Dict[str, Any]:
    """
    Multi-domain-safe, generic dummy payload.
    We avoid any hard-coded trading or vertical-specific fields.
    """
    return {
        "trigger_id": f"loadtest-{i}",
        "parsed": {
            "intent": "test.load",
            "action": "noop",
            "confidence": 0.99,
            "domain": "generic",
            "context": {},
        },
        "metadata": {
            "org_id": "loadtest-org",
            "user_id": "loadtest-user",
            "source": "loadtest",
            "channel": "script",
        },
    }


def run_load_test(batch_size: int = 120, pause_seconds: float = 0.0) -> List[str]:
    """
    Enqueue batch_size triggers as fast as possible (optionally with small pauses)
    and return the list of Celery job IDs.
    """
    job_ids: List[str] = []

    for i in range(batch_size):
        payload = generate_dummy_payload(i)
        job_id = TriggerQueue.enqueue_trigger(payload)
        job_ids.append(job_id)

        if pause_seconds > 0:
            time.sleep(pause_seconds)

    return job_ids


if __name__ == "__main__":
    jobs = run_load_test(batch_size=120, pause_seconds=0.0)
    print(f"Enqueued {len(jobs)} trigger jobs.")
