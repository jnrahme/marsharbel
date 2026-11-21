(async function () {
  'use strict';
  const { config, configured, status, captcha } = window.Testimony;
  const form = document.getElementById('feedback-form');
  const message = document.getElementById('submit-status');
  const submit = document.getElementById('send-feedback-btn');
  const availability = document.getElementById('feedback-availability');
  const verification = document.getElementById('turnstile-slot');
  const readiness = document.getElementById('submit-readiness');
  const touched = new Set();
  const field = name => form.elements.namedItem(name);
  try {
    const url = new URL(window.location.href);
    const ref = document.referrer && new URL(document.referrer).hostname.endsWith('marsharbel.com') ? document.referrer : '';
    field('page_url').value = url.searchParams.get('page') || ref.slice(0, 300);
  } catch { field('page_url').value = ''; }

  let challenge; let sending = false; let submitted = false;
  const issues = () => {
    const problems = [];
    const messageLength = field('message').value.trim().length;
    if (messageLength < 10 || messageLength > 2000) problems.push(['message', `Write 10–2,000 characters for your message (${messageLength} entered).`]);
    const email = field('email').value.trim();
    if (email && !/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email)) problems.push(['email', 'Check the email address, or leave it empty.']);
    if (field('display_name').value.trim().length > 80) problems.push(['display_name', 'Keep the name to 80 characters or fewer.']);
    if (!challenge?.token()) problems.push(['captcha', 'Complete human verification: check “I am human”.']);
    return problems;
  };
  const updateSubmit = () => {
    const problems = issues();
    submit.disabled = !configured || !config.submissionsEnabled || sending || problems.length > 0 || !form.checkValidity();
    const error = document.getElementById('message-error');
    const problem = problems.find(([key]) => key === 'message');
    const show = touched.has('message') && Boolean(problem);
    error.hidden = !show;
    error.textContent = show ? problem[1] : '';
    for (const name of ['message', 'email', 'display_name']) {
      field(name).setAttribute('aria-invalid', String(!submitted && problems.some(([key]) => key === name)));
    }
    verification.closest('.human-verification').classList.toggle('field-missing', !submitted && problems.some(([key]) => key === 'captcha'));
    readiness.replaceChildren();
    if (!configured || !config.submissionsEnabled || submitted) return;
    if (sending) { readiness.textContent = 'Sending your feedback. Please wait…'; return; }
    if (!problems.length) { readiness.textContent = 'Everything is complete. You can send your feedback.'; return; }
    const title = document.createElement('p'); title.textContent = 'Before you can send:';
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
    availability.textContent = 'Feedback is temporarily paused. This form cannot send your message yet.';
    status(message, 'Feedback is safely paused. Your message has not been sent.');
    return;
  }
  try {
    challenge = await captcha(verification, 'submit_feedback');
    updateSubmit();
  } catch {
    status(message, 'Human verification could not load. Reload this page and try again.', true);
    return;
  }
  form.addEventListener('submit', async () => {
    if (sending) return;
    const problems = issues();
    if (problems.length || !form.checkValidity()) {
      touched.add('message'); updateSubmit();
      status(message, problems.map(([, text]) => text).join(' ') || 'Check the highlighted fields before sending.', true);
      const first = problems.find(([key]) => key !== 'captcha');
      if (first) field(first[0]).focus(); else message.focus();
      return;
    }
    const fd = new FormData(form);
    const payload = { display_name: fd.get('display_name').trim(), email: fd.get('email').trim(), category: fd.get('category'), message: fd.get('message').trim(), page_url: fd.get('page_url').trim(), website: fd.get('website') };
    sending = true; updateSubmit(); submit.textContent = 'Sending…';
    status(message, 'Sending your feedback. Please wait…');
    try {
      const response = await fetch(`${config.supabaseUrl}/functions/v1/submit-feedback`, {
        method: 'POST', headers: { 'Content-Type':'application/json', apikey:config.supabaseAnonKey },
        body: JSON.stringify({ ...payload, turnstile_token:challenge.token() }), signal:AbortSignal.timeout(20000)
      });
      const result = await response.json().catch(() => null);
      if (!response.ok) {
        const fallback = response.status === 429 ? 'Limit reached. Please wait and try again later.' : response.status === 403 ? 'Human verification failed or expired. Please complete it again.' : 'The feedback service is temporarily unavailable. Your message is still here. Please try again later.';
        throw new Error(response.status >= 500 ? fallback : result?.message || fallback);
      }
      if (result?.accepted !== true || !result.reference) throw new Error('Sending could not be confirmed. Keep your message and try again later.');
      submitted = true; touched.clear(); form.reset();
      status(message, `Thank you. Your feedback was received and will be read by a person. Save this reference: ${result.reference}`);
    } catch (error) {
      status(message, error.name === 'TimeoutError' ? 'The request timed out. Your message is still here. Please wait before retrying to avoid duplicate submissions.' : error instanceof TypeError ? 'We could not connect to the feedback service. Your message is still here. Check your connection and try again.' : error.message, true);
    } finally {
      challenge.reset(); sending = false; updateSubmit(); submit.textContent = 'Send feedback'; message.focus();
    }
  });
})();
