(async () => {
  'use strict';

  const section = document.getElementById('monthly-prayer');
  if (!section) return;

  const config = document.getElementById('sc-home-labels');
  const labels = config ? JSON.parse(config.textContent) : await fetch('/locales/en/home-copy.json').then(response => {
    if (!response.ok) throw new Error('HOME_CATALOG_UNAVAILABLE');
    return response.json();
  });
  const message = key => {
    const value = labels['home.runtime.monthly.' + key];
    if (typeof value !== 'string') throw new Error('HOME_MESSAGE_MISSING:' + key);
    return value;
  };
  const guide = section.querySelector('details');
  const status = section.querySelector('[data-prayer-status]');
  const timing = section.querySelector('[data-prayer-timing]');
  let previousDay = '';

  // Use the visitor's local calendar, including when a tab stays open overnight.
  // Only set the disclosure on a new day so manual open/close choices are respected.
  function updatePrayerDay() {
    const now = new Date();
    const dayKey = `${now.getFullYear()}-${now.getMonth()}-${now.getDate()}`;
    if (dayKey === previousDay) return;
    previousDay = dayKey;

    const day = now.getDate();
    const active = day === 21 || day === 22;
    section.classList.toggle('is-prayer-day', active);
    guide.open = active;
    status.textContent = active ? message('active') : message('invitation');

    if (active) {
      timing.textContent = day === 21
        ? message('prepare')
        : message('today');
    } else {
      const nextGathering = new Date(now.getFullYear(), now.getMonth() + (day > 22 ? 1 : 0), 21);
      const month = new Intl.DateTimeFormat(document.documentElement.lang || 'en', { month: 'long' }).format(nextGathering);
      timing.textContent = message('next').replace('{month}', month);
    }
  }

  updatePrayerDay();
  window.setInterval(updatePrayerDay, 60_000);
  document.addEventListener('visibilitychange', () => {
    if (!document.hidden) updatePrayerDay();
  });
})();
