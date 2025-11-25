# backend/app/services/parsing/masking.py
from __future__ import annotations

import re
from typing import Any, Dict


# ------------------------------------------------------------
# Regular expressions for PII detection
# ------------------------------------------------------------

# Email addresses
EMAIL_RE = re.compile(
    r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
)

# Phone numbers (+90 555..., +1-202..., etc.)
PHONE_RE = re.compile(
    r"\+?\d[\d\- ]{7,}\d"
)

# Generic IDs (6+ alphanumeric characters)
ID_RE = re.compile(
    r"\b[A-Z0-9]{6,}\b",
    flags=re.IGNORECASE
)

# Simple name pattern (capitalized words)
# Light protection to avoid over-masking
NAME_RE = re.compile(
    r"\b([A-Z][a-z]{2,})(\s+[A-Z][a-z]{2,})?\b"
)


# ------------------------------------------------------------
# PII Masking Functions
# ------------------------------------------------------------

def mask_pii(text: Any) -> Any:
    """
    Mask PII inside strings.
    Returns unchanged value for non-strings.

    Masks:
    - emails
    - phone numbers
    - IDs
    - person-like names (mildly)
    """
    if not isinstance(text, str):
        return text

    masked = text
    masked = EMAIL_RE.sub("[EMAIL_MASKED]", masked)
    masked = PHONE_RE.sub("[PHONE_MASKED]", masked)
    masked = ID_RE.sub("[ID_MASKED]", masked)
    masked = NAME_RE.sub("[NAME_MASKED]", masked)

    return masked


def mask_reasoning(reasoning: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recursively mask PII in nested reasoning traces.
    Supports:
    - dict
    - list
    - strings
    - primitive values
    """
    if not isinstance(reasoning, dict):
        return reasoning

    masked: Dict[str, Any] = {}

    for key, value in reasoning.items():

        if isinstance(value, str):
            masked[key] = mask_pii(value)

        elif isinstance(value, dict):
            masked[key] = mask_reasoning(value)

        elif isinstance(value, list):
            new_list = []
            for item in value:
                if isinstance(item, str):
                    new_list.append(mask_pii(item))
                elif isinstance(item, dict):
                    new_list.append(mask_reasoning(item))
                else:
                    new_list.append(item)
            masked[key] = new_list

        else:
            masked[key] = value

    return masked
