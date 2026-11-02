(async function () {
  'use strict';
  const { client, config, configured, node, status, rpc, captcha } = window.Testimony;
  const login = document.getElementById('admin-login-form'); const message = document.getElementById('admin-status');
  const panel = document.getElementById('admin-panel'); const mfa = document.getElementById('admin-mfa-form');
  const pending = document.getElementById('pending-list');
  let factorId; let challenge; let busy = false;
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
  function cardBody(row) {
    const page = row.page_url ? `\nReported from: ${row.page_url}` : '';
    const name = row.display_name || 'Anonymous reader';
    return `[Visitor feedback - ${row.category}] ${row.message.slice(0, 80)}${row.message.length > 80 ? '…' : ''}\n\nFrom: ${name}${row.email ? ` <${row.email}>` : ''}${page}\nReference: ${row.id}\n\n${row.message}`;
  }
  function card(row) {
    const article = node('article', null, 'card testimony-card');
    const meta = node('p', `${row.category} · revision ${row.revision} · ${new Date(row.created_at).toLocaleString()}${row.page_url ? ` · from ${row.page_url}` : ''}`);
    article.append(node('h3', row.display_name || 'Anonymous reader'), meta, node('p', row.message, 'testimony-text'));
    if (row.email) article.append(node('p', `Reply address: ${row.email}`, 'source-meta'));
    const reason = node('textarea'); reason.rows = 2; reason.placeholder = 'Note for the audit log (required to reject)';
    reason.className = 'testimony-text'; reason.setAttribute('aria-label', 'Moderation note');
    const row1 = node('div', null, 'cta-row');
    const approve = node('button', 'Approve for board', 'btn primary'); approve.type = 'button';
    const reject = node('button', 'Reject', 'btn subtle'); reject.type = 'button';
    const copy = node('button', 'Copy board card text', 'btn subtle'); copy.type = 'button';
    copy.addEventListener('click', async () => {
      try { await navigator.clipboard.writeText(cardBody(row)); announce('Board card text copied. Create the card on the board, then approve this item.'); }
      catch { announce('Copy failed. Select the text and copy it manually.', true); }
    });
    approve.addEventListener('click', () => action(approve, () => rpc('feedback_moderate', { p_id: row.id, p_revision: row.revision, p_action: 'approve', p_reason: reason.value.trim() || 'Approved for board' }), 'Approved. Create the board card from the copied text; automatic card creation is not wired yet.'));
    reject.addEventListener('click', () => {
      const note = reason.value.trim();
      if (note.length < 10) { announce('Enter a note of at least 10 characters before rejecting.', true); reason.focus(); return; }
      action(reject, () => rpc('feedback_moderate', { p_id: row.id, p_revision: row.revision, p_action: 'reject', p_reason: note }), 'Rejected and closed.');
    });
    row1.append(approve, copy, reject);
    article.append(reason, row1);
    return article;
  }
  async function refresh() {
    const [queue, audit] = await Promise.all([
      rpc('feedback_queue', { p_limit: 50 }),
      client.from('feedback_audit').select('action,reason,created_at').order('created_at', { ascending: false }).limit(30)
    ]);
    pending.replaceChildren(...queue.map(card));
    if (!queue.length) pending.append(node('p', 'The queue is empty. New feedback will appear here.'));
    if (!audit.error) document.getElementById('audit-list').replaceChildren(...audit.data.map(row => node('li', `${new Date(row.created_at).toLocaleString()} — ${row.action}: ${row.reason || ''}`)));
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
  document.getElementById('refresh-queue').addEventListener('click',e=>action(e.currentTarget,()=>refresh(),'Queue refreshed.'));
  try{await authenticate();}catch(error){accessFailure(error);}
})();
