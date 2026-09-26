// Prayer finder: filters the prayer-page cards on prayer-library by what the
// visitor types. Cards carry data-keywords; matching is case-insensitive
// substring over title + keywords. No network, no storage.
(function () {
  var input = document.getElementById('prayer-finder-q');
  var grid = document.getElementById('prayer-finder-grid');
  var empty = document.getElementById('prayer-finder-empty');
  if (!input || !grid) return;
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
  });
})();
