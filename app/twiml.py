"""TwiML helpers for voice responses."""

from __future__ import annotations

from xml.sax.saxutils import escape


def voice_say_and_gather(action_url: str, say_text: str, timeout: int = 6) -> str:
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Gather input="speech" action="{escape(action_url)}" method="POST" speechTimeout="auto" timeout="{timeout}">
    <Say>{escape(say_text)}</Say>
  </Gather>
  <Say>I didn't catch that. We'll text you to follow up.</Say>
</Response>
"""


def voice_say_and_hangup(say_text: str) -> str:
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Say>{escape(say_text)}</Say>
  <Hangup/>
</Response>
"""


def voice_dial(number_e164: str, say_text: str) -> str:
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Say>{escape(say_text)}</Say>
  <Dial>{escape(number_e164)}</Dial>
</Response>
"""


def sms_message(body: str) -> str:
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Message>{escape(body)}</Message>
</Response>
"""
