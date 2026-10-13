/* Mount reviewed template content only on its New York publication date. */
(function () {
  var template = document.getElementById('saint-of-the-day-template');
  if (!template || !template.content) return;
  var card = null;
  function refresh() {
    var parts = new Intl.DateTimeFormat('en-US', {
      timeZone: 'America/New_York', year: 'numeric', month: '2-digit', day: '2-digit'
    }).formatToParts(new Date());
    var values = {};
    parts.forEach(function (part) { values[part.type] = part.value; });
    var active = template.getAttribute('data-saint-date') === values.year + '-' + values.month + '-' + values.day;
    if (active && !card) {
      var anchor = document.querySelector(template.getAttribute('data-saint-after'));
      if (!anchor) return;
      var fragment = document.importNode(template.content, true);
      card = fragment.querySelector('#saint-of-the-day');
      if (!card) return;
      anchor.after(fragment);
    } else if (!active && card) {
      card.remove();
      card = null;
    }
  }
  refresh();
  document.addEventListener('visibilitychange', refresh);
  setInterval(refresh, 60000);
}());
