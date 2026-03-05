(function () {
  const cfg = window.TESTIMONY_CONFIG || {};
  const statusEl = document.getElementById('submit-status');
  const form = document.getElementById('testimony-form');
  const submitButton = document.getElementById('submit-testimony-btn');
  const turnstileSlot = document.getElementById('turnstile-slot');

  const show = (msg, type) => {
    if (!statusEl) return;
    statusEl.textContent = msg;
    statusEl.className = `submit-status ${type || ''}`.trim();
  };

  const hasSupabaseConfig = Boolean(
    cfg.supabaseUrl &&
    cfg.supabaseAnonKey &&
    !cfg.supabaseUrl.includes('YOUR_PROJECT') &&
    !cfg.supabaseAnonKey.includes('YOUR_SUPABASE')
  );
  const hasTurnstileKey = Boolean(cfg.turnstileSiteKey && !cfg.turnstileSiteKey.includes('YOUR_'));
  const hasTurnstileVerifyEndpoint = Boolean(cfg.turnstileVerifyEndpoint);

  if (!hasSupabaseConfig) {
    show('Configuration missing: set Supabase URL/Anon key in testimony-config.js.', 'warn');
  }

  const supabase = window.supabase?.createClient(cfg.supabaseUrl || '', cfg.supabaseAnonKey || '');

  if (hasTurnstileKey) {
    turnstileSlot.innerHTML = `<div class="cf-turnstile" data-sitekey="${cfg.turnstileSiteKey}"></div>`;
  } else {
    turnstileSlot.innerHTML = '<p class="source-meta">Human verification is required. Configure Turnstile in testimony-config.js.</p>';
  }

  const getRemainingCooldown = () => {
    const key = 'testimony_last_submit_at';
    const last = Number(localStorage.getItem(key) || 0);
    const now = Date.now();
    const minGap = 60 * 1000;
    if (now - last < minGap) {
      return Math.ceil((minGap - (now - last)) / 1000);
    }
    return 0;
  };

  const stampCooldown = () => {
    localStorage.setItem('testimony_last_submit_at', String(Date.now()));
  };

  form?.addEventListener('submit', async (e) => {
    e.preventDefault();
    show('Submitting...', '');
    if (!hasSupabaseConfig || !supabase) {
      show('Supabase client not configured.', 'warn');
      return;
    }

    const wait = getRemainingCooldown();
    if (wait > 0) {
      show(`Please wait ${wait}s before submitting again.`, 'warn');
      return;
    }

    const data = new FormData(form);
    const honeypot = (data.get('website') || '').toString().trim();
    if (honeypot) {
      show('Spam protection triggered.', 'error');
      return;
    }

    const payload = {
      full_name: (data.get('full_name') || '').toString().trim(),
      email: (data.get('email') || '').toString().trim() || null,
      country: (data.get('country') || '').toString().trim() || null,
      parish: (data.get('parish') || '').toString().trim() || null,
      event_date: (data.get('event_date') || '').toString().trim() || null,
      healing_type: (data.get('healing_type') || '').toString().trim() || null,
      testimony_text: (data.get('testimony_text') || '').toString().trim(),
      contact_permission: Boolean(data.get('contact_permission')),
      consent_publish: Boolean(data.get('consent_publish')),
      language: (data.get('language') || 'en').toString(),
      status: 'pending',
      verification_note: 'Pending human review',
      meta: {
        user_agent: navigator.userAgent,
        submitted_from: window.location.hostname,
        turnstile_present: !!document.querySelector('input[name="cf-turnstile-response"]')
      }
    };

    if (!payload.full_name || payload.full_name.length < 2) {
      show('Please provide your full name.', 'warn');
      return;
    }
    if (!payload.testimony_text || payload.testimony_text.length < 60) {
      show('Please provide more detail (at least 60 characters).', 'warn');
      return;
    }
    if (!payload.consent_publish) {
      show('Please confirm consent for review/publication.', 'warn');
      return;
    }

    const turnstileToken = (data.get('cf-turnstile-response') || '').toString();
    if ((cfg.requireTurnstile !== false) && (!hasTurnstileKey || !hasTurnstileVerifyEndpoint)) {
      show('Submission is locked until Turnstile is fully configured.', 'warn');
      return;
    }

    if (hasTurnstileKey && !turnstileToken) {
      show('Please complete the human verification.', 'warn');
      return;
    }

    if (hasTurnstileVerifyEndpoint && turnstileToken) {
      try {
        const verifyRes = await fetch(cfg.turnstileVerifyEndpoint, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ token: turnstileToken })
        });
        const verifyJson = await verifyRes.json().catch(() => ({ success: false }));
        if (!verifyRes.ok) {
          show('Human verification endpoint error. Please try again.', 'error');
          return;
        }
        if (!verifyJson.success) {
          show('Human verification failed. Please try again.', 'error');
          return;
        }
      } catch (_) {
        show('Could not verify human check right now. Try again.', 'error');
        return;
      }
    }

    submitButton.disabled = true;
    const { error } = await supabase.from('testimonies').insert([payload]);
    submitButton.disabled = false;

    if (error) {
      show(`Submission failed: ${error.message}`, 'error');
      return;
    }

    stampCooldown();
    form.reset();
    show('Thank you. Your testimony was received and is pending human review.', 'ok');
  });
})();
