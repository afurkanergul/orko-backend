# backend/app/services/parsing/_local_test_day2_samples.py

from backend.app.services.parsing.parser_engine import get_default_parser_engine

def main() -> None:
    engine = get_default_parser_engine()

    samples = [
        "sell 500 tons of corn to ACME at market price",
        "book shipment of 300 tons soybeans from Santos to Rotterdam",
        "draft sales contract for 1000 tons sugar to Client Y",
    ]

    for s in samples:
        parsed = engine.parse_command(s, context={"source": "day2_smoke"})
        print("\n=== INPUT ===")
        print(s)
        print("=== PARSED ===")
        print(parsed if isinstance(parsed, dict) else parsed.to_dict())

if __name__ == "__main__":
    main()
