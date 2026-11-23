import pytest
from pydantic import ValidationError

from app.schemas.extraction import ExperimentInput, Extraction
from app.services.extraction import build_response
from tests.conftest import OBJECTIVE, extraction_data, make_run


@pytest.mark.parametrize(
    "field,value",
    [
        ("population_size", -1),
        ("population_size", True),
        ("population_size", "100"),
        ("population_size", 2.5),
        ("baseline_sd", 0),
        ("baseline_sd", float("nan")),
        ("baseline_mean", float("inf")),
        ("baseline_conversion_rate", 0),
        ("baseline_conversion_rate", 1),
        ("target_relative_uplift", -0.1),
        ("target_relative_uplift", 11),
        ("metric_type", "clustered"),
        ("primary_metric", "  "),
        ("unexpected", "ignored?"),
    ],
)
def test_rejects_invalid_values(field, value):
    with pytest.raises(ValidationError):
        ExperimentInput(objective=OBJECTIVE, **{field: value})


@pytest.mark.parametrize("objective", ["", " " * 40, "short", "x" * 4001])
def test_objective_bounds(objective):
    with pytest.raises(ValidationError):
        ExperimentInput(objective=objective)


@pytest.mark.parametrize(
    "values",
    [
        {"metric_type": "binary", "baseline_mean": 12},
        {"metric_type": "continuous", "baseline_conversion_rate": 0.1},
        {"baseline_conversion_rate": 0.9, "target_relative_uplift": 0.2},
        {"baseline_mean": 0, "target_relative_uplift": 0.05},
    ],
)
def test_rejects_incompatible_assumptions(values):
    with pytest.raises(ValidationError):
        ExperimentInput(objective=OBJECTIVE, **values)


def test_unknown_fields_stay_null_and_cannot_create_statistics():
    result = build_response(ExperimentInput(objective=OBJECTIVE), make_run(), "test")
    assert result.facts.baseline_mean.value is None
    assert result.facts.baseline_sd.value is None
    assert result.facts.population_size.value == 100000
    assert result.facts.target_relative_uplift.value == 0.05
    assert result.facts.population_size.requires_confirmation
    assert result.statistics_status == "not_implemented"
    questions = {q.field: q.reason for q in result.questions}
    assert questions["baseline_mean"] == questions["baseline_sd"] == "missing"
    assert questions["target_relative_uplift"] == "confirmation"
    assert "baseline_conversion_rate" not in questions


def test_structured_inputs_are_authoritative_but_conflicts_visible():
    data = ExperimentInput(objective=OBJECTIVE, population_size=5000)
    result = build_response(data, make_run(), "test")
    assert result.facts.population_size.value == 5000
    assert result.facts.population_size.source == "user_provided"
    assert not result.facts.population_size.requires_confirmation
    assert result.status == "needs_attention"
    assert result.conflicts[0].extracted_value == 100000


def test_incompatible_merged_values_need_attention():
    data = ExperimentInput(objective=OBJECTIVE, metric_type="binary")
    extracted = extraction_data()
    extracted["baseline_mean"] = {"value": 5, "quote": "5%"}
    result = build_response(data, make_run(extracted), "test")
    assert any(conflict.field == "assumptions" for conflict in result.conflicts)
    assert result.status == "needs_attention"


def test_complete_confirmed_intake_is_not_a_completed_review():
    data = ExperimentInput(
        objective=OBJECTIVE,
        population_size=100000,
        primary_metric="average card spending",
        metric_type="continuous",
        baseline_mean=200,
        baseline_sd=80,
        target_relative_uplift=0.05,
    )
    result = build_response(data, make_run(), "test")
    assert result.status == "extraction_complete"
    assert result.questions == []
    assert result.statistics_status == "not_implemented"
    assert "review_complete" not in result.states


def test_evidence_must_occur_in_source():
    data = extraction_data()
    data["baseline_sd"] = {"value": 123, "quote": "the SD is 123"}
    with pytest.raises(ValueError, match="quote"):
        Extraction.model_validate(data).check_evidence(OBJECTIVE)


def test_null_extraction_does_not_invent_type_or_baselines():
    blank = {field: None for field in Extraction.model_fields}
    result = build_response(ExperimentInput(objective=OBJECTIVE), make_run(blank), "test")
    assert all(getattr(result.facts, name).value is None for name in blank)
    assert {q.field for q in result.questions} == {
        "metric_type",
        "primary_metric",
        "population_size",
        "target_relative_uplift",
    }


def test_metric_wording_difference_is_visible_without_asserting_a_conflict():
    data = ExperimentInput(
        objective=OBJECTIVE,
        population_size=100000,
        primary_metric="mean spending per customer",
        metric_type="continuous",
        baseline_mean=200,
        baseline_sd=80,
        target_relative_uplift=0.05,
    )
    result = build_response(data, make_run(), "test")
    assert result.status == "extraction_complete"
    assert result.conflicts == []
    assert result.facts.primary_metric.value == "mean spending per customer"
    assert result.metric_wording_note.extracted_value == "average card spending"
    assert "does not prove a conflict" in result.metric_wording_note.message


def test_wording_note_does_not_hide_a_real_outcome_type_conflict():
    data = ExperimentInput(
        objective=OBJECTIVE,
        primary_metric="mean spending per customer",
        metric_type="binary",
        baseline_conversion_rate=0.1,
    )
    result = build_response(data, make_run(), "test")
    assert result.status == "needs_attention"
    assert {conflict.field for conflict in result.conflicts} == {"metric_type"}
    assert result.metric_wording_note is not None
