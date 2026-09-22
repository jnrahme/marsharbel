(async function () {
  'use strict';
  const { client, config, configured, node, status, captcha } = window.Testimony;
  const form = document.getElementById('testimony-form'); const message = document.getElementById('submit-status');
  const submit = document.getElementById('submit-testimony-btn'); const preview = document.getElementById('testimony-preview');
  const confirm = document.getElementById('confirm-testimony'); let challenge; let payload; let sending = false;
  submit.disabled = true;
  if (!configured || !config.submissionsEnabled) { status(message, 'Submissions are safely paused while the protected intake service is configured.'); return; }
  try {
    const { data: { session } } = await client.auth.getSession();
    if (!session?.user?.email_confirmed_at) { status(message, 'Sign in with a verified email address before submitting. Use Your account above.'); return; }
    challenge = await captcha(document.getElementById('turnstile-slot'), 'submit_testimony'); submit.disabled = false;
  } catch { status(message, 'Human verification could not load. Please reload and try again.', true); return; }
  form.addEventListener('submit', e => {
    e.preventDefault(); if (!form.reportValidity()) return;
    const fd = new FormData(form);
    payload = { display_name: fd.get('display_name').trim(), story: fd.get('story').trim(), country: fd.get('country').trim(), language: fd.get('language'), event_date: fd.get('event_date'), age_attested: fd.has('age_confirmed'), consent_publish: fd.has('consent_publish'), ai_consent: fd.has('ai_consent'), website: fd.get('website') };
    const content = document.getElementById('preview-content');
    content.replaceChildren(node('p', 'Reader-submitted testimony — reviewed for publication', 'kicker'), node('h3', payload.display_name), node('p', [payload.country, payload.event_date].filter(Boolean).join(' · ')), node('p', payload.story, 'testimony-text'));
    preview.hidden = false; form.hidden = true; confirm.focus();
  });
  document.getElementById('edit-preview').addEventListener('click', () => { if (sending) return; preview.hidden = true; form.hidden = false; submit.focus(); });
  confirm.addEventListener('click', async () => {
    if (sending || !payload) return;
    if (!challenge.token()) { preview.hidden = true; form.hidden = false; return status(message, 'Human verification expired. Complete it and preview again.', true); }
    sending = true; confirm.disabled = true;
    try {
      const { data: { session } } = await client.auth.getSession();
      if (!session) throw new Error('Your session expired. Sign in again.');
      const response = await fetch(`${config.supabaseUrl}/functions/v1/submit-testimony`, { method: 'POST', headers: { 'Content-Type':'application/json', apikey:config.supabaseAnonKey, Authorization:`Bearer ${session.access_token}` }, body: JSON.stringify({ ...payload, turnstile_token:challenge.token() }), signal:AbortSignal.timeout(20000) });
      const result = await response.json(); if (!response.ok) throw new Error(result.message || 'Submission unavailable.');
      form.reset(); preview.hidden = true; form.hidden = false; payload = null;
      status(message, 'Your story is private and pending review. Follow its status in Your account.');
      message.focus();
    } catch (error) { status(message, error.name === 'TimeoutError' ? 'The request timed out. Check Your account before retrying.' : error.message, true); preview.hidden = true; form.hidden = false; }
    finally { challenge.reset(); sending = false; confirm.disabled = false; }
  });
})();
