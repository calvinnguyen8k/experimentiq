from typing import Annotated, Literal

from pydantic import Field, model_validator

from app.schemas.extraction import ExperimentInput, Metadata, StrictModel

DesignText = Annotated[str, Field(min_length=1, max_length=800)]
Notes = Annotated[list[DesignText], Field(max_length=10)]
CORE_FIELDS = (
    "hypothesis",
    "treatment",
    "control",
    "randomization_unit",
    "primary_metric",
    "observation_period",
    "allocation",
)


class DesignDraft(StrictModel):
    design_family: Literal["independent_two_arm", "unsupported", "unclear"]
    hypothesis: DesignText | None
    treatment: DesignText | None
    control: DesignText | None
    randomization_unit: DesignText | None
    primary_metric: DesignText | None
    observation_period: DesignText | None
    allocation: DesignText | None
    rationale: DesignText
    assumptions: Notes
    open_questions: Notes
    limitations: Notes

    @model_validator(mode="after")
    def complete_supported_proposal(self):
        if self.design_family == "independent_two_arm":
            if any(getattr(self, field) is None for field in CORE_FIELDS):
                raise ValueError("A supported proposal needs all core design fields.")
        return self


class DesignResponse(StrictModel):
    request_id: str
    status: Literal["proposal_ready", "needs_attention"]
    source: Literal["llm_suggested"] = "llm_suggested"
    metric_source: Literal["user_provided", "llm_suggested"]
    design: DesignDraft
    planning_inputs: ExperimentInput
    statistics_status: Literal["not_implemented"] = "not_implemented"
    metadata: Metadata
