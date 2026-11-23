import json
import logging
from time import perf_counter
from uuid import uuid4

from starlette.responses import JSONResponse

logger = logging.getLogger("experimentiq")
MAX_BODY_BYTES = 24 * 1024


def error_response(request_id, code, message, status, fields=None):
    headers = {"Retry-After": "60"} if status == 429 else None
    return JSONResponse(
        {
            "error": {
                "code": code,
                "message": message,
                "request_id": request_id,
                "fields": fields or [],
            }
        },
        status_code=status,
        headers=headers,
    )


class RequestGuard:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        request_id = str(uuid4())
        state = scope.setdefault("state", {})
        state["request_id"] = request_id
        started = perf_counter()
        status = 500
        response_started = False

        async def traced_send(message):
            nonlocal status, response_started
            if message["type"] == "http.response.start":
                response_started = True
                status = message["status"]
                message["headers"] = list(message.get("headers", [])) + [
                    (b"x-request-id", request_id.encode()),
                    (b"cache-control", b"no-store"),
                ]
            await send(message)

        async def reject(code, message, status_code):
            state["error_category"] = code
            await error_response(request_id, code, message, status_code)(
                scope, receive, traced_send
            )

        try:
            if scope["method"] in {"POST", "PUT", "PATCH"}:
                headers = dict(scope["headers"])
                if headers.get(b"content-type", b"").split(b";")[0].strip() != b"application/json":
                    await reject("unsupported_media_type", "Send an application/json request.", 415)
                    return
                body = bytearray()
                while True:
                    message = await receive()
                    if message["type"] == "http.disconnect":
                        return
                    body.extend(message.get("body", b""))
                    if len(body) > MAX_BODY_BYTES:
                        await reject("payload_too_large", "Request exceeds the 24 KiB limit.", 413)
                        return
                    if not message.get("more_body", False):
                        break
                delivered = False

                async def replay():
                    nonlocal delivered
                    if not delivered:
                        delivered = True
                        return {"type": "http.request", "body": bytes(body), "more_body": False}
                    return await receive()

                await self.app(scope, replay, traced_send)
            else:
                await self.app(scope, receive, traced_send)
        except Exception:
            if response_started:
                raise
            await reject("internal_error", "Something went wrong. Please try again.", 500)
        finally:
            route = scope.get("route")
            logger.info(
                json.dumps(
                    {
                        "event": "http_request",
                        "request_id": request_id,
                        "route": getattr(route, "path", "unmatched"),
                        "status": status,
                        "latency_ms": round((perf_counter() - started) * 1000),
                        "error_category": state.get("error_category"),
                        "validation_failures": state.get("validation_failures", 0),
                        **state.get("usage", {}),
                    }
                )
            )
