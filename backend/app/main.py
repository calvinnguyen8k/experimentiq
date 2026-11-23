import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from openai import AsyncOpenAI

from app.api.middleware import RequestGuard, error_response
from app.api.routes import router
from app.config import Settings
from app.errors import ServiceError
from app.llm.extraction import Extractor, OpenAIExtractor
from app.schemas.extraction import ExperimentInput
from app.services.limits import RequestLimits

logging.basicConfig(level=logging.INFO, format="%(message)s")
# Provider HTTP logs are unnecessary; application logs contain only bounded metadata.
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("openai").setLevel(logging.WARNING)


def create_app(settings: Settings | None = None, extractor: Extractor | None = None) -> FastAPI:
    settings = settings or Settings()

    @asynccontextmanager
    async def lifespan(app):
        client = None
        if extractor is None:
            key = settings.openai_api_key
            if key and key.get_secret_value().strip():
                client = AsyncOpenAI(
                    api_key=key.get_secret_value(),
                    timeout=settings.provider_timeout_seconds,
                    max_retries=1,
                )
            app.state.extractor = OpenAIExtractor(settings, client)
        else:
            app.state.extractor = extractor
        try:
            yield
        finally:
            if client:
                await client.close()

    app = FastAPI(title="ExperimentIQ API", version="0.1.0", lifespan=lifespan)
    app.state.model = settings.openai_model
    app.state.limits = RequestLimits(
        settings.rate_limit_per_minute,
        settings.global_rate_limit_per_minute,
        settings.max_concurrent_requests,
    )
    app.add_middleware(RequestGuard)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
        expose_headers=["X-Request-ID", "Retry-After"],
    )

    @app.exception_handler(ServiceError)
    async def service_error(request: Request, exc: ServiceError):
        request.state.error_category = exc.code
        return error_response(request.state.request_id, exc.code, exc.message, exc.status)

    @app.exception_handler(RequestValidationError)
    async def invalid_input(request: Request, exc: RequestValidationError):
        # Pydantic's default error body echoes input; do not expose it.
        known = set(ExperimentInput.model_fields)
        fields = sorted(
            {str(part) for error in exc.errors() for part in error["loc"] if part in known}
        )
        request.state.error_category = "invalid_input"
        request.state.validation_failures = len(exc.errors())
        message = (
            "Check the indicated fields and their allowed ranges. "
            "Use mean/SD for continuous outcomes or a rate for binary outcomes; "
            "relative increases require a positive mean or a target rate below 1."
        )
        return error_response(request.state.request_id, "invalid_input", message, 422, fields)

    app.include_router(router)
    return app


app = create_app()
