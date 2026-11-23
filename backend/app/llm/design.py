import json
from pathlib import Path
from typing import Protocol

from openai import AsyncOpenAI

from app.config import Settings
from app.llm.structured import StructuredRun, run_structured
from app.schemas.design import DesignDraft
from app.schemas.extraction import ExperimentInput

PROMPT_VERSION = "design_v1"
PROMPT = (Path(__file__).parent / "prompts" / f"{PROMPT_VERSION}.txt").read_text()


class Designer(Protocol):
    async def generate(self, data: ExperimentInput) -> StructuredRun[DesignDraft]: ...


class OpenAIDesigner:
    def __init__(self, settings: Settings, client: AsyncOpenAI | None = None):
        self.settings = settings
        self.client = client

    async def generate(self, data: ExperimentInput) -> StructuredRun[DesignDraft]:
        content = json.dumps(
            {
                "objective": data.objective,
                "confirmed_inputs": data.model_dump(exclude={"objective"}, exclude_none=True),
            }
        )
        return await run_structured(
            client=self.client,
            settings=self.settings,
            schema=DesignDraft,
            prompt=PROMPT,
            prompt_version=PROMPT_VERSION,
            content=content,
            label="AI design generation",
            validate=lambda draft: None,
        )
