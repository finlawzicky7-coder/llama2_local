from ringback.emergency import is_emergency


def test_universal_911_triggers():
    assert is_emergency("call 911 right now") is True


def test_gas_leak_triggers():
    assert is_emergency("I think we have a gas leak in the basement") is True


def test_normal_request_does_not_trigger():
    assert is_emergency("the AC is making a weird noise") is False


def test_tenant_keywords_trigger():
    assert is_emergency("the heat is out in the nursery", ["heat is out"]) is True


def test_short_keyword_uses_word_boundary():
    # "no" is dangerous as a substring; we use word-boundary matching so that
    # "nothing" / "annoying" don't trip a tenant keyword of "no".
    assert is_emergency("there is no service to my unit", ["no"]) is True
    assert is_emergency("nothing is wrong, just a checkup", ["no"]) is False
    assert is_emergency("the thermostat is annoying", ["no"]) is False


def test_empty_utterance_is_not_emergency():
    assert is_emergency("") is False
    assert is_emergency("", ["fire"]) is False


def test_case_insensitive():
    assert is_emergency("FIRE in the kitchen") is True
