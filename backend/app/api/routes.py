from fastapi import APIRouter, Request

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
