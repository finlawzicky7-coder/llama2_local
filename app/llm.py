"""LLM adapter — provider-agnostic.

`LLMClient.complete()` returns a single assistant message. Tools are
called by name when the model emits `<tool name="…">{json}</tool>` —
we use a tiny tag-style protocol so we don't depend on any specific
provider's function-calling format. The model is instructed in the
system prompt how to emit tool calls.

Two implementations:

- `FakeLLMClient`: scripted responses keyed by step index. Used in
  tests so the runtime is fully exercised without network.
- `HTTPLLMClient`: posts to any OpenAI-compatible chat-completions
  endpoint configured via `LLM_BASE_URL` + `LLM_API_KEY` + `LLM_MODEL`.
  Provider-agnostic, no SDK lock-in.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Optional, Protocol

import httpx


@dataclass
class LLMMessage:
    role: str  # "system" | "user" | "assistant"
    content: str


@dataclass
class LLMResponse:
    text: str

    def parse_tool_call(self) -> Optional[tuple[str, dict]]:
        """Return (tool_name, args) if the response contains a tool call."""
        m = re.search(r'<tool\s+name="([^"]+)">(.*?)</tool>', self.text, re.DOTALL)
        if not m:
            return None
        name = m.group(1)
        try:
            args = json.loads(m.group(2).strip() or "{}")
        except json.JSONDecodeError:
            return None
        if not isinstance(args, dict):
            return None
        return name, args


class LLMClient(Protocol):
    async def complete(self, messages: list[LLMMessage]) -> LLMResponse: ...


class FakeLLMClient:
    """Returns scripted responses in order. Useful in tests."""

    def __init__(self, scripted: list[str]):
        self._scripted = list(scripted)
        self.received: list[list[LLMMessage]] = []

    async def complete(self, messages: list[LLMMessage]) -> LLMResponse:
        self.received.append(list(messages))
        if not self._scripted:
            return LLMResponse(text="")
        return LLMResponse(text=self._scripted.pop(0))


class HTTPLLMClient:
    """OpenAI-compatible chat-completions client."""

    def __init__(self, base_url: str, api_key: str, model: str, timeout: float = 20.0):
        if not base_url or not api_key or not model:
            raise ValueError("base_url, api_key, and model are required")
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._model = model
        self._timeout = timeout

    async def complete(self, messages: list[LLMMessage]) -> LLMResponse:
        body = {
            "model": self._model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "temperature": 0.2,
        }
        headers = {"Authorization": f"Bearer {self._api_key}"}
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            r = await client.post(f"{self._base_url}/chat/completions", json=body, headers=headers)
            r.raise_for_status()
            data = r.json()
        text = data["choices"][0]["message"]["content"]
        return LLMResponse(text=text)
