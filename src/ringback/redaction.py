"""PII redaction for logs.

The `redact()` function takes a dict and returns a sibling dict with
known-sensitive fields replaced by a stable hash prefix. We use a
non-reversible hash so logs can correlate (same caller -> same token)
without leaking the underlying value.

Sensitive keys:
    - phone, phone_e164, from, from_e164, to, to_e164, caller
    - email, billing_email
    - name, customer_name, full_name
    - address, street, line1, line2

Everything else passes through untouched.
"""

from __future__ import annotations

import hashlib
from typing import Any, Mapping

_SENSITIVE_KEYS = {
    "phone",
    "phone_e164",
    "from",
    "from_e164",
    "to",
    "to_e164",
    "caller",
    "email",
    "billing_email",
    "name",
    "customer_name",
    "full_name",
    "address",
    "street",
    "line1",
    "line2",
}


def _hash(value: str) -> str:
    if not value:
        return ""
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()
    return f"sha256:{digest[:12]}"


def redact(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Return a new dict with sensitive fields hashed."""
    if payload is None:
        return {}
    out: dict[str, Any] = {}
    for k, v in payload.items():
        lk = k.lower()
        if lk in _SENSITIVE_KEYS and isinstance(v, str):
            out[k] = _hash(v)
        elif isinstance(v, dict):
            out[k] = redact(v)
        elif isinstance(v, list):
            out[k] = [redact(item) if isinstance(item, dict) else item for item in v]
        else:
            out[k] = v
    return out
