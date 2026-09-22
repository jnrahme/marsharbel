(async function () {
  'use strict';
  const { client, config, configured, node, status, rpc, captcha } = window.Testimony;
  const form = document.getElementById('account-login'); const message = document.getElementById('account-status');
  const panel = document.getElementById('account-panel'); const list = document.getElementById('my-testimonies');
  const button = form.querySelector('button'); let challenge;
  if (!configured || !config.accountsEnabled) { status(message, 'Accounts are safely paused while the protected service is connected.'); return; }
  form.querySelector('input').disabled = false;
  async function refresh() {
    const { data: { session } } = await client.auth.getSession();
    form.hidden = Boolean(session); panel.hidden = !session;
    if (!session) {
      list.replaceChildren();
      if (!challenge) challenge = await captcha(document.getElementById('account-captcha'), 'login');
      button.disabled = false; return;
    }
    status(message, 'Signed in. Only you and the moderator can see these submissions.');
    const { data, error } = await client.from('testimony_submissions').select('id,display_name,story,status,revision,author_message,created_at').eq('author_id', session.user.id).order('created_at', { ascending: false }).limit(50);
    if (error) throw new Error('Your stories could not be loaded. Please try again.');
    list.replaceChildren();
    if (!data.length) list.append(node('p', 'You have not submitted a story yet.'));
    for (const row of data) {
      const card = node('article', null, 'card testimony-card');
      card.append(node('h3', row.display_name), node('p', row.status.replaceAll('_',' '), 'tag'), node('p', row.story, 'testimony-text'));
      if (row.author_message) card.append(node('p', `Moderator: ${row.author_message}`));
      if (!['withdrawn','rejected'].includes(row.status)) {
        const edit = node('details'); edit.append(node('summary', 'Edit this story'));
        const editForm = node('form', null, 'testimony-form');
        const nameLabel = node('label', 'Public display name'); const name = node('input'); name.value = row.display_name; name.required = true; name.minLength = 2; name.maxLength = 80; nameLabel.append(name);
        const storyLabel = node('label', 'Revised testimony'); const story = node('textarea'); story.value = row.story; story.required = true; story.minLength = 60; story.maxLength = 7000; storyLabel.append(story);
        const save = node('button', 'Save and send for review', 'btn primary'); save.type = 'submit';
        editForm.append(nameLabel, storyLabel, node('p', 'Saving removes any published version immediately. The revised story will receive new screening and human review.'), save);
        editForm.addEventListener('submit', async e => {
          e.preventDefault(); save.disabled = true;
          try { await rpc('testimony_author_action', { p_id: row.id, p_action: 'edit', p_revision: row.revision, p_payload: { display_name: name.value.trim(), story: story.value.trim() } }); await refresh(); }
          catch (error) { status(message, error.message, true); } finally { save.disabled = false; }
        });
        edit.append(editForm); card.append(edit);
        const withdraw = node('button', 'Withdraw and remove from website', 'btn subtle'); withdraw.type = 'button';
        withdraw.addEventListener('click', async () => {
          if (!window.confirm('Withdraw this testimony? Any public version will be removed immediately.')) return;
          withdraw.disabled = true;
          try { await rpc('testimony_author_action', { p_id: row.id, p_action: 'withdraw', p_revision: row.revision }); await refresh(); }
          catch (error) { status(message, error.message, true); } finally { withdraw.disabled = false; }
        }); card.append(withdraw);
      }
      list.append(card);
    }
  }
  form.addEventListener('submit', async e => {
    e.preventDefault(); if (!challenge?.token()) return status(message, 'Complete the human verification first.', true);
    button.disabled = true;
    try {
      const { error } = await client.auth.signInWithOtp({ email: new FormData(form).get('email'), options: { emailRedirectTo: new URL('account.html', location.href).href, captchaToken: challenge.token() } });
      if (error) throw new Error('Unable to send a sign-in link. Please try again later.');
      status(message, 'Check your email for a sign-in link. Follow it to verify your address and open your account.');
    } catch (error) { status(message, error.message, true); }
    finally { challenge.reset(); button.disabled = false; }
  });
  document.getElementById('account-logout').addEventListener('click', async () => { await client.auth.signOut(); location.reload(); });
  client.auth.onAuthStateChange(event => { if (event === 'INITIAL_SESSION') return; setTimeout(() => refresh().catch(error => status(message, error.message, true)), 0); });
  try { await refresh(); } catch (error) { status(message, error.message, true); }
})();
