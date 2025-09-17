from __future__ import annotations

from typing import Any, Dict, List

from utils import groq_chat_completion
from schemas import LLMModeration

MODERATION_SYSTEM_PROMPT = (
    "You are a strict safety classifier for a chat with children aged 4-8.\n"
    "Consider the ENTIRE conversation history to infer intent.\n"
    "Return ONLY a JSON object with keys: intent, must_block, category, severity, reasons.\n"
    "intent must be 'good' or 'bad' (bad = needs more details/concern).\n"
    "must_block is a boolean true/false when content is disallowed for kids (e.g., sexual explicit, self-harm instructions, hate).\n"
    "category is one of: weapons, harassment, self_harm, sexual, drugs, hacking, pii, other.\n"
    "severity is a float from 0.0 to 1.0.\n"
    "reasons is a short list of strings."
)


def classify_intent(messages: List[Dict[str, str]]) -> Dict[str, Any]:
    analysis = groq_chat_completion(
        messages=[
            {"role": "system", "content": MODERATION_SYSTEM_PROMPT},
            *messages,
        ],
        response_schema=LLMModeration,
    )
    # Ensure required keys exist with defaults
    return {
        "intent": analysis.get("intent", "good"),
        "must_block": bool(analysis.get("must_block", False)),
        "category": analysis.get("category", "other"),
        "severity": float(analysis.get("severity", 0.0)),
        "reasons": analysis.get("reasons", []),
    }


