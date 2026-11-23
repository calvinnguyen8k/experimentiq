from typing import Annotated, Generic, Literal, TypeVar

from pydantic import BaseModel, ConfigDict, Field, model_validator

MetricType = Literal["binary", "continuous"]
ShortText = Annotated[str, Field(min_length=1, max_length=200)]
Population = Annotated[int, Field(ge=2, le=1_000_000_000)]
Mean = Annotated[float, Field(ge=-1e12, le=1e12)]
SD = Annotated[float, Field(gt=0, le=1e12)]
Rate = Annotated[float, Field(gt=0, lt=1)]
Uplift = Annotated[float, Field(gt=0, le=10)]
FieldName = Literal[
    "population_size",
    "primary_metric",
    "metric_type",
    "baseline_mean",
    "baseline_sd",
    "baseline_conversion_rate",
    "target_relative_uplift",
]


class StrictModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid", strict=True, allow_inf_nan=False, str_strip_whitespace=True
    )


class ExperimentInput(StrictModel):
    objective: Annotated[str, Field(min_length=20, max_length=4000)]
    population_size: Population | None = None
    primary_metric: ShortText | None = None
    metric_type: MetricType | None = None
    baseline_mean: Mean | None = None
    baseline_sd: SD | None = None
    baseline_conversion_rate: Rate | None = None
    target_relative_uplift: Uplift | None = None

    @model_validator(mode="after")
    def compatible_assumptions(self):
        if self.metric_type == "binary":
            if self.baseline_mean is not None or self.baseline_sd is not None:
                raise ValueError("Binary outcomes require a conversion rate, not mean/SD.")
        if self.metric_type == "continuous" and self.baseline_conversion_rate is not None:
            raise ValueError("Continuous outcomes require mean/SD, not a conversion rate.")
        if self.baseline_conversion_rate is not None and self.target_relative_uplift is not None:
            if self.baseline_conversion_rate * (1 + self.target_relative_uplift) >= 1:
                raise ValueError("The target conversion rate must be less than one.")
        if self.baseline_mean is not None and self.target_relative_uplift is not None:
            if self.baseline_mean <= 0:
                raise ValueError("Relative increase requires a positive baseline mean.")
        return self


T = TypeVar("T")


class Evidence(StrictModel, Generic[T]):
    value: T
    quote: Annotated[str, Field(min_length=1, max_length=500)]


class Extraction(StrictModel):
    # Required-but-nullable fields generate a strict OpenAI structured-output schema.
    population_size: Evidence[Population] | None
    primary_metric: Evidence[ShortText] | None
    metric_type: Evidence[MetricType] | None
    baseline_mean: Evidence[Mean] | None
    baseline_sd: Evidence[SD] | None
    baseline_conversion_rate: Evidence[Rate] | None
    target_relative_uplift: Evidence[Uplift] | None

    def check_evidence(self, objective: str) -> None:
        for name in type(self).model_fields:
            item = getattr(self, name)
            if item is not None and item.quote not in objective:
                raise ValueError("Extraction quote is not present in the objective.")


class Fact(StrictModel, Generic[T]):
    value: T | None
    source: Literal["user_provided", "llm_extracted", "missing"]
    evidence: str | None
    requires_confirmation: bool


class Facts(StrictModel):
    population_size: Fact[Population]
    primary_metric: Fact[ShortText]
    metric_type: Fact[MetricType]
    baseline_mean: Fact[Mean]
    baseline_sd: Fact[SD]
    baseline_conversion_rate: Fact[Rate]
    target_relative_uplift: Fact[Uplift]


class Question(StrictModel):
    field: FieldName
    reason: Literal["missing", "confirmation"]
    question: str


class Conflict(StrictModel):
    field: str
    supplied_value: str | float | int | None
    extracted_value: str | float | int | None
    message: str


class Metadata(StrictModel):
    model: str
    prompt_version: str
    latency_ms: int
    attempts: int
    input_tokens: int | None
    output_tokens: int | None
    estimated_cost_usd: float | None


class ExtractionResponse(StrictModel):
    request_id: str
    status: Literal["extraction_complete", "missing_information", "needs_attention"]
    states: list[str]
    facts: Facts
    questions: list[Question]
    conflicts: list[Conflict]
    statistics_status: Literal["not_implemented"] = "not_implemented"
    metadata: Metadata


class ErrorDetail(StrictModel):
    code: str
    message: str
    request_id: str
    fields: list[str] = []


class APIError(StrictModel):
    error: ErrorDetail
