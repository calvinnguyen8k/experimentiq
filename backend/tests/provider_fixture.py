import json

import httpx

from tests.conftest import extraction_data


def provider_response(data=None, *, status="completed", refusal=False):
    content = (
        {"type": "refusal", "refusal": "Cannot comply"}
        if refusal
        else {
            "type": "output_text",
            "text": json.dumps(data if data is not None else extraction_data()),
            "annotations": [],
        }
    )
    return {
        "id": "resp_test",
        "object": "response",
        "created_at": 0,
        "status": status,
        "error": None,
        "incomplete_details": None,
        "model": "gpt-4.1-mini",
        "output": [
            {
                "id": "msg_test",
                "type": "message",
                "role": "assistant",
                "status": "completed",
                "content": [content],
            }
        ],
        "parallel_tool_calls": False,
        "tool_choice": "auto",
        "tools": [],
        "usage": {"input_tokens": 100, "output_tokens": 50, "total_tokens": 150},
    }


def successful_transport(request):
    return httpx.Response(200, json=provider_response())
