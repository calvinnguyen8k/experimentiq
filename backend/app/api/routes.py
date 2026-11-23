from fastapi import APIRouter, Request

from app.schemas.design import DesignResponse
from app.schemas.extraction import APIError, ExperimentInput, ExtractionResponse
from app.services.extraction import build_response

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
    limits = request.app.state.limits
    limits.acquire(request.client.host if request.client else "unknown")
    try:
        run = await request.app.state.extractor.extract(data.objective)
        request.state.usage = {
            **run.metadata.model_dump(exclude={"latency_ms"}),
            "provider_latency_ms": run.metadata.latency_ms,
        }
        return build_response(data, run, request.state.request_id)
    finally:
        limits.release()


@router.post(
    "/api/v1/experiments/design",
    response_model=DesignResponse,
    responses={status: {"model": APIError} for status in [413, 415, 422, 429, 500, 502, 503, 504]},
)
async def propose_design(data: ExperimentInput, request: Request):
    request.state.usage = {"model": request.app.state.model}
    limits = request.app.state.limits
    limits.acquire(request.client.host if request.client else "unknown")
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
        limits.release()
