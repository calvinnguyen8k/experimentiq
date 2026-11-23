import json

import httpx
import pytest
from fastapi.testclient import TestClient
from openai import AsyncOpenAI
from pydantic import ValidationError

from app.config import Settings
from app.errors import ServiceError
from app.llm.design import OpenAIDesigner
from app.llm.structured import StructuredRun
from app.main import create_app
from app.schemas.design import DesignDraft, DesignResponse
from app.schemas.extraction import ExperimentInput
from tests.conftest import OBJECTIVE, FakeExtractor, make_run
from tests.provider_fixture import design_data, provider_response

PATH = "/api/v1/experiments/design"


class FakeDesigner:
    def __init__(self, data=None, error=None):
        self.data = design_data() if data is None else data
        self.error = error
        self.calls = 0

    async def generate(self, data):
        self.calls += 1
        if self.error:
            raise self.error
        return StructuredRun(DesignDraft.model_validate(self.data), make_run().metadata)


def client_for(designer):
    return TestClient(
        create_app(
            Settings(_env_file=None, openai_api_key=None),
            FakeExtractor(),
            designer,
        )
    )


def test_design_preserves_confirmed_inputs_and_never_computes_statistics():
    inputs = dict(
        objective=OBJECTIVE,
        primary_metric="my explicitly defined metric",
        metric_type="continuous",
        baseline_mean=200,
        baseline_sd=100,
        population_size=100000,
        target_relative_uplift=0.05,
    )
    with client_for(FakeDesigner()) as client:
        response = client.post(PATH, json=inputs)
    assert response.status_code == 200
    result = DesignResponse.model_validate(response.json())
    assert result.status == "proposal_ready"
    assert result.source == "llm_suggested"
    assert result.metric_source == "user_provided"
    assert result.design.primary_metric == inputs["primary_metric"]
    assert result.planning_inputs == ExperimentInput(**inputs)
    assert result.statistics_status == "not_implemented"


def test_missing_baselines_allow_a_draft_and_remain_null():
    with client_for(FakeDesigner()) as client:
        response = client.post(PATH, json={"objective": OBJECTIVE})
    result = response.json()
    assert response.status_code == 200
    assert result["status"] == "proposal_ready"
    assert result["planning_inputs"]["baseline_mean"] is None
    assert result["planning_inputs"]["baseline_sd"] is None
    assert result["planning_inputs"]["population_size"] is None
    assert result["metric_source"] == "llm_suggested"


@pytest.mark.parametrize("family", ["unsupported", "unclear"])
def test_unsupported_or_unclear_design_needs_attention(family):
    data = design_data()
    data.update(design_family=family, allocation=None, hypothesis=None)
    with client_for(FakeDesigner(data)) as client:
        response = client.post(PATH, json={"objective": OBJECTIVE})
    assert response.status_code == 200
    assert response.json()["status"] == "needs_attention"


def test_design_requires_configured_provider():
    with TestClient(create_app(Settings(_env_file=None, openai_api_key=None))) as client:
        response = client.post(PATH, json={"objective": OBJECTIVE})
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "llm_not_configured"


def test_reject_client_supplied_facts_and_result_before_provider():
    designer = FakeDesigner()
    with client_for(designer) as client:
        response = client.post(PATH, json={"objective": OBJECTIVE, "sample_size": 123})
    assert response.status_code == 422
    assert designer.calls == 0


def test_design_failure_is_safe_and_releases_capacity():
    designer = FakeDesigner(error=ServiceError("llm_unavailable", "Try again later."))
    with client_for(designer) as client:
        response = client.post(PATH, json={"objective": OBJECTIVE})
        assert client.app.state.limits.active == 0
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "llm_unavailable"


def test_design_and_extraction_share_a_rate_budget():
    with client_for(FakeDesigner()) as client:
        for i in range(5):
            path = PATH if i % 2 else "/api/v1/experiments/extract"
            assert client.post(path, json={"objective": OBJECTIVE}).status_code == 200
        assert client.post(PATH, json={"objective": OBJECTIVE}).status_code == 429


def test_supported_draft_requires_core_fields_and_rejects_extra_results():
    data = design_data()
    data["control"] = None
    with pytest.raises(ValidationError):
        DesignDraft.model_validate(data)
    data = design_data()
    data["sample_size"] = 1000
    with pytest.raises(ValidationError):
        DesignDraft.model_validate(data)


async def test_designer_sdk_keeps_data_in_user_message_and_unknowns_out_of_confirmed_inputs():
    payloads = []

    def handler(request):
        payloads.append(json.loads(request.content))
        return httpx.Response(200, json=provider_response(design_data()))

    async with AsyncOpenAI(
        api_key="test-only-not-a-real-key",
        max_retries=0,
        http_client=httpx.AsyncClient(transport=httpx.MockTransport(handler)),
    ) as client:
        designer = OpenAIDesigner(Settings(_env_file=None), client)
        result = await designer.generate(ExperimentInput(objective=OBJECTIVE))
    payload = payloads[0]
    assert payload["store"] is False
    assert payload["text"]["format"]["strict"] is True
    assert payload["input"][0]["role"] == "user"
    assert json.loads(payload["input"][0]["content"])["confirmed_inputs"] == {}
    assert result.metadata.prompt_version == "design_v1"


async def test_designer_repairs_once_then_reports_invalid_response():
    calls = 0

    def handler(request):
        nonlocal calls
        calls += 1
        return httpx.Response(200, json=provider_response({"sample_size": 1000}))

    async with AsyncOpenAI(
        api_key="test-only-not-a-real-key",
        max_retries=0,
        http_client=httpx.AsyncClient(transport=httpx.MockTransport(handler)),
    ) as client:
        with pytest.raises(ServiceError) as exc:
            await OpenAIDesigner(Settings(_env_file=None), client).generate(
                ExperimentInput(objective=OBJECTIVE)
            )
    assert exc.value.code == "llm_invalid_response"
    assert calls == 2
