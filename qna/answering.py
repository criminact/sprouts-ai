from __future__ import annotations

from typing import Dict, List

from utils import groq_chat_completion
from schemas import LLMAnswer


ANSWER_SYSTEM_PROMPT = (
    "You help kids (4-8). Answer briefly, clearly, and kindly.\n"
    "Use simple words. Encourage curiosity. Avoid unsafe instructions.\n"
    "Return ONLY a JSON object with keys message and suggested_next.\n"
    "Example: {\"message\": \"a short answer\", \"suggested_next\": \"a gentle follow-up\"}."
)


def safe_answer(messages: List[Dict[str, str]]) -> Dict:
    response = groq_chat_completion(
        messages=[{"role": "system", "content": ANSWER_SYSTEM_PROMPT}, *messages],
        response_schema=LLMAnswer,
    )
    # Ensure keys exist
    if "message" not in response:
        response["message"] = "I'm here to help! What would you like to know?"
    response.setdefault("suggested_next", None)
    return response


