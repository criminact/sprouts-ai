from __future__ import annotations

from fastapi import APIRouter, HTTPException
from metrics import REQUESTS_TOTAL, UNSAFE_FLAGGED_TOTAL

from schemas import AskRequest, AskResponse
from guardrail.moderation import classify_intent
from guardrail.pii import mask_basic_pii
from qna.answering import safe_answer
from qna.clarifier import ask_intent

router = APIRouter()

@router.get("/health")
def health() -> dict:
    return {"status": "OK"}

@router.get("/metrics")
def metrics_summary() -> dict:
    # Build a friendly JSON summary of our custom metrics
    requests_total = 0
    requests_by_safe: dict = {}
    requests_by_status: dict = {}

    for metric in REQUESTS_TOTAL.collect():
        for sample in metric.samples:
            if sample.name != "app_requests_total":
                continue
            value = int(sample.value)
            requests_total += value
            safe = sample.labels.get("safe", "unknown")
            status = sample.labels.get("status_code", "unknown")
            requests_by_safe[safe] = requests_by_safe.get(safe, 0) + value
            requests_by_status[status] = requests_by_status.get(status, 0) + value

    unsafe_total = 0
    unsafe_by_reason: dict = {}
    for metric in UNSAFE_FLAGGED_TOTAL.collect():
        for sample in metric.samples:
            if sample.name != "app_unsafe_flagged_total":
                continue
            value = int(sample.value)
            unsafe_total += value
            reason = sample.labels.get("reason", "other")
            unsafe_by_reason[reason] = unsafe_by_reason.get(reason, 0) + value

    return {
        "requests": {
            "total": requests_total,
            "by_safe": requests_by_safe,
            "by_status_code": requests_by_status,
        },
        "unsafe_flagged": {
            "total": unsafe_total,
            "by_reason": unsafe_by_reason,
        },
    }

@router.post("/ask")
def ask(payload: AskRequest) -> AskResponse:
    try:
        messages = [m.dict() for m in payload.messages]

        # PII masking before moderation
        last = messages[-1]["content"] if messages else ""
        masked_last, _ = mask_basic_pii(last)
        mod_input = messages[:-1] + [{"role": messages[-1]["role"], "content": masked_last}]

        # Intent classification over full history
        moderation = classify_intent(mod_input)

        action = "clarify" if (moderation.get("must_block") or moderation.get("intent") == "bad") else "allow"

        # Dynamic approach: when blocked, first ask a gentle intent question instead of hard refusal
        if action == "block" or action == "clarify":
            # record unsafe by category
            UNSAFE_FLAGGED_TOTAL.labels(reason=moderation.get("category", "other")).inc()
            q = ask_intent(messages)  # {message}
            # mark request as processed (safe=false)
            REQUESTS_TOTAL.labels(endpoint="/ask", status_code="200", safe="false").inc()
            return AskResponse(
                type="clarify",
                message=q.get("message", "Can you tell me more about why?"),
                suggested_next=None,
                safety={"action": "clarify", **moderation},
            )

        # allow
        ans = safe_answer(messages)
        REQUESTS_TOTAL.labels(endpoint="/ask", status_code="200", safe="true").inc()
        return AskResponse(
            type="answer",
            message=ans.get("message", ""),
            suggested_next=ans.get("suggested_next"),
            safety={"action": action, **moderation},
        )
    except HTTPException as e:
        print(f"HTTPException: {e.detail}")
        REQUESTS_TOTAL.labels(endpoint="/ask", status_code=str(e.status_code), safe="false").inc()
        raise HTTPException(status_code=500, detail=e.detail)
    except Exception as exc:
        print(f"Exception: {exc}")
        REQUESTS_TOTAL.labels(endpoint="/ask", status_code="500", safe="false").inc()
        raise HTTPException(status_code=500, detail=str(exc))


