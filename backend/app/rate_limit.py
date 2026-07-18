from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from math import ceil
from threading import Lock
from time import monotonic
from typing import Callable


@dataclass(frozen=True)
class RateLimitDecision:
    allowed: bool
    retry_after: int = 0


class LoginRateLimiter:
    """Single-process failed-login limiter for the showcase API."""

    def __init__(
        self,
        *,
        attempt_limit: int,
        window_seconds: int,
        clock: Callable[[], float] = monotonic,
    ) -> None:
        if attempt_limit < 1 or window_seconds < 1:
            raise ValueError("Rate-limit values must be positive")
        self.attempt_limit = attempt_limit
        self.window_seconds = window_seconds
        self._clock = clock
        self._failures: dict[str, deque[float]] = {}
        self._lock = Lock()

    @staticmethod
    def key(client_ip: str, username: str) -> str:
        return f"{client_ip.strip().lower()}::{username.strip().lower()}"

    def check(self, key: str) -> RateLimitDecision:
        with self._lock:
            failures = self._failures.get(key)
            if failures is None:
                return RateLimitDecision(allowed=True)
            now = self._clock()
            self._prune(failures, now)
            if not failures:
                self._failures.pop(key, None)
                return RateLimitDecision(allowed=True)
            return self._decision(failures, now)

    def register_failure(self, key: str) -> RateLimitDecision:
        with self._lock:
            now = self._clock()
            failures = self._failures.setdefault(key, deque())
            self._prune(failures, now)
            failures.append(now)
            return self._decision(failures, now)

    def reset(self, key: str) -> None:
        with self._lock:
            self._failures.pop(key, None)

    def _prune(self, failures: deque[float], now: float) -> None:
        cutoff = now - self.window_seconds
        while failures and failures[0] <= cutoff:
            failures.popleft()

    def _decision(self, failures: deque[float], now: float) -> RateLimitDecision:
        if len(failures) < self.attempt_limit:
            return RateLimitDecision(allowed=True)
        retry_after = max(1, ceil(self.window_seconds - (now - failures[0])))
        return RateLimitDecision(allowed=False, retry_after=retry_after)
