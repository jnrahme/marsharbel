(async function () {
  'use strict';
  const { client, config, configured, status, captcha } = window.Testimony;
  const form = document.getElementById('testimony-form');
  const message = document.getElementById('submit-status');
  const submit = document.getElementById('submit-testimony-btn');
  const availability = document.getElementById('submission-availability');
  const verification = document.getElementById('turnstile-slot');
  let challenge; let sending = false;
  const updateSubmit = () => {
    const name = form.elements.namedItem('display_name').value.trim();
    const story = form.elements.namedItem('story').value.trim();
    submit.disabled = !configured || !config.submissionsEnabled || sending || !challenge?.token() || !form.checkValidity() || name.length < 2 || story.length < 60;
  };
  form.addEventListener('input', updateSubmit);
  form.addEventListener('change', updateSubmit);
  verification.addEventListener('verificationchange', updateSubmit);
  form.addEventListener('submit', e => e.preventDefault());
  message.tabIndex = -1;
  submit.disabled = true;
  if (!configured || !config.submissionsEnabled) {
    availability.hidden = false;
    availability.textContent = 'Submissions are temporarily closed. This form cannot send your story yet.';
    status(message, 'Submissions are safely paused. Your story has not been sent.');
    if (config.submissionCaptchaProvider === 'hcaptcha' ? config.hcaptchaSiteKey : config.turnstileSiteKey) {
      try { await captcha(verification, 'submit_testimony'); }
      catch { verification.textContent = 'Human verification could not load. Reload this page or open it in Chrome.'; }
    } else verification.textContent = 'Human verification is not configured yet.';
    return;
  }
  try {
    challenge = await captcha(verification, 'submit_testimony');
    updateSubmit();
  } catch {
    status(message, 'Human verification could not load. Reload this page and try again.', true);
    return;
  }
  form.addEventListener('submit', async () => {
    if (sending || !form.reportValidity()) return;
    if (!challenge.token()) {
      status(message, 'Complete human verification above before submitting.', true);
      message.focus(); return;
    }
    const fd = new FormData(form);
    const payload = { display_name: fd.get('display_name').trim(), story: fd.get('story').trim(), country: fd.get('country').trim(), language: fd.get('language'), event_date: fd.get('event_date'), age_attested: fd.has('age_confirmed'), consent_publish: fd.has('consent_publish'), ai_consent: fd.has('ai_consent'), website: fd.get('website') };
    sending = true; submit.disabled = true; submit.textContent = 'Submitting…';
    try {
      const response = await fetch(`${config.supabaseUrl}/functions/v1/submit-testimony`, {
        method: 'POST', headers: { 'Content-Type':'application/json', apikey:config.supabaseAnonKey },
        body: JSON.stringify({ ...payload, turnstile_token:challenge.token() }), signal:AbortSignal.timeout(20000)
      });
      const result = await response.json();
      if (!response.ok) throw new Error(result.message || 'Submission unavailable. Please try again later.');
      if (result.accepted !== true || !result.reference) throw new Error('Submission could not be confirmed. Keep your text and try again later.');
      form.reset();
      status(message, `Testimony submitted. Your story is private and pending review. Save this reference: ${result.reference}`);
    } catch (error) {
      status(message, error.name === 'TimeoutError' ? 'The request timed out. Your text is still here. Please wait before retrying to avoid duplicate submissions.' : error.message, true);
    } finally {
      challenge.reset(); sending = false; updateSubmit(); submit.textContent = 'Submit testimony'; message.focus();
    }
  });
})();
