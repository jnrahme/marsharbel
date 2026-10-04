/* Pure page-identity language routing. No topic substitutes, prefs, or network translation. */
(function (root, factory) {
  var api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.SC_SAME_PAGE = api;
})(typeof window === 'object' ? window : globalThis, function () {

  function pathKey(path) {
    var clean = path.replace(/\/index(?:\.html)?$/, '/').replace(/\.html$/, '').replace(/\/$/, '');
    return clean || '/';
  }
  function locate(manifest, pathname) {
    if (!manifest || manifest.version !== 1) return null;
    var key = pathKey(pathname), found = null;
    Object.keys(manifest.pages || {}).forEach(function (id) {
      var page = manifest.pages[id];
      Object.keys(page.variants || {}).forEach(function (lang) {
        var variant = page.variants[lang];
        [variant.path].concat(variant.aliases || []).forEach(function (path) {
          if (pathKey(path) === key) {
            if (found && (found.pageID !== id || found.language !== lang)) throw new Error('ambiguous-page-identity');
            found = { pageID: id, language: lang, page: page, variant: variant };
          }
        });
      });
    });
    return found;
  }
  function verified(page, variant) {
    var proof = variant && variant.proof;
    return !!(page && variant && variant.status === 'verified' &&
      /^[a-f0-9]{64}$/.test(page.sourceSha256 || '') &&
      /^[a-f0-9]{40}$/.test(page.sourceRevision || '') &&
      /^[a-f0-9]{64}$/.test(variant.contentSha256 || '') &&
      variant.sourceSha256 === page.sourceSha256 && proof &&
      proof.keyedTextComplete === true && proof.mediaParity === true &&
      proof.linkParity === true && proof.schemaParity === true &&
      proof.anchorParity === true && proof.interactionParity === true &&
      typeof proof.editorialReview === 'string' && !!proof.editorialReview &&
      typeof proof.nativeSampleReview === 'string' && !!proof.nativeSampleReview &&
      typeof proof.renderedReview === 'string' && !!proof.renderedReview);
  }
  function resolve(manifest, href, requested, actualLanguage) {
    var url = new URL(href), current = locate(manifest, url.pathname);
    var language = current ? current.language : actualLanguage;
    requested = ((manifest && manifest.aliases || {})[String(requested).toLowerCase()] || requested);
    var result = { available: false, href: href, contentLanguage: language, pageID: current && current.pageID, reason: 'translation-unavailable' };
    if (requested === language) { result.available = true; result.reason = 'same-language'; return result; }
    if (!current || !(manifest.languages || []).includes(requested)) return result;
    var target = current.page.variants[requested];
    if (!verified(current.page, current.variant) || !verified(current.page, target)) return result;
    if (url.hash) {
      var key;
      try { key = decodeURIComponent(url.hash.slice(1)); } catch (_) { return result; }
      var anchors = current.page.anchorIDs || {};
      var logical = Object.keys(anchors).find(function (id) { return anchors[id][language] === key; });
      if (!logical || !anchors[logical][requested]) { result.reason = 'anchor-unavailable'; return result; }
      url.hash = anchors[logical][requested];
    }
    url.pathname = target.path;
    url.searchParams.delete('lang');
    result.available = true; result.href = url.toString(); result.contentLanguage = requested; result.reason = 'verified-twin';
    return result;
  }
  return { pathKey: pathKey, locate: locate, verified: verified, resolve: resolve };
});
