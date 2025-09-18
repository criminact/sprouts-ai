from __future__ import annotations

from prometheus_client import Counter

# Total requests processed for key endpoints
REQUESTS_TOTAL = Counter(
    "app_requests_total",
    "Total requests processed",
    labelnames=("endpoint", "status_code", "safe"),
)

# Total number of unsafe prompts flagged by moderation
UNSAFE_FLAGGED_TOTAL = Counter(
    "app_unsafe_flagged_total",
    "Total unsafe prompts flagged",
    labelnames=("reason",),
)


