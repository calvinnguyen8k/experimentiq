from pydantic import ValidationError

from app.llm.extraction import ExtractionRun
from app.schemas.extraction import (
    Conflict,
    ExperimentInput,
    ExtractionResponse,
    Facts,
    MetricWordingNote,
    Question,
)

QUESTIONS = {
    "population_size": "How many eligible independent units are available?",
    "primary_metric": "What is the primary metric, including its unit and measurement window?",
    "metric_type": "Is the outcome binary (conversion) or continuous (a mean)?",
    "baseline_mean": "What is the baseline mean in the metric's units?",
    "baseline_sd": "What is the baseline standard deviation in the same units?",
    "baseline_conversion_rate": "What is the baseline conversion rate as a decimal (0–1)?",
    "target_relative_uplift": "What relative increase matters (for example, 0.05 for 5%)?",
}


def build_response(
    data: ExperimentInput, run: ExtractionRun, request_id: str
) -> ExtractionResponse:
    run.extraction.check_evidence(data.objective)
    facts = {}
    conflicts = []
    metric_wording_note = None
    for name in type(run.extraction).model_fields:
        supplied = getattr(data, name)
        extracted = getattr(run.extraction, name)
        if supplied is not None:
            facts[name] = dict(
                value=supplied, source="user_provided", evidence=None, requires_confirmation=False
            )
            if extracted is not None and supplied != extracted.value and name == "primary_metric":
                metric_wording_note = MetricWordingNote(
                    supplied_value=supplied,
                    extracted_value=extracted.value,
                    message="Your metric wording differs from the AI extraction. "
                    "Your definition is retained. Different wording alone does not prove a "
                    "conflict; check that both describe the outcome you intend to measure.",
                )
            elif extracted is not None and supplied != extracted.value:
                conflicts.append(
                    Conflict(
                        field=name,
                        supplied_value=supplied,
                        extracted_value=extracted.value,
                        message="The form and prose differ. "
                        "The form value is retained; reconcile both.",
                    )
                )
        elif extracted is not None:
            facts[name] = dict(
                value=extracted.value,
                source="llm_extracted",
                evidence=extracted.quote,
                requires_confirmation=True,
            )
        else:
            facts[name] = dict(
                value=None, source="missing", evidence=None, requires_confirmation=False
            )
    normalized = Facts.model_validate(facts)
    merged = {key: fact["value"] for key, fact in facts.items()}
    try:
        ExperimentInput(objective=data.objective, **merged)
    except ValidationError:
        conflicts.append(
            Conflict(
                field="assumptions",
                supplied_value=None,
                extracted_value=None,
                message="The combined metric type and numeric assumptions are incompatible. "
                "Check baseline fields and effect size before continuing.",
            )
        )
    required = ["metric_type", "primary_metric", "population_size", "target_relative_uplift"]
    if normalized.metric_type.value == "continuous":
        required += ["baseline_mean", "baseline_sd"]
    elif normalized.metric_type.value == "binary":
        required += ["baseline_conversion_rate"]
    questions = []
    for name in QUESTIONS:
        fact = facts[name]
        if fact["requires_confirmation"]:
            questions.append(
                Question(
                    field=name,
                    reason="confirmation",
                    question=f"Confirm {name.replace('_', ' ')} "
                    "in the optional inputs, then rerun.",
                )
            )
        elif name in required and fact["value"] is None:
            questions.append(Question(field=name, reason="missing", question=QUESTIONS[name]))
    status = (
        "needs_attention"
        if conflicts
        else ("missing_information" if questions else "extraction_complete")
    )
    states = ["input_received", "facts_extracted"]
    if questions:
        states.append("missing_info")
    if conflicts:
        states.append("needs_attention")
    if not questions and not conflicts:
        states.append("extraction_complete")
    return ExtractionResponse(
        request_id=request_id,
        status=status,
        states=states,
        facts=normalized,
        questions=questions,
        conflicts=conflicts,
        metric_wording_note=metric_wording_note,
        metadata=run.metadata,
    )
