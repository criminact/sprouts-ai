from __future__ import annotations

from typing import Dict, List

from utils import groq_chat_completion
from schemas import LLMClarify


CLARIFY_SYSTEM_PROMPT = (
    "You are careful and kind. Ask one short question to understand intent.\n"
    "Child is 4-8. Keep it friendly. Do NOT give instructions.\n"
    "Return ONLY a JSON object with key message."
)


def ask_intent(messages: List[Dict[str, str]]) -> Dict:
    response = groq_chat_completion(
        messages=[
            {"role": "system", "content": CLARIFY_SYSTEM_PROMPT},
            *messages,
        ],
        response_schema=LLMClarify,
    )
    if "message" not in response:
        response["message"] = "Can you tell me what you want to do with that?"
    return response


