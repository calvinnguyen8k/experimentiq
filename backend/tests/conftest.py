import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.llm.extraction import ExtractionRun
from app.main import create_app
from app.schemas.extraction import Extraction, Metadata

OBJECTIVE = (
    "We want to test personalized credit-card promotions versus generic promotions for "
    "100,000 eligible customers. Our goal is to increase average card spending by 5%."
)


def extraction_data():
    return json.loads((Path(__file__).parent / "fixtures" / "extraction.json").read_text())


def make_run(data=None):
    return ExtractionRun(
        Extraction.model_validate(data if data is not None else extraction_data()),
        Metadata(
            model="test-fixture",
            prompt_version="extract_v1",
            latency_ms=1,
            attempts=1,
            input_tokens=10,
            output_tokens=20,
            estimated_cost_usd=None,
        ),
    )


class FakeExtractor:
    def __init__(self, run=None, error=None):
        self.run = run or make_run()
        self.error = error
        self.calls = 0

    async def extract(self, objective):
        self.calls += 1
        if self.error:
            raise self.error
        return self.run


@pytest.fixture
def fake():
    return FakeExtractor()


@pytest.fixture
def client(fake):
    app = create_app(Settings(_env_file=None, openai_api_key=None), fake)
    with TestClient(app) as client:
        yield client
