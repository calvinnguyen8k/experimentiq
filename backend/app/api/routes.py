from fastapi import APIRouter, Request

from app.errors import ServiceError
from app.schemas.design import DesignResponse
from app.schemas.extraction import APIError, ExperimentInput, ExtractionResponse
from app.schemas.review import ReviewRequest, ReviewResponse
from app.schemas.statistics import StatisticalRequest, StatisticalResult
from app.services.extraction import build_response
from app.services.shared_limits import acquire, release
from app.services.statistics import calculate

router = APIRouter()


@router.get("/health")
async def health():
    return {"status": "ok", "service": "experimentiq", "version": "0.1.0"}


@router.post(
    "/api/v1/experiments/extract",
    response_model=ExtractionResponse,
    responses={status: {"model": APIError} for status in [413, 415, 422, 429, 500, 502, 503, 504]},
)
async def extract(data: ExperimentInput, request: Request):
    request.state.usage = {"model": request.app.state.model}
    await acquire(request)
    try:
        run = await request.app.state.extractor.extract(data.objective)
        request.state.usage = {
            **run.metadata.model_dump(exclude={"latency_ms"}),
            "provider_latency_ms": run.metadata.latency_ms,
        }
        return build_response(data, run, request.state.request_id)
    finally:
        await release(request)


@router.post("/api/v1/statistics/sample-size", response_model=StatisticalResult)
async def sample_size(data: StatisticalRequest, request: Request):
    await acquire(request)
    try:
        return calculate(data, request.state.request_id)
    finally:
        await release(request)


@router.post("/api/v1/experiments/review", response_model=ReviewResponse)
async def review(data: ReviewRequest, request: Request):
    inputs = data.statistical_request
    if data.design.design_family != inputs.design_family:
        raise ServiceError(
            "invalid_input", "Design family and calculator assumptions disagree.", 422
        )
    if data.design.primary_metric != inputs.primary_metric:
        raise ServiceError(
            "invalid_input", "Design and calculator must use the same primary metric.", 422
        )
    statistics = calculate(inputs, request.state.request_id)
    if statistics.status != "computed":
        raise ServiceError("invalid_input", " ".join(statistics.questions), 422)
    await acquire(request)
    request.state.usage = {"model": request.app.state.model}
    try:
        run = await request.app.state.critic.review(data, statistics.model_copy(deep=True))
        request.state.usage = {
            **run.metadata.model_dump(exclude={"latency_ms"}),
            "provider_latency_ms": run.metadata.latency_ms,
        }
        critique = run.value.model_copy(deep=True)
        critique.risks.sort(key=lambda risk: {"high": 0, "medium": 1, "low": 2}[risk.severity])
        checks = list(statistics.warnings)
        if data.design.open_questions:
            checks.append(
                "Proposal questions remain open; review them before running an experiment."
            )
        if data.design.assumptions:
            checks.append("Proposal assumptions are acknowledged, not independently verified.")
        attention = bool(checks or critique.unresolved_assumptions or critique.risks)
        return ReviewResponse(
            request_id=request.state.request_id,
            status="review_needs_attention" if attention else "review_complete",
            objective=data.objective,
            design=data.design,
            statistics=statistics,
            critique=critique,
            checks=checks,
            metadata=run.metadata,
        )
    finally:
        await release(request)


@router.post(
    "/api/v1/experiments/design",
    response_model=DesignResponse,
    responses={status: {"model": APIError} for status in [413, 415, 422, 429, 500, 502, 503, 504]},
)
async def propose_design(data: ExperimentInput, request: Request):
    request.state.usage = {"model": request.app.state.model}
    await acquire(request)
    try:
        run = await request.app.state.designer.generate(data)
        request.state.usage = {
            **run.metadata.model_dump(exclude={"latency_ms"}),
            "provider_latency_ms": run.metadata.latency_ms,
        }
        design = run.value
        if data.primary_metric is not None:
            design = design.model_copy(update={"primary_metric": data.primary_metric})
        return DesignResponse(
            request_id=request.state.request_id,
            status="proposal_ready"
            if design.design_family == "independent_two_arm"
            else "needs_attention",
            metric_source="user_provided" if data.primary_metric is not None else "llm_suggested",
            design=design,
            planning_inputs=data,
            metadata=run.metadata,
        )
    finally:
        await release(request)
