import asyncio
from collections.abc import Callable
from dataclasses import dataclass
from time import perf_counter
from typing import Generic, TypeVar

from openai import APIError, APITimeoutError, AsyncOpenAI
from pydantic import BaseModel, ValidationError

from app.config import Settings
from app.errors import ServiceError
from app.schemas.extraction import Metadata

T = TypeVar("T", bound=BaseModel)


@dataclass
class StructuredRun(Generic[T]):
    value: T
    metadata: Metadata


async def run_structured(
    *,
    client: AsyncOpenAI | None,
    settings: Settings,
    schema: type[T],
    prompt: str,
    prompt_version: str,
    content: str,
    label: str,
    validate: Callable[[T], None],
) -> StructuredRun[T]:
    if client is None:
        raise ServiceError(
            "llm_not_configured",
            f"{label} is not configured. Add OPENAI_API_KEY to the backend environment.",
        )

    async def execute():
        started = perf_counter()
        input_tokens = output_tokens = 0
        usage_complete = True
        for attempt in range(1, 3):
            instructions = prompt
            if attempt == 2:
                instructions += (
                    "\nThe prior attempt failed validation. Follow the schema strictly. "
                    "Use null for unknowns. Do not invent facts or numerical assumptions."
                )
            try:
                response = await client.responses.parse(
                    model=settings.openai_model,
                    instructions=instructions,
                    input=[{"role": "user", "content": content}],
                    text_format=schema,
                    max_output_tokens=settings.max_output_tokens,
                    store=False,
                )
                if response.usage:
                    input_tokens += response.usage.input_tokens
                    output_tokens += response.usage.output_tokens
                else:
                    usage_complete = False
                if any(
                    getattr(part, "type", None) == "refusal"
                    for item in response.output
                    for part in getattr(item, "content", [])
                ):
                    raise ServiceError(
                        "llm_unavailable",
                        "The provider could not process this objective. "
                        "Try a synthetic A/B test idea.",
                    )
                if response.status != "completed" or response.output_parsed is None:
                    raise ValueError("Incomplete structured response.")
                parsed = schema.model_validate(response.output_parsed)
                validate(parsed)
            except (ValidationError, ValueError):
                usage_complete = False
                if attempt == 2:
                    raise ServiceError(
                        "llm_invalid_response",
                        f"{label} returned an answer that could not be validated. "
                        "Try clarifying the objective.",
                        502,
                    ) from None
                continue
            cost = None
            if (
                usage_complete
                and settings.input_cost_per_million is not None
                and settings.output_cost_per_million is not None
            ):
                cost = (
                    input_tokens * settings.input_cost_per_million
                    + output_tokens * settings.output_cost_per_million
                ) / 1_000_000
            return StructuredRun(
                parsed,
                Metadata(
                    model=response.model,
                    prompt_version=prompt_version,
                    latency_ms=round((perf_counter() - started) * 1000),
                    attempts=attempt,
                    input_tokens=input_tokens if usage_complete else None,
                    output_tokens=output_tokens if usage_complete else None,
                    estimated_cost_usd=cost,
                ),
            )
        raise AssertionError("Unreachable")

    try:
        return await asyncio.wait_for(execute(), timeout=settings.extraction_deadline_seconds)
    except (TimeoutError, APITimeoutError) as exc:
        raise ServiceError(
            "llm_timeout", f"{label} timed out. Please try again shortly.", 504
        ) from exc
    except APIError as exc:
        raise ServiceError(
            "llm_unavailable", f"{label} is temporarily unavailable. Please try again later."
        ) from exc
