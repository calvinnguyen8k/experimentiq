from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from openai import AsyncOpenAI

from app.config import Settings
from app.llm.structured import run_structured
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
        run = await run_structured(
            client=self.client,
            settings=self.settings,
            schema=Extraction,
            prompt=PROMPT,
            prompt_version=PROMPT_VERSION,
            content=objective,
            label="AI extraction",
            validate=lambda value: value.check_evidence(objective),
        )
        return ExtractionRun(run.value, run.metadata)
