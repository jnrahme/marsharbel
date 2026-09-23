(async function () {
  'use strict';
  const { client, config, configured, node, status, rpc, captcha } = window.Testimony;
  const login = document.getElementById('admin-login-form'); const message = document.getElementById('admin-status');
  const panel = document.getElementById('admin-panel'); const mfa = document.getElementById('admin-mfa-form');
  const pending = document.getElementById('pending-list'); const approved = document.getElementById('approved-list');
  let factorId; let challenge; let approvedOffset = 0; let offset = 0; let busy = false;
  const show = (text, error = false) => status(message, text, error);
  const retryAccess = node('button','Retry loading admin panel','btn subtle');
  retryAccess.type='button'; retryAccess.hidden=true; message.after(retryAccess);
  const accessFailure = error => { show(error.message,true); retryAccess.hidden=false; };
  retryAccess.addEventListener('click',async()=>{retryAccess.disabled=true;try{await authenticate();}catch(error){accessFailure(error);}finally{retryAccess.disabled=false;}});
  const demo = ['localhost', '127.0.0.1'].includes(location.hostname) && new URLSearchParams(location.search).get('demo') === '1';
  const demoRows = [
    ['Hope during a difficult week', 'FICTIONAL DEMO: During a stressful week, I made time for prayer each evening. Remembering Saint Charbel helped me slow down and reach out to my family for support. I felt more hopeful by the end of the week.', 'A straightforward personal account for practicing approval.'],
    ['A story needing more detail', 'FICTIONAL DEMO: Something meaningful happened after I prayed for Saint Charbel’s intercession. I would like to share my experience, but I have not included when it happened or what changed in my daily life.', 'Practice requesting clarification: ask what happened and when.'],
    ['Promotional submission', 'FICTIONAL DEMO: Please publish an advertisement for my online shop in the testimony section. This message is a promotional example rather than a personal story of prayer or an experience of Saint Charbel’s intercession.', 'Practice rejecting unrelated promotional content.']
  ].map(([name, story, summary], index) => ({id:`demo-${index+1}`,display_name:`DEMO ${index+1} — ${name}`,story,status:'pending',review_state:'complete',revision:1,review_notes:{summary:`Simulated review, not AI output. ${summary}`,recommendation:'review',flags:[],questions:[]}}));
  const initialDemos = JSON.stringify(demoRows);
  const feedback = node('p', '', 'admin-feedback');
  feedback.id = 'admin-feedback'; feedback.setAttribute('role','status'); feedback.tabIndex = -1; feedback.hidden = true;
  panel.prepend(feedback);
  const announce = (text, error = false) => {
    feedback.textContent = text; feedback.hidden = false;
    feedback.classList.toggle('warn', error); feedback.focus();
  };
  async function moderate(row, kind, reason, override) {
    if (!demo) return rpc('testimony_moderate', { p_id:row.id, p_revision:row.revision, p_action:kind, p_reason:reason, p_override:override });
    if (['reject','clarify'].includes(kind) && reason.length < 10) throw new Error('Add a reason of at least 10 characters.');
    row.status = {approve:'approved',reject:'rejected',clarify:'needs_clarification',unpublish:'pending'}[kind];
    row.revision++;
    row.author_message = reason;
    const audit = document.getElementById('audit-list');
    audit.prepend(node('li', `DEMO: ${row.display_name} — ${kind}${reason ? `: ${reason}` : ''}`));
  }
  if (!configured || !config.moderationEnabled) {
    // Allow typing without implying that backend setup is complete. Block native
    // form submission too, so pressing Enter cannot put credentials in the URL.
    login.addEventListener('submit', event => event.preventDefault());
    const button = login.querySelector('button[type="submit"]');
    button.disabled = true;
    button.textContent = 'Sign-in unavailable during setup';
    login.setAttribute('aria-describedby', 'admin-status');
    show('You can type in these fields. Sign-in is not enabled yet: the admin account and security setup must be completed first. Nothing entered here is submitted while setup is paused.');
    return;
  }
  if (config.moderatorMfaRequired === false) {
    document.querySelector('.security-note span').textContent = 'Only the site moderator can review private submissions or publish stories. Sign in with your email, password, and human verification. Two-step verification is temporarily disabled. Moderation actions are recorded in the audit history.';
  }
  async function action(button, fn, success = 'Changes saved.') {
    if (busy) return; busy = true; button.disabled = true;
    try { await fn(); await refresh(); announce(success); } catch (error) { announce(error.message, true); }
    finally { busy = false; button.disabled = false; }
  }
  function card(row) {
    const article = node('article', null, 'card testimony-card');
    article.append(node('h3', row.display_name), node('p', `${row.status.replaceAll('_', ' ')} · screening: ${row.review_state} · revision ${row.revision}`), node('p', row.story, 'testimony-text'));
    if (row.review_notes) {
      const review = node('details'); review.open = true; review.append(node('summary', demo ? 'Practice review notes' : row.review_notes.source === 'human' ? 'Moderator review notes' : 'AI screening notes — not verification'));
      review.append(node('p', row.review_notes.summary || 'No summary'), node('p', `Suggested handling: ${row.review_notes.recommendation || 'human review'}`));
      for (const flag of row.review_notes.flags || []) review.append(node('p', `Flag: ${flag.replaceAll('_', ' ')}`));
      if (row.review_notes.duplicate) review.append(node('p', 'An exact duplicate exists in the private queue.'));
      for (const question of row.review_notes.questions || []) review.append(node('p', question));
      article.append(review);
    }
    if (row.author_message) article.append(node('p', `Your last decision reason: ${row.author_message}`));
    if (row.status === 'needs_clarification') {
      article.append(node('p', 'Waiting for the author to revise their story before it can be approved.'));
      if (demo) {
        const reply = node('button', 'Simulate author reply', 'btn subtle'); reply.type = 'button';
        reply.addEventListener('click', () => action(reply, async () => {
          row.story += '\nFICTIONAL DEMO UPDATE: This happened during a difficult week in September. Prayer helped me reach out to my family and feel less alone.';
          row.status='pending'; row.revision++; row.author_message='';
        }, 'Demo reply received. The story is ready for review again.'));
        article.append(reply);
      }
    }
    const label = node('label', 'Message to author / decision reason'); label.className = 'testimony-form';
    const reason = node('textarea'); reason.maxLength = 1000; reason.rows = 3; label.append(reason); article.append(label);
    const reasonHelp = node('p', 'To reject, request clarification, or unpublish, enter a reason of at least 10 characters.');
    reasonHelp.id = `reason-help-${row.id}`;
    const reasonError = node('p', '', 'submit-status warn');
    reasonError.id = `reason-error-${row.id}`;
    reasonError.setAttribute('role', 'alert'); reasonError.hidden = true;
    reason.setAttribute('aria-describedby', `${reasonHelp.id} ${reasonError.id}`);
    reason.addEventListener('input', () => { reasonError.hidden = true; reason.removeAttribute('aria-invalid'); });
    article.append(reasonHelp, reasonError);
    const overrideLabel = node('label', null, 'inline-check'); const override = node('input'); override.type = 'checkbox';
    overrideLabel.append(override, document.createTextNode('Override the daily publication cap (requires a reason).')); if (!demo) article.append(overrideLabel);
    const buttons = node('div', null, 'cta-row');
    for (const [kind, title] of row.status === 'approved' ? [['unpublish','Unpublish']] : [['approve','Approve and publish'],['clarify','Request clarification'],['reject','Reject']]) {
      if (!demo && !row.author_id && kind === 'clarify') continue;
      const button = node('button', demo && kind === 'approve' ? 'Approve demo' : title, 'btn subtle'); button.type = 'button';
      if (kind === 'approve') button.disabled = row.status !== 'pending' || row.review_state !== 'complete';
      button.addEventListener('click', () => {
        const needsReason = kind !== 'approve' || override.checked;
        if (needsReason && reason.value.trim().length < 10) {
          reasonError.textContent = 'Please enter a reason of at least 10 characters above, then try again.';
          reasonError.hidden = false; reason.setAttribute('aria-invalid', 'true');
          reason.focus(); return;
        }
        const resultText = {approve:demo?'Demo approved. See Approved below; nothing was published.':'Story approved and published.',reject:'Story rejected and removed from the pending queue.',clarify:'Clarification requested. The story is waiting for an author reply.',unpublish:demo?'Demo returned to the pending queue.':'Story unpublished and returned for review.'}[kind];
        return action(button, () => moderate(row, kind, reason.value.trim(), kind === 'approve' && override.checked), resultText);
      });
      buttons.append(button);
    }
    if (!demo && row.status === 'pending' && row.review_state !== 'complete') {
      const manual = node('button', 'Record my manual review', 'btn subtle'); manual.type = 'button';
      article.append(node('p', 'You can personally check this story for spam, privacy and suitability. Enter review notes of at least 30 characters, then record your review. Approval remains a separate action.'));
      manual.addEventListener('click', () => {
        if (reason.value.trim().length < 30) { reasonError.textContent = 'Enter review notes of at least 30 characters.'; reasonError.hidden = false; reason.focus(); return; }
        return action(manual, () => rpc('testimony_manual_review', {p_id:row.id,p_revision:row.revision,p_reason:reason.value.trim()}), 'Manual review recorded. Review the story again, then approve or reject it.');
      }); buttons.append(manual);
    }
    if (row.review_state === 'failed' && row.status === 'pending') {
      const retry = node('button','Retry AI screening','btn subtle'); retry.type = 'button'; retry.addEventListener('click', () => action(retry, () => rpc('testimony_retry_review', {p_id:row.id}))); buttons.append(retry);
    }
    article.append(buttons); return article;
  }
  async function refresh() {
    if (demo) {
      panel.classList.add('demo-mode');
      panel.querySelector(':scope > article').hidden = true;
      for (const id of ['save-controls','pause-all','refresh-reviews']) document.getElementById(id).disabled = true;
      if (!document.getElementById('demo-notice')) {
        const notice = node('div', null, 'security-note');
        notice.append(node('strong','DEMO PRACTICE — nothing publishes publicly.'),node('p','Try approving one story, rejecting another with a reason, and requesting clarification on the third. These fictional examples reset when you reload.'));
        const reset = node('button','Reset demo stories','btn subtle'); reset.type='button';
        reset.addEventListener('click',()=>{demoRows.splice(0,demoRows.length,...JSON.parse(initialDemos));document.getElementById('audit-list').replaceChildren();refresh();announce('Three demo stories restored.');});
        notice.append(reset);
        notice.id = 'demo-notice'; panel.prepend(notice);
        const rejected = node('section'); rejected.id='demo-rejected';
        rejected.append(node('h2','Rejected demos'),node('div',null,'testimony-grid'));
        approved.after(rejected);
      }
      pending.replaceChildren(...demoRows.filter(r=>['pending','needs_clarification'].includes(r.status)).map(card));
      approved.replaceChildren(...demoRows.filter(r=>r.status==='approved').map(card));
      if (!pending.childElementCount) pending.append(node('p','All demo stories have been reviewed. Reload to start again.'));
      if (!approved.childElementCount) approved.append(node('p','No approved demos yet. Nothing here is published.'));
      const rejectedList=document.querySelector('#demo-rejected > div');
      rejectedList.replaceChildren(...demoRows.filter(r=>r.status==='rejected').map(row=>{const item=node('article',null,'card testimony-card');item.append(node('h3',row.display_name),node('p',`Rejected: ${row.author_message}`));return item;}));
      if(!rejectedList.childElementCount)rejectedList.append(node('p','No rejected demos yet.'));
      document.getElementById('queue-position').textContent=`${demoRows.filter(r=>r.status==='pending').length} pending · ${demoRows.filter(r=>r.status==='needs_clarification').length} awaiting reply`;
      document.getElementById('approved-position').textContent='Approved demos — not published';
      for (const id of ['queue-previous','queue-next','approved-previous','approved-next']) document.getElementById(id).disabled=true;
      document.getElementById('report-list').replaceChildren(node('p','No reports in demo mode.'));
      return;
    }
    const [queue, published, controls, reports, audit] = await Promise.all([
      client.from('testimony_submissions').select('*').in('status',['pending','needs_clarification']).order('created_at',{ascending:true}).range(offset,offset+19),
      client.from('testimony_submissions').select('*').eq('status','approved').order('updated_at',{ascending:false}).range(approvedOffset,approvedOffset+19),
      client.from('testimony_controls').select('*').single(),
      client.from('testimony_reports').select('id,publication_id,reason,created_at').eq('resolved',false).order('created_at',{ascending:true}).limit(50),
      client.from('testimony_audit').select('action,reason,created_at,submission_id').order('created_at',{ascending:false}).limit(30)
    ]);
    if ([queue,published,controls,reports,audit].some(result => result.error)) throw new Error('Unable to load the review queue. Check your connection and sign in again if needed.');
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
      // Remove abandoned unverified enrollments before starting a fresh one.
      for(const factor of (factors.data.all || factors.data.totp).filter(f=>f.factor_type==='totp' && f.status!=='verified')) await client.auth.mfa.unenroll({factorId:factor.id});
      const enrolled=await client.auth.mfa.enroll({factorType:'totp',friendlyName:'Saint Charbel moderator'});
      if(enrolled.error)throw new Error('Unable to enroll an authenticator.');
      factorId=enrolled.data.id;document.getElementById('mfa-enrollment').hidden=false;
      // Supabase JS already returns the QR as an SVG data URL.
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
  document.getElementById('save-controls').addEventListener('click',e=>action(e.currentTarget,()=>rpc('testimony_set_controls',{p_intake:document.getElementById('control-intake').checked,p_publishing:document.getElementById('control-publishing').checked,p_screening:document.getElementById('control-screening').checked})));
  document.getElementById('pause-all').addEventListener('click',e=>action(e.currentTarget,()=>rpc('testimony_set_controls',{p_intake:false,p_publishing:false,p_screening:false})));
  document.getElementById('queue-previous').addEventListener('click',()=>{offset=Math.max(0,offset-20);refresh().catch(error=>show(error.message,true));});
  document.getElementById('queue-next').addEventListener('click',()=>{offset+=20;refresh().catch(error=>show(error.message,true));});
  document.getElementById('approved-previous').addEventListener('click',()=>{approvedOffset=Math.max(0,approvedOffset-20);refresh().catch(error=>show(error.message,true));});
  document.getElementById('approved-next').addEventListener('click',()=>{approvedOffset+=20;refresh().catch(error=>show(error.message,true));});
  document.getElementById('refresh-reviews').addEventListener('click',()=>refresh().catch(error=>show(error.message,true)));
  try{await authenticate();}catch(error){accessFailure(error);}
})();
