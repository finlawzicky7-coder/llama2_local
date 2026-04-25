from ringback.twilio_signing import compute_signature, verify_signature


# Reference vector — this exact case is documented in Twilio's signature
# validation guide: same auth_token, URL, and params produce the signature
# below. We pin it here to detect any drift in our implementation.
AUTH_TOKEN = "12345"
URL = "https://mycompany.com/myapp.php?foo=1&bar=2"
PARAMS = {
    "CallSid": "CA1234567890ABCDE",
    "Caller": "+14158675309",
    "Digits": "1234",
    "From": "+14158675309",
    "To": "+18005551212",
}
EXPECTED = "RSOYDt4T1cUTdK1PDd93/VVr8B8="


def test_compute_signature_matches_known_vector():
    assert compute_signature(AUTH_TOKEN, URL, PARAMS) == EXPECTED


def test_verify_signature_accepts_valid():
    assert verify_signature(AUTH_TOKEN, URL, PARAMS, EXPECTED) is True


def test_verify_signature_rejects_tampered_param():
    bad = dict(PARAMS, Digits="9999")
    assert verify_signature(AUTH_TOKEN, URL, bad, EXPECTED) is False


def test_verify_signature_rejects_empty_signature():
    assert verify_signature(AUTH_TOKEN, URL, PARAMS, "") is False


def test_verify_signature_rejects_wrong_token():
    assert verify_signature("wrong-token", URL, PARAMS, EXPECTED) is False
