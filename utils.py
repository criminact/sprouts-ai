from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional, Type

from groq import Groq


__all__ = ["groq_chat_completion"]


def groq_chat_completion(
    prompt: Optional[str] = None,
    messages: Optional[List[Dict[str, str]]] = None,
    *,
    model: str = "moonshotai/kimi-k2-instruct-0905",
    api_key: Optional[str] = None,
    extra_params: Optional[Dict[str, Any]] = None,
    response_schema: Optional[Type[Any]] = None,
) -> Dict[str, Any]:
    """Request a non-streaming JSON response from Groq chat completions.

    Minimal configuration: provide either ``prompt`` or ``messages``. Optionally override the
    ``model`` and ``api_key``. All other request parameters follow sensible defaults matching
    the given sample and can be overridden via ``extra_params`` if necessary.
    If ``response_schema`` (Pydantic BaseModel subclass) is provided, Groq will be asked to
    return that JSON schema and the output will be validated before returning as a dict.
    """
    if (prompt is None) == (messages is None):
        raise ValueError("Provide exactly one of 'prompt' or 'messages'.")

    # Normalize messages from prompt if needed
    if messages is None and prompt is not None:
        messages = [{"role": "user", "content": prompt}]

    # Configure API key (require either param or env var)
    resolved_api_key = api_key or os.getenv("GROQ_API_KEY")
    if not resolved_api_key:
        raise ValueError(
            "GROQ_API_KEY is not set. Set the environment variable or pass api_key explicitly."
        )
    client = Groq(api_key=resolved_api_key)

    # Build request parameters with minimal but sensible defaults for JSON output
    request_params: Dict[str, Any] = {
        "model": model,
        "messages": messages,
        "temperature": 0.6,
        "max_completion_tokens": 8192,
        "top_p": 1.0,
        # "reasoning_effort": "high",
        "stream": False,
        "response_format": {"type": "json_object"},
        "stop": None,
    }

    # If a Pydantic schema is provided, request strict json_schema output
    if response_schema is not None:
        try:
            schema = response_schema.model_json_schema()  # type: ignore[attr-defined]
        except Exception as exc:
            raise ValueError(
                "response_schema must be a Pydantic BaseModel subclass"
            ) from exc
        request_params["response_format"] = {
            "type": "json_schema",
            "json_schema": {
                "name": response_schema.__name__,
                "schema": schema,
            },
        }

    if extra_params:
        request_params.update(extra_params)

    completion = client.chat.completions.create(**request_params)

    # Extract and parse JSON content from the first choice message
    try:
        choice0 = completion.choices[0]
        message_obj = getattr(choice0, "message", None) or choice0.get("message")  # type: ignore[union-attr]
        if isinstance(message_obj, dict):
            content = message_obj.get("content")
        else:
            content = getattr(message_obj, "content", None)
    except Exception as exc:
        raise ValueError("Unexpected response structure from Groq.") from exc

    if not content:
        raise ValueError("Empty content received from Groq.")

    raw_obj = json.loads(content)

    # Validate with Pydantic if schema provided; return plain dict
    if response_schema is not None:
        try:
            validated = response_schema.model_validate(raw_obj)  # type: ignore[attr-defined]
            return json.loads(validated.model_dump_json())
        except Exception as exc:
            raise ValueError("Failed to validate JSON content against response_schema.") from exc

    return raw_obj


