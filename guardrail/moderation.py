from __future__ import annotations

from typing import Any, Dict, List

from utils import groq_chat_completion

MODERATION_SYSTEM_PROMPT = (
    "You are a strict safety classifier for a chat with children aged 4-8.\n"
    "Consider the ENTIRE conversation history to infer intent.\n"
    "Return ONLY JSON with keys: intent, must_block, category, severity, reasons.\n"
    "intent: 'good' or 'bad' (bad = needs more details/concern).\n"
    "must_block: true if content is disallowed for kids (e.g., sexual explicit, self-harm instructions, hate).\n"
    "category: one of weapons, harassment, self_harm, sexual, drugs, hacking, pii, other.\n"
    "severity: float 0.0-1.0.\n"
    "reasons: short list of strings." 
)

def classify_intent(messages: List[Dict[str, str]]) -> Dict[str, Any]:
    analysis = groq_chat_completion(
        messages=[
            {"role": "system", "content": MODERATION_SYSTEM_PROMPT},
            *messages,
        ],
        model="openai/gpt-oss-20b",
        extra_params={
            "temperature": 0
        },
    )
    # Ensure required keys exist with defaults
    return {
        "intent": analysis.get("intent", "good"),
        "must_block": bool(analysis.get("must_block", False)),
        "category": analysis.get("category", "other"),
        "severity": float(analysis.get("severity", 0.0)),
        "reasons": analysis.get("reasons", []),
    }


