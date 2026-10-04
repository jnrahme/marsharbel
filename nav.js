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

    // Keep an opened dropdown inside the viewport (large text can wrap the nav so a menu lands near either edge).
    var fitMenu = function () {
      var sub = g.querySelector('.nav-sub');
      if (!sub || window.innerWidth <= 820) return;
      sub.style.left = '';
      sub.style.right = '';
      sub.style.maxHeight = '';
      var r = sub.getBoundingClientRect();
      var pad = 8;
      // Tall menus (large text) scroll inside themselves instead of running off the bottom of the viewport.
      var room = window.innerHeight - r.top - pad;
      if (room > 120 && r.height > room) sub.style.maxHeight = room + 'px';
      if (r.width > window.innerWidth - pad * 2) return;
      var shift = 0;
      if (r.right > window.innerWidth - pad) shift = window.innerWidth - pad - r.right;
      if (r.left + shift < pad) shift = pad - r.left;
      if (shift) sub.style.left = shift + 'px';
    };
    g.addEventListener('mouseenter', fitMenu);
    g.addEventListener('focusin', fitMenu);
    g.addEventListener('click', function () { setTimeout(fitMenu, 0); });
    g.addEventListener('mouseenter', function () {
      if (!coarse()) {
        document.documentElement.classList.remove('nav-suppress');
        parent.setAttribute('aria-expanded', 'true');
      }
    });
    g.addEventListener('mouseleave', function () {
      if (!g.contains(document.activeElement) && !g.classList.contains('open')) {
        parent.setAttribute('aria-expanded', 'false');
      }
    });
    g.addEventListener('focusin', function () {
      if (!document.documentElement.classList.contains('nav-suppress')) {
        parent.setAttribute('aria-expanded', 'true');
      }
    });

    parent.addEventListener('click', function (e) {
      if (!coarse()) return; // desktop: link navigates normally
      if (!g.classList.contains('open')) {
        e.preventDefault();
        closeAll(g);
        document.documentElement.classList.remove('nav-suppress');
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
        if (!g.contains(document.activeElement)) {
          g.classList.remove('open');
          parent.setAttribute('aria-expanded', String(!coarse() && g.matches(':hover') && !document.documentElement.classList.contains('nav-suppress')));
        }
      }, 0);
    });
  });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Tab') document.documentElement.classList.remove('nav-suppress');
    if (e.key === 'Escape') {
      var focusedGroup = document.activeElement.closest('.nav-group');
      document.documentElement.classList.add('nav-suppress');
      closeAll();
      if (focusedGroup) focusedGroup.querySelector('.nav-parent').focus();
    }
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
    if (!coarse()) groups.forEach(function (g) {
      var parent = g.querySelector('.nav-parent');
      if (parent) parent.setAttribute('aria-expanded', String(g.matches(':hover') || g.contains(document.activeElement) || g.classList.contains('open')));
    });
  }, { passive: true });
  document.addEventListener('click', function (e) {
    if (!e.target.closest('.nav-group')) closeAll();
  });
})();
