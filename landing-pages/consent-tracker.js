/* consent-tracker.js
 * Captures the exact consent text + version + IP + UA + Turnstile token + UTM
 * and POSTs to the n8n lead-capture webhook with HMAC signing on the server side.
 *
 * The HMAC secret is NOT embedded here. The browser POSTs to a thin server-side
 * proxy (Cloudflare Worker / Vercel function) which adds the HMAC header, then
 * forwards to n8n. This prevents secret exposure in the page.
 */

(() => {
  const form  = document.getElementById('lead-form');
  const thanks = document.getElementById('thanks');
  if (!form) return;

  // Pre-populate hidden context fields.
  const params = new URLSearchParams(location.search);
  form.querySelector('[name=landing_page_url]').value = location.href;
  form.querySelector('[name=referrer_url]').value     = document.referrer || '';
  for (const k of ['utm_source','utm_medium','utm_campaign','utm_content','utm_term']) {
    const el = form.querySelector(`[name=${k}]`);
    if (el) el.value = params.get(k) || '';
  }

  // Snapshot the exact disclosure text for evidence.
  const tpmoEl     = document.getElementById('tpmo-disclaimer');
  const tpmoText   = tpmoEl ? tpmoEl.innerText.trim() : '';
  const tpmoVersion = tpmoEl ? (tpmoEl.dataset.version || 'unknown') : 'unknown';

  function consentText() {
    // Concatenate every label inside .consent-block — that's what the user agreed to.
    const block = form.querySelector('.consent-block');
    if (!block) return '';
    return Array.from(block.querySelectorAll('label,span,p,legend'))
      .map(el => el.innerText.trim()).filter(Boolean).join('\n');
  }

  function consentedEntities() {
    return Array.from(form.querySelectorAll('input[type=checkbox][data-entity]')).map(el => ({
      name: el.dataset.entity,
      role: 'TPMO',
      accepted: el.checked
    }));
  }

  async function sha256(s) {
    const buf = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(s));
    return Array.from(new Uint8Array(buf)).map(b => b.toString(16).padStart(2, '0')).join('');
  }

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    if (!form.reportValidity()) return;

    // Cloudflare Turnstile token
    const turnstileToken = document.querySelector('[name="cf-turnstile-response"]')?.value;
    if (!turnstileToken) {
      alert('Please complete the human-verification challenge.');
      return;
    }

    const data = Object.fromEntries(new FormData(form).entries());
    const consent_text = consentText();
    const consent_version = tpmoVersion;
    const evidence = JSON.stringify({
      consent_text, consent_version,
      tpmo_disclaimer_text: tpmoText,
      consented_entities: consentedEntities(),
      page_url: location.href,
      submitted_at: new Date().toISOString(),
      ua: navigator.userAgent
    });
    const evidence_hash = await sha256(evidence);

    const payload = {
      first_name: data.first_name,
      last_name: data.last_name,
      phone: data.phone,
      email: data.email,
      zip_code: data.zip_code,
      state: data.state,
      medicare_status: data.medicare_status,
      current_plan_type: data.current_plan_type || null,
      desired_help: data.desired_help || null,
      birth_month: data.birth_month ? Number(data.birth_month) : null,
      birth_year: data.birth_year ? Number(data.birth_year) : null,
      source: data.source,
      campaign_id: data.campaign_id || null,
      landing_page_url: data.landing_page_url,
      referrer_url: data.referrer_url,
      utm_source: data.utm_source,
      utm_medium: data.utm_medium,
      utm_campaign: data.utm_campaign,
      utm_content: data.utm_content,
      utm_term: data.utm_term,

      consent_given: true,
      consent_text,
      consent_version,
      consented_entities: consentedEntities(),
      tpmo_disclaimer_shown: true,
      evidence_hash,

      turnstile_token: turnstileToken
    };

    const submitBtn = form.querySelector('button[type=submit]');
    submitBtn.disabled = true;
    submitBtn.textContent = 'Sending…';

    try {
      const r = await fetch('/api/lead-capture', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(payload),
        credentials: 'omit'
      });
      if (!r.ok) {
        const body = await r.text();
        throw new Error(`Server ${r.status}: ${body.slice(0,200)}`);
      }
      form.hidden = true;
      thanks.hidden = false;
      // Track conversion in your analytics here (no PII).
      if (window.gtag) gtag('event', 'lead_submit', {channel: payload.source});
    } catch (err) {
      console.error(err);
      alert('Something went wrong submitting your request. Please call us at the number in the footer.');
      submitBtn.disabled = false;
      submitBtn.textContent = 'Request my callback';
    }
  });
})();
