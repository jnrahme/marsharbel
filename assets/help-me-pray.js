// Help Me Pray: renders localized cards from /assets/help-me-pray-data.json.
// Contract: no prayer body text, Begin disabled until per-card gates close,
// no English fallback (missing locale renders nothing but the chrome notice).
const NEED_ORDER = ['restart', 'family', 'illness', 'gratitude', 'discouragement', 'maronite'];

function el(tag, cls, text) {
  const n = document.createElement(tag);
  if (cls) n.className = cls;
  if (text !== undefined) n.textContent = text;
  return n;
}

function renderCard(card, ui, page) {
  const c = card.copy;
  const art = el('article', 'hmp-card');
  art.appendChild(el('h3', null, c.question));
  if (!card.beginEnabled) art.appendChild(el('span', 'hmp-status', ui.inReview));
  const ans = el('div', 'hmp-field');
  ans.appendChild(el('p', 'hmp-label', ui.practicalAnswer));
  for (const line of c.practicalAnswer.split('\n')) if (line.trim()) ans.appendChild(el('p', null, line));
  art.appendChild(ans);
  const why = el('div', 'hmp-field');
  why.appendChild(el('p', 'hmp-label', ui.why));
  why.appendChild(el('p', null, c.why));
  art.appendChild(why);
  const src = el('div', 'hmp-field');
  src.appendChild(el('p', 'hmp-label', ui.source));
  let srcLine = c['source.publisher'] + ' - ' + c['source.section'] + ' · ' + c['source.label'];
  if (card.sourceAuthor) srcLine += ' · ' + card.sourceAuthor;
  src.appendChild(el('p', null, srcLine));
  const more = el('a', null, ui.readMore);
  more.href = card.sourceURL;
  more.rel = 'noopener noreferrer';
  more.target = '_blank';
  src.appendChild(more);
  art.appendChild(src);
  const pt = el('div', 'hmp-field');
  pt.appendChild(el('p', 'hmp-label', ui.practiceType));
  pt.appendChild(el('p', null, c.practiceType));
  art.appendChild(pt);
  const bound = el('div', 'hmp-field');
  bound.appendChild(el('p', 'hmp-label', ui.boundary));
  bound.appendChild(el('p', null, c.boundaryNote));
  art.appendChild(bound);
  const target = el('div', 'hmp-field');
  target.appendChild(el('p', 'hmp-label', c['prayerTarget.heading'] + ' (' + c['prayerTarget.type'] + ')'));
  art.appendChild(target);
  const begin = el('button', 'hmp-begin', ui.begin);
  begin.disabled = !card.beginEnabled;
  if (!card.beginEnabled) target.appendChild(el('p', 'hmp-notready', ui.notReady));
  art.appendChild(begin);
  return art;
}

async function boot() {
  const app = document.getElementById('hmp-app');
  if (!app) return;
  const lang = document.documentElement.lang || 'en';
  let data;
  try {
    data = await (await fetch('/assets/help-me-pray-data.json')).json();
  } catch (e) { return; }
  const pack = data[lang];
  if (!pack) return;
  const { ui, cards, needs } = pack;
  const byNeed = {};
  for (const [id, card] of Object.entries(cards)) {
    (byNeed[card.needKey] = byNeed[card.needKey] || []).push([id, card]);
  }
  const sections = {};
  for (const need of NEED_ORDER) {
    const sec = el('section', 'hmp-need');
    sec.id = 'need-' + need;
    sec.appendChild(el('h2', null, needs[need] || ''));
    const list = el('div', 'hmp-list');
    const rows = byNeed[need] || [];
    if (!rows.length) list.appendChild(el('p', null, ui.noResults));
    for (const [, card] of rows) list.appendChild(renderCard(card, ui, pack.page));
    sec.appendChild(list);
    sections[need] = sec;
    app.appendChild(sec);
  }
  const nav = document.getElementById('hmp-nav');
  if (nav) {
    nav.addEventListener('click', (ev) => {
      const a = ev.target.closest('a[data-need]');
      if (!a) return;
      ev.preventDefault();
      const need = a.dataset.need;
      const active = a.getAttribute('aria-pressed') === 'true';
      for (const link of nav.querySelectorAll('a[data-need]')) link.setAttribute('aria-pressed', 'false');
      for (const [k, sec] of Object.entries(sections)) sec.hidden = !active && k !== need;
      if (!active) a.setAttribute('aria-pressed', 'true');
    });
  }
}

boot();
