/* Music page: one player, a track list, continuous playback. The YouTube player API loads on the first tap. */
(function () {
  var root = document.querySelector('[data-playlist]');
  if (!root) return;
  var items = Array.prototype.slice.call(root.querySelectorAll('.track'));
  function idxOf(it) { return it.dataset.ytIndex ? parseInt(it.dataset.ytIndex, 10) : 0; }
  var el = function (s) { return root.querySelector(s); };
  var titleEl = el('[data-now-title]'), translitEl = el('[data-now-translit]'), creditEl = el('[data-now-credit]');
  var upNext = el('[data-up-next]'), openEl = el('[data-open]'), labelEl = el('[data-now-label]');
  var player = null, apiState = 'idle', index = 0, pending = null, playing = false;

  /* Labels come from the locale's music-playlist catalog: inlined as #sc-playlist-labels on mirrors, fetched from the English catalog otherwise. */
  var labels = {};
  function lab(k) { var v = labels['playlist.' + k]; return typeof v === 'string' ? v : ''; }
  function loadLabels() {
    var cfg = document.getElementById('sc-playlist-labels');
    if (cfg) { try { return Promise.resolve(JSON.parse(cfg.textContent)); } catch (e) { return Promise.resolve({}); } }
    return fetch('/locales/en/music-playlist.json').then(function (r) { return r.ok ? r.json() : {}; }).catch(function () { return {}; });
  }
  function text(i, sel) { return items[i].querySelector(sel); }
  function show(i) {
    index = i;
    items.forEach(function (li, k) {
      if (k === i) li.setAttribute('aria-current', 'true'); else li.removeAttribute('aria-current');
    });
    var it = items[i];
    titleEl.textContent = text(i, '.track-title').textContent;
    translitEl.textContent = text(i, '.track-translit').textContent;
    creditEl.innerHTML = text(i, '.track-credit').innerHTML;
    openEl.href = it.dataset.ytList ? 'https://www.youtube.com/playlist?list=' + it.dataset.ytList + '&index=' + (idxOf(it) + 1) : 'https://www.youtube.com/watch?v=' + it.dataset.yt;
    var n = items[i + 1];
    upNext.textContent = n ? lab('upNext') + text(i + 1, '.track-translit').textContent : lab('lastTrack');
    root.classList.toggle('is-playing', playing);
  }
  function setPlaying(v) { playing = v; root.classList.toggle('is-playing', v); labelEl.textContent = v ? lab('nowPlaying') : lab('selected'); }

  function loadApi(cb) {
    if (apiState === 'ready') return cb();
    pending = cb;
    if (apiState === 'loading') return;
    apiState = 'loading';
    var prev = window.onYouTubeIframeAPIReady;
    window.onYouTubeIframeAPIReady = function () {
      if (prev) prev();
      player = new YT.Player('playlist-player', {
        host: 'https://www.youtube-nocookie.com',
        events: {
          onReady: function () { apiState = 'ready'; var f = pending; pending = null; if (f) f(); },
          onStateChange: function (e) {
            if (e.data === 1) {
              setPlaying(true);
              var cur = items[index];
              if (cur.dataset.ytList) {
                var pi = player.getPlaylistIndex();
                if (pi !== idxOf(cur)) for (var k = 0; k < items.length; k++) if (items[k].dataset.ytList === cur.dataset.ytList && idxOf(items[k]) === pi) { show(k); setPlaying(true); break; }
              }
            }
            else if (e.data === 2) setPlaying(false);
            else if (e.data === 0) {
              setPlaying(false);
              var inList = items[index].dataset.ytList;
              if (inList) { var nx = items[index + 1]; if (nx && nx.dataset.ytList === inList) return; }
              if (index < items.length - 1) play(index + 1);
            }
          },
          onError: function () { setPlaying(false); if (index < items.length - 1) play(index + 1); }
        }
      });
    };
    var s = document.createElement('script');
    s.src = 'https://www.youtube.com/iframe_api';
    s.onerror = function () { apiState = 'failed'; openEl.focus(); };
    document.head.appendChild(s);
  }
  function play(i) {
    show(i);
    loadApi(function () {
      var d = items[i].dataset;
      if (d.ytList) player.loadPlaylist({ listType: 'playlist', list: d.ytList, index: idxOf(items[i]) });
      else player.loadVideoById(d.yt);
    });
  }
  items.forEach(function (li, i) {
    li.querySelector('.track-play').addEventListener('click', function () { play(i); });
  });
  el('[data-next]').addEventListener('click', function () { if (index < items.length - 1) play(index + 1); });
  el('[data-prev]').addEventListener('click', function () { if (index > 0) play(index - 1); });
  show(0);
  loadLabels().then(function (l) { labels = l; show(index); setPlaying(playing); });
})();
