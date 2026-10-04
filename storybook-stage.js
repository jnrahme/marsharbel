/* Reader stage: direction-aware page turn, progress dots, swipe + arrow keys.
   Observes the existing reader; never changes its state machine. */
(function () {
  var panel = document.querySelector('.storybook-panel');
  var step = document.getElementById('story-step');
  var prev = document.getElementById('story-prev');
  var next = document.getElementById('story-next');
  var controls = document.querySelector('.storybook-controls');
  if (!panel || !step || !prev || !next || !controls) return;
  var last = 0, dots = null, timer = 0;

  function parse() {
    var m = (step.textContent || '').match(/(\d+)\D+(\d+)/);
    return m ? { n: +m[1], total: +m[2] } : null;
  }
  // Dot labels reuse the page's own localized "Page N of M" string, so no English lives in this file.
  function label(i) {
    return (step.textContent || '').replace(/\d+/, i);
  }
  function buildDots(total) {
    if (total > 16) return;
    if (dots && dots.children.length === total) return;
    if (dots) dots.remove();
    dots = document.createElement('div');
    dots.className = 'st-dots';
    for (var i = 1; i <= total; i++) {
      var b = document.createElement('button');
      b.type = 'button';
      b.setAttribute('aria-label', label(i));
      b.dataset.page = i;
      dots.appendChild(b);
    }
    dots.addEventListener('click', function (e) {
      var b = e.target.closest('button');
      if (!b) return;
      var target = +b.dataset.page, cur = last, guard = 0;
      var btn = target > cur ? next : prev;
      while (cur !== target && guard++ < 40) {
        if (btn.disabled) break;
        btn.click();
        var p = parse(); if (!p || p.n === cur) break; cur = p.n;
      }
    });
    controls.appendChild(dots);
  }
  function sync() {
    var p = parse(); if (!p) return;
    buildDots(p.total);
    if (dots) Array.prototype.forEach.call(dots.children, function (b, i) {
      if (i + 1 === p.n) b.setAttribute('aria-current', 'step'); else b.removeAttribute('aria-current');
    });
    if (last && p.n !== last) {
      var cls = p.n > last ? 'st-fwd' : 'st-back';
      panel.classList.remove('st-fwd', 'st-back');
      void panel.offsetWidth;
      panel.classList.add(cls);
      clearTimeout(timer);
      timer = setTimeout(function () { panel.classList.remove('st-fwd', 'st-back'); }, 620);
    }
    last = p.n;
  }
  new MutationObserver(sync).observe(step, { childList: true, characterData: true, subtree: true });
  sync();

  // swipe (touch) - horizontal intent only, never fights vertical scroll
  var x0 = 0, y0 = 0, t0 = 0;
  panel.addEventListener('touchstart', function (e) { var t = e.touches[0]; x0 = t.clientX; y0 = t.clientY; t0 = Date.now(); }, { passive: true });
  panel.addEventListener('touchend', function (e) {
    var t = e.changedTouches[0], dx = t.clientX - x0, dy = t.clientY - y0;
    if (Math.abs(dx) > 56 && Math.abs(dx) > Math.abs(dy) * 1.6 && Date.now() - t0 < 700) {
      var b = dx < 0 ? next : prev; if (!b.disabled) b.click();
    }
  }, { passive: true });

})();
