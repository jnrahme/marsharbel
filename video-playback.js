/* Local YouTube iframe event adapter. No remote API script, autoplay, retry,
   telemetry, media proxy or restriction bypass. Links also work without JS. */
(() => {
  const origin = 'https://www.youtube-nocookie.com';
  const players = new Map();
  function send(frame, message) {
    frame.contentWindow?.postMessage(JSON.stringify(message), origin);
  }
  function subscribe(frame) {
    send(frame, { event: 'listening', id: frame.id, channel: 'widget' });
    send(frame, { event: 'command', func: 'addEventListener', args: ['onError'] });
  }
  for (const fallback of document.querySelectorAll('.video-fallback[data-video-id]')) {
    const frame = fallback.closest('article')?.querySelector('iframe');
    if (!frame) continue;
    const url = new URL(frame.src);
    if (url.origin !== origin || url.pathname !== `/embed/${fallback.dataset.videoId}`) continue;
    frame.id = `video-${fallback.dataset.videoId}`;
    url.searchParams.set('enablejsapi', '1');
    url.searchParams.set('origin', window.location.origin);
    // Send the site origin, not the page path/query or any visitor data.
    frame.referrerPolicy = 'strict-origin-when-cross-origin';
    frame.addEventListener('load', () => {
      subscribe(frame);
      // The player can install its listener after load. Bounded handshake only;
      // never reload or retry playback.
      let attempts = 0;
      const timer = setInterval(() => {
        subscribe(frame);
        if (++attempts === 5) clearInterval(timer);
      }, 1000);
    });
    players.set(frame.contentWindow, { frame, fallback });
    frame.src = url.href;
  }
  window.addEventListener('message', event => {
    if (event.origin !== origin) return;
    const player = players.get(event.source);
    if (!player) return;
    let data;
    try { data = typeof event.data === 'string' ? JSON.parse(event.data) : event.data; } catch { return; }
    if (!data || typeof data !== 'object') return;
    if (data.event === 'onReady') { subscribe(player.frame); return; }
    if (data.event !== 'onError' || !Number.isInteger(data.info)) return;
    const message = [...player.fallback.querySelectorAll('template[data-error]')]
      .find(node => node.dataset.error.split(' ').includes(String(data.info)));
    if (!message) return;
    player.fallback.querySelector('[role="status"]').textContent = message.content.textContent;
    // Keep the focused iframe alive so keyboard focus is never discarded.
    if (document.activeElement !== player.frame) player.frame.hidden = true;
    player.fallback.dataset.state = String(data.info);
  });
})();
