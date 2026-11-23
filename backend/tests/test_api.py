import json
import logging

import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.errors import ServiceError
from app.main import create_app
from app.schemas.extraction import ExtractionResponse
from tests.conftest import OBJECTIVE, FakeExtractor

PATH = "/api/v1/experiments/extract"


def test_health_without_key(client, fake):
    assert client.get("/health").json()["status"] == "ok"
    assert fake.calls == 0


def test_full_api_contract(client):
    response = client.post(PATH, json={"objective": OBJECTIVE})
    assert response.status_code == 200
    result = ExtractionResponse.model_validate(response.json())
    assert result.request_id == response.headers["x-request-id"]
    assert result.status == "missing_information"
    assert "no-store" in response.headers["cache-control"]


def test_missing_key_is_setup_error():
    with TestClient(create_app(Settings(_env_file=None, openai_api_key=None))) as client:
        response = client.post(PATH, json={"objective": OBJECTIVE})
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "llm_not_configured"


@pytest.mark.parametrize(
    "code,status",
    [
        ("llm_unavailable", 503),
        ("llm_timeout", 504),
        ("llm_invalid_response", 502),
    ],
)
def test_provider_failure_envelope(code, status):
    fake = FakeExtractor(error=ServiceError(code, "Safe explanation", status))
    with TestClient(create_app(Settings(_env_file=None), fake)) as client:
        response = client.post(PATH, json={"objective": OBJECTIVE})
    assert response.status_code == status
    assert response.json()["error"]["code"] == code


def test_validation_does_not_echo_input_or_call_provider(client, fake):
    response = client.post(PATH, json={"objective": OBJECTIVE, "population_size": "secret-string"})
    assert response.status_code == 422
    assert "secret-string" not in response.text
    assert "population_size" in response.json()["error"]["fields"]
    assert fake.calls == 0


def test_malformed_json_and_content_type(client):
    assert (
        client.post(PATH, content="{", headers={"Content-Type": "application/json"}).status_code
        == 422
    )
    assert client.post(PATH, content="not json").status_code == 415


def test_body_limit(client, fake):
    response = client.post(PATH, json={"objective": "x" * 25000})
    assert response.status_code == 413
    assert response.json()["error"]["code"] == "payload_too_large"
    assert fake.calls == 0


def test_rate_limit_cannot_be_bypassed_by_forwarded_header(client, fake):
    for i in range(5):
        assert (
            client.post(
                PATH, json={"objective": OBJECTIVE}, headers={"X-Forwarded-For": f"1.2.3.{i}"}
            ).status_code
            == 200
        )
    response = client.post(PATH, json={"objective": OBJECTIVE})
    assert response.status_code == 429
    assert response.headers["retry-after"] == "60"
    assert fake.calls == 5


def test_cors_allowlist(client):
    headers = {"Origin": "http://localhost:3000", "Access-Control-Request-Method": "POST"}
    assert (
        client.options(PATH, headers=headers).headers["access-control-allow-origin"]
        == headers["Origin"]
    )
    headers["Origin"] = "https://untrusted.example"
    assert "access-control-allow-origin" not in client.options(PATH, headers=headers).headers


def test_logs_contain_metadata_not_objective(client, caplog):
    with caplog.at_level(logging.INFO, logger="experimentiq"):
        response = client.post(PATH, json={"objective": OBJECTIVE})
    assert OBJECTIVE not in caplog.text
    records = [json.loads(r.message) for r in caplog.records if r.name == "experimentiq"]
    assert records[-1]["request_id"] == response.json()["request_id"]
    assert records[-1]["model"] == "test-fixture"


def test_unexpected_exception_is_safe_and_releases_capacity():
    fake = FakeExtractor(error=RuntimeError("sensitive provider exception"))
    app = create_app(Settings(_env_file=None), fake)
    with TestClient(app) as client:
        response = client.post(PATH, json={"objective": OBJECTIVE})
    assert response.status_code == 500
    assert "sensitive" not in response.text
    assert app.state.limits.active == 0


def test_future_routes_are_not_claimed_as_implemented(client):
    assert client.post("/api/v1/experiments/review", json={}).status_code == 422
    assert client.post("/api/v1/statistics/sample-size", json={}).status_code == 422


@pytest.mark.parametrize(
    "values,message,fields",
    [
        (
            {"metric_type": "binary", "baseline_mean": 0.02, "baseline_sd": 0.02},
            "You selected Binary. Clear baseline mean",
            {"metric_type", "baseline_mean", "baseline_sd"},
        ),
        (
            {"metric_type": "continuous", "baseline_conversion_rate": 0.1},
            "You selected Continuous. Clear baseline conversion rate",
            {"metric_type", "baseline_conversion_rate"},
        ),
        (
            {"baseline_conversion_rate": 0.9, "target_relative_uplift": 0.2},
            "imply a target of 100% or more",
            {"baseline_conversion_rate", "target_relative_uplift"},
        ),
        (
            {"baseline_mean": 0, "target_relative_uplift": 0.05},
            "baseline mean greater than zero",
            {"baseline_mean", "target_relative_uplift"},
        ),
        ({"baseline_sd": 0}, "standard deviation must be greater than zero", {"baseline_sd"}),
    ],
)
def test_validation_explains_the_specific_problem(client, fake, values, message, fields):
    response = client.post(PATH, json={"objective": OBJECTIVE, **values})
    assert response.status_code == 422
    error = response.json()["error"]
    assert message in error["message"]
    assert set(error["fields"]) == fields
    assert fake.calls == 0
