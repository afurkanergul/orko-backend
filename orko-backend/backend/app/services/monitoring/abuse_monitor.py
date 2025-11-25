# backend/app/services/monitoring/abuse_monitor.py

import logging
from typing import Optional

import redis

from backend.app.core.config import settings

logger = logging.getLogger(__name__)


class AbuseMonitor:
    """
    Tracks repeated rate-limit violations for users/orgs.

    Multi-industry: no assumptions about domain.
    Only counts repeated exceeding of trigger limits (abuse detection).
    """

    def __init__(self) -> None:
        # Use same Redis as the rate limiter
        self._redis = redis.from_url(settings.RATE_LIMIT_REDIS_URL)
        self._window = 300  # 5 minutes

    def _key(self, user_id: Optional[str], org_id: Optional[str]) -> str:
        uid = user_id or "anonymous"
        oid = org_id or "no-org"
        return f"trigger:abuse:{oid}:{uid}"

    def record_violation(self, user_id: Optional[str], org_id: Optional[str]) -> int:
        key = self._key(user_id, org_id)
        pipe = self._redis.pipeline()

        pipe.incr(key, 1)
        pipe.expire(key, self._window)

        count, _ = pipe.execute()
        count = int(count)

        # Optional: external alerting hook
        if count >= 5:
            logger.warning(
                "AbuseMonitor: repeated rate-limit violations (count=%s, org=%s, user=%s)",
                count,
                org_id or "no-org",
                user_id or "anonymous",
            )

        return count
