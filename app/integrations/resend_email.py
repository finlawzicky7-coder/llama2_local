"""Resend email integration."""

from __future__ import annotations

import logging
from typing import Optional

import httpx

from app.digest import EmailPort

log = logging.getLogger(__name__)


class ResendEmail(EmailPort):
    def __init__(self, api_key: str, sender: str, timeout: float = 10.0):
        if not api_key:
            raise ValueError("RESEND_API_KEY is required")
        self._api_key = api_key
        self._sender = sender
        self._timeout = timeout

    async def send(self, to: str, subject: str, body: str) -> str:
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            r = await client.post(
                "https://api.resend.com/emails",
                json={"from": self._sender, "to": [to], "subject": subject, "text": body},
                headers={"Authorization": f"Bearer {self._api_key}"},
            )
            r.raise_for_status()
            return r.json().get("id", "")
