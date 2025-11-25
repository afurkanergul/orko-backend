from pathlib import Path
from typing import Dict, Any, List
import yaml

BASE_DIR = Path(__file__).resolve().parent
CONFIG_DIR = BASE_DIR / "config"
DOMAIN_EXAMPLES_PATH = CONFIG_DIR / "domain_examples.yml"


class DomainRegistry:
    """
    Central registry for multi-domain AI parsing.

    Responsibilities:
    - Load domain_examples.yml
    - Expose domains + examples
    - Provide heuristic domain classifier
    - Provide keyword index for routing
    """

    def __init__(self):
        self._data = self._load()
        self._keywords = self._build_keyword_index()

    # ---------------------------------------------------------
    # Load YAML
    # ---------------------------------------------------------
    def _load(self) -> Dict[str, Any]:
        if not DOMAIN_EXAMPLES_PATH.exists():
            return {}
        with DOMAIN_EXAMPLES_PATH.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        return data

    # ---------------------------------------------------------
    # Keyword index for lightweight classification
    # ---------------------------------------------------------
    def _build_keyword_index(self) -> Dict[str, List[str]]:
        return {
            "trading": ["contract", "pnl", "hedge", "position", "shipment", "mt", "fob"],
            "logistics": ["truck", "vessel", "warehouse", "ship", "delivery", "eta", "silo"],
            "finance": ["invoice", "cashflow", "budget", "payable", "receivable"],
            "hr": ["employee", "payroll", "vacation", "leave", "recruit", "hire"],
            "it_ops": ["incident", "ticket", "deployment", "service", "cluster", "restart"],
            "legal": ["nda", "contract", "compliance", "legal", "terms"],
            "sales_marketing": ["campaign", "lead", "opportunity", "sales", "crm", "outbound"],
            "customer_support": ["support", "ticket", "sla", "csat", "customer"],
            "analytics": ["report", "dashboard", "kpi", "metric", "analysis"],
            "operations": ["checklist", "approval", "task", "maintenance", "operation"],
        }

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------
    @property
    def domains(self) -> List[str]:
        return list(self._data.keys())

    def get_examples(self, domain: str) -> Dict[str, Any]:
        return self._data.get(domain, {})

    # ---------------------------------------------------------
    # Heuristic Domain Classifier
    # ---------------------------------------------------------
    def guess_domain(self, command: str) -> str:
        text = command.lower()
        for domain, keywords in self._keywords.items():
            if any(k in text for k in keywords):
                return domain

        # fallback priority:
        if "operations" in self._data:
            return "operations"

        # fallback to first domain defined in YAML
        return next(iter(self._data.keys()), "operations")
