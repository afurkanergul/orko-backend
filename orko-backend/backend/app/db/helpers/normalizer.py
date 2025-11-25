# backend/app/db/helpers/normalizer.py

from typing import Any, Dict, List
from datetime import datetime, timezone

KNOWN_SOURCES = {"telegram", "whatsapp", "gmail", "drive", "sharepoint"}

def _to_iso8601(ts: Any) -> str:
    """
    Convert common timestamp inputs to an ISO-8601 'Z' string.
    Accepts datetime, int/float epoch seconds, or string.
    Falls back to 'now' if nothing sensible is provided.
    """
    if isinstance(ts, datetime):
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        return ts.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    if isinstance(ts, (int, float)):
        return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat().replace("+00:00", "Z")
    if isinstance(ts, str):
        # Best effort: try to parse common forms; if it fails, return as-is if it already looks ISO.
        try:
            # Very permissive parse:
            parsed = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            return parsed.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
        except Exception:
            # If string is already like '2025-11-23T00:00:00Z', keep it.
            if "T" in ts:
                return ts
    # Fallback to now:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def normalize_payload(payload: Dict[str, Any], default_org_id: int = 1) -> Dict[str, Any]:
    """
    Ensure the canonical shape:
      source (lowercase, known set),
      timestamp (ISO string),
      content (string),
      attachments (list),
      org_id (int).
    Non-destructive: if extra fields exist (sender, channel_msg_id, etc.), we keep them.
    """
    data = dict(payload) if payload else {}

    # ----- source -----
    src = str(data.get("source", "")).strip().lower()
    if src not in KNOWN_SOURCES:
        # Keep it lowercase anyway; you can decide later if you want to reject unknowns.
        src = src or "unknown"
    data["source"] = src

    # ----- timestamp -----
    data["timestamp"] = _to_iso8601(data.get("timestamp"))

    # ----- content -----
    content = data.get("content", "")
    if content is None:
        content = ""
    data["content"] = str(content)

    # ----- attachments -----
    atts = data.get("attachments", [])
    if atts is None:
        atts = []
    if not isinstance(atts, list):
        atts = [atts]
    data["attachments"] = atts  # type: List[Any]

    # ----- org_id -----
    try:
        org_id = int(data.get("org_id", default_org_id))
    except Exception:
        org_id = default_org_id
    data["org_id"] = org_id

    return data
