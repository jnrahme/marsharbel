/* Grouped navigation: touch/mobile tap-to-open, Escape/outside-click close, aria sync.
   Desktop hover and keyboard use pure CSS (:hover / :focus-within). */
(function () {
  var groups = Array.prototype.slice.call(document.querySelectorAll('.nav-group'));
  if (!groups.length) return;

  function closeAll(except) {
    groups.forEach(function (g) {
      if (g === except) return;
      g.classList.remove('open');
      var p = g.querySelector('.nav-parent');
      if (p) {
        p.setAttribute('aria-expanded', 'false');
        // release focus so :focus-within cannot hold a closed menu open
        var ae = document.activeElement;
        if (ae && g.contains(ae)) ae.blur();
      }
    });
  }

  function coarse() {
    return window.matchMedia('(hover: none)').matches || window.innerWidth <= 820;
  }

  groups.forEach(function (g) {
    var parent = g.querySelector('.nav-parent');
    if (!parent) return;

    parent.addEventListener('click', function (e) {
      if (!coarse()) return; // desktop: link navigates normally
      if (!g.classList.contains('open')) {
        e.preventDefault();
        closeAll(g);
        g.classList.add('open');
        parent.setAttribute('aria-expanded', 'true');
      } else {
        e.preventDefault(); // second tap closes the dropdown; never navigate on toggle
        closeAll();
        // touch leaves a sticky :hover on the parent; suppress it from holding the menu open
        document.documentElement.classList.add('nav-suppress');
      }
    });

    g.addEventListener('focusout', function () {
      window.setTimeout(function () {
        if (!g.contains(document.activeElement)) closeAll();
      }, 0);
    });
  });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') closeAll();
  });
  // Conventional behavior: an open dropdown closes when the page scrolls
  // (the pinned bar stays). Scrolls inside the mobile panel do not reach this.
  var scrollHideTimer = null;
  window.addEventListener('scroll', function () {
    closeAll();
    // suppress hover/focus re-open until the pointer actually moves again
    document.documentElement.classList.add('nav-suppress');
    // Release nav focus so focus-within does not hold a dropdown open
    var ae = document.activeElement;
    if (ae && ae.closest && ae.closest('.nav-group')) ae.blur();
    // Force-hide hover/focus dropdowns while the page is scrolling
    document.documentElement.classList.add('nav-scrolling');
    if (scrollHideTimer) window.clearTimeout(scrollHideTimer);
    scrollHideTimer = window.setTimeout(function () {
      document.documentElement.classList.remove('nav-scrolling');
    }, 180);
  }, { passive: true });
  document.addEventListener('mousemove', function () {
    document.documentElement.classList.remove('nav-suppress');
  }, { passive: true });
  document.addEventListener('click', function (e) {
    if (!e.target.closest('.nav-group')) closeAll();
  });
})();
