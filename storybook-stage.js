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

  // Next-book suggestion: when the last page is open, offer the next book on the library shelf.
  // Reads the shelf in stories.html (sections, order, titles, covers), so a new book needs no change here.
  var shelfPromise = null, nextCard = null;
  function loadShelf() {
    if (!shelfPromise) {
      shelfPromise = fetch('./stories', { credentials: 'same-origin' }).then(function (r) { return r.ok ? r : fetch('./stories.html'); }).then(function (r) { return r.ok ? r.text() : ''; })
        .then(function (html) {
          if (!html) return [];
          var doc = new DOMParser().parseFromString(html, 'text/html');
          return Array.prototype.map.call(doc.querySelectorAll('.promo-card'), function (card) {
            var a = card.querySelector('a[href]'), img = card.querySelector('img'), h = card.querySelector('h4'), p = card.querySelector('p');
            var sec = card.closest('.shelf-section'), head = sec && sec.querySelector('h3');
            if (!a || !img || !h || !card.closest('.shelf-section')) return null;
            return { slug: a.getAttribute('href').replace(/^\.\//, '').replace(/\.html$/, '').split(/[?#]/)[0],
              href: new URL(a.getAttribute('href'), location.href).href, cover: new URL(img.getAttribute('src'), location.href).href,
              title: h.textContent.trim(), blurb: p ? p.textContent.trim() : '', shelf: head ? head.textContent.trim() : '' };
          }).filter(Boolean);
        }).catch(function () { return []; });
    }
    return shelfPromise;
  }
  function pickNext(list) {
    var here = location.pathname.split('/').pop().replace(/\.html$/, '');
    var i = list.findIndex(function (b) { return b.slug === here; });
    if (i < 0 || list.length < 2) return null;
    return list[(i + 1) % list.length];
  }
  function showNext(on) {
    if (!on) { if (nextCard) nextCard.hidden = true; return; }
    loadShelf().then(function (list) {
      var b = pickNext(list); if (!b) return;
      if (!nextCard) {
        nextCard = document.createElement('a');
        nextCard.className = 'st-next';
        nextCard.innerHTML = '<span class="st-next-art"><img alt="" decoding="async"></span>' +
          '<span class="st-next-body"><span class="st-next-kicker"></span><span class="st-next-title"></span><span class="st-next-blurb"></span>' +
          '<span class="st-next-go" aria-hidden="true"></span></span>';
        panel.parentNode.appendChild(nextCard);
      }
      nextCard.href = b.href;
      nextCard.querySelector('img').src = b.cover;
      nextCard.querySelector('.st-next-kicker').textContent = b.shelf;
      nextCard.querySelector('.st-next-title').textContent = b.title;
      nextCard.querySelector('.st-next-blurb').textContent = b.blurb;
      nextCard.querySelector('.st-next-go').innerHTML = '&rarr;';
      nextCard.hidden = false;
      nextCard.classList.remove('is-in'); void nextCard.offsetWidth; nextCard.classList.add('is-in');
    });
  }

  // True page flip: a leaf with a front and a back face turns about the spine (desktop) or lifts away (phone).
  var mqPhone = window.matchMedia('(max-width:740px)'), mqCalm = window.matchMedia('(prefers-reduced-motion:reduce)');
  var keyAt = 0; document.addEventListener('keydown', function (e) { if (e.key === 'ArrowLeft' || e.key === 'ArrowRight') keyAt = Date.now(); }, true);
  var snap = null, flipEnd = null, flipTimer = 0;
  function pageEls() { return { art: panel.querySelector('.storybook-illustration'), text: panel.querySelector('.storybook-text') }; }
  function ghost(el) {
    var c = el.cloneNode(true);
    c.removeAttribute('id'); c.setAttribute('aria-hidden', 'true'); c.setAttribute('inert', '');
    Array.prototype.forEach.call(c.querySelectorAll('[id]'), function (n) { n.removeAttribute('id'); });
    Array.prototype.forEach.call(c.querySelectorAll('a,button,input,select,textarea,details'), function (n) { n.setAttribute('tabindex', '-1'); });
    return c;
  }
  function take() {
    var e = pageEls(); if (!e.art || !e.text) { snap = null; return; }
    snap = { art: ghost(e.art), text: ghost(e.text), all: null, refl: panel.classList.contains('is-reflection-page') };
    snap.all = Array.prototype.map.call(panel.children, function (n) { return n.matches('.storybook-illustration,.storybook-text') ? ghost(n) : null; }).filter(Boolean);
  }
  function div(cls, kids) { var d = document.createElement('div'); [].concat(cls).forEach(function (c) { d.classList.add(c); }); (kids || []).forEach(function (k) { d.appendChild(k); }); return d; }
  function endFlip() {
    clearTimeout(flipTimer);
    var st = panel.querySelector('.st-flip'); if (st) st.remove();
    panel.classList.remove('st-flipping', 'st-flip-f', 'st-flip-b', 'st-flip-phone');
    flipEnd = null;
  }
  function startFlip(fwd, old) {
    if (flipEnd) endFlip();
    var phone = mqPhone.matches, now = pageEls();
    if (!old || !now.art || !now.text) return false;
    var stage = div('st-flip'), ms;
    if (phone) {
      var leaf = div(['st-leaf', 'st-leaf-phone', fwd ? 'is-up' : 'is-down'], old.all.map(function (n) { return n; }));
      leaf.appendChild(div('st-sh'));
      stage.appendChild(div('st-cast'));
      stage.appendChild(leaf);
      ms = 640;
    } else {
      if (old.refl || panel.classList.contains('is-reflection-page')) return false;
      var under = fwd ? old.art : old.text, front = fwd ? old.text : old.art, back = ghost(fwd ? now.art : now.text);
      under.classList.add('st-under'); under.classList.add(fwd ? 'is-l' : 'is-r');
      var leaf2 = div(['st-leaf', fwd ? 'is-f' : 'is-b'], [
        div(['st-face', 'st-front'], [front, div('st-sh')]),
        div(['st-face', 'st-back'], [back, div('st-sh')])
      ]);
      stage.appendChild(under); stage.appendChild(div(['st-cast', fwd ? 'is-r' : 'is-l'])); stage.appendChild(leaf2);
      ms = 860;
    }
    panel.appendChild(stage);
    panel.classList.remove('st-fwd', 'st-back');
    panel.classList.add('st-flipping'); panel.classList.add(phone ? 'st-flip-phone' : (fwd ? 'st-flip-f' : 'st-flip-b'));
    flipTimer = setTimeout(endFlip, ms + 80);
    flipEnd = true;
    return true;
  }
  function sync() {
    var p = parse(); if (!p) return;
    buildDots(p.total);
    if (dots) Array.prototype.forEach.call(dots.children, function (b, i) {
      if (i + 1 === p.n) b.setAttribute('aria-current', 'step'); else b.removeAttribute('aria-current');
    });
    var flipped = false;
    if (last && p.n !== last && !mqCalm.matches && Date.now() - keyAt > 400) flipped = startFlip(p.n > last, snap);
    if (!flipped && last && p.n !== last) {
      var cls = p.n > last ? 'st-fwd' : 'st-back';
      panel.classList.remove('st-fwd', 'st-back');
      void panel.offsetWidth;
      panel.classList.add(cls);
      clearTimeout(timer);
      timer = setTimeout(function () { panel.classList.remove('st-fwd', 'st-back'); }, 620);
    }
    last = p.n;
    if (!flipped) take(); else take();
    showNext(p.n === p.total);
  }
  new MutationObserver(sync).observe(step, { childList: true, characterData: true, subtree: true });
  take();
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
