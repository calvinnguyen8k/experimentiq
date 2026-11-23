import json

from app.api.middleware import RequestGuard


async def test_chunked_body_limit_without_content_length():
    called = False
    sent = []
    chunks = iter(
        [
            {"type": "http.request", "body": b"x" * 16000, "more_body": True},
            {"type": "http.request", "body": b"x" * 16000, "more_body": False},
        ]
    )

    async def downstream(scope, receive, send):
        nonlocal called
        called = True

    async def receive():
        return next(chunks)

    async def send(message):
        sent.append(message)

    await RequestGuard(downstream)(
        {"type": "http", "method": "POST", "headers": [(b"content-type", b"application/json")]},
        receive,
        send,
    )
    assert not called
    assert sent[0]["status"] == 413
    assert json.loads(sent[1]["body"])["error"]["code"] == "payload_too_large"
