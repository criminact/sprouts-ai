from __future__ import annotations

from fastapi import APIRouter, HTTPException

from schemas import AskRequest, AskResponse
from guardrail.moderation import classify_intent
from guardrail.pii import mask_basic_pii
from qna.answering import safe_answer
from qna.clarifier import ask_intent

router = APIRouter()

@router.get("/health")
def health() -> dict:
    return {"status": "OK"}

@router.post("/ask")
def ask(payload: AskRequest) -> AskResponse:
    try:
        messages = [m.dict() for m in payload.messages]

        # PII masking before moderation
        last = messages[-1]["content"] if messages else ""
        masked_last, _ = mask_basic_pii(last)
        mod_input = messages[:-1] + [{"role": messages[-1]["role"], "content": masked_last}]

        print(f"Mod input: {mod_input}")

        # Intent classification over full history
        moderation = classify_intent(mod_input)

        action = "clarify" if (moderation.get("must_block") or moderation.get("intent") == "bad") else "allow"

        print(f"Moderation: {moderation}")
        print(f"Action: {action}")
        print(f"Category: {moderation['category']}")

        # Dynamic approach: when blocked, first ask a gentle intent question instead of hard refusal
        if action == "block" or action == "clarify":
            q = ask_intent(messages)  # {message}
            return AskResponse(
                type="clarify",
                message=q.get("message", "Can you tell me more about why?"),
                suggested_next=None,
                safety={"action": "clarify", **moderation},
            )

        # allow
        ans = safe_answer(messages)
        return AskResponse(
            type="answer",
            message=ans.get("message", ""),
            suggested_next=ans.get("suggested_next"),
            safety={"action": action, **moderation},
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


