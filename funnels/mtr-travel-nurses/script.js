import { insertLead, logEvent } from '../../shared/supabase-client.js';
import { routeLead } from '../../shared/lead-router.js';

const FUNNEL = 'mtr';

function getUTM() {
  const p = new URLSearchParams(location.search);
  return {
    utm_source:   p.get('utm_source')   || null,
    utm_medium:   p.get('utm_medium')   || null,
    utm_campaign: p.get('utm_campaign') || null,
  };
}

async function onSubmit(e) {
  e.preventDefault();
  const form = e.currentTarget;
  const data = Object.fromEntries(new FormData(form).entries());

  // Coerce numeric fields.
  if (data.budget_or_revenue) data.budget_or_revenue = Number(data.budget_or_revenue);

  const { funnel_source, lead_score, upsell_funnel } = routeLead(data, FUNNEL);

  const payload = {
    ...data,
    funnel_source,
    lead_score,
    raw_payload: { upsell_funnel, page: location.pathname },
    ...getUTM(),
  };

  form.querySelector('button[type="submit"]').disabled = true;
  const { ok, lead, error } = await insertLead(payload);

  if (!ok) {
    console.error('[mtr] insert failed', error);
    alert('Something went wrong. Please try again or text (916) 555-0137.');
    form.querySelector('button[type="submit"]').disabled = false;
    return;
  }

  await logEvent(lead.id, FUNNEL, 'form_submit', { lead_score, upsell_funnel });

  form.hidden = true;
  document.getElementById('form-success').hidden = false;
}

document.getElementById('lead-form').addEventListener('submit', onSubmit);

// Fire a "view" event once per session.
if (!sessionStorage.getItem('mtr_view')) {
  sessionStorage.setItem('mtr_view', '1');
  logEvent(null, FUNNEL, 'view', { path: location.pathname, ...getUTM() });
}
