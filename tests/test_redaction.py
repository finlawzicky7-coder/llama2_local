from ringback.redaction import redact


def test_redacts_phone_and_email():
    out = redact({"phone": "+14155551212", "email": "owner@example.com", "id": "abc"})
    assert out["phone"].startswith("sha256:")
    assert out["email"].startswith("sha256:")
    assert out["id"] == "abc"


def test_same_value_redacts_to_same_token():
    a = redact({"from_e164": "+14155551212"})["from_e164"]
    b = redact({"from_e164": "+14155551212"})["from_e164"]
    assert a == b


def test_different_values_redact_to_different_tokens():
    a = redact({"phone": "+14155551212"})["phone"]
    b = redact({"phone": "+14155551213"})["phone"]
    assert a != b


def test_recurses_into_nested():
    out = redact({"call": {"from_e164": "+14155551212", "duration": 90}})
    assert out["call"]["from_e164"].startswith("sha256:")
    assert out["call"]["duration"] == 90


def test_handles_lists_of_dicts():
    out = redact({"events": [{"name": "Alice"}, {"name": "Bob"}]})
    assert all(item["name"].startswith("sha256:") for item in out["events"])


def test_passes_unknown_keys_through():
    payload = {"booking_id": "uuid-here", "status": "booked"}
    assert redact(payload) == payload
