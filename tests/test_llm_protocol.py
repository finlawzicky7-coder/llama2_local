"""Tests for the LLM tool-call protocol parser."""

from app.llm import LLMResponse


def test_parse_tool_call_returns_name_and_args():
    r = LLMResponse(text='Sure. <tool name="send_sms">{"to_e164":"+14155551212","body":"hi"}</tool>')
    parsed = r.parse_tool_call()
    assert parsed is not None
    name, args = parsed
    assert name == "send_sms"
    assert args == {"to_e164": "+14155551212", "body": "hi"}


def test_parse_tool_call_returns_none_when_absent():
    r = LLMResponse(text="No tool call here.")
    assert r.parse_tool_call() is None


def test_parse_tool_call_handles_multiline_args():
    r = LLMResponse(text='<tool name="create_booking">\n  {\n  "scheduled_for_iso":"2026-05-01T15:00:00+00:00"\n  }\n</tool>')
    parsed = r.parse_tool_call()
    assert parsed is not None
    assert parsed[0] == "create_booking"


def test_parse_tool_call_returns_none_on_bad_json():
    r = LLMResponse(text='<tool name="x">{not json</tool>')
    assert r.parse_tool_call() is None


def test_parse_tool_call_returns_none_on_non_object_args():
    r = LLMResponse(text='<tool name="x">[1,2,3]</tool>')
    assert r.parse_tool_call() is None
