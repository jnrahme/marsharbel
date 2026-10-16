/* Site search: header trigger and overlay. Loads search-core.js first (see translate.js). Every page, every locale. */
(function () {
  'use strict';
  if (window.__scSearchInit || !window.SCSearchCore) return;
  window.__scSearchInit = true;
  var core = window.SCSearchCore;

  // Strings per locale. Native-speaker read pending for all non-English rows (tracked with the release).
  var L = {
    en: { open: 'Search', ph: 'Search prayers, saints, places…', pop: 'Popular pages', rec: 'Recent searches', clear: 'Clear', none: 'No results for “{q}”', help: 'Check the spelling or try a shorter word.', one: '1 result', many: '{n} results', close: 'Close search', err: 'Search is unavailable right now. Please try again.', eng: 'In English' },
    es: { open: 'Buscar', ph: 'Busca oraciones, santos, lugares…', pop: 'Páginas populares', rec: 'Búsquedas recientes', clear: 'Borrar', none: 'Sin resultados para «{q}»', help: 'Revisa la ortografía o prueba una palabra más corta.', one: '1 resultado', many: '{n} resultados', close: 'Cerrar búsqueda', err: 'La búsqueda no está disponible ahora. Inténtalo de nuevo.', eng: 'En inglés' },
    fr: { open: 'Rechercher', ph: 'Rechercher prières, saints, lieux…', pop: 'Pages populaires', rec: 'Recherches récentes', clear: 'Effacer', none: 'Aucun résultat pour « {q} »', help: 'Vérifiez l’orthographe ou essayez un mot plus court.', one: '1 résultat', many: '{n} résultats', close: 'Fermer la recherche', err: 'La recherche est indisponible pour le moment. Réessayez.', eng: 'En anglais' },
    de: { open: 'Suchen', ph: 'Gebete, Heilige, Orte suchen…', pop: 'Beliebte Seiten', rec: 'Letzte Suchen', clear: 'Löschen', none: 'Keine Ergebnisse für „{q}“', help: 'Prüfen Sie die Schreibweise oder versuchen Sie ein kürzeres Wort.', one: '1 Ergebnis', many: '{n} Ergebnisse', close: 'Suche schließen', err: 'Die Suche ist gerade nicht verfügbar. Bitte versuchen Sie es erneut.', eng: 'Auf Englisch' },
    it: { open: 'Cerca', ph: 'Cerca preghiere, santi, luoghi…', pop: 'Pagine popolari', rec: 'Ricerche recenti', clear: 'Cancella', none: 'Nessun risultato per «{q}»', help: 'Controlla l’ortografia o prova una parola più breve.', one: '1 risultato', many: '{n} risultati', close: 'Chiudi la ricerca', err: 'La ricerca non è disponibile al momento. Riprova.', eng: 'In inglese' },
    pt: { open: 'Pesquisar', ph: 'Pesquise orações, santos, lugares…', pop: 'Páginas populares', rec: 'Pesquisas recentes', clear: 'Limpar', none: 'Nenhum resultado para “{q}”', help: 'Verifique a ortografia ou tente uma palavra mais curta.', one: '1 resultado', many: '{n} resultados', close: 'Fechar pesquisa', err: 'A pesquisa não está disponível agora. Tente novamente.', eng: 'Em inglês' },
    pl: { open: 'Szukaj', ph: 'Szukaj modlitw, świętych, miejsc…', pop: 'Popularne strony', rec: 'Ostatnie wyszukiwania', clear: 'Wyczyść', none: 'Brak wyników dla „{q}”', help: 'Sprawdź pisownię lub spróbuj krótszego słowa.', one: 'Wyniki: 1', many: 'Wyniki: {n}', close: 'Zamknij wyszukiwanie', err: 'Wyszukiwanie jest teraz niedostępne. Spróbuj ponownie.', eng: 'Po angielsku' },
    ru: { open: 'Поиск', ph: 'Искать молитвы, святых, места…', pop: 'Популярные страницы', rec: 'Недавние запросы', clear: 'Очистить', none: 'Ничего не найдено по запросу «{q}»', help: 'Проверьте написание или попробуйте более короткое слово.', one: 'Найдено: 1', many: 'Найдено: {n}', close: 'Закрыть поиск', err: 'Поиск сейчас недоступен. Попробуйте ещё раз.', eng: 'На английском' },
    ar: { open: 'بحث', ph: 'ابحث عن صلوات وقدّيسين وأماكن…', pop: 'صفحات شائعة', rec: 'عمليات البحث الأخيرة', clear: 'مسح', none: 'لا نتائج لـ «{q}»', help: 'تحقّق من الإملاء أو جرّب كلمة أقصر.', one: 'النتائج: 1', many: 'النتائج: {n}', close: 'إغلاق البحث', err: 'البحث غير متاح الآن. حاول مرة أخرى.', eng: 'بالإنجليزية' },
    hi: { open: 'खोजें', ph: 'प्रार्थनाएँ, संत, स्थान खोजें…', pop: 'लोकप्रिय पृष्ठ', rec: 'हाल की खोजें', clear: 'मिटाएँ', none: '“{q}” के लिए कोई परिणाम नहीं', help: 'वर्तनी जाँचें या छोटा शब्द आज़माएँ।', one: 'परिणाम: 1', many: 'परिणाम: {n}', close: 'खोज बंद करें', err: 'खोज अभी उपलब्ध नहीं है। कृपया फिर कोशिश करें।', eng: 'अंग्रेज़ी में' },
    th: { open: 'ค้นหา', ph: 'ค้นหาคำอธิษฐาน นักบุญ สถานที่…', pop: 'หน้ายอดนิยม', rec: 'การค้นหาล่าสุด', clear: 'ล้าง', none: 'ไม่พบผลลัพธ์สำหรับ “{q}”', help: 'ตรวจสอบการสะกดหรือลองคำที่สั้นลง', one: 'ผลลัพธ์: 1', many: 'ผลลัพธ์: {n}', close: 'ปิดการค้นหา', err: 'ขณะนี้ไม่สามารถค้นหาได้ โปรดลองอีกครั้ง', eng: 'ภาษาอังกฤษ' },
    'zh-Hans': { open: '搜索', ph: '搜索祈祷文、圣人、地点……', pop: '热门页面', rec: '最近搜索', clear: '清除', none: '未找到“{q}”的结果', help: '请检查拼写，或尝试更短的词。', one: '结果：1', many: '结果：{n}', close: '关闭搜索', err: '搜索暂时不可用，请稍后再试。', eng: '英文' }
  };
  var htmlLang = document.documentElement.getAttribute('lang') || 'en';
  var loc = L[htmlLang] ? htmlLang : (L[htmlLang.split('-')[0]] ? htmlLang.split('-')[0] : 'en');
  var T = L[loc];
  var dir = document.documentElement.getAttribute('dir') || (loc === 'ar' ? 'rtl' : 'ltr');
  var INDEX_BASE = '/search-index/';

  var ICON_SEARCH = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><circle cx="10.5" cy="10.5" r="6.5"/><path d="M15.5 15.5 21 21"/></svg>';
  var ICON_CLOSE = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" aria-hidden="true" focusable="false"><path d="M6 6l12 12M18 6 6 18"/></svg>';

  function el(tag, cls, attrs) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (attrs) for (var k in attrs) e.setAttribute(k, attrs[k]);
    return e;
  }
  function fmt(s, vars) { return s.replace(/\{(\w+)\}/g, function (_, k) { return vars[k]; }); }
  function shortTitle(t) { return String(t).split(/\s[|:\u2013\u2014-]\s/)[0]; }

  // ---------- index loading ----------
  var cache = {};
  function loadIndex(code) {
    if (cache[code]) return cache[code];
    cache[code] = fetch(INDEX_BASE + code + '.json', { credentials: 'same-origin' }).then(function (r) {
      if (!r.ok) throw new Error('index ' + r.status);
      return r.json();
    }).then(function (rows) { return core.prepare(rows); }).catch(function (e) { delete cache[code]; throw e; });
    return cache[code];
  }
  var indexLoc = loc;

  // ---------- recent searches ----------
  var RK = 'sc-search-recent';
  function getRecent() { try { return JSON.parse(localStorage.getItem(RK) || '[]').slice(0, 5); } catch (e) { return []; } }
  function setRecent(list) { try { localStorage.setItem(RK, JSON.stringify(list.slice(0, 5))); } catch (e) { /* private mode */ } }
  function pushRecent(q) {
    q = q.trim(); if (q.length < 2) return;
    var list = getRecent().filter(function (x) { return x !== q; }); list.unshift(q); setRecent(list);
  }

  // ---------- overlay ----------
  var root, input, listEl, bodyEl, statusEl, srEl, trigger, panel;
  var open = false, results = [], active = -1, lastFocus = null, token = 0, built = false;

  function build() {
    if (built) return; built = true;
    root = el('div', 'scs-root', { hidden: '', lang: htmlLang, dir: dir });
    var scrim = el('div', 'scs-scrim');
    panel = el('div', 'scs-panel', { role: 'dialog', 'aria-modal': 'true', 'aria-label': T.open });
    var bar = el('div', 'scs-bar');
    bar.insertAdjacentHTML('beforeend', ICON_SEARCH);
    input = el('input', 'scs-input', {
      type: 'search', role: 'combobox', 'aria-expanded': 'false', 'aria-controls': 'scs-list', 'aria-autocomplete': 'list',
      autocomplete: 'off', autocapitalize: 'off', autocorrect: 'off', spellcheck: 'false', enterkeyhint: 'search',
      placeholder: T.ph, 'aria-label': T.open, name: 'q'
    });
    var closeBtn = el('button', 'scs-close', { type: 'button', 'aria-label': T.close });
    closeBtn.innerHTML = ICON_CLOSE;
    bar.appendChild(input); bar.appendChild(closeBtn);
    bodyEl = el('div', 'scs-body');
    statusEl = el('p', 'scs-status', { 'aria-hidden': 'true' });
    srEl = el('p', 'scs-sr', { role: 'status', 'aria-live': 'polite' });
    listEl = el('ul', 'scs-list', { id: 'scs-list', role: 'listbox', 'aria-label': T.open });
    bodyEl.appendChild(statusEl); bodyEl.appendChild(listEl);
    panel.appendChild(bar); panel.appendChild(bodyEl); panel.appendChild(srEl);
    root.appendChild(scrim); root.appendChild(panel);
    document.body.appendChild(root);

    scrim.addEventListener('click', close);
    closeBtn.addEventListener('click', close);
    input.addEventListener('input', run);
    input.addEventListener('keydown', onKey);
    root.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') { e.preventDefault(); close(); return; }
      if (e.key === 'Tab') {
        var f = [input, closeBtn];
        var i = f.indexOf(document.activeElement);
        if (e.shiftKey && i <= 0) { e.preventDefault(); closeBtn.focus(); }
        else if (!e.shiftKey && i === f.length - 1) { e.preventDefault(); input.focus(); }
        else if (i === -1) { e.preventDefault(); input.focus(); }
      }
    });
    listEl.addEventListener('mousemove', function (e) {
      var a = e.target.closest && e.target.closest('.scs-row');
      if (a) setActive(Number(a.getAttribute('data-i')), false);
    });
    listEl.addEventListener('click', function (e) {
      var a = e.target.closest && e.target.closest('.scs-row');
      if (a) pushRecent(input.value);
    });
  }

  function onKey(e) {
    if (e.key === 'ArrowDown') { e.preventDefault(); if (results.length) setActive((active + 1) % results.length, true); }
    else if (e.key === 'ArrowUp') { e.preventDefault(); if (results.length) setActive((active - 1 + results.length) % results.length, true); }
    else if (e.key === 'Home' && results.length && input.selectionStart === 0 && input.selectionEnd === 0) { e.preventDefault(); setActive(0, true); }
    else if (e.key === 'End' && results.length && input.selectionStart === input.value.length) { e.preventDefault(); setActive(results.length - 1, true); }
    else if (e.key === 'Enter') {
      var a = listEl.querySelector('.scs-row[data-i="' + active + '"]');
      if (a) { e.preventDefault(); pushRecent(input.value); window.location.assign(a.getAttribute('href')); }
    }
  }

  function setActive(i, scroll) {
    active = i;
    var rows = listEl.querySelectorAll('.scs-row');
    for (var k = 0; k < rows.length; k++) {
      var on = Number(rows[k].getAttribute('data-i')) === i;
      rows[k].setAttribute('aria-selected', on ? 'true' : 'false');
      if (on) {
        input.setAttribute('aria-activedescendant', rows[k].id);
        if (scroll) rows[k].scrollIntoView({ block: 'nearest' });
      }
    }
  }

  function addMarked(host, text, ranges) {
    var pos = 0;
    (ranges || []).forEach(function (r) {
      if (r[0] < pos) return;
      if (r[0] > pos) host.appendChild(document.createTextNode(text.slice(pos, r[0])));
      var m = document.createElement('mark'); m.textContent = text.slice(r[0], r[1]); host.appendChild(m);
      pos = r[1];
    });
    if (pos < text.length) host.appendChild(document.createTextNode(text.slice(pos)));
  }

  function clearList() {
    while (listEl.firstChild) listEl.removeChild(listEl.firstChild);
    var extra = bodyEl.querySelectorAll('.scs-group,.scs-none,.scs-divider');
    for (var i = 0; i < extra.length; i++) extra[i].remove();
  }

  function renderRows(items, englishStart, toks) {
    items.forEach(function (it, i) {
      if (i === englishStart && englishStart >= 0) {
        var dv = el('li', 'scs-divider', { role: 'presentation' }); dv.textContent = T.eng; listEl.appendChild(dv);
      }
      var li = el('li', null, { role: 'presentation' });
      var a = el('a', 'scs-row', { id: 'scs-o-' + i, role: 'option', href: it.doc.url, tabindex: '-1', 'aria-selected': 'false', 'data-i': String(i) });
      if (it.en) { a.setAttribute('lang', 'en'); a.setAttribute('dir', 'ltr'); }
      var t = el('span', 'scs-title'); addMarked(t, it.doc.title, core.titleRanges(it.doc, toks));
      var p = el('span', 'scs-path'); p.textContent = it.doc.url === '/' ? '/' : it.doc.url;
      var sn = core.snippet(it.doc, toks, 150);
      a.appendChild(t); a.appendChild(p);
      if (sn.text) { var s = el('span', 'scs-snip'); addMarked(s, sn.text, sn.ranges); a.appendChild(s); }
      li.appendChild(a); listEl.appendChild(li);
    });
  }

  function chipLink(href, text) { var a = el('a', 'scs-chip', { href: href }); a.textContent = text; return a; }

  function renderEmpty(prepared) {
    clearList(); results = []; active = -1;
    input.setAttribute('aria-expanded', 'false'); input.removeAttribute('aria-activedescendant');
    statusEl.textContent = ''; srEl.textContent = '';
    var recent = getRecent();
    if (recent.length) {
      var g = el('div', 'scs-group'); var h = el('h3'); h.textContent = T.rec;
      var clr = el('button', 'scs-clear', { type: 'button' }); clr.textContent = T.clear;
      clr.addEventListener('click', function () { setRecent([]); renderEmpty(prepared); input.focus(); });
      h.appendChild(clr); g.appendChild(h);
      var chips = el('div', 'scs-chips');
      recent.forEach(function (q) {
        var b = el('button', 'scs-chip', { type: 'button' }); b.textContent = q;
        b.addEventListener('click', function () { input.value = q; run(); input.focus(); });
        chips.appendChild(b);
      });
      g.appendChild(chips); bodyEl.appendChild(g);
    }
    if (prepared && prepared.length) {
      // Curated stems first (same page in any locale that keeps the English slug), then priority order.
      var STEMS = ['prayer-library', 'novena', 'prayer-for-healing', 'miracles', 'annaya', 'encyclopedia', 'rosary', 'saints'];
      var pop = [], seen = {};
      var leaf = function (u) { return u.replace(/\/+$/, '').split('/').pop() || ''; };
      var add = function (d) { if (!seen[d.url] && d.url.replace(/\/+$/, '').split('/').filter(Boolean).length > (loc === 'en' ? 0 : 1) && pop.length < 7) { seen[d.url] = 1; pop.push(d); } };
      STEMS.forEach(function (st) { var m = prepared.filter(function (d) { return leaf(d.url).indexOf(st) >= 0 && !/story|stories|kids/.test(d.url); })[0]; if (m) add(m); });
      prepared.forEach(function (d) { if (!/story|stories|kids/.test(d.url)) add(d); });
      if (pop.length) {
        var g2 = el('div', 'scs-group'); var h2 = el('h3'); h2.textContent = T.pop; g2.appendChild(h2);
        var c2 = el('div', 'scs-chips');
        pop.forEach(function (d) { c2.appendChild(chipLink(d.url, shortTitle(d.title))); });
        g2.appendChild(c2); bodyEl.appendChild(g2);
      }
    }
  }

  var prepared = null, preparedEn = null;
  function run() {
    var q = input.value, my = ++token;
    if (!prepared) return;
    if (!q.trim()) { renderEmpty(prepared); return; }
    var hits = core.search(prepared, q, 12);
    var englishStart = -1;
    function finish(en) {
      if (my !== token) return;
      var items = hits.map(function (h) { return { doc: h.doc, en: false }; });
      var tk = hits.length ? hits[0].tokens : core.tokens(q);
      if (en && en.length) {
        englishStart = items.length;
        en.forEach(function (h) { items.push({ doc: h.doc, en: true }); });
      }
      clearList();
      results = items;
      if (!items.length) {
        var none = el('div', 'scs-none'); var st = el('strong'); st.textContent = fmt(T.none, { q: q.trim() });
        var sp = el('span'); sp.textContent = T.help; none.appendChild(st); none.appendChild(sp); bodyEl.appendChild(none);
        statusEl.textContent = ''; srEl.textContent = fmt(T.none, { q: q.trim() });
        input.setAttribute('aria-expanded', 'false'); input.removeAttribute('aria-activedescendant'); active = -1;
        return;
      }
      renderRows(items, englishStart, tk);
      var label = items.length === 1 ? T.one : fmt(T.many, { n: items.length });
      statusEl.textContent = label; srEl.textContent = label;
      input.setAttribute('aria-expanded', 'true');
      setActive(0, false);
      bodyEl.scrollTop = 0;
    }
    // Locales with a thin catalogue also show English matches, labelled, below the local ones.
    if (loc !== 'en' && hits.length < 5) {
      loadIndex('en').then(function (en) {
        preparedEn = en;
        var enHits = core.search(en, q, 8);
        var have = {}; hits.forEach(function (h) { have[h.doc.url] = 1; });
        finish(enHits.filter(function (h) { return !have[h.doc.url]; }).slice(0, 8));
      }).catch(function () { finish(null); });
    } else finish(null);
  }

  function lockScroll(on) { document.documentElement.classList.toggle('scs-lock', on); }

  function openSearch(prefill) {
    if (open) return;
    build(); open = true;
    lastFocus = document.activeElement;
    root.hidden = false; lockScroll(true);
    void root.offsetWidth; // start the transition from the closed state
    root.classList.add('scs-open');
    input.value = prefill || '';
    input.focus({ preventScroll: true });
    renderEmpty(prepared);
    loadIndex(indexLoc).then(function (p) { prepared = p; if (open) run(); }).catch(function () {
      if (!open) return;
      clearList(); var none = el('div', 'scs-none'); var sp = el('span'); sp.textContent = T.err; none.appendChild(sp); bodyEl.appendChild(none);
    });
  }

  function close() {
    if (!open) return; open = false;
    root.classList.remove('scs-open'); lockScroll(false);
    var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    setTimeout(function () { if (!open) root.hidden = true; }, reduce ? 0 : 200);
    if (lastFocus && document.contains(lastFocus) && lastFocus.focus) lastFocus.focus({ preventScroll: true });
    else if (trigger) trigger.focus({ preventScroll: true });
  }

  // ---------- header trigger ----------
  function mountTrigger() {
    var host = document.querySelector('.topbar .nav') || document.querySelector('.masthead') || document.querySelector('header .site-shell') || document.querySelector('header > .shell') || document.querySelector('header');
    if (!host || document.querySelector('.scs-trigger')) return;
    trigger = el('button', 'scs-trigger', { type: 'button', 'aria-label': T.open, 'aria-haspopup': 'dialog', title: T.open });
    trigger.innerHTML = ICON_SEARCH;
    var lab = el('span', 'scs-trigger-label'); lab.textContent = T.open; trigger.appendChild(lab);
    if (host.classList.contains('nav')) { host.classList.add('scs-grid'); trigger.classList.add('scs-in-grid'); }
    host.appendChild(trigger);
    trigger.addEventListener('click', function () { openSearch(''); });
    var warm = function () { loadIndex(indexLoc).then(function (p) { prepared = p; }).catch(function () {}); };
    trigger.addEventListener('pointerenter', warm, { once: true });
    trigger.addEventListener('focus', warm, { once: true });
  }

  document.addEventListener('keydown', function (e) {
    if (open) return;
    var t = e.target, tag = t && t.tagName;
    var typing = tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT' || (t && t.isContentEditable);
    if ((e.key === 'k' || e.key === 'K') && (e.metaKey || e.ctrlKey) && !e.altKey) { e.preventDefault(); openSearch(''); }
    else if (e.key === '/' && !typing && !e.metaKey && !e.ctrlKey && !e.altKey) { e.preventDefault(); openSearch(''); }
  });
  window.addEventListener('pagehide', function () { lockScroll(false); });

  // Public hook (also used by internal links and tests).
  window.SCSearch = { open: openSearch, close: close };

  function ready(fn) { if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', fn, { once: true }); else fn(); }
  // Mount once the stylesheet is applied, so the button never flashes unstyled.
  ready(function () {
    var css = document.querySelector('link[data-scs-css]');
    if (css && !css.sheet) { css.addEventListener('load', mountTrigger, { once: true }); css.addEventListener('error', mountTrigger, { once: true }); }
    else mountTrigger();
  });
})();
