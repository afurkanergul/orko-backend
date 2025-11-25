from backend.app.services.parsing.parser_engine import get_default_parser_engine
import json

if __name__ == "__main__":
    engine = get_default_parser_engine()
    risky = engine.parse_command("delete all triggers", context={"source": "test"})
    print(json.dumps(risky, indent=2))
