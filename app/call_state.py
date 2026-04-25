"""Per-call state store.

Twilio's voice <Gather> loop POSTs each turn separately, so the agent
state must persist across requests keyed by `CallSid`. In production
this lives in Postgres (via `events` and `calls.transcript_jsonb`); in
tests we use the in-memory store. We expose both behind a single
interface so route handlers don't care which is in use.

For simplicity and because this state is small + ephemeral (one call),
the default production store is also in-memory per process. For
multi-worker deployments, swap in `RedisCallStateStore` (left as
follow-up — flagged in qa-report.md).
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from typing import Optional

from app.llm import LLMMessage
from ringback.agent_state import AgentContext, State


@dataclass
class CallSession:
    call_id: str  # internal uuid
    tenant_id: str
    twilio_call_sid: str
    from_e164: str
    to_e164: str
    state: State = State.GREETING
    ctx: AgentContext = field(default_factory=AgentContext)
    history: list[LLMMessage] = field(default_factory=list)


class InMemoryCallStateStore:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._by_call_sid: dict[str, CallSession] = {}

    def get(self, twilio_call_sid: str) -> Optional[CallSession]:
        with self._lock:
            return self._by_call_sid.get(twilio_call_sid)

    def put(self, session: CallSession) -> None:
        with self._lock:
            self._by_call_sid[session.twilio_call_sid] = session

    def delete(self, twilio_call_sid: str) -> None:
        with self._lock:
            self._by_call_sid.pop(twilio_call_sid, None)
