# backend/app/services/parsing/fewshot_generator.py

from __future__ import annotations
import json
from pathlib import Path
from backend.app.services.parsing.guardrail_generator import GuardrailGenerator

OUTPUT_PATH = Path("backend/docs/fewshot_suggestions_v2.json")


class FewShotGenerator:
    """
    Builds synthetic few-shot examples based on the error patterns and guardrail suggestions.
    """

    def __init__(self):
        self.guards = GuardrailGenerator().generate()

    def generate(self):
        examples = []

        # Convert domain confusion into few-shots
        for rule in self.guards.get("domain_rules", []):
            examples.append({
                "input": f"User says: '{rule['expected_domain']} specific command with domain ambiguity'",
                "output": {
                    "domain": rule["expected_domain"],
                    "action": "clarified_action",
                    "parameters": {}
                },
                "hint": rule["suggestion"]
            })

        # Action confusion examples
        for rule in self.guards.get("action_rules", []):
            examples.append({
                "input": f"User says a phrase that could mean {rule['wrong_predicted_action']} but should map to {rule['expected_action']}",
                "output": {
                    "domain": "correct_domain",
                    "action": rule["expected_action"],
                    "parameters": {}
                },
                "hint": rule["suggestion"]
            })

        # Parameter rules
        for rule in self.guards.get("parameter_rules", []):
            examples.append({
                "input": f"Command referencing missing parameter '{rule['parameter']}'",
                "output": {
                    "parameters": {rule["parameter"]: "example_value"}
                },
                "hint": rule["suggestion"]
            })

        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        with OUTPUT_PATH.open("w", encoding="utf-8") as f:
            json.dump(examples, f, indent=2)

        return examples
