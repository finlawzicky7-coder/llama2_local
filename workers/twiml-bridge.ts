/**
 * Cloudflare Worker — GET/POST /twiml/medicare-bridge
 *
 * Twilio fetches this URL when an outbound call connects. We:
 *   1. Look up the agent's phone by agent_id (passed as ?agent_id=...).
 *   2. Return TwiML that:
 *      a. Plays the TPMO disclaimer + recording notice via <Say>.
 *      b. Bridges to the agent with dual-channel recording.
 *
 * Bind these as Worker secrets:
 *   - SUPABASE_URL
 *   - SUPABASE_SERVICE_ROLE_KEY
 *   - TWILIO_FROM_NUMBER
 *   - N8N_RECORDING_WEBHOOK_URL  (e.g. https://n8n.your-agency.com/webhook/twilio-recording)
 *   - AGENCY_NAME
 *   - N_CARRIERS                  (string number, e.g. "8")
 *   - N_PLANS                     (string number, e.g. "32")
 */

export interface Env {
  SUPABASE_URL: string;
  SUPABASE_SERVICE_ROLE_KEY: string;
  TWILIO_FROM_NUMBER: string;
  N8N_RECORDING_WEBHOOK_URL: string;
  AGENCY_NAME: string;
  N_CARRIERS: string;
  N_PLANS: string;
}

function xmlEscape(s: string): string {
  return s.replace(/[&<>"']/g, c => ({ '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&apos;' }[c]!));
}

async function fetchAgentPhone(env: Env, agentId: string): Promise<string | null> {
  const url = `${env.SUPABASE_URL}/rest/v1/agents?id=eq.${encodeURIComponent(agentId)}&active=eq.true&select=phone`;
  const r = await fetch(url, {
    headers: {
      apikey: env.SUPABASE_SERVICE_ROLE_KEY,
      authorization: `Bearer ${env.SUPABASE_SERVICE_ROLE_KEY}`,
    }
  });
  if (!r.ok) return null;
  const rows = await r.json() as Array<{ phone: string }>;
  return rows[0]?.phone ?? null;
}

export default {
  async fetch(req: Request, env: Env): Promise<Response> {
    const url = new URL(req.url);
    const agentId = url.searchParams.get('agent_id');
    if (!agentId) {
      return new Response('<Response><Say>Missing agent identifier. Goodbye.</Say><Hangup/></Response>', {
        status: 200,
        headers: { 'content-type': 'application/xml' }
      });
    }

    const agentPhone = await fetchAgentPhone(env, agentId);
    if (!agentPhone) {
      return new Response('<Response><Say>We are unable to connect you to a licensed agent right now. We will follow up shortly. Goodbye.</Say><Hangup/></Response>', {
        status: 200,
        headers: { 'content-type': 'application/xml' }
      });
    }

    const agency = xmlEscape(env.AGENCY_NAME);
    const nCarriers = xmlEscape(env.N_CARRIERS);
    const nPlans = xmlEscape(env.N_PLANS);

    const tpmo =
      `Please hold while we connect you with your licensed Medicare agent at ${agency}. ` +
      `We are not Medicare, the federal government, or a Medicare dot gov representative. ` +
      `We do not offer every plan available in your area. Currently we represent ${nCarriers} organizations ` +
      `which offer ${nPlans} products in your area. Please contact Medicare dot gov, 1 800 Medicare, ` +
      `or your local State Health Insurance Assistance Program for all of your options. ` +
      `This call will be recorded for quality and compliance.`;

    const xml = `<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Say voice="Polly.Joanna">${xmlEscape(tpmo)}</Say>
  <Pause length="1"/>
  <Dial record="record-from-answer-dual"
        recordingStatusCallback="${xmlEscape(env.N8N_RECORDING_WEBHOOK_URL)}"
        recordingStatusCallbackEvent="completed"
        recordingChannels="dual"
        callerId="${xmlEscape(env.TWILIO_FROM_NUMBER)}"
        timeLimit="3600"
        answerOnBridge="true">
    <Number>${xmlEscape(agentPhone)}</Number>
  </Dial>
</Response>`;

    return new Response(xml, {
      status: 200,
      headers: { 'content-type': 'application/xml' }
    });
  }
} satisfies ExportedHandler<Env>;
