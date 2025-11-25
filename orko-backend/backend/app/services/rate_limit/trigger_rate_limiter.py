# backend/app/services/rate_limit/trigger_rate_limiter.py

import time
from typing import Optional
import redis

from backend.app.core.config import settings


class RateLimitExceeded(Exception):
    """Raised when a rate limit has been exceeded."""


class TriggerRateLimiter:
    """
    Redis-backed per-user and per-org rate limiter for trigger requests.

    Multi-industry: no assumptions about domain. Only identity-based throttling.
    """

    def __init__(self) -> None:
        # Dedicated Redis instance/pool for rate limiting
        self._redis = redis.from_url(settings.RATE_LIMIT_REDIS_URL)

        # Config knobs (from .env or defaults)
        self._limit = settings.RATE_LIMIT_PER_MINUTE
        self._window = settings.RATE_LIMIT_WINDOW_SECONDS

    # ---------------------------------------------------------
    # Key helpers
    # ---------------------------------------------------------
    def _key_user(self, user_id: Optional[str]) -> str:
        uid = user_id or "anonymous"
        return f"trigger:rl:user:{uid}"

    def _key_org(self, org_id: Optional[str]) -> str:
        oid = org_id or "no-org"
        return f"trigger:rl:org:{oid}"

    def _now_bucket(self) -> int:
        """
        Fixed window:
        Each time window (e.g., 60s) is represented as epoch//window.
        """
        return int(time.time() // self._window)

    def _build_key(self, prefix: str, bucket: int) -> str:
        return f"{prefix}:b{bucket}"

    # ---------------------------------------------------------
    # Main rate limiter logic
    # ---------------------------------------------------------
    def _hit(self, key_prefix: str) -> int:
        """
        Increments the counter for the current bucket and returns total hits.
        """
        bucket = self._now_bucket()
        key = self._build_key(key_prefix, bucket)
        pipe = self._redis.pipeline()

        pipe.incr(key, 1)                # increment request count
        pipe.expire(key, self._window)   # auto-cleanup after window

        count, _ = pipe.execute()
        return int(count)

    def check_and_increment(self, user_id: Optional[str], org_id: Optional[str]) -> None:
        """
        Increments counters for user and org.
        Raises RateLimitExceeded if either exceeds limit.
        """
        user_prefix = self._key_user(user_id)
        org_prefix = self._key_org(org_id)

        user_count = self._hit(user_prefix)
        org_count = self._hit(org_prefix)

        if user_count > self._limit or org_count > self._limit:
            raise RateLimitExceeded(
                f"Rate limit exceeded "
                f"(user={user_count}/{self._limit}, org={org_count}/{self._limit})"
            )
