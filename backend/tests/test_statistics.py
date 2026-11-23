from math import ceil

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError
from statsmodels.stats.power import NormalIndPower
from statsmodels.stats.proportion import (
    power_proportions_2indep,
    samplesize_proportions_2indep_onetail,
)

from app.config import Settings
from app.main import create_app
from app.schemas.statistics import StatisticalRequest
from app.services.statistics import calculate


def inputs(**changes):
    return StatisticalRequest(
        **{
            "design_family": "independent_two_arm",
            "design_confirmed": True,
            "independent_units": True,
            "primary_metric": "average card spending",
            "metric_type": "continuous",
            "population_size": 100000,
            "baseline_mean": 200.0,
            "baseline_sd": 100.0,
            "effect_value": 0.05,
            **changes,
        }
    )


@pytest.mark.parametrize("ratio", [0.5, 1.0, 2.0, 3.7])
def test_continuous_matches_independent_statsmodels_oracle(ratio):
    data = inputs(allocation_ratio=ratio)
    result = calculate(data, "test")
    oracle = NormalIndPower()
    expected = ceil(oracle.solve_power(effect_size=0.1, alpha=0.05, power=0.8, ratio=ratio))
    assert result.n_control == expected
    assert result.n_treatment == ceil(expected * ratio)
    assert result.achieved_power == pytest.approx(
        oracle.power(
            effect_size=0.1,
            nobs1=result.n_control,
            alpha=0.05,
            ratio=result.n_treatment / result.n_control,
        ),
        abs=1e-12,
    )
    assert result.achieved_power >= 0.8


@pytest.mark.parametrize("ratio", [0.5, 1.0, 2.0, 3.7])
def test_binary_matches_independent_statsmodels_oracle(ratio):
    data = inputs(
        metric_type="binary",
        baseline_mean=None,
        baseline_sd=None,
        baseline_conversion_rate=0.1,
        effect_value=0.2,
        allocation_ratio=ratio,
    )
    result = calculate(data, "test")
    # statsmodels group 1 is control here; diff is control minus treatment.
    expected = ceil(
        samplesize_proportions_2indep_onetail(
            diff=-0.02, prop2=0.12, power=0.8, ratio=ratio, alpha=0.05
        )
    )
    assert result.n_control == expected
    reference_power = power_proportions_2indep(
        diff=-0.02,
        prop2=0.12,
        nobs1=result.n_control,
        ratio=result.n_treatment / result.n_control,
        alpha=0.05,
        return_results=False,
    )
    assert result.achieved_power == pytest.approx(reference_power, abs=1e-12)
    assert result.achieved_power >= 0.8
    assert result.target_rate == pytest.approx(0.12)


def test_reference_and_complete_demo_values():
    result = calculate(inputs(baseline_mean=1.0, baseline_sd=1.0, effect_value=0.5), "test")
    assert result.n_control == result.n_treatment == 63
    result = calculate(inputs(), "test")
    assert result.n_control == result.n_treatment == 1570
    assert result.total == 3140
    assert result.feasible is True


@pytest.mark.parametrize(
    "missing",
    [
        "baseline_sd",
        "baseline_mean",
        "population_size",
        "effect_value",
        "primary_metric",
        "metric_type",
    ],
)
def test_missing_values_never_compute(missing):
    result = calculate(inputs(**{missing: None}), "test")
    assert result.status == "insufficient_information"
    assert result.n_control is result.n_treatment is result.total is result.feasible is None
    assert result.questions


@pytest.mark.parametrize(
    "changes",
    [
        {"alpha": 0},
        {"power": 0.5},
        {"allocation_ratio": 0},
        {"effect_value": 0},
        {"baseline_sd": -1},
        {"baseline_mean": 0},
        {"population_size": True},
        {"baseline_sd": float("nan")},
        {"alpha": float("inf")},
        {"metric_type": "binary", "baseline_conversion_rate": 0.9},
    ],
)
def test_invalid_inputs_rejected(changes):
    with pytest.raises(ValidationError):
        inputs(**changes)


def test_absolute_effect_allows_nonpositive_mean_and_reports_infeasible():
    result = calculate(
        inputs(effect_type="absolute", effect_value=10.0, baseline_mean=-20.0, population_size=100),
        "test",
    )
    assert result.total == 3140
    assert result.feasible is False
    assert result.warnings


@pytest.mark.parametrize("family", ["unsupported", "unclear"])
def test_unsupported_never_computes(family):
    result = calculate(inputs(design_family=family), "test")
    assert result.status == "unsupported_design"
    assert result.total is None


def test_confirmation_and_precision_limits():
    assert calculate(inputs(design_confirmed=False), "t").status == "insufficient_information"
    assert calculate(inputs(independent_units=False), "t").status == "insufficient_information"
    assert calculate(inputs(effect_value=1e-300), "t").status == "calculation_limit"
    assert calculate(inputs(baseline_sd=1e-300), "t").status == "calculation_limit"


def test_snapshot_and_api_without_provider():
    data = inputs()
    result = calculate(data, "test")
    data.baseline_sd = 500
    assert result.inputs.baseline_sd == 100
    with TestClient(create_app(Settings(_env_file=None, openai_api_key=None))) as client:
        response = client.post("/api/v1/statistics/sample-size", json=inputs().model_dump())
        assert response.status_code == 200
        assert response.json()["source"] == "derived"
        assert response.json()["total"] == 3140
