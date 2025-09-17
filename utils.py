from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

from groq import Groq


__all__ = ["groq_chat_completion"]


def groq_chat_completion(
    prompt: Optional[str] = None,
    messages: Optional[List[Dict[str, str]]] = None,
    *,
    model: str = "openai/gpt-oss-20b",
    api_key: Optional[str] = None,
    extra_params: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Request a non-streaming JSON response from Groq chat completions.

    Minimal configuration: provide either ``prompt`` or ``messages``. Optionally override the
    ``model`` and ``api_key``. All other request parameters follow sensible defaults matching
    the given sample and can be overridden via ``extra_params`` if necessary.
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
        "temperature": 1.0,
        "max_completion_tokens": 8192,
        "top_p": 1.0,
        "reasoning_effort": "high",
        "stream": False,
        "response_format": {"type": "json_object"},
        "stop": None,
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

    try:
        return json.loads(content)
    except Exception as exc:
        raise ValueError("Failed to parse JSON content from Groq response.") from exc


