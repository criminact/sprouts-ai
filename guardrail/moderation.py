from __future__ import annotations

from typing import Any, Dict, List

from utils import groq_chat_completion
from schemas import LLMModeration

MODERATION_SYSTEM_PROMPT = (
    "You are a strict safety classifier for a chat with children aged 4-8.\n"
    "Consider the ENTIRE conversation history to infer intent.\n"
    "Use internal reasoning (scratchpad/chain-of-thought) silently; DO NOT reveal your reasoning.\n"
    "Follow this checklist before deciding: (1) Briefly summarize the child's likely intent,\n"
    "(2) consider context from prior turns, (3) map to category (weapons, harassment, self_harm, sexual, drugs, hacking, pii, other),\n"
    "(4) assess severity 0.0-1.0, (5) set intent = good/bad, (6) set must_block if content is disallowed for kids,\n"
    "(7) list 1-3 short reasons.\n"
    "Return ONLY a JSON object with keys: intent, must_block, category, severity, reasons."
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


