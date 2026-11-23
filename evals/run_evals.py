"""Explicit opt-in live evaluation. Never used by the application or ordinary CI."""

import argparse
import asyncio
import json
import statistics
import sys
from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.config import Settings
from app.errors import ServiceError
from app.llm.critique import OpenAICritic
from app.llm.design import OpenAIDesigner
from app.llm.extraction import OpenAIExtractor
from app.schemas.extraction import ExperimentInput
from app.schemas.review import ReviewRequest
from app.schemas.statistics import StatisticalRequest
from app.services.statistics import calculate
from openai import AsyncOpenAI


def score_extraction(actual, expected):
    matches = 0
    for field, value in expected.items():
        evidence = getattr(actual, field)
        extracted = evidence.value if evidence else None
        if isinstance(value, (float, int)) and not isinstance(value, bool):
            matches += extracted is not None and abs(extracted - value) <= 1e-8 * max(
                1, abs(value)
            )
        else:
            matches += extracted == value
    return matches, len(expected)


async def evaluate(args):
    cases = json.loads((ROOT / "evals/cases.json").read_text())[: args.max_cases]
    settings = Settings(_env_file=ROOT / "backend/.env")
    if not settings.openai_api_key:
        raise SystemExit(
            "Live evaluation needs the locally configured backend OPENAI_API_KEY."
        )
    rows = []
    started_at = datetime.now(UTC).isoformat()
    async with AsyncOpenAI(
        api_key=settings.openai_api_key.get_secret_value(),
        timeout=settings.provider_timeout_seconds,
        max_retries=1,
    ) as client:
        extractor, designer, critic = (
            OpenAIExtractor(settings, client),
            OpenAIDesigner(settings, client),
            OpenAICritic(settings, client),
        )
        for case in cases:
            started = perf_counter()
            row = {"id": case["id"], "stages": {}, "error": None}
            try:
                data = ExperimentInput.model_validate(case["inputs"])
                extraction = await extractor.extract(data.objective)
                row["stages"]["extraction"] = extraction.metadata.model_dump()
                row["extraction_matches"], row["extraction_checks"] = score_extraction(
                    extraction.extraction, case["expected_extraction"]
                )
                row["extraction"] = extraction.extraction.model_dump()
                design = await designer.generate(data)
                row["stages"]["design"] = design.metadata.model_dump()
                draft = design.value
                if data.primary_metric:
                    draft = draft.model_copy(
                        update={"primary_metric": data.primary_metric}
                    )
                row["design"] = draft.model_dump()
                row["family_correct"] = draft.design_family == case["expected_family"]
                numeric = StatisticalRequest.model_validate(
                    {
                        **case["statistics"],
                        "design_family": draft.design_family,
                        "primary_metric": draft.primary_metric,
                        "design_confirmed": True,
                        "independent_units": case["expected_family"]
                        == "independent_two_arm",
                    }
                )
                result = calculate(numeric, "evaluation-" + case["id"])
                row["statistics"] = result.model_dump()
                # Offline evaluation also inspects critique on unsupported designs. The UI
                # correctly blocks those before calculation/review; this is a quality probe.
                review = await critic.review(
                    ReviewRequest(
                        objective=data.objective,
                        design=draft,
                        statistical_request=numeric,
                    ),
                    result,
                )
                row["stages"]["critique"] = review.metadata.model_dump()
                row["critique"] = review.value.model_dump()
                text = json.dumps(review.value.model_dump()).lower()
                row["risk_hits"] = sum(
                    any(word in text for word in words)
                    for words in case["risk_keywords"]
                )
                row["risk_checks"] = len(case["risk_keywords"])
                row["numbers_preserved"] = result == calculate(
                    numeric, result.request_id
                )
            except ServiceError as error:
                row["error"] = error.code
            except Exception as error:  # noqa: BLE001 - record safe failure type, never provider text
                row["error"] = type(
                    error
                ).__name__  # Never print exception bodies/credentials.
            row["latency_seconds"] = round(perf_counter() - started, 3)
            rows.append(row)
            print(
                f"{len(rows)}/{len(cases)} {case['id']}: {row['error'] or 'completed'}",
                flush=True,
            )
            write_results(args.output, rows, started_at, settings.openai_model)


def write_results(path, rows, started_at, model):
    latencies = sorted(row["latency_seconds"] for row in rows)

    def fraction(num, den):
        total = sum(row.get(den, 0) for row in rows)
        return sum(row.get(num, 0) for row in rows) / total if total else None

    stages = [metadata for row in rows for metadata in row["stages"].values()]
    costs = [m["estimated_cost_usd"] for m in stages]
    result = {
        "mode": "live_openai",
        "started_at": started_at,
        "model": model,
        "limitations": [
            "Small synthetic development set, not a held-out benchmark or user validation.",
            "Risk keyword recall is an automated proxy; evidence accuracy and reasoning need human review.",
            "Extraction accuracy measures only the annotated fields; it is not overall semantic accuracy.",
            "Schema success counts stages that succeeded after bounded repair, not first-pass validity.",
            "Unsupported cases are critic quality probes outside the gated application workflow.",
            "No claim that assignment quality thresholds are achieved from keyword scoring alone.",
        ],
        "metrics": {
            "cases": len(rows),
            "completed_cases": sum(row["error"] is None for row in rows),
            "validated_stage_rate": len(stages) / (len(rows) * 3),
            "annotated_extraction_accuracy": fraction(
                "extraction_matches", "extraction_checks"
            ),
            "risk_keyword_recall_proxy": fraction("risk_hits", "risk_checks"),
            "design_family_accuracy": sum(
                row.get("family_correct", False) for row in rows
            )
            / len(rows),
            "median_case_seconds": statistics.median(latencies),
            "p95_case_seconds": latencies[
                min(len(latencies) - 1, ceil95(len(latencies)))
            ],
            "known_input_tokens": sum(m["input_tokens"] or 0 for m in stages),
            "known_output_tokens": sum(m["output_tokens"] or 0 for m in stages),
            "estimated_cost_usd": sum(costs)
            if all(c is not None for c in costs)
            else None,
        },
        "cases": rows,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2) + "\n")


def ceil95(n):
    import math

    return math.ceil(0.95 * n) - 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--live",
        action="store_true",
        help="Allow real, billed OpenAI calls (up to 60 stage calls, plus bounded repairs).",
    )
    parser.add_argument("--max-cases", type=int, default=20, choices=range(1, 21))
    parser.add_argument("--output", type=Path, default=ROOT / "evals/results/live.json")
    args = parser.parse_args()
    if not args.live:
        parser.error("Specify --live to explicitly opt in to real provider calls.")
    asyncio.run(evaluate(args))
