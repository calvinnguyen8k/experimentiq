import json

import fakeredis
import httpx
import pytest
from pydantic import ValidationError

from app.config import Settings
from app.errors import ServiceError
from app.services.shared_limits import SCRIPT, SharedLimits


def quota(redis, identity, *, peer="peer", daily=120, concurrent=3, per_client=5):
    return redis.eval(
        SCRIPT,
        4,
        "{experimentiq}:minute",
        peer,
        "{experimentiq}:active",
        "{experimentiq}:daily",
        identity,
        "30",
        str(per_client),
        str(concurrent),
        str(daily),
    ).decode()


def test_atomic_shared_quota_concurrency_and_release():
    redis = fakeredis.FakeRedis()
    assert quota(redis, "a") == "ok"
    assert quota(redis, "b") == "ok"
    assert quota(redis, "c") == "ok"
    assert quota(redis, "d") == "limited"
    redis.zrem("{experimentiq}:active", "a")
    assert quota(redis, "d") == "ok"


def test_daily_cap_survives_new_limiter_clients_and_does_not_charge_rejections():
    redis = fakeredis.FakeRedis()
    assert quota(redis, "a", daily=2) == "ok"
    assert quota(redis, "b", daily=2) == "ok"
    assert quota(redis, "c", peer="other-peer", daily=2) == "daily"
    assert redis.hget("{experimentiq}:daily", "count") == b"2"


def test_expired_concurrency_lease_and_rate_windows_are_cleaned():
    redis = fakeredis.FakeRedis()
    redis.zadd("{experimentiq}:active", {"old": 1})
    redis.zadd("{experimentiq}:minute", {"old": 1})
    assert quota(redis, "new", concurrent=1) == "ok"
    assert quota(redis, "second", peer="another", concurrent=1) == "limited"


def test_peer_budget_is_shared_and_unknown_proxies_are_not_trusted():
    redis = fakeredis.FakeRedis()
    assert quota(redis, "a", per_client=1) == "ok"
    redis.zrem("{experimentiq}:active", "a")
    assert quota(redis, "b", per_client=1) == "limited"
    assert quota(redis, "c", peer="other", per_client=1) == "ok"


@pytest.mark.parametrize(
    "changes",
    [
        {},
        {"redis_rest_url": "http://unsafe", "redis_rest_token": "test"},
        {
            "redis_rest_url": "https://quota.example",
            "redis_rest_token": "test",
            "allowed_origins": ["*"],
        },
    ],
)
def test_production_refuses_unprotected_configuration(changes):
    with pytest.raises(ValidationError):
        Settings(_env_file=None, production_mode=True, **changes)


async def test_rest_quota_fails_closed_and_never_puts_token_or_peer_in_body():
    requests = []

    def handler(request):
        requests.append(request)
        return httpx.Response(200, json={"result": "ok"})

    settings = Settings(
        _env_file=None, redis_rest_url="https://quota.example", redis_rest_token="test-only-redis"
    )
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        limiter = SharedLimits(settings, client)
        await limiter.acquire("192.0.2.1", "request")
    body = requests[0].content.decode()
    assert "192.0.2.1" not in body
    assert "test-only-redis" not in body
    assert json.loads(body)[0] == "EVAL"
    async with httpx.AsyncClient(
        transport=httpx.MockTransport(lambda request: httpx.Response(503))
    ) as client:
        with pytest.raises(ServiceError) as error:
            await SharedLimits(settings, client).acquire("peer", "request")
        assert error.value.code == "quota_unavailable"
