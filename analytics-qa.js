/* Runs synchronously before every Google Analytics config. Never infer QA from UA/IP. */
(function () {
  var marker = window.__MARSHARBEL_QA__;
  if (!marker) {
    try { marker = JSON.parse(sessionStorage.getItem('marsharbel:qa') || 'null'); }
    catch (_) { marker = null; }
  }
  if (!marker || !['monitoring', 'analytics_debug'].includes(marker.kind) ||
      typeof marker.runner !== 'string' || !/^[a-zA-Z0-9_.:/-]{1,100}$/.test(marker.runner)) return;
  window.SC_QA_ANALYTICS = {traffic_type:'qa_monitoring', qa_runner:marker.runner, qa_kind:marker.kind, debug_mode:marker.kind==='analytics_debug'};
  window.dataLayer = window.dataLayer || [];
  (function () { window.dataLayer.push(arguments); })('set', {
    traffic_type: 'qa_monitoring',
    qa_runner: marker.runner,
    qa_kind: marker.kind
  });
})();
