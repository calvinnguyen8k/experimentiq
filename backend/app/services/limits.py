from collections import deque
from time import monotonic

from app.errors import ServiceError


class RequestLimits:
    """Single-event-loop, single-process local limits; no trusted proxy inference."""

    def __init__(self, per_client: int, global_limit: int, concurrent: int):
        self.per_client = per_client
        self.global_limit = global_limit
        self.concurrent = concurrent
        self.events: deque[tuple[float, str]] = deque()
        self.active = 0

    def acquire(self, client: str) -> None:
        now = monotonic()
        while self.events and self.events[0][0] <= now - 60:
            self.events.popleft()
        if (
            len(self.events) >= self.global_limit
            or sum(peer == client for _, peer in self.events) >= self.per_client
            or self.active >= self.concurrent
        ):
            raise ServiceError("rate_limited", "Too many requests. Please wait a minute.", 429)
        self.events.append((now, client))
        self.active += 1

    def release(self) -> None:
        self.active -= 1
