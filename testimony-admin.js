(function () {
  const cfg = window.TESTIMONY_CONFIG || {};
  const supabase = window.supabase?.createClient(cfg.supabaseUrl || '', cfg.supabaseAnonKey || '');

  const loginForm = document.getElementById('admin-login-form');
  const adminStatus = document.getElementById('admin-status');
  const pendingRoot = document.getElementById('pending-list');
  const approvedRoot = document.getElementById('approved-list');
  const adminPanel = document.getElementById('admin-panel');
  const logoutBtn = document.getElementById('admin-logout-btn');

  const show = (msg, type) => {
    adminStatus.textContent = msg;
    adminStatus.className = `submit-status ${type || ''}`.trim();
  };

  const isConfigured = () => (
    supabase &&
    cfg.supabaseUrl &&
    cfg.supabaseAnonKey &&
    !cfg.supabaseUrl.includes('YOUR_PROJECT') &&
    !cfg.supabaseAnonKey.includes('YOUR_SUPABASE')
  );

  const escapeHtml = (str) =>
    String(str || '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');

  // Moderation is restricted to the site-owner admin account. The database
  // enforces this with row-level security (role='moderator' AND aal2); this
  // client-side gate keeps the moderation UI itself hidden from every other
  // signed-in account so regular users never see approve/reject controls.
  const getClaims = (session) => {
    try {
      const part = session.access_token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/');
      return JSON.parse(atob(part)) || {};
    } catch (e) {
      return {};
    }
  };

  const isModerator = (session) => {
    if (!session || !session.access_token) return false;
    const claims = getClaims(session);
    const role = claims.app_metadata && claims.app_metadata.role;
    return role === 'moderator' && claims.aal === 'aal2';
  };

  const denyNonModerator = async () => {
    adminPanel.hidden = true;
    loginForm.style.display = '';
    await supabase.auth.signOut();
    show('This panel is for the site moderator account only. Regular accounts can submit stories and follow their own status, but cannot approve, reject, edit, or publish testimonies.', 'warn');
  };

  const openPanel = () => {
    loginForm.style.display = 'none';
    adminPanel.hidden = false;
    show('Authenticated as moderator.', 'ok');
    refresh();
  };

  const card = (row, actions) => {
    const el = document.createElement('article');
    el.className = 'card testimony-card admin-card';
    el.innerHTML = [
      `<h3>${escapeHtml(row.full_name || 'Anonymous')}</h3>`,
      `<p class="source-meta">${escapeHtml([row.email || '', row.country || '', row.parish || '', row.created_at || ''].filter(Boolean).join(' • '))}</p>`,
      `<p>${escapeHtml(row.testimony_text || '').replace(/\n/g, '<br>')}</p>`,
      '<div class="cta-row"></div>'
    ].join('');
    const rowActions = el.querySelector('.cta-row');
    actions.forEach(({label, fn, cls}) => {
      const b = document.createElement('button');
      b.type = 'button';
      b.className = `btn ${cls || 'subtle'}`;
      b.textContent = label;
      b.addEventListener('click', fn);
      rowActions.appendChild(b);
    });
    return el;
  };

  const refresh = async () => {
    pendingRoot.innerHTML = '';
    approvedRoot.innerHTML = '';

    const { data, error } = await supabase
      .from('testimonies')
      .select('id,full_name,email,country,parish,testimony_text,status,created_at')
      .order('created_at', { ascending: false })
      .limit(400);

    if (error) {
      show(`Load failed: ${error.message}`, 'error');
      return;
    }

    const pending = data.filter((d) => d.status === 'pending');
    const approved = data.filter((d) => d.status === 'approved');

    if (!pending.length) {
      pendingRoot.innerHTML = '<p class="source-meta">No pending testimonies.</p>';
    }
    if (!approved.length) {
      approvedRoot.innerHTML = '<p class="source-meta">No approved testimonies.</p>';
    }

    pending.forEach((row) => {
      pendingRoot.appendChild(card(row, [
        {
          label: 'Approve',
          cls: 'primary',
          fn: async () => {
            const { error: e } = await supabase.from('testimonies').update({ status: 'approved', published_at: new Date().toISOString(), moderated_at: new Date().toISOString() }).eq('id', row.id);
            if (e) return show(e.message, 'error');
            show('Approved.', 'ok');
            refresh();
          }
        },
        {
          label: 'Reject',
          fn: async () => {
            const { error: e } = await supabase.from('testimonies').update({ status: 'rejected', moderated_at: new Date().toISOString() }).eq('id', row.id);
            if (e) return show(e.message, 'error');
            show('Rejected.', 'warn');
            refresh();
          }
        }
      ]));
    });

    approved.forEach((row) => {
      approvedRoot.appendChild(card(row, [
        {
          label: 'Move To Pending',
          fn: async () => {
            const { error: e } = await supabase.from('testimonies').update({ status: 'pending', published_at: null }).eq('id', row.id);
            if (e) return show(e.message, 'error');
            show('Moved back to pending.', 'warn');
            refresh();
          }
        }
      ]));
    });
  };

  if (!isConfigured()) {
    show('Configure Supabase credentials in testimony-config.js first.', 'warn');
    return;
  }

  (async () => {
    const { data } = await supabase.auth.getSession();
    if (!data?.session) return;
    if (isModerator(data.session)) {
      openPanel();
    } else {
      denyNonModerator();
    }
  })();

  loginForm?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const fd = new FormData(loginForm);
    const email = (fd.get('email') || '').toString().trim();
    const password = (fd.get('password') || '').toString();
    if (!email || !password) return show('Email and password are required.', 'warn');

    const { error } = await supabase.auth.signInWithPassword({ email, password });
    if (error) return show(`Login failed: ${error.message}`, 'error');

    const { data } = await supabase.auth.getSession();
    if (data?.session && isModerator(data.session)) {
      openPanel();
    } else {
      denyNonModerator();
    }
  });

  logoutBtn?.addEventListener('click', async () => {
    await supabase.auth.signOut();
    adminPanel.hidden = true;
    loginForm.style.display = '';
    show('Logged out.', '');
  });
})();
