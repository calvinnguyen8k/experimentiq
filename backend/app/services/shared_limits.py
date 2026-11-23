"""Atomic Redis quotas shared across workers/restarts; fail closed on outages."""

import hashlib
from pathlib import Path

import httpx

from app.config import Settings
from app.errors import ServiceError

SCRIPT = (Path(__file__).parent / "quota.lua").read_text()


class SharedLimits:
    def __init__(self, settings: Settings, client: httpx.AsyncClient):
        self.settings, self.client = settings, client

    async def command(self, command):
        try:
            response = await self.client.post(
                self.settings.redis_rest_url,
                headers={
                    "Authorization": f"Bearer {self.settings.redis_rest_token.get_secret_value()}"
                },
                json=command,
                timeout=3,
            )
            response.raise_for_status()
            payload = response.json()
            if "error" in payload or "result" not in payload:
                raise ValueError("Invalid quota response")
            return payload["result"]
        except (httpx.HTTPError, ValueError, TypeError):
            raise ServiceError(
                "quota_unavailable",
                "The demo's usage protection is unavailable. Please retry later.",
                503,
            ) from None

    async def acquire(self, peer: str, request_id: str):
        # No raw IP storage. Never trust arbitrary X-Forwarded-For from the caller.
        identity = hashlib.sha256(peer.encode()).hexdigest()
        result = await self.command(
            [
                "EVAL",
                SCRIPT,
                "4",
                "{experimentiq}:minute",
                f"{{experimentiq}}:peer:{identity}",
                "{experimentiq}:active",
                "{experimentiq}:daily",
                request_id,
                str(self.settings.global_rate_limit_per_minute),
                str(self.settings.rate_limit_per_minute),
                str(self.settings.max_concurrent_requests),
                str(self.settings.daily_request_limit),
            ]
        )
        if result == "daily":
            raise ServiceError(
                "daily_limit",
                "This demo has reached its daily request cap. Try tomorrow (UTC).",
                429,
            )
        if result == "limited":
            raise ServiceError("rate_limited", "Too many requests. Please wait a minute.", 429)
        if result != "ok":
            raise ServiceError(
                "quota_unavailable", "Usage protection could not validate this request.", 503
            )

    async def release(self, request_id: str):
        try:
            await self.command(["ZREM", "{experimentiq}:active", request_id])
        except ServiceError:
            # Lease expires after 75 seconds. A release outage must not replace a valid result.
            pass


async def acquire(request):
    peer = request.client.host if request.client else "unknown"
    limits = request.app.state.limits
    limits.acquire(peer)
    try:
        if request.app.state.shared_limits:
            await request.app.state.shared_limits.acquire(peer, request.state.request_id)
    except Exception:
        limits.release()
        raise


async def release(request):
    request.app.state.limits.release()
    if request.app.state.shared_limits:
        await request.app.state.shared_limits.release(request.state.request_id)
