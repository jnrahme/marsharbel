/* Media pages: pointer-driven 3D tilt on cards. Mouse only, skipped for reduced motion. */
(function () {
  if (!window.matchMedia('(hover: hover) and (pointer: fine)').matches) return;
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  var cards = document.querySelectorAll('.media-hub .song-lead, .media-hub .song-list > .card, .media-hub .grid-2 > .card, .gallery-page figure');
  cards.forEach(function (card) {
    var raf = 0;
    card.addEventListener('pointermove', function (e) {
      if (raf) return;
      raf = requestAnimationFrame(function () {
        raf = 0;
        var r = card.getBoundingClientRect();
        var x = (e.clientX - r.left) / r.width - 0.5;
        var y = (e.clientY - r.top) / r.height - 0.5;
        card.style.setProperty('--ry', (x * 8).toFixed(2) + 'deg');
        card.style.setProperty('--rx', (-y * 6).toFixed(2) + 'deg');
        card.style.setProperty('--sx', (x * 100 + 50).toFixed(0) + '%');
        card.style.setProperty('--sy', (y * 100 + 50).toFixed(0) + '%');
      });
    });
    card.addEventListener('pointerleave', function () {
      card.style.removeProperty('--ry'); card.style.removeProperty('--rx');
    });
  });
})();
