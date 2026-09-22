const observer = new IntersectionObserver(
  entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('on');
      }
    });
  },
  { threshold: 0.15 }
);

document.querySelectorAll('.reveal').forEach(el => {
  // Keep initial content visible, including when JavaScript is unavailable.
  // Only animate content that starts below the viewport.
  if (el.getBoundingClientRect().top >= window.innerHeight) el.classList.add('reveal-pending');
  observer.observe(el);
});

const counters = document.querySelectorAll('[data-count]');
const animateCounter = el => {
  const target = Number(el.dataset.count || 0);
  const duration = 1100;
  const start = performance.now();

  const step = now => {
    const progress = Math.min((now - start) / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3);
    const value = Math.floor(target * eased);
    el.textContent = el.dataset.suffix
      ? `${value.toLocaleString()}${el.dataset.suffix}`
      : value.toLocaleString();

    if (progress < 1) {
      requestAnimationFrame(step);
    }
  };

  requestAnimationFrame(step);
};

const counterObserver = new IntersectionObserver(
  entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting && !entry.target.dataset.animated) {
        animateCounter(entry.target);
        entry.target.dataset.animated = 'true';
      }
    });
  },
  { threshold: 0.3 }
);

counters.forEach(el => counterObserver.observe(el));

const lentElements = {
  date: document.getElementById('lent-countdown-date'),
  days: document.getElementById('lent-days'),
  hours: document.getElementById('lent-hours'),
  minutes: document.getElementById('lent-minutes'),
  seconds: document.getElementById('lent-seconds')
};

const hasLentCountdown = Object.values(lentElements).every(Boolean);

const getGregorianEaster = year => {
  const a = year % 19;
  const b = Math.floor(year / 100);
  const c = year % 100;
  const d = Math.floor(b / 4);
  const e = b % 4;
  const f = Math.floor((b + 8) / 25);
  const g = Math.floor((b - f + 1) / 3);
  const h = (19 * a + b - d - g + 15) % 30;
  const i = Math.floor(c / 4);
  const k = c % 4;
  const l = (32 + 2 * e + 2 * i - h - k) % 7;
  const m = Math.floor((a + 11 * h + 22 * l) / 451);
  const month = Math.floor((h + l - 7 * m + 114) / 31);
  const day = ((h + l - 7 * m + 114) % 31) + 1;
  return new Date(Date.UTC(year, month - 1, day, 0, 0, 0));
};

const getMaroniteLentStart = year => {
  const easter = getGregorianEaster(year);
  const lentStart = new Date(easter);
  lentStart.setUTCDate(lentStart.getUTCDate() - 48);
  return lentStart;
};

const getNextLentStart = now => {
  const thisYear = now.getUTCFullYear();
  const current = getMaroniteLentStart(thisYear);
  return now < current ? current : getMaroniteLentStart(thisYear + 1);
};

const getLentWindow = year => {
  const start = getMaroniteLentStart(year);
  const end = new Date(start);
  end.setUTCDate(end.getUTCDate() + 40);
  return { start, end };
};

const pad = value => String(value).padStart(2, '0');
const padDayCounter = value => (value > 99 ? String(value) : pad(value));

if (hasLentCountdown) {
  const updateCountdown = () => {
    const now = new Date();
    const thisYearWindow = getLentWindow(now.getUTCFullYear());
    const inActiveLent = now >= thisYearWindow.start && now < thisYearWindow.end;
    const target = inActiveLent ? thisYearWindow.end : getNextLentStart(now);
    const diffMs = Math.max(0, target.getTime() - now.getTime());

    const totalSeconds = Math.floor(diffMs / 1000);
    const days = Math.floor(totalSeconds / 86400);
    const hours = Math.floor((totalSeconds % 86400) / 3600);
    const minutes = Math.floor((totalSeconds % 3600) / 60);
    const seconds = totalSeconds % 60;

    lentElements.days.textContent = padDayCounter(days);
    lentElements.hours.textContent = pad(hours);
    lentElements.minutes.textContent = pad(minutes);
    lentElements.seconds.textContent = pad(seconds);

    const formatted = target.toLocaleDateString(undefined, {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      timeZone: 'UTC'
    });

    lentElements.date.textContent = inActiveLent
      ? `Lent ends: ${formatted}`
      : `Next Lent starts: ${formatted}`;
  };

  updateCountdown();
  setInterval(updateCountdown, 1000);
}
