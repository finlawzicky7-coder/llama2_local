from ringback.agent_state import (
    AgentContext,
    Event,
    EventKind,
    State,
    is_terminal,
    transition,
)


def _drive(state, events):
    ctx = AgentContext()
    cur = state
    for ev in events:
        cur = transition(cur, ev, ctx)
    return cur, ctx


def test_happy_path_to_done():
    final, ctx = _drive(
        State.GREETING,
        [
            Event(EventKind.UTTERANCE, "Hi this is Mike at 100 Main"),
            Event(EventKind.UTTERANCE, "100 Main Street, 75001"),
            Event(EventKind.UTTERANCE, "AC not cooling"),
            Event(EventKind.UTTERANCE, "tomorrow morning"),
            Event(EventKind.SLOTS_FETCHED, "3"),
            Event(EventKind.SLOT_PICKED, "B"),
            Event(EventKind.BOOKING_WRITTEN),
        ],
    )
    assert final is State.DONE
    assert ctx.slot_letter == "B"
    assert ctx.slots_offered == 3


def test_emergency_short_circuits():
    final, _ = _drive(
        State.GREETING,
        [
            Event(EventKind.UTTERANCE, "I smell gas"),
            Event(EventKind.EMERGENCY_DETECTED),
        ],
    )
    assert final is State.ROUTED_EMERGENCY
    assert is_terminal(final)


def test_hangup_during_capture_marks_lost():
    final, _ = _drive(
        State.CAPTURE_ADDRESS,
        [Event(EventKind.HANGUP)],
    )
    assert final is State.LOST


def test_timeout_during_await_reply_marks_lost():
    final, _ = _drive(
        State.AWAIT_REPLY,
        [Event(EventKind.TIMEOUT)],
    )
    assert final is State.LOST


def test_invalid_slot_letter_keeps_state():
    final, _ = _drive(
        State.AWAIT_REPLY,
        [Event(EventKind.SLOT_PICKED, "Z")],
    )
    assert final is State.AWAIT_REPLY


def test_terminal_states_are_sticky():
    ctx = AgentContext()
    cur = transition(State.DONE, Event(EventKind.UTTERANCE, "anything"), ctx)
    assert cur is State.DONE
    cur = transition(State.ROUTED_EMERGENCY, Event(EventKind.UTTERANCE, "anything"), ctx)
    assert cur is State.ROUTED_EMERGENCY
    cur = transition(State.LOST, Event(EventKind.UTTERANCE, "anything"), ctx)
    assert cur is State.LOST


def test_no_slots_fetched_marks_lost():
    ctx = AgentContext()
    final = transition(State.PROPOSE_SLOTS, Event(EventKind.SLOTS_FETCHED, "0"), ctx)
    assert final is State.LOST


def test_history_records_every_event():
    final, ctx = _drive(
        State.GREETING,
        [
            Event(EventKind.UTTERANCE, "Mike"),
            Event(EventKind.UTTERANCE, "100 Main"),
            Event(EventKind.HANGUP),
        ],
    )
    assert final is State.LOST
    assert len(ctx.history) == 3
