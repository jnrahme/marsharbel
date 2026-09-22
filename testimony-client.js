(function () {
  'use strict';
  const config = window.TESTIMONY_CONFIG || {};
  const configured = Boolean(window.supabase && /^https:\/\/[^/]+\.supabase\.co$/.test(config.supabaseUrl || '') && config.supabaseAnonKey && !config.supabaseAnonKey.includes('YOUR_'));
  const client = configured ? window.supabase.createClient(config.supabaseUrl, config.supabaseAnonKey) : null;
  const node = (tag, text, className) => { const el = document.createElement(tag); if (text != null) el.textContent = text; if (className) el.className = className; return el; };
  const status = (el, text, error = false) => { el.textContent = text; el.className = `submit-status ${error ? 'warn' : ''}`; };
  const messages = {
    moderator_mfa_required: 'Sign in as the moderator and verify your authenticator code.',
    stale_revision: 'This story changed. Refresh and review the latest version before deciding.',
    screening_required: 'This story needs completed AI screening before publication.',
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
  let captchaPromise;
  async function captcha(host, action) {
    if (!config.turnstileSiteKey) throw new Error('Human verification is not configured.');
    if (!window.turnstile) {
      captchaPromise ||= new Promise((resolve, reject) => {
        const script = document.createElement('script'); script.src = 'https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit';
        script.onload = resolve; script.onerror = () => reject(new Error('Human verification could not load. Please reload.'));
        document.head.appendChild(script);
      });
      await captchaPromise;
    }
    let token = '';
    const id = window.turnstile.render(host, { sitekey: config.turnstileSiteKey, action, callback: value => { token = value; }, 'expired-callback': () => { token = ''; }, 'error-callback': () => { token = ''; } });
    return { token: () => token, reset: () => { token = ''; window.turnstile.reset(id); } };
  }
  window.Testimony = { config, configured, client, node, status, rpc, captcha };
})();
