import pytest

from app.errors import ServiceError
from app.services.limits import RequestLimits


def test_concurrent_cap_and_release():
    limits = RequestLimits(5, 30, 1)
    limits.acquire("one")
    with pytest.raises(ServiceError):
        limits.acquire("two")
    limits.release()
    limits.acquire("two")
    assert limits.active == 1


def test_global_cap_across_clients_and_expiration(monkeypatch):
    now = [100.0]
    monkeypatch.setattr("app.services.limits.monotonic", lambda: now[0])
    limits = RequestLimits(5, 2, 3)
    for peer in ["one", "two"]:
        limits.acquire(peer)
        limits.release()
    with pytest.raises(ServiceError):
        limits.acquire("three")
    now[0] += 61
    limits.acquire("three")
    assert len(limits.events) == 1
