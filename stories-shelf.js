/* Shelf live search over the cards (storybook shelf and saints page). The page works without this script. */
(function () {
  var tools = document.querySelector('[data-shelf-tools]');
  var input = document.getElementById('shelf-q');
  var count = document.getElementById('shelf-count');
  var empty = document.getElementById('shelf-empty');
  var sections = Array.prototype.slice.call(document.querySelectorAll('.shelf-section'));
  var jump = document.querySelector('.shelf-jump');
  if (!tools || !input || !count || !sections.length) return;

  var cards = [];
  sections.forEach(function (section) {
    Array.prototype.forEach.call(section.querySelectorAll('.promo-card'), function (card) {
      var text = (card.getAttribute('data-keywords') || '') + ' ' + card.textContent;
      cards.push({ card: card, section: section, text: fold(text) });
    });
    Array.prototype.forEach.call(section.querySelectorAll('.shelf-card'), function (card) {
      cards.push({ card: card, section: section, text: fold((card.getAttribute('data-keywords') || '') + ' ' + card.textContent) });
    });
  });

  function fold(s) {
    return String(s).toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/[^a-z0-9 ]+/g, ' ').replace(/\s+/g, ' ');
  }

  var L = tools.dataset;
  function plural(n) { return n + ' ' + (n === 1 ? L.one : L.many); }

  function apply() {
    var terms = fold(input.value).trim().split(' ').filter(Boolean);
    var shown = 0;
    var perSection = new Map();
    cards.forEach(function (c) {
      var ok = terms.every(function (t) { return c.text.indexOf(t) !== -1; });
      c.card.hidden = !ok;
      if (ok) { shown++; perSection.set(c.section, (perSection.get(c.section) || 0) + 1); }
    });
    sections.forEach(function (s) { s.hidden = !perSection.get(s); });
    if (jump) {
      Array.prototype.forEach.call(jump.querySelectorAll('a'), function (a) {
        var s = document.getElementById(a.getAttribute('href').slice(1));
        var n = perSection.get(s) || 0;
        var badge = a.querySelector('.shelf-n');
        if (badge) badge.textContent = n;
        a.classList.toggle('is-empty', n === 0);
      });
    }
    empty.hidden = shown !== 0;
    count.textContent = terms.length ? (shown === 0 ? L.none : plural(shown) + ' ' + L.match) : plural(cards.length);
  }

  tools.hidden = false;
  input.addEventListener('input', apply);
  input.addEventListener('keydown', function (e) { if (e.which === 27 && input.value) { input.value = ''; apply(); } });
  var clear = document.querySelector('[data-shelf-clear]');
  if (clear) clear.addEventListener('click', function () { input.value = ''; apply(); input.focus(); });
  var q = new URLSearchParams(location.search).get('q');
  if (q) { input.value = q; apply(); }
})();
