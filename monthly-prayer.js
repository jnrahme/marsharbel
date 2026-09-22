(() => {
  'use strict';

  const section = document.getElementById('monthly-prayer');
  if (!section) return;

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
    status.textContent = active ? 'We are united in prayer today' : 'Our monthly invitation';

    if (active) {
      timing.textContent = day === 21
        ? 'Today, we prepare our hearts. Tomorrow, we gather in prayer.'
        : 'Today is our monthly day of prayer. Bring your heart to Christ.';
    } else {
      const nextGathering = new Date(now.getFullYear(), now.getMonth() + (day > 22 ? 1 : 0), 21);
      const month = new Intl.DateTimeFormat(document.documentElement.lang || 'en', { month: 'long' }).format(nextGathering);
      timing.textContent = `Our next gathering: ${month} 21 & 22. Begin preparing in prayer today.`;
    }
  }

  updatePrayerDay();
  window.setInterval(updatePrayerDay, 60_000);
  document.addEventListener('visibilitychange', () => {
    if (!document.hidden) updatePrayerDay();
  });
})();
