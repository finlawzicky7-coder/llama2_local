# Sales Scripts

| File | Use |
|---|---|
| `scripts/first-call.md` | Speed-to-lead first conversation, end to end |
| `scripts/voicemail.md` | Three voicemail variants (V1/V2/V3) |
| `scripts/sms-cadence.md` | 6-step SMS cadence + reply handling |
| `scripts/email-cadence.md` | 6 email templates (referenced from workflow 07) |
| `scripts/objections.md` | Top 10 objections with compliant responses |
| `scripts/appointment-setting.md` | When and how to ask for the appointment + SOA |
| `scripts/no-show-recovery.md` | Day-0 through day-7 recovery cadence |
| `scripts/aep-followup.md` | AEP-specific cadence + pre/post-AEP |
| `scripts/t65-birthday.md` | T65/IEP-aligned cadence year-round |

## Versioning

Scripts are part of compliance. Treat them like code:

- Each file carries no inline version — instead, the **commit hash** is the version.
- Compliance officer signs off on every PR that modifies any file in `sales/scripts/`.
- The agent training program references the file paths; each new version triggers a retraining requirement.
- Production CRM links to `sales/scripts/<filename>.md` so agents always see the live, reviewed version.

## Training pre-flight (must be signed off before an agent goes live)

- [ ] Read all 9 files end to end.
- [ ] Mock first-call with a peer; recording reviewed by team lead.
- [ ] Compliance quiz: TPMO disclaimer wording, opt-out triggers, prohibited claims, SOA timing.
- [ ] State licenses verified and entered in `agent_licenses`.
- [ ] Carrier appointments verified and entered in `agent_carrier_appointments`.
- [ ] Recording review on first 5 live calls before solo dialing.
