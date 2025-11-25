# backend/app/services/parsing/pattern_miner.py

from __future__ import annotations
import json
from collections import defaultdict
from pathlib import Path

ERROR_FILE = Path("backend/tests/eval/results/parser_eval_errors_v2.jsonl")


class PatternMiner:
    """
    Scans v2 evaluation errors and detects systematic issues:
    - Domain confusion
    - Action grouping errors
    - Missing parameters
    - Frequently misinterpreted phrasing
    """

    def __init__(self):
        self.errors = []
        self._load()

    def _load(self):
        if not ERROR_FILE.exists():
            return
        with ERROR_FILE.open("r", encoding="utf-8") as f:
            for line in f:
                self.errors.append(json.loads(line))

    def domain_confusion_patterns(self):
        matrix = defaultdict(lambda: defaultdict(int))
        for e in self.errors:
            exp = e["expected_domain"]
            pred = e["predicted_domain"] or "none"
            matrix[exp][pred] += 1
        return matrix

    def action_confusion_patterns(self):
        patterns = defaultdict(lambda: defaultdict(int))
        for e in self.errors:
            exp = e["expected_action"]
            pred = e["predicted_action"] or "none"
            patterns[exp][pred] += 1
        return patterns

    def missing_parameter_patterns(self):
        missing = defaultdict(int)
        for e in self.errors:
            exp = e["expected_parameters"]
            got = e["raw_parsed"].get("parameters", {}) or {}
            for k in exp.keys():
                if k not in got:
                    missing[k] += 1
        return missing

    def phrasing_patterns(self):
        tokens = defaultdict(int)
        for e in self.errors:
            for w in e["command"].split():
                tokens[w.lower()] += 1
        return {k: v for k, v in tokens.items() if v > 1}  # frequent terms

    def summarize(self):
        return {
            "domain_confusion": self.domain_confusion_patterns(),
            "action_confusion": self.action_confusion_patterns(),
            "missing_parameters": self.missing_parameter_patterns(),
            "frequent_phrasing_tokens": self.phrasing_patterns(),
        }
