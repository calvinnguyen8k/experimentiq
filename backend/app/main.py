import logging
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from openai import AsyncOpenAI

from app.api.middleware import RequestGuard, error_response
from app.api.routes import router
from app.api.validation import validation_feedback
from app.config import Settings
from app.errors import ServiceError
from app.llm.critique import Critic, OpenAICritic
from app.llm.design import Designer, OpenAIDesigner
from app.llm.extraction import Extractor, OpenAIExtractor
from app.services.limits import RequestLimits
from app.services.shared_limits import SharedLimits

logging.basicConfig(level=logging.INFO, format="%(message)s")
# Provider HTTP logs are unnecessary; application logs contain only bounded metadata.
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("openai").setLevel(logging.WARNING)


def create_app(
    settings: Settings | None = None,
    extractor: Extractor | None = None,
    designer: Designer | None = None,
    critic: Critic | None = None,
) -> FastAPI:
    settings = settings or Settings()

    @asynccontextmanager
    async def lifespan(app):
        client = None
        quota_client = httpx.AsyncClient() if settings.production_mode else None
        app.state.shared_limits = SharedLimits(settings, quota_client) if quota_client else None
        if extractor is None or designer is None or critic is None:
            key = settings.openai_api_key
            if key and key.get_secret_value().strip():
                client = AsyncOpenAI(
                    api_key=key.get_secret_value(),
                    timeout=settings.provider_timeout_seconds,
                    max_retries=1,
                )
        app.state.extractor = extractor or OpenAIExtractor(settings, client)
        app.state.designer = designer or OpenAIDesigner(settings, client)
        app.state.critic = critic or OpenAICritic(settings, client)
        try:
            yield
        finally:
            if client:
                await client.close()
            if quota_client:
                await quota_client.aclose()

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
        message, fields = validation_feedback(exc.errors())
        request.state.error_category = "invalid_input"
        request.state.validation_failures = len(exc.errors())
        return error_response(request.state.request_id, "invalid_input", message, 422, fields)

    app.include_router(router)
    return app


app = create_app()
