// Tiny browser-side Supabase insert helper. No dependency on the Supabase JS
// SDK — just fetch + the REST endpoint. Keeps landing pages zero-build.
//
// Usage:
//   import { insertLead, logEvent } from '/shared/supabase-client.js';
//   await insertLead({ ...formData, funnel_source: 'mtr' });

const SUPABASE_URL  = window.__SUPABASE_URL__  || '';
const SUPABASE_ANON = window.__SUPABASE_ANON__ || '';

function endpoint(table) {
  return `${SUPABASE_URL}/rest/v1/${table}`;
}

function headers() {
  return {
    'Content-Type': 'application/json',
    'apikey':        SUPABASE_ANON,
    'Authorization': `Bearer ${SUPABASE_ANON}`,
    'Prefer':        'return=representation',
  };
}

export async function insertLead(lead) {
  if (!SUPABASE_URL || !SUPABASE_ANON) {
    console.warn('[supabase] missing config; lead not persisted', lead);
    return { ok: false, error: 'missing_config' };
  }

  const res = await fetch(endpoint('leads'), {
    method: 'POST',
    headers: headers(),
    body: JSON.stringify(lead),
  });

  if (!res.ok) {
    const error = await res.text();
    return { ok: false, error };
  }
  const [row] = await res.json();
  return { ok: true, lead: row };
}

export async function logEvent(leadId, funnelSource, eventType, payload) {
  if (!SUPABASE_URL || !SUPABASE_ANON) return;
  await fetch(endpoint('funnel_events'), {
    method: 'POST',
    headers: headers(),
    body: JSON.stringify({
      lead_id: leadId,
      funnel_source: funnelSource,
      event_type: eventType,
      payload,
    }),
  }).catch(() => {});
}
