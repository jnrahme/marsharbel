(async function () {
  'use strict';
  const { client, config, configured, node, status, rpc, captcha } = window.Testimony;
  const login = document.getElementById('admin-login-form'); const message = document.getElementById('admin-status');
  const panel = document.getElementById('admin-panel'); const mfa = document.getElementById('admin-mfa-form');
  const statsGrid = document.getElementById('stats-grid');
  const controlsSummary = document.getElementById('controls-summary');
  const sendToggle = document.getElementById('send-toggle');
  const issuesList = document.getElementById('issues-list');
  const listStatus = document.getElementById('list-status');
  const subscriberList = document.getElementById('subscriber-list');
  let factorId; let challenge; let busy = false; let controls; let page = 0;
  const PAGE_SIZE = 50;
  const show = (text, error = false) => status(message, text, error);
  const retryAccess = node('button','Retry loading admin panel','btn subtle');
  retryAccess.type='button'; retryAccess.hidden=true; message.after(retryAccess);
  const accessFailure = error => { show(error.message,true); retryAccess.hidden=false; };
  retryAccess.addEventListener('click',async()=>{retryAccess.disabled=true;try{await authenticate();}catch(error){accessFailure(error);}finally{retryAccess.disabled=false;}});
  const feedback = node('p', '', 'admin-feedback');
  feedback.id = 'admin-feedback'; feedback.setAttribute('role','status'); feedback.tabIndex = -1; feedback.hidden = true;
  panel.prepend(feedback);
  const announce = (text, error = false) => {
    feedback.textContent = text; feedback.hidden = false;
    feedback.classList.toggle('warn', error); feedback.focus();
  };
  if (!configured || !config.moderationEnabled) {
    login.addEventListener('submit', event => event.preventDefault());
    const button = login.querySelector('button[type="submit"]');
    button.disabled = true;
    button.textContent = 'Sign-in unavailable during setup';
    login.setAttribute('aria-describedby', 'admin-status');
    show('Sign-in is not enabled yet: the admin account and security setup must be completed first. Nothing entered here is submitted while setup is paused.');
    return;
  }
  async function action(button, fn, success = 'Changes saved.') {
    if (busy) return; busy = true; button.disabled = true;
    try { await fn(); await refresh(); announce(success); } catch (error) { announce(error.message, true); }
    finally { busy = false; button.disabled = false; }
  }
  const fmt = value => value ? new Date(value).toLocaleString() : 'not yet';
  function statCard(label, value) {
    const card = node('article', null, 'card testimony-card');
    card.append(node('h3', String(value)), node('p', label, 'source-meta'));
    return card;
  }
  function renderStats(s) {
    statsGrid.replaceChildren(
      statCard('Total subscribers', s.total ?? 0),
      statCard('Confirmed', s.confirmed ?? 0),
      statCard('Pending confirmation', s.pending ?? 0),
      statCard('Unsubscribed', s.unsubscribed ?? 0),
      statCard('Confirmed this week', s.confirmed_7d ?? 0),
      statCard('Confirmed this month', s.confirmed_30d ?? 0)
    );
  }
  function renderControls() {
    if (!controls) return;
    controlsSummary.textContent = `Daily send is ${controls.send_enabled ? 'ENABLED' : 'disabled'}. Signup is ${controls.signup_enabled ? 'open' : 'closed'} (limit ${controls.daily_signup_limit}/day). Send cap ${controls.daily_send_cap}/day.`;
    sendToggle.textContent = controls.send_enabled ? 'Pause the daily send' : 'Enable the daily send';
    sendToggle.disabled = false;
  }
  function renderIssues(rows) {
    issuesList.replaceChildren(...rows.map(row => {
      const card = node('article', null, 'card testimony-card');
      const state = row.send_completed_at ? `completed ${fmt(row.send_completed_at)}` : row.send_started_at ? `started ${fmt(row.send_started_at)}` : 'not started';
      card.append(node('h3', row.issue_date), node('p', `${row.mystery || 'mystery pending'} · prayer: ${row.prayer_key || 'pending'} · ${state}`, 'source-meta'),
        node('p', `Attempted ${row.attempted} · sent ${row.sent} · failed ${row.failed}`, 'testimony-text'));
      return card;
    }));
    if (!rows.length) issuesList.append(node('p', 'No daily issues yet. The first send creates one.'));
  }
  function renderList(rows) {
    if (!rows.length) { subscriberList.replaceChildren(node('p', 'No subscribers in this view.')); return; }
    const table = node('table');
    const head = node('tr');
    for (const label of ['Email', 'Status', 'Locale', 'Confirmed', 'Signed up']) head.append(node('th', label));
    table.append(head);
    for (const row of rows) {
      const tr = node('tr');
      tr.append(node('td', row.email), node('td', row.status), node('td', row.locale), node('td', fmt(row.confirmed_at)), node('td', fmt(row.created_at)));
      table.append(tr);
    }
    subscriberList.replaceChildren(table);
  }
  async function refresh() {
    const [stats, ctl, issues, subs, log, audit] = await Promise.all([
      rpc('prayer_subscriber_stats', {}),
      rpc('prayer_admin_controls', {}),
      rpc('prayer_admin_issues', { p_limit: 14 }),
      rpc('prayer_subscriber_list', { p_status: listStatus.value, p_limit: PAGE_SIZE, p_offset: page * PAGE_SIZE }),
      rpc('prayer_admin_send_log', { p_limit: 50 }),
      rpc('prayer_admin_audit_list', { p_limit: 30 })
    ]);
    controls = ctl;
    renderStats(stats); renderControls(); renderIssues(issues); renderList(subs);
    document.getElementById('list-prev').disabled = page === 0;
    document.getElementById('list-next').disabled = subs.length < PAGE_SIZE;
    const logEl = document.getElementById('send-log');
    logEl.replaceChildren(...log.map(row => node('p', `${fmt(row.created_at)} — ${row.status}${row.error ? `: ${row.error}` : ''}`, 'source-meta')));
    if (!log.length) logEl.append(node('p', 'Nothing sent yet.'));
    document.getElementById('audit-list').replaceChildren(...audit.map(row => node('li', `${fmt(row.created_at)} — ${row.action}: ${row.detail || ''}`)));
  }
  async function authenticate() {
    retryAccess.hidden=true;
    panel.hidden = true; mfa.hidden = true;
    const {data:{user},error} = await client.auth.getUser();
    if (error || !user) { login.hidden=false;if (!challenge) challenge = await captcha(document.getElementById('admin-captcha'), 'login');return; }
    if (user.app_metadata?.role !== 'moderator') { await client.auth.signOut(); login.hidden=false; throw new Error('This area is for the site moderator only.'); }
    login.hidden=true;
    if (config.moderatorMfaRequired === false) {
      await refresh(); panel.hidden=false; show('Signed in as moderator.'); return;
    }
    const assurance=await client.auth.mfa.getAuthenticatorAssuranceLevel();
    if(assurance.error)throw new Error('Unable to check MFA.');
    if(assurance.data.currentLevel==='aal2') { await refresh(); panel.hidden=false;show('Signed in as moderator with MFA.');return; }
    const factors=await client.auth.mfa.listFactors(); if(factors.error)throw new Error('Unable to load authenticator factors.');
    const verified=factors.data.totp.find(f=>f.status==='verified');
    if(verified) { factorId=verified.id;document.getElementById('mfa-enrollment').hidden=true; }
    else {
      for(const factor of (factors.data.all || factors.data.totp).filter(f=>f.factor_type==='totp' && f.status!=='verified')) await client.auth.mfa.unenroll({factorId:factor.id});
      const enrolled=await client.auth.mfa.enroll({factorType:'totp',friendlyName:'Saint Charbel moderator'});
      if(enrolled.error)throw new Error('Unable to enroll an authenticator.');
      factorId=enrolled.data.id;document.getElementById('mfa-enrollment').hidden=false;
      document.getElementById('mfa-qr').src=enrolled.data.totp.qr_code;
      document.getElementById('mfa-secret').textContent=enrolled.data.totp.secret;
    }
    mfa.hidden=false;show('Enter the current code from your authenticator.');
  }
  login.addEventListener('submit',async e=>{e.preventDefault();const button=login.querySelector('button');button.disabled=true;let attempted=false;try{if (!challenge) challenge=await captcha(document.getElementById('admin-captcha'),'login');if(!challenge.token())throw new Error('Complete human verification first.');const fd=new FormData(login);attempted=true;const result=await client.auth.signInWithPassword({email:fd.get('email'),password:fd.get('password'),options:{captchaToken:challenge.token()}});if(result.error)throw new Error('Sign-in failed. Check your credentials.');login.reset();try{await authenticate();}catch(error){accessFailure(error);}}catch(error){show(error.message,true);}finally{button.disabled=false;if(attempted)challenge?.reset();}});
  mfa.addEventListener('submit',async e=>{e.preventDefault();const button=mfa.querySelector('button');button.disabled=true;try{const result=await client.auth.mfa.challengeAndVerify({factorId,code:new FormData(mfa).get('code')});if(result.error)throw new Error('Invalid or expired authenticator code.');mfa.reset();await authenticate();}catch(error){show(error.message,true);}finally{button.disabled=false;}});
  document.getElementById('admin-logout-btn').addEventListener('click',async()=>{
    const { error } = await client.auth.signOut({ scope: 'local' });
    if (error) { show('Could not sign out. Please try again.', true); return; }
    window.Testimony.adminSession?.forget();
    location.reload();
  });
  document.getElementById('refresh-dashboard').addEventListener('click',e=>action(e.currentTarget,()=>refresh(),'Dashboard refreshed.'));
  sendToggle.addEventListener('click', () => action(sendToggle, async () => {
    const next = !controls?.send_enabled;
    const result = await rpc('prayer_admin_set_send_enabled', { p_enabled: next });
    controls = { ...controls, send_enabled: result.send_enabled };
  }, controls?.send_enabled ? 'Daily send paused.' : 'Daily send ENABLED. The next 6 AM run will email confirmed subscribers.'));
  listStatus.addEventListener('change', () => { page = 0; action(document.getElementById('refresh-dashboard'), () => refresh(), 'List updated.'); });
  document.getElementById('list-prev').addEventListener('click', () => { if (page > 0) { page--; action(document.getElementById('refresh-dashboard'), () => refresh(), 'List updated.'); } });
  document.getElementById('list-next').addEventListener('click', () => { page++; action(document.getElementById('refresh-dashboard'), () => refresh(), 'List updated.'); });
  try{await authenticate();}catch(error){accessFailure(error);}
})();
