/**
 * Cloudflare Worker — POST /api/lead-capture
 *
 * Sits between the browser form and n8n. Responsibilities:
 *
 *  1. Verify Cloudflare Turnstile token (server-side).
 *  2. Validate basic shape of the payload.
 *  3. Compute HMAC-SHA256 over the raw body with WEBHOOK_HMAC_SECRET.
 *  4. Forward to n8n with the signature header.
 *  5. Strip the secret from any response surface.
 *
 * Bind these as Worker secrets:
 *   - TURNSTILE_SECRET           (from Cloudflare dashboard)
 *   - WEBHOOK_HMAC_SECRET        (must match n8n env var)
 *   - N8N_LEAD_CAPTURE_URL       (e.g. https://n8n.your-agency.com/webhook/medicare-lead-capture)
 */

export interface Env {
  TURNSTILE_SECRET: string;
  WEBHOOK_HMAC_SECRET: string;
  N8N_LEAD_CAPTURE_URL: string;
}

const REQUIRED_FIELDS = [
  'first_name','last_name','phone','email','zip_code','state',
  'medicare_status','source','consent_given','consent_text',
  'consent_version','tpmo_disclaimer_shown','consented_entities',
  'turnstile_token'
];

async function verifyTurnstile(token: string, ip: string, secret: string): Promise<boolean> {
  const body = new FormData();
  body.append('secret', secret);
  body.append('response', token);
  if (ip) body.append('remoteip', ip);
  const r = await fetch('https://challenges.cloudflare.com/turnstile/v0/siteverify', {
    method: 'POST', body
  });
  const json = await r.json() as { success: boolean };
  return json.success === true;
}

async function hmacSha256Hex(secret: string, message: string): Promise<string> {
  const enc = new TextEncoder();
  const key = await crypto.subtle.importKey(
    'raw', enc.encode(secret),
    { name: 'HMAC', hash: 'SHA-256' }, false, ['sign']
  );
  const sig = await crypto.subtle.sign('HMAC', key, enc.encode(message));
  return Array.from(new Uint8Array(sig)).map(b => b.toString(16).padStart(2, '0')).join('');
}

function jsonResponse(status: number, body: object): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'content-type': 'application/json', 'x-content-type-options': 'nosniff' }
  });
}

export default {
  async fetch(req: Request, env: Env): Promise<Response> {
    if (req.method !== 'POST') return jsonResponse(405, { error: 'method_not_allowed' });

    // Capture raw text exactly as we'll forward it — HMAC must match what n8n recomputes.
    const raw = await req.text();
    let payload: any;
    try { payload = JSON.parse(raw); } catch { return jsonResponse(400, { error: 'invalid_json' }); }

    for (const k of REQUIRED_FIELDS) {
      if (payload[k] === undefined || payload[k] === null || payload[k] === '') {
        return jsonResponse(400, { error: 'missing_field', field: k });
      }
    }
    if (payload.consent_given !== true) return jsonResponse(400, { error: 'consent_not_given' });
    if (payload.tpmo_disclaimer_shown !== true) return jsonResponse(400, { error: 'tpmo_not_shown' });

    const ip = req.headers.get('cf-connecting-ip') || '';
    const ok = await verifyTurnstile(payload.turnstile_token, ip, env.TURNSTILE_SECRET);
    if (!ok) return jsonResponse(403, { error: 'turnstile_failed' });

    // Rebuild the body without the turnstile token before forwarding (n8n doesn't need it).
    const fwd = { ...payload };
    delete fwd.turnstile_token;
    const fwdRaw = JSON.stringify(fwd);

    const signature = await hmacSha256Hex(env.WEBHOOK_HMAC_SECRET, fwdRaw);

    const upstream = await fetch(env.N8N_LEAD_CAPTURE_URL, {
      method: 'POST',
      headers: {
        'content-type': 'application/json',
        'x-signature': signature,
        // Pass through real IP + UA so workflow 01 captures them in consent_logs.
        'cf-connecting-ip': ip,
        'user-agent': req.headers.get('user-agent') || ''
      },
      body: fwdRaw
    });

    // Don't leak upstream errors to the browser; respond shape is stable.
    if (!upstream.ok) {
      console.error('upstream_error', upstream.status, await upstream.text());
      return jsonResponse(502, { error: 'upstream_unavailable' });
    }

    return jsonResponse(200, { status: 'received' });
  }
} satisfies ExportedHandler<Env>;
