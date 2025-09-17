from __future__ import annotations

from typing import Dict, List

from utils import groq_chat_completion


ANSWER_SYSTEM_PROMPT = (
    "You help kids (4-8). Answer briefly, clearly, and kindly.\n"
    "Use simple words. Encourage curiosity. Avoid unsafe instructions.\n"
    "Return JSON: {\"message\": \"...\", \"suggested_next\": \"...\"}."
)


def safe_answer(messages: List[Dict[str, str]]) -> Dict:
    response = groq_chat_completion(
        messages=[{"role": "system", "content": ANSWER_SYSTEM_PROMPT}, *messages],
        model="openai/gpt-oss-20b",
        extra_params={"temperature": 0.6},
    )
    # Ensure keys exist
    if "message" not in response:
        response["message"] = "I'm here to help! What would you like to know?"
    response.setdefault("suggested_next", None)
    return response


