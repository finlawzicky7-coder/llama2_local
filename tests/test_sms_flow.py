def test_sms_stop_keyword_returns_optout_message(client, bundle):
    r = client.post(
        "/sms/incoming",
        data={"From": "+14155551212", "To": "+18005551212", "Body": "STOP", "MessageSid": "SM1"},
    )
    assert r.status_code == 200
    assert "Acme HVAC" in r.text
    assert "won't receive" in r.text or "STOP" in r.text


def test_sms_help_keyword_returns_help(client, bundle):
    r = client.post(
        "/sms/incoming",
        data={"From": "+14155551212", "To": "+18005551212", "Body": "HELP", "MessageSid": "SM2"},
    )
    assert r.status_code == 200
    assert "STOP" in r.text


def test_sms_unconfigured_number(client, bundle):
    r = client.post(
        "/sms/incoming",
        data={"From": "+14155551212", "To": "+18885559999", "Body": "hi", "MessageSid": "SM3"},
    )
    assert r.status_code == 200
    assert "not configured" in r.text


def test_sms_drives_runtime(client, bundle):
    from app.llm import FakeLLMClient
    bundle.llm = FakeLLMClient(scripted=["What's the address and the issue?"])

    r = client.post(
        "/sms/incoming",
        data={"From": "+14155551212", "To": "+18005551212", "Body": "Hi this is Mike", "MessageSid": "SM4"},
    )
    assert r.status_code == 200
    assert "<Message>" in r.text
    assert "address" in r.text.lower()
