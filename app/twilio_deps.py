"""FastAPI dependency that verifies Twilio webhook signatures.

In tests, set `SKIP_TWILIO_SIGNATURE=true` to bypass.
"""

from __future__ import annotations

from fastapi import HTTPException, Request

from app.config import get_settings
from ringback.twilio_signing import verify_signature


async def verify_twilio_signature(request: Request) -> None:
    settings = get_settings()
    if settings.skip_twilio_signature or settings.app_env == "development":
        # Development: skip if no token configured.
        if not settings.twilio_auth_token:
            return
    if not settings.twilio_auth_token:
        raise HTTPException(status_code=503, detail="twilio not configured")

    sig = request.headers.get("X-Twilio-Signature", "")
    url = str(request.url)
    form = await request.form()
    params = {k: v for k, v in form.items() if isinstance(v, str)}
    if not verify_signature(settings.twilio_auth_token, url, params, sig):
        raise HTTPException(status_code=403, detail="bad twilio signature")
