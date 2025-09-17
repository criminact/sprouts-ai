from __future__ import annotations

import re
from typing import Tuple

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"\b\+?[0-9][0-9()\-\s]{6,}[0-9]\b")

def mask_basic_pii(text: str) -> Tuple[str, bool]:
    """Mask simple PII patterns. Returns (masked_text, had_pii)."""
    had = False
    def _mask(pattern, s):
        nonlocal had
        def repl(match):
            had = True
            return "[REDACTED]"
        return pattern.sub(repl, s)

    masked = _mask(EMAIL_RE, text)
    masked = _mask(PHONE_RE, masked)
    return masked, had


