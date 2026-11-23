"""Two-sided normal planning approximations. No LLM or network dependencies."""

from math import ceil, isfinite, sqrt

from scipy.stats import norm

from app.schemas.statistics import StatisticalRequest, StatisticalResult

MAX_ARM = 1_000_000_000
ASSUMPTIONS = [
    "Independent units, two arms, random assignment, fixed horizon and one primary outcome.",
    "Two-sided normal approximation; no continuity correction or finite-population correction.",
    "No clustering, pairing, repeated measures, sequential testing or heavy interference.",
    "No attrition allowance; counts are analyzable units. Pool feasibility is not a "
    "duration estimate.",
    "Power is an approximation under supplied assumptions, not an observed result or guarantee.",
]


def calculate(data: StatisticalRequest, request_id: str) -> StatisticalResult:
    base = dict(request_id=request_id, inputs=data.model_copy(deep=True), assumptions=ASSUMPTIONS)
    if data.design_family != "independent_two_arm":
        return StatisticalResult(
            **base,
            status="unsupported_design",
            questions=["Revise to an independent two-arm design or use a specialist method."],
        )
    questions = []
    if not data.design_confirmed:
        questions.append("Review and confirm the proposed design.")
    if not data.independent_units:
        questions.append("Confirm independent units and a two-arm fixed-horizon comparison.")
    required = ["primary_metric", "metric_type", "population_size", "effect_value"]
    if data.metric_type == "continuous":
        required += ["baseline_mean", "baseline_sd"]
    if data.metric_type == "binary":
        required += ["baseline_conversion_rate"]
    questions += [
        f"Provide {name.replace('_', ' ')}." for name in required if getattr(data, name) is None
    ]
    if questions:
        return StatisticalResult(**base, status="insufficient_information", questions=questions)

    r, za, zb = data.allocation_ratio, norm.isf(data.alpha / 2), norm.ppf(data.power)
    delta = data.effect_value
    p0, p1 = data.baseline_conversion_rate, None
    if data.effect_type == "relative":
        delta *= data.baseline_mean if data.metric_type == "continuous" else p0
    if data.metric_type == "binary":
        p1 = p0 + delta

    def variances(ratio):
        if data.metric_type == "continuous":
            variance = data.baseline_sd**2 * (1 + 1 / ratio)
            return variance, variance
        pooled = (p0 + ratio * p1) / (1 + ratio)
        return pooled * (1 - pooled) * (1 + 1 / ratio), p0 * (1 - p0) + p1 * (1 - p1) / ratio

    def power(nc, nt):
        v0, v1 = variances(nt / nc)
        shift = delta * sqrt(nc) / sqrt(v1)
        critical = za * sqrt(v0 / v1)
        return float(norm.sf(critical - shift) + norm.cdf(-critical - shift))

    def limit():
        return StatisticalResult(
            **base,
            status="calculation_limit",
            questions=[
                "These assumptions exceed the calculator's precision or "
                "one-billion-units-per-arm limit. "
                "Review the effect and baseline scale with a statistician."
            ],
        )

    if delta <= 0 or not isfinite(delta) or (p1 is not None and p1 == p0):
        return limit()
    v0, v1 = variances(r)
    if min(v0, v1) <= 0:
        return limit()
    standardized = (za * sqrt(v0) + zb * sqrt(v1)) / delta
    if not isfinite(standardized) or standardized > sqrt(MAX_ARM):
        return limit()
    nc = max(2, ceil(standardized**2))
    nt = max(2, ceil(r * nc))
    # Recheck actual integer allocation, not the requested floating-point ratio.
    for _ in range(64):
        if max(nc, nt) > MAX_ARM:
            return limit()
        achieved = power(nc, nt)
        if achieved >= data.power:
            break
        nc += max(1, ceil(nc * 0.001))
        nt = max(2, ceil(r * nc))
    else:
        return limit()
    warnings = []
    assumptions = list(ASSUMPTIONS)
    if p1 is not None:
        if min(nc * p0, nc * (1 - p0), nt * p1, nt * (1 - p1)) < 10:
            warnings.append(
                "Expected successes or failures are below 10 in an arm; the normal "
                "approximation may be unreliable."
            )
    else:
        assumptions.append("A common baseline standard deviation is assumed in both arms.")
        if min(nc, nt) < 30:
            warnings.append(
                "An arm has fewer than 30 units; check distribution shape and use a "
                "t-based or simulation plan when appropriate."
            )
    feasible = nc + nt <= data.population_size
    if not feasible:
        warnings.append(
            "Required sample exceeds the eligible population; this plan is not "
            "feasible with the supplied pool."
        )
    return StatisticalResult(
        **{**base, "assumptions": assumptions},
        status="computed",
        n_control=nc,
        n_treatment=nt,
        total=nc + nt,
        actual_allocation_ratio=nt / nc,
        achieved_power=achieved,
        absolute_effect=delta,
        target_rate=p1,
        feasible=feasible,
        formula_id="continuous_normal_v1" if p1 is None else "binary_pooled_normal_v1",
        warnings=warnings,
    )
