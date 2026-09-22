(async function () {
  'use strict';
  const { client, config, configured, node, status, rpc, captcha } = window.Testimony;
  const login = document.getElementById('admin-login-form'); const message = document.getElementById('admin-status');
  const panel = document.getElementById('admin-panel'); const mfa = document.getElementById('admin-mfa-form');
  const pending = document.getElementById('pending-list'); const approved = document.getElementById('approved-list');
  let factorId; let challenge; let approvedOffset = 0; let offset = 0; let busy = false;
  const show = (text, error = false) => status(message, text, error);
  if (!configured || !config.moderationEnabled) { login.querySelectorAll('input,button').forEach(e => { e.disabled = true; }); show('Moderation is paused until the protected service is connected.'); return; }
  async function action(button, fn) {
    if (busy) return; busy = true; button.disabled = true;
    try { await fn(); await refresh(); show('Saved.'); } catch (error) { show(error.message, true); }
    finally { busy = false; button.disabled = false; }
  }
  function card(row) {
    const article = node('article', null, 'card testimony-card');
    article.append(node('h3', row.display_name), node('p', `${row.status.replaceAll('_', ' ')} · screening: ${row.review_state} · revision ${row.revision}`), node('p', row.story, 'testimony-text'));
    if (row.review_notes) {
      const review = node('details'); review.open = true; review.append(node('summary', 'AI screening notes — not verification'));
      review.append(node('p', row.review_notes.summary || 'No summary'), node('p', `Suggested handling: ${row.review_notes.recommendation || 'human review'}`));
      for (const flag of row.review_notes.flags || []) review.append(node('p', `Flag: ${flag.replaceAll('_', ' ')}`));
      if (row.review_notes.duplicate) review.append(node('p', 'An exact duplicate exists in the private queue.'));
      for (const question of row.review_notes.questions || []) review.append(node('p', question));
      article.append(review);
    }
    const label = node('label', 'Message to author / decision reason'); label.className = 'testimony-form';
    const reason = node('textarea'); reason.maxLength = 1000; reason.rows = 3; label.append(reason); article.append(label);
    const overrideLabel = node('label', null, 'inline-check'); const override = node('input'); override.type = 'checkbox';
    overrideLabel.append(override, document.createTextNode('Override the daily publication cap (requires a reason).')); article.append(overrideLabel);
    const buttons = node('div', null, 'cta-row');
    for (const [kind, title] of row.status === 'approved' ? [['unpublish','Unpublish']] : [['approve','Approve and publish'],['clarify','Request clarification'],['reject','Reject']]) {
      const button = node('button', title, 'btn subtle'); button.type = 'button';
      if (kind === 'approve') button.disabled = row.status !== 'pending' || row.review_state !== 'complete';
      button.addEventListener('click', () => action(button, () => rpc('testimony_moderate', { p_id:row.id, p_revision:row.revision, p_action:kind, p_reason:reason.value.trim(), p_override:kind === 'approve' && override.checked })));
      buttons.append(button);
    }
    if (row.review_state === 'failed' && row.status === 'pending') {
      const retry = node('button','Retry AI screening','btn subtle'); retry.type = 'button'; retry.addEventListener('click', () => action(retry, () => rpc('testimony_retry_review', {p_id:row.id}))); buttons.append(retry);
    }
    article.append(buttons); return article;
  }
  async function refresh() {
    const [queue, published, controls, reports, audit] = await Promise.all([
      client.from('testimony_submissions').select('*').in('status',['pending','needs_clarification']).order('created_at',{ascending:true}).range(offset,offset+19),
      client.from('testimony_submissions').select('*').eq('status','approved').order('updated_at',{ascending:false}).range(approvedOffset,approvedOffset+19),
      client.from('testimony_controls').select('*').single(),
      client.from('testimony_reports').select('id,publication_id,reason,created_at').eq('resolved',false).order('created_at',{ascending:true}).limit(50),
      client.from('testimony_audit').select('action,reason,created_at,submission_id').order('created_at',{ascending:false}).limit(30)
    ]);
    if ([queue,published,controls,reports,audit].some(result => result.error)) throw new Error('Unable to load protected data. Verify your moderator role and MFA, then sign in again.');
    pending.replaceChildren(...queue.data.map(card)); approved.replaceChildren(...published.data.map(card));
    if (!queue.data.length) pending.append(node('p','No pending stories on this page.'));
    if (!published.data.length) approved.append(node('p','No published reader submissions.'));
    document.getElementById('queue-previous').disabled = offset === 0; document.getElementById('queue-next').disabled = queue.data.length < 20;
    document.getElementById('queue-position').textContent = `Queue page ${Math.floor(offset / 20) + 1}`;
    document.getElementById('approved-previous').disabled = approvedOffset === 0; document.getElementById('approved-next').disabled = published.data.length < 20;
    document.getElementById('approved-position').textContent = `Published page ${Math.floor(approvedOffset / 20) + 1}`;
    for (const key of ['intake','publishing','screening']) document.getElementById(`control-${key}`).checked = controls.data[`${key}_enabled`];
    const reportList = document.getElementById('report-list'); reportList.replaceChildren();
    for (const report of reports.data) {
      const item = node('article',null,'card testimony-card'); item.append(node('p',`Reported testimony: ${report.publication_id || 'already removed'}`),node('p',report.reason));
      const resolve = node('button','Mark report resolved','btn subtle'); resolve.type='button';resolve.addEventListener('click',()=>action(resolve,()=>rpc('testimony_resolve_report',{p_id:report.id})));item.append(resolve);
      if (report.publication_id) { const inspect=node('button','Load reported story','btn subtle');inspect.type='button';inspect.addEventListener('click',async()=>{try{const result=await client.from('testimony_submissions').select('*').eq('id',report.publication_id).single();if(result.error)throw result.error;item.append(card(result.data));inspect.remove();}catch{show('Could not load the reported story.',true);}});item.append(inspect); }
      reportList.append(item);
    }
    if (!reports.data.length) reportList.append(node('p','No unresolved reports.'));
    document.getElementById('audit-list').replaceChildren(...audit.data.map(row=>node('li',`${new Date(row.created_at).toLocaleString()} — ${row.action}: ${row.reason || row.submission_id || ''}`)));
  }
  async function authenticate() {
    panel.hidden = true; mfa.hidden = true;
    const {data:{user},error} = await client.auth.getUser();
    if (error || !user) { login.hidden=false;if (!challenge) challenge = await captcha(document.getElementById('admin-captcha'), 'login');return; }
    if (user.app_metadata?.role !== 'moderator') { await client.auth.signOut(); login.hidden=false; throw new Error('This area is for the site moderator only.'); }
    login.hidden=true;
    const assurance=await client.auth.mfa.getAuthenticatorAssuranceLevel();
    if(assurance.error)throw new Error('Unable to check MFA.');
    if(assurance.data.currentLevel==='aal2') { panel.hidden=false; await refresh();show('Signed in as moderator with MFA.');return; }
    const factors=await client.auth.mfa.listFactors(); if(factors.error)throw new Error('Unable to load authenticator factors.');
    const verified=factors.data.totp.find(f=>f.status==='verified');
    if(verified) { factorId=verified.id;document.getElementById('mfa-enrollment').hidden=true; }
    else {
      // Remove abandoned unverified enrollments before starting a fresh one.
      for(const factor of factors.data.totp.filter(f=>f.status!=='verified')) await client.auth.mfa.unenroll({factorId:factor.id});
      const enrolled=await client.auth.mfa.enroll({factorType:'totp',friendlyName:'Saint Charbel moderator'});
      if(enrolled.error)throw new Error('Unable to enroll an authenticator.');
      factorId=enrolled.data.id;document.getElementById('mfa-enrollment').hidden=false;
      document.getElementById('mfa-qr').src=`data:image/svg+xml;charset=utf-8,${encodeURIComponent(enrolled.data.totp.qr_code)}`;
      document.getElementById('mfa-secret').textContent=enrolled.data.totp.secret;
    }
    mfa.hidden=false;show('Enter the current code from your authenticator.');
  }
  login.addEventListener('submit',async e=>{e.preventDefault();const button=login.querySelector('button');button.disabled=true;try{if (!challenge) challenge=await captcha(document.getElementById('admin-captcha'),'login');if(!challenge.token())throw new Error('Complete human verification first.');const fd=new FormData(login);const result=await client.auth.signInWithPassword({email:fd.get('email'),password:fd.get('password'),options:{captchaToken:challenge.token()}});if(result.error)throw new Error('Sign-in failed. Check your credentials.');login.reset();await authenticate();}catch(error){show(error.message,true);}finally{button.disabled=false;challenge?.reset();}});
  mfa.addEventListener('submit',async e=>{e.preventDefault();const button=mfa.querySelector('button');button.disabled=true;try{const result=await client.auth.mfa.challengeAndVerify({factorId,code:new FormData(mfa).get('code')});if(result.error)throw new Error('Invalid or expired authenticator code.');mfa.reset();await authenticate();}catch(error){show(error.message,true);}finally{button.disabled=false;}});
  document.getElementById('admin-logout-btn').addEventListener('click',async()=>{await client.auth.signOut();location.reload();});
  document.getElementById('save-controls').addEventListener('click',e=>action(e.currentTarget,()=>rpc('testimony_set_controls',{p_intake:document.getElementById('control-intake').checked,p_publishing:document.getElementById('control-publishing').checked,p_screening:document.getElementById('control-screening').checked})));
  document.getElementById('pause-all').addEventListener('click',e=>action(e.currentTarget,()=>rpc('testimony_set_controls',{p_intake:false,p_publishing:false,p_screening:false})));
  document.getElementById('queue-previous').addEventListener('click',()=>{offset=Math.max(0,offset-20);refresh().catch(error=>show(error.message,true));});
  document.getElementById('queue-next').addEventListener('click',()=>{offset+=20;refresh().catch(error=>show(error.message,true));});
  document.getElementById('approved-previous').addEventListener('click',()=>{approvedOffset=Math.max(0,approvedOffset-20);refresh().catch(error=>show(error.message,true));});
  document.getElementById('approved-next').addEventListener('click',()=>{approvedOffset+=20;refresh().catch(error=>show(error.message,true));});
  document.getElementById('refresh-reviews').addEventListener('click',()=>refresh().catch(error=>show(error.message,true)));
  try{await authenticate();}catch(error){show(error.message,true);}
})();
