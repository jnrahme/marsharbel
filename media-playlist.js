/* Music page: one player, a track list, continuous playback. The YouTube player API loads on the first tap. */
(function () {
  var root = document.querySelector('[data-playlist]');
  if (!root) return;
  var items = Array.prototype.slice.call(root.querySelectorAll('.track'));
  var el = function (s) { return root.querySelector(s); };
  var titleEl = el('[data-now-title]'), translitEl = el('[data-now-translit]'), creditEl = el('[data-now-credit]');
  var upNext = el('[data-up-next]'), openEl = el('[data-open]'), labelEl = el('[data-now-label]');
  var player = null, apiState = 'idle', index = 0, pending = null, playing = false;

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
    openEl.href = 'https://www.youtube.com/watch?v=' + it.dataset.yt;
    var n = items[i + 1];
    upNext.textContent = n ? 'Up next: ' + text(i + 1, '.track-translit').textContent : 'Last track in the playlist';
    root.classList.toggle('is-playing', playing);
  }
  function setPlaying(v) { playing = v; root.classList.toggle('is-playing', v); labelEl.textContent = v ? 'Now playing' : 'Selected'; }

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
            if (e.data === 1) setPlaying(true);
            else if (e.data === 2) setPlaying(false);
            else if (e.data === 0) { setPlaying(false); if (index < items.length - 1) play(index + 1); }
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
    loadApi(function () { player.loadVideoById(items[i].dataset.yt); });
  }
  items.forEach(function (li, i) {
    li.querySelector('.track-play').addEventListener('click', function () { play(i); });
  });
  el('[data-next]').addEventListener('click', function () { if (index < items.length - 1) play(index + 1); });
  el('[data-prev]').addEventListener('click', function () { if (index > 0) play(index - 1); });
  show(0);
})();
