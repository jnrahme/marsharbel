(function () {
  'use strict';
  const cfg = window.TESTIMONY_CONFIG || {};
  const form = document.getElementById('testimony-form');
  const statusEl = document.getElementById('submit-status');
  const submitButton = document.getElementById('submit-testimony-btn');
  const turnstileSlot = document.getElementById('turnstile-slot');
  const startedAt = Date.now();
  let submitting = false;
  const show = (message, type) => { statusEl.textContent = message; statusEl.className = `submit-status ${type || ''}`.trim(); };
  const turnstileReady = Boolean(cfg.turnstileSiteKey && !cfg.turnstileSiteKey.includes('YOUR_'));
  const endpointReady = Boolean(cfg.submissionEndpoint);
  const supabaseConfigured = Boolean(cfg.supabaseUrl && !cfg.supabaseUrl.includes('YOUR_') && cfg.supabaseAnonKey && !cfg.supabaseAnonKey.includes('YOUR_'));
  let supabaseClient = null;
  if (supabaseConfigured && window.supabase) supabaseClient = window.supabase.createClient(cfg.supabaseUrl, cfg.supabaseAnonKey);
  // Accounts are required to submit: intake stays closed until Supabase Auth is configured.
  const intakeOpen = cfg.submissionsEnabled === true && turnstileReady && endpointReady && supabaseClient !== null;
  if (turnstileReady) turnstileSlot.innerHTML = `<div class="cf-turnstile" data-sitekey="${cfg.turnstileSiteKey}" data-action="submit_testimony"></div>`;
  else turnstileSlot.innerHTML = '<p class="source-meta">Human verification is not configured yet.</p>';
  if (!intakeOpen) { submitButton.disabled = true; show('Submissions are safely paused while the protected intake service is configured.', 'warn'); }
  const clean = (fd, name, max) => (fd.get(name) || '').toString().trim().slice(0, max);
  form?.addEventListener('submit', async (event) => {
    event.preventDefault();
    if (!intakeOpen || submitting) return;
    const fd = new FormData(form);
    if (clean(fd, 'website', 200)) return show('Submission blocked.', 'error');
    if (Date.now() - startedAt < 3500) return show('Please take a moment to review your testimony.', 'warn');
    const payload = {full_name:clean(fd,'full_name',120),email:clean(fd,'email',160)||null,language:clean(fd,'language',12)||'en',country:clean(fd,'country',120)||null,parish:clean(fd,'parish',180)||null,event_date:clean(fd,'event_date',10)||null,healing_type:clean(fd,'healing_type',160)||null,testimony_text:clean(fd,'testimony_text',7000),age_confirmed:fd.has('age_confirmed'),contact_permission:fd.has('contact_permission'),consent_publish:fd.has('consent_publish'),turnstile_token:clean(fd,'cf-turnstile-response',4096),website:'',elapsed_ms:Date.now()-startedAt};
    if (payload.full_name.length < 2) return show('Please provide your full name.', 'warn');
    if (payload.testimony_text.length < 60) return show('Please provide at least 60 characters.', 'warn');
    if (!payload.age_confirmed) return show('You must confirm that you are 18 or older.', 'warn');
    if (!payload.consent_publish) return show('Please confirm the consent statement.', 'warn');
    if (!payload.turnstile_token) return show('Please complete the human verification.', 'warn');
    const { data: sessionData } = await supabaseClient.auth.getSession();
    const accessToken = sessionData && sessionData.session ? sessionData.session.access_token : '';
    if (!accessToken) return show('Please sign in to your account before submitting.', 'warn');
    submitting = true; submitButton.disabled = true; show('Sending for private review...', '');
    try {
      const response = await fetch(cfg.submissionEndpoint,{method:'POST',headers:{'Content-Type':'application/json','Accept':'application/json','Authorization':`Bearer ${accessToken}`},credentials:'omit',cache:'no-store',body:JSON.stringify(payload)});
      const result = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(result.message || 'The protected intake could not accept this submission.');
      form.reset(); if (window.turnstile) window.turnstile.reset(); show('Thank you. Your testimony is private and pending human review.', 'ok');
    } catch (error) { show(error.message || 'Submission failed. Please try again later.', 'error'); if (window.turnstile) window.turnstile.reset(); }
    finally { submitting = false; submitButton.disabled = !intakeOpen; }
  });
})();
