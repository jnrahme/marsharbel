(function () {
  'use strict';
  const title = document.getElementById('result-title');
  const text = document.getElementById('result-text');
  const actions = document.getElementById('result-actions');
  const message = document.getElementById('result-status');
  const params = new URLSearchParams(location.search);
  const state = params.get('r') || '';
  const token = params.get('token') || '';
  const tokenOk = /^[0-9a-f-]{36}\.[0-9a-f]{64}$/.test(token);

  const link = (href, label, cls) => {
    const a = document.createElement('a');
    a.className = cls || 'btn primary';
    a.href = href;
    a.textContent = label;
    return a;
  };
  const show = (heading, body, ctaNodes) => {
    title.textContent = heading;
    text.textContent = body;
    actions.replaceChildren(...ctaNodes);
    document.title = heading + ' | Saint Charbel';
  };
  const states = {
    confirmed: () => show('You are subscribed',
      'Your subscription is confirmed. Tomorrow morning you will receive the rosary mystery of the day, a link to the Maronite prayers of the day, and a prayer to Saint Charbel.',
      [link('./', 'Back to marsharbel.com')]),
    ended: () => show('Subscription ended',
      'This subscription was ended. You can subscribe again any time from the daily prayer page.',
      [link('./daily-prayer', 'Subscribe again')]),
    invalid: () => show('Link not recognized',
      'This link is not valid or has already been used. If you already confirmed, you are all set - nothing more to do. Otherwise, sign up again to get a fresh link.',
      [link('./daily-prayer', 'Daily prayer page')]),
    paused: () => show('Temporarily paused',
      'The subscription service is temporarily paused. Please try the link again later.',
      [link('./', 'Back to marsharbel.com')]),
    unsubscribed: () => show('You are unsubscribed',
      'Done - no further daily prayer emails will arrive. Thank you for praying with us.',
      [link('./daily-prayer', 'Subscribe again')]),
    'already-unsubscribed': () => show('Already unsubscribed',
      'This address is already off the daily prayer list. No further emails will arrive.',
      [link('./daily-prayer', 'Subscribe again')]),
    error: () => show('Something went wrong',
      'We could not complete that request. Please try the link again, and if it keeps failing, sign up again from the daily prayer page.',
      [link('./daily-prayer', 'Daily prayer page')]),
    'confirm-unsub': () => {
      if (!tokenOk) { states.invalid(); return; }
      const confirm = document.createElement('button');
      confirm.type = 'button';
      confirm.className = 'btn primary';
      confirm.textContent = 'Yes, unsubscribe me';
      confirm.addEventListener('click', async () => {
        confirm.disabled = true;
        message.textContent = 'Unsubscribing you. Please wait…';
        try {
          const base = (window.TESTIMONY_CONFIG || {}).supabaseUrl || '';
          const response = await fetch(`${base}/functions/v1/unsubscribe-prayer?token=${encodeURIComponent(token)}`, { method: 'POST' });
          const data = await response.json().catch(() => ({}));
          if (response.ok && (data.ok || data.already)) {
            states.unsubscribed();
            message.textContent = '';
          } else {
            show('Link not recognized', 'This unsubscribe link is no longer valid. If you are still receiving emails, use the unsubscribe link in the latest one.', [link('./daily-prayer', 'Daily prayer page')]);
            message.textContent = '';
          }
        } catch {
          confirm.disabled = false;
          message.textContent = 'We could not reach the subscription service. Check your connection and try again.';
        }
      });
      show('Unsubscribe from the daily prayer?',
        'Are you sure? You will stop receiving the daily rosary mystery, the Maronite prayers of the day, and the Saint Charbel prayer.',
        [confirm, link('./daily-prayer', 'Keep my subscription', 'btn subtle')]);
    }
  };
  (states[state] || states.invalid)();
})();
