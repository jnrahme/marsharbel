/* Site search core: folding, scoring, snippets. No DOM. Used by search.js in the browser and by node tests.
   Index rows are [url, title, description, headings, body, priority]. */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else root.SCSearchCore = factory();
})(typeof self !== 'undefined' ? self : this, function () {
  var EXTRA = { 'ß': 'ss', 'ł': 'l', 'đ': 'd', 'ø': 'o', 'æ': 'ae', 'œ': 'oe', 'ı': 'i' };
  var ARABIC_MAP = { 'إ': 'ا', 'أ': 'ا', 'آ': 'ا', 'ٱ': 'ا', 'ى': 'ي', 'ة': 'ه', 'ؤ': 'و', 'ئ': 'ي' };
  var STRIP = /[\u0300-\u036f\u064b-\u065f\u0670\u0640\u200c\u200d\u00ad]/;

  // Fold one string to a comparable form. When withMap is true also return the
  // original index of every folded char, so snippets can highlight original text.
  function fold(input, withMap) {
    var s = String(input == null ? '' : input);
    var out = '';
    var map = withMap ? [] : null;
    for (var i = 0; i < s.length; i++) {
      var c = s.charAt(i);
      if (STRIP.test(c)) continue;
      var d = c.length === 1 && c.charCodeAt(0) > 127 ? c.normalize('NFD') : c;
      // Precomposed letters fold to their base letter. Standalone Indic and Thai
      // signs are separate characters and are kept as written.
      if (d.length > 1) d = d.charAt(0);
      d = d.toLowerCase();
      if (EXTRA[d]) d = EXTRA[d];
      else if (ARABIC_MAP[d]) d = ARABIC_MAP[d];
      out += d;
      if (map) for (var k = 0; k < d.length; k++) map.push(i);
    }
    return withMap ? { s: out, map: map } : out;
  }

  function tokens(query) {
    var q = fold(query);
    var m = q.match(/[\p{L}\p{N}\p{M}]+/gu) || [];
    var seen = {};
    return m.filter(function (t) { if (seen[t]) return false; seen[t] = 1; return true; });
  }

  var HAN = /[\u3400-\u9fff]/;
  function minLen(t) { return HAN.test(t) || /[\u0e00-\u0e7f]/.test(t) ? 1 : 2; }

  function wordStart(hay, idx) {
    if (idx === 0) return true;
    return !/[\p{L}\p{N}\p{M}]/u.test(hay.charAt(idx - 1));
  }

  function wordEnd(hay, idx, len) {
    var e = idx + len;
    return e >= hay.length || !/[\p{L}\p{N}\p{M}]/u.test(hay.charAt(e));
  }

  // One-edit tolerance on title words, for tokens of 5+ letters.
  function oneEdit(a, b) {
    if (a === b) return true;
    var la = a.length, lb = b.length;
    if (Math.abs(la - lb) > 1) return false;
    var i = 0;
    while (i < la && i < lb && a.charAt(i) === b.charAt(i)) i++;
    if (la === lb) {
      if (a.slice(i + 1) === b.slice(i + 1)) return true;
      return a.charAt(i) === b.charAt(i + 1) && a.charAt(i + 1) === b.charAt(i) && a.slice(i + 2) === b.slice(i + 2);
    }
    return la > lb ? a.slice(i + 1) === b.slice(i) : a.slice(i) === b.slice(i + 1);
  }

  function fuzzyInWords(token, text) {
    if (token.length < 5 || HAN.test(token)) return false;
    var words = text.match(/[\p{L}\p{N}]+/gu) || [];
    for (var i = 0; i < words.length; i++) {
      var w = words[i];
      if (oneEdit(token, w) || (w.length > token.length && oneEdit(token, w.slice(0, token.length)))) return true;
    }
    return false;
  }

  // Prepare an index once: fold every field.
  function prepare(rows) {
    return rows.map(function (r) {
      return {
        url: r[0], title: r[1] || '', desc: r[2] || '', heads: r[3] || '', body: r[4] || '', pri: r[5] || 0.5,
        ft: fold(r[1]), fd: fold(r[2]), fh: fold(r[3]), fb: fold(r[4])
      };
    });
  }

  function scoreDoc(doc, toks) {
    var total = 0;
    for (var i = 0; i < toks.length; i++) {
      var t = toks[i], s = 0, at;
      at = doc.ft.indexOf(t);
      if (at >= 0) { s += 20; if (wordStart(doc.ft, at)) s += 12; if (wordStart(doc.ft, at) && wordEnd(doc.ft, at, t.length)) s += 8; if (at === 0) s += 4; }
      else if (fuzzyInWords(t, doc.ft + ' ' + doc.fh)) s += 14;
      var ah = doc.fh.indexOf(t);
      if (ah >= 0) { s += wordStart(doc.fh, ah) ? 9 : 4; }
      var ad = doc.fd.indexOf(t);
      if (ad >= 0) { s += wordStart(doc.fd, ad) ? 5 : 2; }
      var ab = doc.fb.indexOf(t);
      if (ab >= 0) {
        s += wordStart(doc.fb, ab) ? 3 : 1;
        var n = 0, p = ab;
        while (n < 4 && (p = doc.fb.indexOf(t, p + t.length)) >= 0) n++;
        s += n * 0.5;
      }
      if (!s) return 0; // every token must land somewhere
      total += s;
    }
    return total;
  }

  function search(prepared, query, limit) {
    var toks = tokens(query).filter(function (t) { return t.length >= minLen(t); });
    if (!toks.length) return [];
    var hits = [];
    for (var i = 0; i < prepared.length; i++) {
      var sc = scoreDoc(prepared[i], toks);
      if (sc > 0) hits.push({ doc: prepared[i], score: sc + prepared[i].pri * 4 - prepared[i].url.length * 0.01 });
    }
    hits.sort(function (a, b) { return b.score - a.score; });
    return hits.slice(0, limit || 20).map(function (h) { return { doc: h.doc, score: h.score, tokens: toks }; });
  }

  // Returns {text, ranges:[[start,end]...]} where ranges index into text.
  function snippet(doc, toks, maxLen) {
    maxLen = maxLen || 150;
    var sources = [doc.desc, doc.body, doc.heads];
    var pick = null;
    for (var i = 0; i < sources.length && !pick; i++) {
      var src = sources[i];
      if (!src) continue;
      var f = fold(src, true);
      var best = -1;
      for (var j = 0; j < toks.length; j++) {
        var at = f.s.indexOf(toks[j]);
        if (at >= 0 && (best < 0 || at < best)) best = at;
      }
      if (best >= 0) pick = { src: src, f: f, at: best };
    }
    if (!pick) {
      var base = doc.desc || doc.body || '';
      return { text: base.length > maxLen ? base.slice(0, maxLen).replace(/\s+\S*$/, '') + '…' : base, ranges: [] };
    }
    var origAt = pick.f.map[pick.at];
    var start = Math.max(0, origAt - Math.floor(maxLen * 0.3));
    if (start > 0) { var sp = pick.src.indexOf(' ', start); if (sp > -1 && sp < origAt) start = sp + 1; }
    var end = Math.min(pick.src.length, start + maxLen);
    if (end < pick.src.length) { var sp2 = pick.src.lastIndexOf(' ', end); if (sp2 > origAt) end = sp2; }
    var text = pick.src.slice(start, end);
    var prefix = start > 0 ? '… ' : '', suffix = end < pick.src.length ? ' …' : '';
    var ranges = [];
    for (var k = 0; k < toks.length; k++) {
      var from = 0, idx;
      while ((idx = pick.f.s.indexOf(toks[k], from)) >= 0 && ranges.length < 12) {
        var o1 = pick.f.map[idx], o2 = pick.f.map[idx + toks[k].length - 1] + 1;
        if (o1 >= start && o2 <= end) ranges.push([o1 - start + prefix.length, o2 - start + prefix.length]);
        from = idx + Math.max(1, toks[k].length);
        if (o1 > end) break;
      }
    }
    ranges.sort(function (a, b) { return a[0] - b[0]; });
    var merged = [];
    ranges.forEach(function (r) {
      var last = merged[merged.length - 1];
      if (last && r[0] <= last[1]) last[1] = Math.max(last[1], r[1]); else merged.push(r);
    });
    return { text: prefix + text + suffix, ranges: merged };
  }

  function titleRanges(doc, toks) {
    var f = fold(doc.title, true), ranges = [];
    toks.forEach(function (t) {
      var at = f.s.indexOf(t);
      if (at >= 0) ranges.push([f.map[at], f.map[at + t.length - 1] + 1]);
    });
    ranges.sort(function (a, b) { return a[0] - b[0]; });
    var merged = [];
    ranges.forEach(function (r) {
      var last = merged[merged.length - 1];
      if (last && r[0] <= last[1]) last[1] = Math.max(last[1], r[1]); else merged.push(r);
    });
    return merged;
  }

  return { fold: fold, tokens: tokens, prepare: prepare, search: search, snippet: snippet, titleRanges: titleRanges };
});
