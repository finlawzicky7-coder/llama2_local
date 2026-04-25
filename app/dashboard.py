"""Server-rendered minimal operator dashboard."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse

from app.deps import RuntimeBundle, get_runtime

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def index() -> str:
    return (
        "<!doctype html><html><head><title>Ringback</title></head>"
        "<body style='font-family:system-ui;max-width:720px;margin:2rem auto;padding:1rem'>"
        "<h1>Ringback</h1>"
        "<p>The inbound after-hours assistant for home-services contractors.</p>"
        "<ul>"
        "<li><a href='/healthz'>health</a></li>"
        "<li><a href='/dashboard/demo'>demo dashboard (replace 'demo' with your tenant id)</a></li>"
        "</ul></body></html>"
    )


@router.get("/healthz")
async def healthz() -> dict:
    return {"ok": True}


@router.get("/dashboard/{tenant_id}", response_class=HTMLResponse)
async def dashboard(tenant_id: str, bundle: RuntimeBundle = Depends(get_runtime)) -> str:
    tenant = await bundle.tenants.get(tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="tenant not found")
    since = datetime.now(timezone.utc) - timedelta(days=7)
    bookings = await bundle.bookings.list_recent(tenant.id, since)
    rows = "".join(
        f"<tr><td>{b.scheduled_for.isoformat()}</td><td>{b.status}</td>"
        f"<td>{b.job_type_label or ''}</td></tr>"
        for b in bookings
    ) or "<tr><td colspan='3'><em>no bookings yet</em></td></tr>"
    return (
        f"<!doctype html><html><head><title>{tenant.brand} — Ringback</title></head>"
        f"<body style='font-family:system-ui;max-width:920px;margin:2rem auto;padding:1rem'>"
        f"<h1>{tenant.brand}</h1>"
        f"<p>Plan: <code>{tenant.plan}</code> · Timezone: <code>{tenant.timezone}</code></p>"
        f"<h2>Recent bookings (7d)</h2>"
        f"<table border='1' cellpadding='6' cellspacing='0'>"
        f"<thead><tr><th>scheduled for</th><th>status</th><th>job</th></tr></thead>"
        f"<tbody>{rows}</tbody></table>"
        f"</body></html>"
    )
