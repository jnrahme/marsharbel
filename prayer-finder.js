// Prayer finder: filters the prayer-page cards on prayer-library by what the
// visitor types. Cards carry data-keywords; matching is case-insensitive
// substring over title + keywords. No network, no storage.
(function () {
  var input = document.getElementById('prayer-finder-q');
  var grid = document.getElementById('prayer-finder-grid');
  var empty = document.getElementById('prayer-finder-empty');
  if (!input || !grid) return;
  // Screen-reader announcement of the result count. English only until native-reviewed translations exist.
  var msgs = {
    en: ['No prayer pages match.', '1 prayer page shown.', '{n} prayer pages shown.']
  };
  var set = msgs.en;
  var live = document.createElement('p');
  live.id = 'prayer-finder-count';
  live.className = 'sr-only';
  live.setAttribute('role', 'status');
  live.setAttribute('aria-live', 'polite');
  live.style.cssText = 'position:absolute;width:1px;height:1px;margin:-1px;padding:0;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0';
  grid.parentNode.insertBefore(live, grid);
  var timer;
  function announce(n) {
    clearTimeout(timer);
    timer = setTimeout(function () {
      live.textContent = n === 0 ? set[0] : n === 1 ? set[1] : set[2].replace('{n}', n);
    }, 400);
  }
  var cards = Array.prototype.slice.call(grid.querySelectorAll('.prayer-finder-card'));
  var index = cards.map(function (card) {
    return {
      el: card,
      text: (card.textContent + ' ' + (card.getAttribute('data-keywords') || '')).toLowerCase()
    };
  });
  input.addEventListener('input', function () {
    var q = input.value.trim().toLowerCase();
    var words = q.split(/\s+/).filter(Boolean);
    var shown = 0;
    index.forEach(function (item) {
      var hit = words.every(function (w) { return item.text.indexOf(w) !== -1; });
      item.el.style.display = hit ? '' : 'none';
      if (hit) shown++;
    });
    if (empty) empty.hidden = shown !== 0;
    announce(shown);
  });
})();
