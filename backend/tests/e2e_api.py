"""Test-only server. Explicitly launched by Playwright, never imported by app.main."""

import httpx
from openai import AsyncOpenAI

from app.config import Settings
from app.llm.critique import OpenAICritic
from app.llm.design import OpenAIDesigner
from app.llm.extraction import OpenAIExtractor
from app.main import create_app
from app.services.limits import RequestLimits
from tests.provider_fixture import successful_transport

settings = Settings(
    _env_file=None,
    openai_api_key=None,
    rate_limit_per_minute=30,
    global_rate_limit_per_minute=30,
    allowed_origins=["http://127.0.0.1:3100"],
)
client = AsyncOpenAI(
    api_key="test-only-not-a-real-key",
    max_retries=0,
    http_client=httpx.AsyncClient(transport=httpx.MockTransport(successful_transport)),
)
app = create_app(
    settings,
    OpenAIExtractor(settings, client),
    OpenAIDesigner(settings, client),
    OpenAICritic(settings, client),
)

# Isolated fixture server: avoid test-order dependence on wall-clock rate windows.
# Production limit configuration and behavior are covered separately by API tests.
app.state.limits = RequestLimits(1000, 1000, 3)
