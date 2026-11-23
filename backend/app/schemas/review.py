from typing import Annotated, Literal

from pydantic import Field

from app.schemas.design import DesignDraft, DesignText, Notes
from app.schemas.extraction import Metadata, StrictModel
from app.schemas.statistics import StatisticalRequest, StatisticalResult


class DesignRisk(StrictModel):
    category: Annotated[str, Field(min_length=1, max_length=100)]
    severity: Literal["high", "medium", "low"]
    evidence: DesignText
    explanation: DesignText
    recommendation: DesignText


class Critique(StrictModel):
    summary: DesignText
    risks: Annotated[list[DesignRisk], Field(max_length=10)]
    unresolved_assumptions: Notes


class ReviewRequest(StrictModel):
    objective: Annotated[str, Field(min_length=20, max_length=4000)]
    design: DesignDraft
    statistical_request: StatisticalRequest


class ReviewResponse(StrictModel):
    request_id: str
    status: Literal["review_complete", "review_needs_attention"]
    objective: str
    design: DesignDraft
    statistics: StatisticalResult
    critique: Critique
    checks: list[str]
    metadata: Metadata
