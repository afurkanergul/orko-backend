# backend/tests/e2e/robustness_test.py

from typing import Dict, List

from backend.app.services.parsing.parser_engine import ParserEngine


ROBUST_COMMANDS: List[str] = [
    # Long command
    "Please generate a detailed cross-region revenue report for all enterprise "
    "customers in EMEA and North America for the last three completed quarters, "
    "grouped by product family and sales channel, and highlight any anomalies "
    "bigger than 10 percent deviation from trend.",
    # Typos / shorthand
    "pls gen qtrly cashflw rpt 4 emea asap",
    # Code-mixed / multilingual
    "Lütfen EMEA için aylık satış raporunu oluştur ve top 10 müşteriyi göster.",
    "Crea un informe de tickets abiertos de soporte para ACME en este mes.",
    # Half-finished
    "Need to check inventory for smart watches in...",
    # Emojis / noise
    "Show all high priority 🚨 incidents for prod env, last 24h",
]


def run_robustness_smoke() -> Dict[str, bool]:
    parser = ParserEngine()
    results: Dict[str, bool] = {}

    for cmd in ROBUST_COMMANDS:
        try:
            parsed = parser.parse_command(cmd, context={})
            # Basic sanity: parser should return a dict with keys
            ok = isinstance(parsed, dict) and "action" in parsed and "domain" in parsed
            results[cmd] = ok
        except Exception:
            results[cmd] = False

    return results


if __name__ == "__main__":
    res = run_robustness_smoke()
    for cmd, ok in res.items():
        status = "OK" if ok else "FAIL"
        print(f"[{status}] {cmd[:80]}...")
