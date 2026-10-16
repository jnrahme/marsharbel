// Progressive enhancement: the static home news rows are the crawlable fallback. When the content
// API answers with a valid, different list, the rows are rebuilt from it. Any failure leaves the
// server-rendered HTML untouched.
(function () {
  var API = 'https://api.marsharbel.com/api/v1/news';
  var box = document.querySelector('#latest-news .home-news-rows');
  if (!box || !window.fetch) return;
  var loc = (document.documentElement.lang || 'en').slice(0, 2);
  var safe = function (s, re) { return typeof s === 'string' && re.test(s); };
  var ctl = new AbortController();
  var t = setTimeout(function () { ctl.abort(); }, 4000);
  fetch(API + '?locale=' + encodeURIComponent(loc) + '&limit=12', { signal: ctl.signal, credentials: 'omit' })
    .then(function (r) { if (!r.ok) throw new Error('api'); return r.json(); })
    .then(function (d) {
      clearTimeout(t);
      if (d.fallback && loc !== 'en') return;
      var rows = (d.items || []).filter(function (i) {
        return i.kind === 'row' && i.title && safe(i.href, /^\/[^/]/) && i.image && safe(i.image.src, /^\/media\//);
      }).slice(0, 5);
      if (rows.length < 3) return;
      var same = Array.prototype.map.call(box.querySelectorAll('a.home-news-row'), function (a) { return a.getAttribute('href'); }).join('|') ===
        rows.map(function (i) { return i.href; }).join('|');
      if (same) return;
      var frag = document.createDocumentFragment();
      rows.forEach(function (i) {
        var a = document.createElement('a'); a.className = 'home-news-row'; a.href = i.href;
        var ph = document.createElement('span'); ph.className = 'home-news-photo';
        var im = document.createElement('img'); im.src = i.image.src; im.alt = i.image.alt || '';
        if (i.image.width) im.width = i.image.width; if (i.image.height) im.height = i.image.height;
        im.loading = 'lazy'; im.decoding = 'async'; ph.appendChild(im);
        var cp = document.createElement('span'); cp.className = 'home-news-copy';
        [['home-news-meta', i.date], ['home-news-title', i.title], ['home-news-credit', i.credit]].forEach(function (p) {
          if (!p[1]) return; var s = document.createElement('span'); s.className = p[0]; s.textContent = p[1]; cp.appendChild(s);
        });
        a.appendChild(ph); a.appendChild(cp); frag.appendChild(a);
      });
      box.replaceChildren(frag);
    })
    .catch(function () { clearTimeout(t); });
})();
