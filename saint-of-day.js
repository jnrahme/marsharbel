/* Mount reviewed template content only on its New York publication date. */
(function () {
  var card = null;
  function refresh() {
    var parts = new Intl.DateTimeFormat('en-US', {
      timeZone: 'America/New_York', year: 'numeric', month: '2-digit', day: '2-digit'
    }).formatToParts(new Date());
    var values = {};
    parts.forEach(function (part) { values[part.type] = part.value; });
    var today = values.year + '-' + values.month + '-' + values.day;
    var match = null;
    document.querySelectorAll('template[data-saint-date]').forEach(function (template) {
      if (template.getAttribute('data-saint-date') === today) match = template;
    });
    if (card && card.getAttribute('data-saint-date') !== today) {
      card.remove();
      card = null;
    }
    if (match && !card) {
      var anchor = document.querySelector(match.getAttribute('data-saint-after'));
      if (!anchor) return;
      var fragment = document.importNode(match.content, true);
      card = fragment.querySelector('#saint-of-the-day');
      if (!card) return;
      anchor.after(fragment);
    }
  }
  refresh();
  document.addEventListener('visibilitychange', refresh);
  setInterval(refresh, 60000);
}());
