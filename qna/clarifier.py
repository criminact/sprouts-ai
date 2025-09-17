from __future__ import annotations

from typing import Dict, List

from utils import groq_chat_completion


CLARIFY_SYSTEM_PROMPT = (
    "You are careful and kind. Ask one short question to understand intent.\n"
    "Child is 4-8. Keep it friendly.\n"
    "Return JSON: {\"message\": \"...\"}."
)


def ask_intent(messages: List[Dict[str, str]]) -> Dict:
    response = groq_chat_completion(
        messages=[
            {"role": "system", "content": CLARIFY_SYSTEM_PROMPT},
            *messages,
        ],
        model="openai/gpt-oss-20b",
        extra_params={"temperature": 0.4},
    )
    if "message" not in response:
        response["message"] = "Can you tell me what you want to do with that?"
    return response


