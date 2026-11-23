import asyncio
import json

import httpx
import pytest
from openai import AsyncOpenAI

from app.config import Settings
from app.errors import ServiceError
from app.llm.extraction import OpenAIExtractor
from tests.conftest import OBJECTIVE, extraction_data
from tests.provider_fixture import provider_response


async def run_provider(handler, **settings):
    async with AsyncOpenAI(
        api_key="test-only-not-a-real-key",
        max_retries=0,
        http_client=httpx.AsyncClient(transport=httpx.MockTransport(handler)),
    ) as client:
        return await OpenAIExtractor(Settings(_env_file=None, **settings), client).extract(
            OBJECTIVE
        )


async def test_real_sdk_builds_strict_schema_and_parses_response():
    requests = []

    def handler(request):
        requests.append(json.loads(request.content))
        return httpx.Response(200, json=provider_response())

    result = await run_provider(handler, input_cost_per_million=0.4, output_cost_per_million=1.6)
    payload = requests[0]
    assert payload["store"] is False
    assert payload["text"]["format"]["strict"] is True
    assert payload["text"]["format"]["schema"]["additionalProperties"] is False
    assert payload["max_output_tokens"] == 2500
    assert payload["input"][0] == {"role": "user", "content": OBJECTIVE}
    assert result.extraction.baseline_sd is None
    assert result.metadata.input_tokens == 100
    assert result.metadata.estimated_cost_usd == pytest.approx(0.00012)


async def test_one_repair_for_invented_evidence_then_success():
    calls = 0

    def handler(request):
        nonlocal calls
        calls += 1
        data = extraction_data()
        if calls == 1:
            data["baseline_sd"] = {"value": 100, "quote": "invented SD"}
        return httpx.Response(200, json=provider_response(data))

    result = await run_provider(handler)
    assert calls == result.metadata.attempts == 2
    assert result.extraction.baseline_sd is None
    assert result.metadata.estimated_cost_usd is None


async def test_invalid_schema_stops_after_one_repair():
    calls = 0

    def handler(request):
        nonlocal calls
        calls += 1
        return httpx.Response(200, json=provider_response({"unexpected": 123}))

    with pytest.raises(ServiceError) as exc:
        await run_provider(handler)
    assert exc.value.code == "llm_invalid_response"
    assert calls == 2


@pytest.mark.parametrize("status", [401, 429, 500])
async def test_provider_errors_do_not_expose_details(status):
    def handler(request):
        return httpx.Response(status, json={"error": {"message": "private-text", "type": "test"}})

    with pytest.raises(ServiceError) as exc:
        await run_provider(handler)
    assert exc.value.code == "llm_unavailable"
    assert "private-text" not in exc.value.message


async def test_provider_timeout():
    def handler(request):
        raise httpx.ReadTimeout("private-text", request=request)

    with pytest.raises(ServiceError) as exc:
        await run_provider(handler)
    assert exc.value.status == 504


async def test_overall_deadline():
    async def handler(request):
        await asyncio.sleep(0.1)
        return httpx.Response(200, json=provider_response())

    with pytest.raises(ServiceError) as exc:
        await run_provider(handler, extraction_deadline_seconds=0.01)
    assert exc.value.code == "llm_timeout"


async def test_refusal_is_not_fake_success():
    def handler(request):
        return httpx.Response(200, json=provider_response(refusal=True))

    with pytest.raises(ServiceError) as exc:
        await run_provider(handler)
    assert exc.value.code == "llm_unavailable"


async def test_incomplete_response_is_not_accepted():
    def handler(request):
        return httpx.Response(200, json=provider_response(status="incomplete"))

    with pytest.raises(ServiceError) as exc:
        await run_provider(handler)
    assert exc.value.code == "llm_invalid_response"
