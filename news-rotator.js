// Rotates the four latest headlines inside the homepage hero card.
(function () {
  var items = document.querySelectorAll('.news-rotator-item');
  if (items.length < 2) return;
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  var box = document.querySelector('.news-rotator-card');
  var i = 0;
  var timer = null;
  function show(n) {
    items[i].classList.remove('is-active');
    i = ((n % items.length) + items.length) % items.length;
    items[i].classList.add('is-active');
  }
  function start() {
    if (timer === null) timer = window.setInterval(function () { show(i + 1); }, 5000);
  }
  function stop() {
    if (timer !== null) { window.clearInterval(timer); timer = null; }
  }
  box.addEventListener('mouseenter', stop);
  box.addEventListener('mouseleave', start);
  box.addEventListener('focusin', stop);
  box.addEventListener('focusout', start);
  box.addEventListener('touchstart', stop, { passive: true });
  box.addEventListener('touchend', start);
  document.addEventListener('visibilitychange', function () {
    if (document.hidden) { stop(); } else { start(); }
  });
  start();
})();
