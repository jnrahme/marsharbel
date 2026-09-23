(function () {
  'use strict';
  const config = window.TESTIMONY_CONFIG || {};
  const configured = Boolean(window.supabase && /^https:\/\/[^/]+\.supabase\.co$/.test(config.supabaseUrl || '') && config.supabaseAnonKey && !config.supabaseAnonKey.includes('YOUR_'));
  const rememberControl = document.getElementById('admin-remember-browser');
  let adminSession;
  if (rememberControl) {
    const key = 'sc-moderator-session';
    const preference = 'sc-moderator-remember';
    let remembered = localStorage.getItem(preference) === 'yes';
    const storage = {
      getItem: name => (remembered ? localStorage : sessionStorage).getItem(name),
      setItem: (name, value) => (remembered ? localStorage : sessionStorage).setItem(name, value),
      removeItem: name => { localStorage.removeItem(name); sessionStorage.removeItem(name); }
    };
    // Move the previous automatically persisted moderator session to the new
    // explicit storage choice; ordinary reader sessions stay separate.
    if (configured) {
      const legacyKey = `sb-${new URL(config.supabaseUrl).hostname.split('.')[0]}-auth-token`;
      const legacySession = localStorage.getItem(legacyKey);
      let legacyUser;
      try { legacyUser = JSON.parse(legacySession)?.user; } catch { /* Ignore invalid old data. */ }
      if (legacyUser?.app_metadata?.role === 'moderator') {
        if (!storage.getItem(key)) storage.setItem(key, legacySession);
        localStorage.removeItem(legacyKey);
      }
    }
    const setRemembered = value => {
      const session = storage.getItem(key);
      storage.removeItem(key);
      remembered = value;
      if (value) localStorage.setItem(preference, 'yes');
      else localStorage.removeItem(preference);
      if (session) storage.setItem(key, session);
      rememberControl.checked = value;
    };
    rememberControl.checked = remembered;
    rememberControl.addEventListener('change', () => setRemembered(rememberControl.checked));
    adminSession = { storage, storageKey: key, forget: () => { storage.removeItem(key); setRemembered(false); } };
  }
  const client = configured ? window.supabase.createClient(config.supabaseUrl, config.supabaseAnonKey,
    adminSession ? { auth: { storage: adminSession.storage, storageKey: adminSession.storageKey, persistSession: true, detectSessionInUrl: false } } : undefined) : null;
  const node = (tag, text, className) => { const el = document.createElement(tag); if (text != null) el.textContent = text; if (className) el.className = className; return el; };
  const status = (el, text, error = false) => { el.textContent = text; el.className = `submit-status ${error ? 'warn' : ''}`; };
  const messages = {
    moderator_mfa_required: 'Sign in with the authorized moderator account.',
    stale_revision: 'This story changed. Refresh and review the latest version before deciding.',
    screening_required: 'Record your manual review or complete automated screening before publication.',
    review_reason_required: 'Enter review notes between 30 and 1,000 characters.',
    publication_limit: 'The daily publication limit is reached. An explicit override and reason are required.',
    publishing_paused: 'Publishing is paused. Enable it in the controls first.',
    intake_paused: 'New submissions and edits are temporarily paused.',
    pending_limit: 'You already have three stories awaiting review.',
    rate_limited: 'The daily limit has been reached. Please try another day.',
    reason_required: 'Please give a reason of at least 10 characters.',
    override_reason_required: 'Explain the publication-limit override in at least 10 characters.',
    closed_submission: 'This story is closed. It cannot be edited or republished.',
    not_found: 'This item is no longer available.', verified_account_required: 'Verify your email before continuing.'
  };
  async function rpc(name, args) {
    if (!client) throw new Error('This service is not configured yet.');
    const { data, error } = await client.rpc(name, args);
    const problem = error?.message || data?.error;
    if (problem) throw new Error(messages[problem] || 'The action could not be completed. Please refresh and try again.');
    return data;
  }
  const captchaLoads = {};
  async function captcha(host, action) {
    const provider = action === 'submit_testimony' ? (config.submissionCaptchaProvider || 'turnstile') : 'turnstile';
    if (!['turnstile', 'hcaptcha'].includes(provider)) throw new Error('Unknown verification provider.');
    const sitekey = provider === 'hcaptcha' ? config.hcaptchaSiteKey : config.turnstileSiteKey;
    if (!sitekey) throw new Error('Human verification is not configured.');
    const widget = node('div');
    const progress = node('p', 'Loading human verification…', 'submit-status');
    progress.setAttribute('role', 'status');
    const retry = node('button', 'Retry human verification', 'btn subtle captcha-retry');
    retry.type = 'button'; retry.hidden = true;
    host.replaceChildren(widget, progress, retry);
    let token = ''; let id; let api; let loading = false;
    const changed = () => host.dispatchEvent(new Event('verificationchange'));
    const fail = text => { token = ''; progress.textContent = text; retry.hidden = false; changed(); };
    async function load() {
      if (loading) return;
      loading = true; retry.hidden = true; token = ''; changed();
      progress.textContent = 'Loading human verification…';
      try {
        if (!window[provider]) {
          captchaLoads[provider] ||= new Promise((resolve, reject) => {
            const script = document.createElement('script');
            const callback = `testimonyCaptchaLoaded_${provider}`;
            const timer = setTimeout(() => { script.remove(); delete window[callback]; reject(new Error('timeout')); }, 15000);
            window[callback] = () => { clearTimeout(timer); delete window[callback]; resolve(); };
            script.src = provider === 'hcaptcha'
              ? `https://js.hcaptcha.com/1/api.js?render=explicit&onload=${callback}`
              : `https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit&onload=${callback}`;
            script.onerror = () => { clearTimeout(timer); script.remove(); delete window[callback]; reject(new Error('load')); };
            // Turnstile is ready on script load; hCaptcha documents its onload callback.
            script.onload = () => { if (provider === 'turnstile' && window[provider]?.render) { clearTimeout(timer); delete window[callback]; resolve(); } };
            document.head.appendChild(script);
          }).catch(error => { delete captchaLoads[provider]; throw error; });
          await captchaLoads[provider];
        }
        api = window[provider];
        if (id !== undefined) api.remove(id);
        widget.replaceChildren();
        progress.textContent = provider === 'hcaptcha' ? 'Check “I am human” above to continue.' : 'Checking your browser… Please wait before continuing.';
        id = api.render(widget, { sitekey, theme: 'dark', size: 'normal',
          ...(provider === 'turnstile' ? { action, appearance: 'always' } : {}),
          callback: value => { token = value; retry.hidden = true; progress.textContent = 'Human verification complete.'; changed(); },
          'expired-callback': () => fail('Human verification expired. Please retry the check.'),
          'timeout-callback': () => fail('Human verification timed out. Please retry the check.'),
          'error-callback': () => { fail('Human verification could not complete. Retry the check; your story will stay here.'); return true; }
        });
      } catch { fail('Human verification could not load. Check your connection and retry; your story will stay here.'); }
      finally { loading = false; }
    }
    retry.addEventListener('click', load);
    await load();
    return { token: () => token, reset: () => {
      token = ''; changed();
      if (api && id !== undefined) { retry.hidden = true; progress.textContent = 'Please complete human verification again.'; api.reset(id); }
      else load();
    } };
  }
  window.Testimony = { config, configured, client, node, status, rpc, captcha, adminSession };
})();
