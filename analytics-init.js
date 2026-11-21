(function () {
  if (location.hostname !== 'marsharbel.com' && location.hostname !== 'www.marsharbel.com') return;
  var tag = document.createElement('script');
  tag.async = true;
  tag.src = 'https://www.googletagmanager.com/gtag/js?id=G-CJX1M0VFKP';
  document.head.appendChild(tag);
  window.dataLayer = window.dataLayer || [];
  window.gtag = function () { window.dataLayer.push(arguments); };
  window.gtag('js', new Date());
  if (window.__MARSHARBEL_QA__) window.gtag('set', { traffic_type: 'internal' });
  window.gtag('config', 'G-CJX1M0VFKP');
  // Finite event vocabulary. Never copy page URLs, form fields or arbitrary
  // parameters into analytics. QA runs produce no growth events.
  window.MarGrowth = {
    event: function (name, method) {
      if (window.__MARSHARBEL_QA__ || typeof window.gtag !== 'function') return false;
      if (!['daily_prayer_signup', 'share', 'testimony_submit', 'outbound_youtube'].includes(name)) return false;
      var params = {};
      if (name === 'share') {
        if (!['native', 'copy', 'facebook', 'x', 'whatsapp', 'telegram', 'viber', 'email', 'pinterest', 'line', 'vk'].includes(method)) return false;
        params.method = method;
      }
      try { window.gtag('event', name, params); return true; } catch (_) { return false; }
    }
  };
  document.addEventListener('click', function (event) {
    if (event.defaultPrevented || (event.button !== undefined && event.button !== 0)) return;
    var link = event.target && event.target.closest && event.target.closest('a[href]');
    if (!link) return;
    var url;
    try { url = new URL(link.href, location.href); } catch (_) { return; }
    if ((url.protocol === 'https:' || url.protocol === 'http:') &&
        /^(?:www\.|m\.)?(?:youtube\.com|youtu\.be)$/.test(url.hostname)) {
      window.MarGrowth.event('outbound_youtube');
    }
  });
})();
