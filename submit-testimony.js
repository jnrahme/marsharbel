(async function () {
  'use strict';
  const { config, configured, status, captcha } = window.Testimony;
  const form = document.getElementById('testimony-form');
  const message = document.getElementById('submit-status');
  const submit = document.getElementById('submit-testimony-btn');
  const availability = document.getElementById('submission-availability');
  const verification = document.getElementById('turnstile-slot');
  const readiness = document.getElementById('submit-readiness');
  const touched = new Set();
  const field = name => form.elements.namedItem(name);
  let challenge; let sending = false; let submitted = false;
  const issues = () => {
    const problems = [];
    const nameLength = field('display_name').value.trim().length;
    const storyLength = field('story').value.trim().length;
    if (nameLength < 2 || nameLength > 80) problems.push(['display_name', 'Enter a display name with 2–80 characters (at least 2).']);
    if (storyLength < 60 || storyLength > 7000) problems.push(['story', `Write 60–7,000 characters for your story (${storyLength} entered).`]);
    const date = field('event_date');
    if (date.validity.badInput || (date.value && date.value > new Date().toISOString().slice(0, 10))) problems.push(['event_date', 'Choose an event date that is today or earlier.']);
    if (!field('country').checkValidity()) problems.push(['country', 'Keep the country name to 100 characters or fewer.']);
    if (!field('age_confirmed').checked) problems.push(['age_confirmed', 'Confirm that you are 18 or older.']);
    if (!field('consent_publish').checked) problems.push(['consent_publish', 'Confirm your permission and consent to publication.']);
    if (!field('ai_consent').checked) problems.push(['ai_consent', 'Confirm that you understand the screening notice.']);
    if (!challenge?.token()) problems.push(['captcha', 'Complete human verification: check “I am human”.']);
    return problems;
  };
  const updateSubmit = () => {
    const problems = issues();
    submit.disabled = !configured || !config.submissionsEnabled || sending || problems.length > 0 || !form.checkValidity();
    for (const [name, errorId] of [['display_name', 'name-error'], ['story', 'story-error']]) {
      const error = document.getElementById(errorId);
      const problem = problems.find(([key]) => key === name);
      const show = touched.has(name) && Boolean(problem);
      error.hidden = !show;
      error.textContent = show ? problem[1] : '';
      field(name).setAttribute('aria-invalid', String(show));
    }
    readiness.replaceChildren();
    if (!configured || !config.submissionsEnabled || submitted) return;
    if (sending) { readiness.textContent = 'Sending your testimony. Please wait…'; return; }
    if (!problems.length) { readiness.textContent = 'Everything is complete. You can submit your testimony.'; return; }
    const title = document.createElement('p'); title.textContent = 'Before you can submit:';
    const list = document.createElement('ul');
    for (const [, text] of problems) { const item = document.createElement('li'); item.textContent = text; list.append(item); }
    readiness.append(title, list);
  };
  form.addEventListener('input', event => { touched.add(event.target.name); submitted = false; updateSubmit(); });
  form.addEventListener('change', event => { touched.add(event.target.name); submitted = false; updateSubmit(); });
  form.addEventListener('focusout', event => { touched.add(event.target.name); updateSubmit(); });
  verification.addEventListener('verificationchange', updateSubmit);
  updateSubmit();
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
    if (sending) return;
    const problems = issues();
    if (problems.length || !form.checkValidity()) {
      touched.add('display_name'); touched.add('story'); updateSubmit();
      status(message, problems.map(([, text]) => text).join(' ') || 'Check the highlighted fields before submitting.', true);
      const first = problems.find(([key]) => key !== 'captcha');
      if (first) field(first[0]).focus(); else message.focus();
      return;
    }
    const fd = new FormData(form);
    const payload = { display_name: fd.get('display_name').trim(), story: fd.get('story').trim(), country: fd.get('country').trim(), language: fd.get('language'), event_date: fd.get('event_date'), age_attested: fd.has('age_confirmed'), consent_publish: fd.has('consent_publish'), ai_consent: fd.has('ai_consent'), website: fd.get('website') };
    sending = true; updateSubmit(); submit.textContent = 'Submitting…';
    status(message, 'Sending your testimony. Please wait…');
    try {
      const response = await fetch(`${config.supabaseUrl}/functions/v1/submit-testimony`, {
        method: 'POST', headers: { 'Content-Type':'application/json', apikey:config.supabaseAnonKey },
        body: JSON.stringify({ ...payload, turnstile_token:challenge.token() }), signal:AbortSignal.timeout(20000)
      });
      const result = await response.json().catch(() => null);
      if (!response.ok) {
        const fallback = response.status === 429 ? 'Submission limit reached. Please wait and try again later.' : response.status === 403 ? 'Human verification failed or expired. Please complete it again.' : 'The submission service is temporarily unavailable. Your text is still here. Please try again later.';
        throw new Error(response.status >= 500 ? fallback : result?.message || fallback);
      }
      if (result?.accepted !== true || !result.reference) throw new Error('Submission could not be confirmed. Keep your text and try again later.');
      submitted = true; touched.clear(); form.reset();
      status(message, `Testimony submitted. Your story is private and pending review. Save this reference: ${result.reference}`);
    } catch (error) {
      status(message, error.name === 'TimeoutError' ? 'The request timed out. Your text is still here. Please wait before retrying to avoid duplicate submissions.' : error instanceof TypeError ? 'We could not connect to the submission service. Your text is still here. Check your connection and try again.' : error.message, true);
    } finally {
      challenge.reset(); sending = false; updateSubmit(); submit.textContent = 'Submit testimony'; message.focus();
    }
  });
})();
