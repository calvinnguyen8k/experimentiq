from pathlib import Path
from typing import Protocol

from openai import AsyncOpenAI

from app.config import Settings
from app.llm.structured import StructuredRun, run_structured
from app.schemas.review import Critique, ReviewRequest
from app.schemas.statistics import StatisticalResult

PROMPT_VERSION = "critic_v1"
PROMPT = (Path(__file__).parent / "prompts" / f"{PROMPT_VERSION}.txt").read_text()


class Critic(Protocol):
    async def review(
        self, data: ReviewRequest, statistics: StatisticalResult
    ) -> StructuredRun[Critique]: ...


class OpenAICritic:
    def __init__(self, settings: Settings, client: AsyncOpenAI | None = None):
        self.settings, self.client = settings, client

    async def review(
        self, data: ReviewRequest, statistics: StatisticalResult
    ) -> StructuredRun[Critique]:
        import json

        return await run_structured(
            client=self.client,
            settings=self.settings,
            schema=Critique,
            prompt=PROMPT,
            prompt_version=PROMPT_VERSION,
            content=json.dumps({**data.model_dump(), "statistics": statistics.model_dump()}),
            label="AI risk review",
            validate=lambda critique: None,
        )
