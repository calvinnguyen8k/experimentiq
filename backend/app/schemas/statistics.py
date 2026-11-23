from typing import Annotated, Literal

from pydantic import Field, model_validator
from pydantic_core import PydanticCustomError

from app.schemas.extraction import SD, Mean, MetricType, Population, Rate, ShortText, StrictModel


class StatisticalRequest(StrictModel):
    design_family: Literal["independent_two_arm", "unsupported", "unclear"]
    design_confirmed: bool = False
    independent_units: bool = False
    primary_metric: ShortText | None = None
    metric_type: MetricType | None = None
    population_size: Population | None = None
    baseline_mean: Mean | None = None
    baseline_sd: SD | None = None
    baseline_conversion_rate: Rate | None = None
    effect_type: Literal["absolute", "relative"] = "relative"
    effect_value: Annotated[float, Field(gt=0, le=1e12)] | None = None
    alpha: Annotated[float, Field(ge=0.000001, le=0.5)] = 0.05
    power: Annotated[float, Field(gt=0.5, le=0.999999)] = 0.8
    allocation_ratio: Annotated[float, Field(ge=0.01, le=100)] = 1.0

    @model_validator(mode="after")
    def compatible(self):
        if self.metric_type == "binary":
            if self.baseline_mean is not None or self.baseline_sd is not None:
                raise PydanticCustomError("binary_with_mean", "Incompatible baseline.")
            p0 = self.baseline_conversion_rate
            if p0 is not None and self.effect_value is not None:
                delta = (
                    self.effect_value * p0 if self.effect_type == "relative" else self.effect_value
                )
                if p0 + delta >= 1:
                    raise PydanticCustomError("stat_target_rate", "Target must be below one.")
        if self.metric_type == "continuous":
            if self.baseline_conversion_rate is not None:
                raise PydanticCustomError("continuous_with_rate", "Incompatible baseline.")
            if self.effect_type == "relative" and self.baseline_mean is not None:
                if self.baseline_mean <= 0:
                    raise PydanticCustomError("stat_relative_mean", "Positive mean required.")
        return self


class StatisticalResult(StrictModel):
    request_id: str
    source: Literal["derived"] = "derived"
    status: Literal[
        "computed", "insufficient_information", "unsupported_design", "calculation_limit"
    ]
    inputs: StatisticalRequest
    n_control: int | None = None
    n_treatment: int | None = None
    total: int | None = None
    actual_allocation_ratio: float | None = None
    achieved_power: float | None = None
    absolute_effect: float | None = None
    target_rate: float | None = None
    feasible: bool | None = None
    formula_id: str | None = None
    assumptions: list[str] = Field(default_factory=list)
    questions: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
