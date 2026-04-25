"""Twilio request-signature verification.

Twilio signs every webhook request with HMAC-SHA1 over a canonical
representation of the URL + form params (or the raw JSON body for JSON
webhooks). This module exposes a verifier used as a FastAPI dependency
in production and called directly from unit tests.

Reference algorithm:
    canonical = url + concat_sorted_keys_and_values(form)
    expected  = base64(hmac_sha1(auth_token, canonical))

We compare in constant time.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
from typing import Mapping


def compute_signature(auth_token: str, url: str, params: Mapping[str, str]) -> str:
    """Return the base64 HMAC-SHA1 signature Twilio would produce."""
    if not isinstance(auth_token, str) or not auth_token:
        raise ValueError("auth_token must be a non-empty string")
    if not isinstance(url, str) or not url:
        raise ValueError("url must be a non-empty string")

    canonical = url
    for key in sorted(params.keys()):
        canonical += key + str(params[key])

    digest = hmac.new(
        auth_token.encode("utf-8"),
        canonical.encode("utf-8"),
        hashlib.sha1,
    ).digest()
    return base64.b64encode(digest).decode("ascii")


def verify_signature(
    auth_token: str,
    url: str,
    params: Mapping[str, str],
    received_signature: str,
) -> bool:
    """Constant-time signature comparison."""
    if not received_signature:
        return False
    expected = compute_signature(auth_token, url, params)
    return hmac.compare_digest(expected, received_signature)
