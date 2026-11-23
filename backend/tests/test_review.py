import json

import httpx
import pytest
from fastapi.testclient import TestClient
from openai import AsyncOpenAI

from app.config import Settings
from app.errors import ServiceError
from app.llm.critique import OpenAICritic
from app.llm.structured import StructuredRun
from app.main import create_app
from app.schemas.review import Critique, ReviewRequest
from app.services.statistics import calculate
from tests.conftest import OBJECTIVE, make_run
from tests.provider_fixture import critique_data, design_data, provider_response
from tests.test_statistics import inputs

PATH = "/api/v1/experiments/review"


def payload(**changes):
    return {
        "objective": OBJECTIVE,
        "design": design_data(),
        "statistical_request": inputs().model_dump(),
        **changes,
    }


class FakeCritic:
    def __init__(self, error=None):
        self.calls = 0
        self.error = error

    async def review(self, data, statistics):
        self.calls += 1
        if self.error:
            raise self.error
        statistics.total = 999  # Reviewer cannot mutate the retained server result.
        return StructuredRun(Critique.model_validate(critique_data()), make_run().metadata)


def client_for(critic):
    return TestClient(create_app(Settings(_env_file=None, openai_api_key=None), critic=critic))


def test_review_recomputes_and_preserves_statistics_and_flags_unresolved_assumptions():
    with client_for(FakeCritic()) as client:
        response = client.post(PATH, json=payload())
    assert response.status_code == 200
    result = response.json()
    assert result["statistics"]["total"] == 3140
    assert result["statistics"]["source"] == "derived"
    assert result["statistics"]["request_id"] == result["request_id"]
    assert result["status"] == "review_needs_attention"
    assert result["checks"]


@pytest.mark.parametrize(
    "change",
    [
        {"baseline_sd": None},
        {"design_confirmed": False},
        {"primary_metric": "different metric"},
        {"design_family": "unsupported"},
        {"independent_units": False},
    ],
)
def test_invalid_review_never_calls_provider(change):
    critic = FakeCritic()
    data = payload(statistical_request=inputs(**change).model_dump())
    with client_for(critic) as client:
        assert client.post(PATH, json=data).status_code == 422
    assert critic.calls == 0


def test_reject_injected_sample_size_and_missing_key():
    with client_for(FakeCritic()) as client:
        assert client.post(PATH, json=payload(statistics={"total": 1})).status_code == 422
    with TestClient(create_app(Settings(_env_file=None, openai_api_key=None))) as client:
        assert client.post(PATH, json=payload()).status_code == 503


def test_review_failure_releases_capacity_and_preserves_safe_error():
    with client_for(FakeCritic(ServiceError("llm_unavailable", "Please retry."))) as client:
        assert client.post(PATH, json=payload()).status_code == 503
        assert client.app.state.limits.active == 0


def test_infeasible_plan_can_be_reviewed_but_keeps_warning():
    with client_for(FakeCritic()) as client:
        result = client.post(
            PATH, json=payload(statistical_request=inputs(population_size=100).model_dump())
        ).json()
    assert result["statistics"]["feasible"] is False
    assert any("exceeds" in check for check in result["checks"])


async def test_critic_sdk_receives_immutable_numbers_and_cannot_return_them():
    bodies = []

    def handler(request):
        bodies.append(json.loads(request.content))
        return httpx.Response(200, json=provider_response(critique_data()))

    async with AsyncOpenAI(
        api_key="test-only-not-a-real-key",
        max_retries=0,
        http_client=httpx.AsyncClient(transport=httpx.MockTransport(handler)),
    ) as client:
        request = ReviewRequest.model_validate(payload())
        run = await OpenAICritic(Settings(_env_file=None), client).review(
            request, calculate(request.statistical_request, "test")
        )
    assert run.metadata.prompt_version == "critic_v1"
    assert bodies[0]["store"] is False
    assert json.loads(bodies[0]["input"][0]["content"])["statistics"]["total"] == 3140
    assert "statistics" not in bodies[0]["text"]["format"]["schema"]["properties"]
