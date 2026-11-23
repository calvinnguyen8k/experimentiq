import asyncio
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter
from typing import Protocol

from openai import APIError, APITimeoutError, AsyncOpenAI
from pydantic import ValidationError

from app.config import Settings
from app.errors import ServiceError
from app.schemas.extraction import Extraction, Metadata

PROMPT_VERSION = "extract_v1"
PROMPT = (Path(__file__).parent / "prompts" / f"{PROMPT_VERSION}.txt").read_text()


@dataclass
class ExtractionRun:
    extraction: Extraction
    metadata: Metadata


class Extractor(Protocol):
    async def extract(self, objective: str) -> ExtractionRun: ...


class OpenAIExtractor:
    def __init__(self, settings: Settings, client: AsyncOpenAI | None = None):
        self.settings = settings
        self.client = client

    async def extract(self, objective: str) -> ExtractionRun:
        if self.client is None:
            raise ServiceError(
                "llm_not_configured",
                "AI extraction is not configured. Add OPENAI_API_KEY to the backend environment.",
            )
        try:
            return await asyncio.wait_for(
                self._extract(objective), timeout=self.settings.extraction_deadline_seconds
            )
        except (TimeoutError, APITimeoutError) as exc:
            raise ServiceError(
                "llm_timeout", "AI extraction timed out. Please try again shortly.", 504
            ) from exc
        except APIError as exc:
            raise ServiceError(
                "llm_unavailable",
                "AI extraction is temporarily unavailable. Please try again later.",
            ) from exc

    async def _extract(self, objective: str) -> ExtractionRun:
        started = perf_counter()
        input_tokens = output_tokens = 0
        usage_complete = True
        for attempt in range(1, 3):
            instructions = PROMPT
            if attempt == 2:
                instructions += (
                    "\nThe prior attempt failed validation. Re-extract conservatively. "
                    "Use null for unsupported fields and exact source substrings for quotes."
                )
            try:
                response = await self.client.responses.parse(
                    model=self.settings.openai_model,
                    instructions=instructions,
                    input=[{"role": "user", "content": objective}],
                    text_format=Extraction,
                    max_output_tokens=self.settings.max_output_tokens,
                    store=False,
                )
                if response.usage:
                    input_tokens += response.usage.input_tokens
                    output_tokens += response.usage.output_tokens
                else:
                    usage_complete = False
                if any(
                    getattr(content, "type", None) == "refusal"
                    for item in response.output
                    for content in getattr(item, "content", [])
                ):
                    raise ServiceError(
                        "llm_unavailable",
                        "The provider could not process this objective. "
                        "Try a synthetic A/B test idea.",
                    )
                if response.status != "completed" or response.output_parsed is None:
                    raise ValueError("Incomplete structured response.")
                parsed = Extraction.model_validate(response.output_parsed)
                parsed.check_evidence(objective)
            except (ValidationError, ValueError):
                # SDK parse failures may not expose token usage. Never report a false total.
                usage_complete = False
                if attempt == 2:
                    raise ServiceError(
                        "llm_invalid_response",
                        "AI returned facts that could not be validated. "
                        "Try clarifying the objective.",
                        502,
                    ) from None
                continue
            cost = None
            settings = self.settings
            if (
                usage_complete
                and settings.input_cost_per_million is not None
                and settings.output_cost_per_million is not None
            ):
                cost = (
                    input_tokens * settings.input_cost_per_million
                    + output_tokens * settings.output_cost_per_million
                ) / 1_000_000
            return ExtractionRun(
                extraction=parsed,
                metadata=Metadata(
                    model=response.model,
                    prompt_version=PROMPT_VERSION,
                    latency_ms=round((perf_counter() - started) * 1000),
                    attempts=attempt,
                    input_tokens=input_tokens if usage_complete else None,
                    output_tokens=output_tokens if usage_complete else None,
                    estimated_cost_usd=cost,
                ),
            )
        raise AssertionError("Unreachable")
