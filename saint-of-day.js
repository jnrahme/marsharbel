/* Show a dated reviewed unit only on its date in the publication timezone. */
(function () {
  var card = document.getElementById('saint-of-the-day');
  if (!card) return;
  function refresh() {
    var parts = new Intl.DateTimeFormat('en-US', {
      timeZone: 'America/New_York', year: 'numeric', month: '2-digit', day: '2-digit'
    }).formatToParts(new Date());
    var values = {};
    parts.forEach(function (part) { values[part.type] = part.value; });
    card.hidden = card.getAttribute('data-saint-date') !== values.year + '-' + values.month + '-' + values.day;
  }
  refresh();
  document.addEventListener('visibilitychange', refresh);
  setInterval(refresh, 60000);
}());
