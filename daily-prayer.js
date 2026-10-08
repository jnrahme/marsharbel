(async function () {
  'use strict';
  const testimony = window.Testimony || {};
  const { config, configured, captcha } = testimony;
  // If the client script never executed (stub-served by the edge challenge), keep the
  // paused path working with a local status helper instead of crashing.
  const status = testimony.status || ((el, text, error = false) => { el.textContent = text; el.className = `submit-status ${error ? 'warn' : ''}`; });
  const form = document.getElementById('subscribe-form');
  const message = document.getElementById('submit-status');
  const submit = document.getElementById('subscribe-btn');
  const availability = document.getElementById('subscribe-availability');
  const verification = document.getElementById('turnstile-slot');
  const readiness = document.getElementById('submit-readiness');
  const touched = new Set();
  const field = name => form.elements.namedItem(name);

  let challenge; let sending = false; let submitted = false;
  const issues = () => {
    const problems = [];
    const email = field('email').value.trim();
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email)) problems.push(['email', 'Enter a valid email address.']);
    if (!challenge?.token()) problems.push(['captcha', 'Complete human verification: check “I am human”.']);
    return problems;
  };
  const updateSubmit = () => {
    const problems = issues();
    submit.disabled = !configured || sending || problems.length > 0 || !form.checkValidity();
    const error = document.getElementById('email-error');
    const problem = problems.find(([key]) => key === 'email');
    const show = touched.has('email') && Boolean(problem);
    error.hidden = !show;
    error.textContent = show ? problem[1] : '';
    field('email').setAttribute('aria-invalid', String(!submitted && problems.some(([key]) => key === 'email')));
    verification.closest('.human-verification').classList.toggle('field-missing', !submitted && problems.some(([key]) => key === 'captcha'));
    readiness.replaceChildren();
    if (!configured || submitted) return;
    if (sending) { readiness.textContent = 'Subscribing you. Please wait…'; return; }
    if (!problems.length) { readiness.textContent = 'Everything is complete. You can subscribe.'; return; }
    const title = document.createElement('p'); title.textContent = 'Before you can subscribe:';
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
  if (!configured) {
    availability.hidden = false;
    availability.textContent = 'Subscriptions are temporarily paused. This form cannot subscribe you yet.';
    status(message, 'Subscriptions are safely paused. You have not been subscribed.', true);
    return;
  }
  try {
    challenge = await captcha(verification, 'subscribe_prayer');
    updateSubmit();
  } catch {
    status(message, 'Human verification could not load. Reload this page and try again.', true);
    return;
  }
  form.addEventListener('submit', async () => {
    if (sending) return;
    const problems = issues();
    if (problems.length || !form.checkValidity()) {
      touched.add('email'); updateSubmit();
      status(message, problems.map(([, text]) => text).join(' ') || 'Check the highlighted fields before subscribing.', true);
      const first = problems.find(([key]) => key !== 'captcha');
      if (first) field(first[0]).focus(); else message.focus();
      return;
    }
    sending = true; updateSubmit(); submit.textContent = 'Subscribing…';
    status(message, 'Subscribing you. Please wait…');
    try {
      const response = await fetch(`${config.supabaseUrl}/functions/v1/subscribe-prayer`, {
        method: 'POST', headers: { 'Content-Type':'application/json', apikey:config.supabaseAnonKey },
        body: JSON.stringify({ email: field('email').value.trim(), locale: 'en', website: field('website').value, turnstile_token: challenge.token() }),
        signal: AbortSignal.timeout(20000)
      });
      const result = await response.json().catch(() => null);
      if (!response.ok && response.status !== 202) {
        const fallback = response.status === 429 ? 'Limit reached. Please wait a few minutes and try again.' : response.status === 403 ? 'Human verification failed or expired. Please complete it again.' : 'The subscription service is temporarily unavailable. Please try again later.';
        throw new Error(response.status >= 500 ? fallback : result?.message || fallback);
      }
      if (result?.accepted !== true) throw new Error('Subscribing could not be confirmed. Please try again later.');
      submitted = true; touched.clear(); form.reset();
      status(message, 'Almost there - check your inbox and tap the confirmation link to start receiving the daily prayer. If you already subscribed, there is nothing new to do.');
    } catch (error) {
      status(message, error.name === 'TimeoutError' ? 'The request timed out. Please wait before retrying to avoid a duplicate attempt.' : error instanceof TypeError ? 'We could not connect to the subscription service. Check your connection and try again.' : error.message, true);
    } finally {
      challenge.reset(); sending = false; updateSubmit(); submit.textContent = 'Send me the daily prayer'; message.focus();
    }
  });
})();
