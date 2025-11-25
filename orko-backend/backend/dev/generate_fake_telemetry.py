from backend.app.services.parsing.parser_engine import ParserEngine
from backend.app.services.workflow.trigger_queue import TriggerQueue

p = ParserEngine()

commands = [
    "Generate a cashflow report for last quarter",
    "Restart the billing service in US cluster",
    "Create a support ticket for ACME about login issues",
    "Create a maintenance checklist for tomorrow morning",
    "List overdue invoices for EMEA",
    "Book a truck for 400 tons barley from Mersin"
]

for cmd in commands:
    parsed = p.parse_command(cmd, context={"user_id": "demo"})

    TriggerQueue.enqueue_trigger({
        "trigger_id": f"demo-{cmd[:5]}",
        "parsed": parsed,
        "metadata": {"simulate": True}
    })

print("Fake telemetry generated.")
