"""Pure state machine for the Ringback voice/SMS agent.

The state machine is intentionally pure (no I/O) so it is trivially
unit-testable. The runtime layer (FastAPI + Twilio + LLM adapter)
drives transitions by feeding `Event`s into `transition()`.

States:
    GREETING            - initial, agent has just answered
    CAPTURE_NAME
    CAPTURE_ADDRESS
    CAPTURE_JOB_TYPE
    CAPTURE_URGENCY
    PROPOSE_SLOTS       - we've sent SMS with options
    AWAIT_REPLY         - waiting for customer's A/B/C reply
    CREATE_BOOKING
    DONE
    ROUTED_EMERGENCY    - terminal, transferred out
    LOST                - terminal, customer dropped / no answer

Emergency detection runs on every inbound utterance in the runtime layer
(see `src/ringback/emergency.py`). The runtime emits
`EMERGENCY_DETECTED` independently of the current state.

Events:
    UTTERANCE(text)     - voice transcript or SMS body
    EMERGENCY_DETECTED  - emergency.is_emergency returned True
    SLOTS_FETCHED(n)    - calendar lookup returned at least 1 slot
    SLOT_PICKED(letter) - customer replied A/B/C
    BOOKING_WRITTEN
    HANGUP
    TIMEOUT
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional


class State(Enum):
    GREETING = auto()
    CAPTURE_NAME = auto()
    CAPTURE_ADDRESS = auto()
    CAPTURE_JOB_TYPE = auto()
    CAPTURE_URGENCY = auto()
    PROPOSE_SLOTS = auto()
    AWAIT_REPLY = auto()
    CREATE_BOOKING = auto()
    DONE = auto()
    ROUTED_EMERGENCY = auto()
    LOST = auto()


class EventKind(Enum):
    UTTERANCE = auto()
    EMERGENCY_DETECTED = auto()
    SLOTS_FETCHED = auto()
    SLOT_PICKED = auto()
    BOOKING_WRITTEN = auto()
    HANGUP = auto()
    TIMEOUT = auto()


@dataclass(frozen=True)
class Event:
    kind: EventKind
    payload: Optional[str] = None


@dataclass
class AgentContext:
    name: Optional[str] = None
    address: Optional[str] = None
    job_type: Optional[str] = None
    urgency: Optional[str] = None
    slot_letter: Optional[str] = None
    slots_offered: int = 0
    history: list[tuple[State, Event]] = field(default_factory=list)


_TERMINAL = {State.DONE, State.ROUTED_EMERGENCY, State.LOST}


def is_terminal(state: State) -> bool:
    return state in _TERMINAL


def transition(state: State, event: Event, ctx: AgentContext) -> State:
    """Return the next state given a current state and an event.

    The function is total: every (state, event) combination either
    advances or stays in place. Unhandled combinations stay in place
    so the runtime can re-prompt without crashing.
    """
    ctx.history.append((state, event))

    if is_terminal(state):
        return state

    if event.kind is EventKind.HANGUP:
        return State.LOST if state is not State.CREATE_BOOKING else state

    if event.kind is EventKind.EMERGENCY_DETECTED:
        return State.ROUTED_EMERGENCY

    if event.kind is EventKind.TIMEOUT:
        if state in {State.AWAIT_REPLY, State.PROPOSE_SLOTS}:
            return State.LOST
        return state

    if state is State.GREETING and event.kind is EventKind.UTTERANCE:
        ctx.name = (event.payload or "").strip() or ctx.name
        return State.CAPTURE_ADDRESS if ctx.name else State.CAPTURE_NAME

    if state is State.CAPTURE_NAME and event.kind is EventKind.UTTERANCE:
        ctx.name = (event.payload or "").strip() or ctx.name
        if ctx.name:
            return State.CAPTURE_ADDRESS
        return state

    if state is State.CAPTURE_ADDRESS and event.kind is EventKind.UTTERANCE:
        ctx.address = (event.payload or "").strip() or ctx.address
        if ctx.address:
            return State.CAPTURE_JOB_TYPE
        return state

    if state is State.CAPTURE_JOB_TYPE and event.kind is EventKind.UTTERANCE:
        ctx.job_type = (event.payload or "").strip() or ctx.job_type
        if ctx.job_type:
            return State.CAPTURE_URGENCY
        return state

    if state is State.CAPTURE_URGENCY and event.kind is EventKind.UTTERANCE:
        ctx.urgency = (event.payload or "").strip() or ctx.urgency
        if ctx.urgency:
            return State.PROPOSE_SLOTS
        return state

    if state is State.PROPOSE_SLOTS and event.kind is EventKind.SLOTS_FETCHED:
        try:
            ctx.slots_offered = int(event.payload or "0")
        except ValueError:
            ctx.slots_offered = 0
        if ctx.slots_offered > 0:
            return State.AWAIT_REPLY
        return State.LOST

    if state is State.AWAIT_REPLY and event.kind is EventKind.SLOT_PICKED:
        letter = (event.payload or "").strip().upper()[:1]
        if letter in {"A", "B", "C"}:
            ctx.slot_letter = letter
            return State.CREATE_BOOKING
        return state

    if state is State.CREATE_BOOKING and event.kind is EventKind.BOOKING_WRITTEN:
        return State.DONE

    return state
