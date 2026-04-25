"""Agent runtime — drives the state machine across real LLM turns.

A "turn" is one inbound utterance (voice transcript or SMS body). The
runtime:

  1. Logs the utterance to the call transcript.
  2. Runs emergency detection. If positive, calls `route_emergency` and
     returns a TwiML/SMS hand-off message to the runtime caller.
  3. Builds a system+history+user prompt for the LLM with the current
     agent state and the tool catalog.
  4. Calls the LLM. Up to MAX_TOOL_HOPS, parses tool calls, runs the
     named tool, feeds the result back in as an `assistant` message.
  5. When the model emits no tool call, returns its plaintext as the
     reply to speak/text.

The runtime does NOT decide TwiML or SMS shape; the route handlers
turn the runtime's `TurnResult.reply_text` into TwiML/SMS responses.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from app.llm import LLMClient, LLMMessage
from app.tools import TOOLS, ToolDeps, detect_inbound_emergency
from app.types import Tenant
from ringback.agent_state import (
    AgentContext,
    Event,
    EventKind,
    State,
    is_terminal,
    transition,
)

MAX_TOOL_HOPS = 4

SYSTEM_PROMPT = """\
You are the inbound after-hours assistant for {brand} (a {trade} services contractor).
Your one and only goal is to qualify the caller and book a service appointment.

Rules:
- Answer in short, friendly, plain spoken English.
- This call may be recorded for quality and scheduling.
- Capture in order: name, service address (with ZIP), short description of the job, urgency.
- After capturing, call lookup_open_slots, then send the slot options as an SMS via send_sms,
  then call create_booking once the caller confirms a slot.
- If the caller mentions an emergency (fire, gas leak, flooding, no heat in winter, smoke),
  IMMEDIATELY call route_emergency.
- When booking is complete, call end_call with a one-sentence summary.
- Never promise pricing. If asked, say a tech will call back with a quote.

To call a tool, emit exactly: <tool name="TOOL_NAME">{{"arg":"value"}}</tool>
Available tools: lookup_open_slots, create_booking, send_sms, route_emergency, end_call.

Tenant config:
- timezone: {tz}
- known job types: {job_types}

Conversation state: {state}
Captured so far: {captured}
"""


@dataclass
class TurnResult:
    reply_text: str
    state: State
    terminal: bool
    tool_calls: list[dict]  # for tests/observability


def _captured(ctx: AgentContext) -> dict:
    return {
        "name": ctx.name,
        "address": ctx.address,
        "job_type": ctx.job_type,
        "urgency": ctx.urgency,
        "slot_letter": ctx.slot_letter,
    }


def _system_prompt(tenant: Tenant, state: State, ctx: AgentContext) -> str:
    return SYSTEM_PROMPT.format(
        brand=tenant.brand,
        trade=", ".join(tenant.job_types) or "home services",
        tz=tenant.timezone,
        job_types=", ".join(tenant.job_types) or "general service",
        state=state.name,
        captured=json.dumps(_captured(ctx)),
    )


def _drive_state_for_utterance(state: State, ctx: AgentContext, utterance: str) -> State:
    return transition(state, Event(EventKind.UTTERANCE, utterance), ctx)


async def run_turn(
    tenant: Tenant,
    state: State,
    ctx: AgentContext,
    utterance: str,
    history: list[LLMMessage],
    llm: LLMClient,
    deps: ToolDeps,
) -> TurnResult:
    if is_terminal(state):
        return TurnResult(reply_text="", state=state, terminal=True, tool_calls=[])

    await deps.calls.append_transcript(deps.call_id, "user", utterance)

    if detect_inbound_emergency(utterance, tenant.emergency_keywords):
        await TOOLS["route_emergency"]({}, deps)
        new_state = transition(state, Event(EventKind.EMERGENCY_DETECTED), ctx)
        return TurnResult(
            reply_text=f"That sounds urgent. I'm transferring you to {tenant.brand}'s on-call line right now — stay on the line.",
            state=new_state,
            terminal=is_terminal(new_state),
            tool_calls=[{"name": "route_emergency", "args": {}, "result": {}}],
        )

    new_state = _drive_state_for_utterance(state, ctx, utterance)

    messages: list[LLMMessage] = [
        LLMMessage(role="system", content=_system_prompt(tenant, new_state, ctx))
    ]
    messages.extend(history)
    messages.append(LLMMessage(role="user", content=utterance))

    tool_calls: list[dict] = []
    reply_text = ""
    for _ in range(MAX_TOOL_HOPS):
        resp = await llm.complete(messages)
        parsed = resp.parse_tool_call()
        if not parsed:
            reply_text = resp.text.strip()
            break
        tool_name, args = parsed
        tool = TOOLS.get(tool_name)
        if tool is None:
            reply_text = "Sorry — I had trouble. Let me try again."
            break
        result = await tool(args, deps)
        tool_calls.append({"name": tool_name, "args": args, "result": result})
        if tool_name == "end_call":
            new_state = State.DONE
            break
        if tool_name == "create_booking":
            new_state = transition(new_state, Event(EventKind.BOOKING_WRITTEN), ctx)
        if tool_name == "lookup_open_slots":
            slot_count = len(result.get("slots", []))
            new_state = transition(new_state, Event(EventKind.SLOTS_FETCHED, str(slot_count)), ctx)
        messages.append(LLMMessage(role="assistant", content=resp.text))
        messages.append(LLMMessage(role="user", content=f"<tool-result>{json.dumps(result)}</tool-result>"))

    if reply_text:
        await deps.calls.append_transcript(deps.call_id, "assistant", reply_text)

    return TurnResult(
        reply_text=reply_text,
        state=new_state,
        terminal=is_terminal(new_state),
        tool_calls=tool_calls,
    )
