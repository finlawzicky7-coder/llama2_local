"""Google Calendar wrapper.

The real implementation uses google-api-python-client + per-tenant
OAuth tokens stored in Postgres. The fake implementation in
`app.repos.FakeCalendar` is used in tests.

To keep the unit-test layer fast and offline, we only declare the
interface here and import the real client lazily.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional

from app.repos import CalendarPort
from app.types import Booking, Slot

log = logging.getLogger(__name__)


class GoogleCalendarClient(CalendarPort):
    """Lazy Google Calendar wrapper — instantiate only when configured."""

    def __init__(self, get_credentials):
        # `get_credentials(tenant_id)` returns an authorized Credentials object.
        self._get_credentials = get_credentials

    async def lookup_open_slots(self, tenant_id: str, after: datetime, count: int) -> list[Slot]:
        try:
            from googleapiclient.discovery import build  # type: ignore
        except ImportError as e:  # pragma: no cover
            raise RuntimeError("google-api-python-client not installed") from e
        creds = self._get_credentials(tenant_id)
        service = build("calendar", "v3", credentials=creds, cache_discovery=False)
        # Real implementation: query freebusy and gap-find. Stubbed return so
        # this module is callable; the meaningful end-to-end test uses FakeCalendar.
        log.info("lookup_open_slots called for tenant=%s after=%s count=%s", tenant_id, after, count)
        return []  # production wiring extends this — see follow-up in qa-report.md

    async def create_event(self, tenant_id: str, booking: Booking) -> str:
        try:
            from googleapiclient.discovery import build  # type: ignore
        except ImportError as e:  # pragma: no cover
            raise RuntimeError("google-api-python-client not installed") from e
        creds = self._get_credentials(tenant_id)
        service = build("calendar", "v3", credentials=creds, cache_discovery=False)
        event = {
            "summary": f"Ringback booking — {booking.job_type_label or 'service'}",
            "description": booking.notes or "",
            "start": {"dateTime": booking.scheduled_for.isoformat()},
            "end": {"dateTime": (booking.scheduled_for.replace(
                hour=(booking.scheduled_for.hour + max(1, booking.duration_minutes // 60)) % 24
            )).isoformat()},
        }
        created = service.events().insert(calendarId="primary", body=event).execute()
        return created.get("id", "")
