from datetime import datetime, timezone, timedelta

import pytest

from ringback.booking import BookingRequest, booking_key


def _req(**overrides):
    base = dict(
        tenant_id="11111111-1111-1111-1111-111111111111",
        customer_phone_e164="+14155551212",
        job_type_label="HVAC service",
        scheduled_for=datetime(2026, 5, 1, 14, 0, tzinfo=timezone.utc),
    )
    base.update(overrides)
    return BookingRequest(**base)


def test_booking_key_is_stable_for_same_inputs():
    a = booking_key(_req())
    b = booking_key(_req())
    assert a == b
    assert a.startswith("bk_")


def test_booking_key_differs_for_different_phone():
    a = booking_key(_req())
    b = booking_key(_req(customer_phone_e164="+14155551213"))
    assert a != b


def test_booking_key_normalizes_to_minute():
    a = booking_key(_req(scheduled_for=datetime(2026, 5, 1, 14, 0, 0, tzinfo=timezone.utc)))
    b = booking_key(_req(scheduled_for=datetime(2026, 5, 1, 14, 0, 59, tzinfo=timezone.utc)))
    assert a == b


def test_booking_key_normalizes_timezone():
    utc_time = datetime(2026, 5, 1, 14, 0, tzinfo=timezone.utc)
    plus_4 = datetime(2026, 5, 1, 18, 0, tzinfo=timezone(timedelta(hours=4)))
    assert booking_key(_req(scheduled_for=utc_time)) == booking_key(_req(scheduled_for=plus_4))


def test_naive_datetime_rejected():
    with pytest.raises(ValueError):
        _req(scheduled_for=datetime(2026, 5, 1, 14, 0))


def test_invalid_phone_rejected():
    with pytest.raises(ValueError):
        _req(customer_phone_e164="4155551212")  # missing leading +


def test_empty_tenant_rejected():
    with pytest.raises(ValueError):
        _req(tenant_id="")
