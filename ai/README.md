# AI Prompts

| File | Purpose | Where used |
|---|---|---|
| `prompts/qualification-agent.md` | Form-time qualification & intake | n8n workflow 03 (`AI_QUAL_SYSTEM_PROMPT` env var) |
| `prompts/inbound-chat-agent.md` | Live web-chat widget on landing pages | Chat widget proxy → n8n |
| `prompts/voice-agent.md` | Real-time voice for callback confirmation only | Vapi/Retell/LiveKit Agent + Twilio bridge |
| `prompts/summarization-agent.md` | Post-call structured summary | Workflow that runs on `recording_uploaded` event |
| `prompts/compliance-auditor.md` | Nightly audit over calls + creative | Cron-triggered companion to workflow 10 |
| `prompts/intent-scorer.md` | Lightweight intent score fallback | Workflow 04 supplement |

## Versioning

- Prompts are versioned `<purpose>-vN`. **Never** edit a published version in place — copy the file, bump the version, update the `prompt_version` written into `ai_qualification_sessions`.
- Compliance reviews and signs off on every new version before it goes to prod.
- Maintain an N-1 rollback ready in env vars for instant revert.

## Model defaults

- Qualification + chat: GPT-4.1-mini (cheap, fast, tool-use-capable). Or Claude Haiku 4.5 if you prefer Anthropic.
- Summarization + audit: GPT-4.1 (or Claude Sonnet 4.6) for higher recall on subtle compliance flags.
- Voice: Vapi/Retell with their default voice models; the system prompt above is provider-agnostic.

## Determinism settings

- Always set `temperature: 0` for qualification and audit.
- Always set `response_format: {type: "json_object"}` (OpenAI) or extract JSON via tool-use (Anthropic).
- Cap `max_tokens` to ~600 for qualification, ~1500 for summarization, ~3000 for audit.
