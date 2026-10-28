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
  function travelIdentity(page, variant, language) {
    if (!variant || !variant.proof || variant.proof.type !== 'reviewed-travel-release') return true;
    if (!page || typeof page.sourcePath !== 'string' || typeof variant.path !== 'string' ||
        !Array.isArray(variant.aliases) || variant.aliases.length) return false;
    var leaf = page.sourcePath.replace(/\.html$/, '');
    var routes = {en:'/' + leaf, de:'/de/' + leaf, 'zh-Hans':'/zh-Hans/' + leaf};
    if (leaf === 'visit-annaya') routes.de='/de/annaya';
    if (leaf === 'saint-charbel-pilgrimage') {routes.de='/de/pilgerreise';routes['zh-Hans']='/zh-Hans/pilgrimage';}
    return Object.hasOwn(routes,language) && variant.path === routes[language];
  }
  function locate(manifest, pathname) {
    if (!manifest || manifest.version !== 1) return null;
    var key = pathKey(pathname), found = null;
    Object.keys(manifest.pages || {}).forEach(function (id) {
      var page = manifest.pages[id];
      Object.keys(page.variants || {}).forEach(function (lang) {
        var variant = page.variants[lang];
        if (!travelIdentity(page,variant,lang)) return;
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
    if (page && variant && proof && proof.type === 'scoped-travel-variant') {
      var leaf = page.sourcePath.replace(/\.html$/, '');
      var sources = ['travel','annaya-tour','bekaa-kafra','bkerke-maronite-patriarchate','cedars-of-god-lebanon','our-lady-of-lebanon-harissa','qadisha-valley','qannoubine-monastery','qozhaya-monastery','saint-charbel-hermitage','saint-charbel-places-lebanon','saint-charbel-trail'];
      var paths = ['/' + leaf, '/de/' + leaf, '/ru/' + leaf];
      if (leaf === 'travel') paths.push('/hi/travel');
      return sources.includes(leaf) && paths.includes(variant.path) && variant.status === 'verified' &&
        ['approved','carried'].includes(proof.state) && proof.nativeReviewStatus === 'not-certified' &&
        typeof proof.scope === 'string' && !!proof.scope && typeof proof.evidenceRef === 'string' && !!proof.evidenceRef &&
        /^[a-f0-9]{64}$/.test(proof.candidateFileSha256 || '') && /^[a-f0-9]{40}$/.test(page.sourceRevision || '') &&
        /^[a-f0-9]{64}$/.test(variant.contentSha256 || '') && proof.reviewedContentSha256 === variant.contentSha256 &&
        variant.sourceSha256 === page.sourceSha256 && Array.isArray(variant.aliases) && variant.aliases.length === 0;
    }
    if (page && variant && proof && proof.type === 'scoped-ar2-variant') {
      var ar2ArPaths = ['/ar/gallery','/ar/saints','/ar/prayer-library','/ar/encyclopedia','/ar/news','/ar/videos','/ar/testimonies','/ar/voice-testimony','/ar/','/ar/feast-day','/ar/litany-of-saint-charbel','/ar/saint-charbel-chaplet','/ar/miracles/eucharistic/','/ar/miracles/eucharistic/amsterdam','/ar/miracles/eucharistic/bolsena-orvieto','/ar/miracles/eucharistic/faverney','/ar/miracles/eucharistic/ivorra','/ar/miracles/eucharistic/lanciano','/ar/miracles/eucharistic/legnica','/ar/miracles/eucharistic/ludbreg','/ar/miracles/eucharistic/santarem','/ar/miracles/eucharistic/siena','/ar/miracles/eucharistic/sokolka','/ar/travel','/ar/qadisha-valley','/ar/qannoubine-monastery','/ar/qozhaya-monastery','/ar/miracles/','/ar/miracles/dafne-gutierrez','/ar/miracles/nohad-el-shami','/ar/miracles/raymond-nader','/ar/rosary']; // /feedback and /submit-testimony excluded: noindex pages never get the control stack (scrum ruling 2026-10-12)
      var ar2EnPaths = ['/gallery','/saints','/prayer-library','/saint-charbel-encyclopedia','/news','/videos','/testimonies','/voice-testimony','/','/saint-charbel-feast-day','/litany-of-saint-charbel','/saint-charbel-chaplet','/miracles/eucharistic/','/miracles/eucharistic/amsterdam','/miracles/eucharistic/bolsena-orvieto','/miracles/eucharistic/faverney','/miracles/eucharistic/ivorra','/miracles/eucharistic/lanciano','/miracles/eucharistic/legnica','/miracles/eucharistic/ludbreg','/miracles/eucharistic/santarem','/miracles/eucharistic/siena','/miracles/eucharistic/sokolka','/travel','/qadisha-valley','/qannoubine-monastery','/qozhaya-monastery','/miracles/','/miracles/dafne-gutierrez','/miracles/nohad-el-shami','/miracles/raymond-nader','/rosary-intro'];
      // Exact index-matched pair (scrum review, PR #750): an en variant must sit at an
      // EN-pinned path, an ar variant at the AR-pinned path of the SAME index, so an
      // Arabic page can never ride under an English route.
      var ar2Code = Object.keys(page.variants || {}).find(function(k){ return page.variants[k] === variant; });
      var ar2Idx = ar2Code === 'en' ? ar2EnPaths.indexOf(variant.path) : ar2Code === 'ar' ? ar2ArPaths.indexOf(variant.path) : -1;
      var ar2PairOk = ar2Idx >= 0 && !!(page.variants.en && page.variants.ar) &&
        page.variants.en.path === ar2EnPaths[ar2Idx] && page.variants.ar.path === ar2ArPaths[ar2Idx];
      return ar2PairOk &&
        variant.status === 'verified' && proof.state === 'approved' &&
        proof.nativeReviewStatus === 'not-certified' &&
        typeof proof.scope === 'string' && !!proof.scope && typeof proof.evidenceRef === 'string' && !!proof.evidenceRef &&
        /^[a-f0-9]{64}$/.test(proof.candidateFileSha256 || '') &&
        /^[a-f0-9]{40}$/.test(page.sourceRevision || '') &&
        /^[a-f0-9]{64}$/.test(variant.contentSha256 || '') &&
        proof.reviewedContentSha256 === variant.contentSha256 &&
        variant.sourceSha256 === page.sourceSha256 &&
        Array.isArray(variant.aliases) && variant.aliases.length === 0;
    }
    if (page && variant && proof && proof.type === 'reviewed-history-master') {
      return page.sourcePath === 'history.html' && proof.family === 'history-master' &&
        variant.status === 'verified' && (proof.renderedReviewStatus === 'approved-history-source-correction-c476eada-9-pages-390-1280' ||
        (['/hi/history','/th/history'].includes(variant.path) && proof.renderedReviewStatus === 'approved-hi-th-preview-render-access-5effc075-390-1280')) &&
        !!proof.catalogReview && !!proof.renderedReview && proof.reviewedContentSha256 === variant.contentSha256 &&
        /^[a-f0-9]{64}$/.test(variant.contentSha256 || '') && variant.sourceSha256 === page.sourceSha256;
    }
    if (page && variant && proof && proof.type === 'reviewed-travel-release') {
      var travelSources = ['travel.html','visit-annaya.html','bekaa-kafra.html','qadisha-valley.html','qannoubine-monastery.html','qozhaya-monastery.html','saint-charbel-hermitage.html','saint-charbel-trail.html','saint-charbel-places-lebanon.html','our-lady-of-lebanon-harissa.html','cedars-of-god-lebanon.html','bkerke-maronite-patriarchate.html','saint-charbel-pilgrimage.html','annaya-tour.html'];
      if (typeof page.sourcePath !== 'string' || typeof variant.path !== 'string' ||
          !Array.isArray(variant.aliases) || variant.aliases.length) return false;
      var sourceLeaf = page.sourcePath.replace(/\.html$/, '');
      var allowedPaths = ['/' + sourceLeaf,
        sourceLeaf === 'visit-annaya' ? '/de/annaya' : sourceLeaf === 'saint-charbel-pilgrimage' ? '/de/pilgerreise' : '/de/' + sourceLeaf,
        sourceLeaf === 'saint-charbel-pilgrimage' ? '/zh-Hans/pilgrimage' : '/zh-Hans/' + sourceLeaf];
      return travelSources.includes(page.sourcePath) && allowedPaths.includes(pathKey(variant.path)) &&
        variant.status === 'verified' && /^[a-f0-9]{64}$/.test(page.sourceSha256 || '') &&
        /^[a-f0-9]{40}$/.test(page.sourceRevision || '') && /^[a-f0-9]{64}$/.test(variant.contentSha256 || '') &&
        variant.sourceSha256 === page.sourceSha256 && proof.reviewedContentSha256 === variant.contentSha256 &&
        proof.nativeReviewStatus === 'pending-post-release' && !!proof.nativeFollowUp &&
        proof.contentReviewMode === 'model-only' && !!proof.editorialReview && !!proof.renderedReview &&
        proof.keyedTextComplete === true && proof.mediaParity === true && proof.linkParity === true &&
        proof.schemaParity === true && proof.anchorParity === true && proof.interactionParity === true;
    }
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
  var VERONICA_MODEL_ONLY_ROUTES = {'en':'/veronica-giuliani-story','ar':'/ar/veronica-giuliani-story','de':'/de/veronica-giuliani-story','es':'/es/veronica-giuliani-story','fr':'/fr/veronica-giuliani-story','hi':'/hi/veronica-giuliani-story','it':'/it/veronica-giuliani-story','pl':'/pl/veronica-giuliani-story','pt':'/pt/veronica-giuliani-story','ru':'/ru/veronica-giuliani-story','th':'/th/veronica-giuliani-story','zh-Hans':'/zh-Hans/veronica-giuliani-story'};
  // Narrow Veronica model-only branch: scope-approved for enabled tests only.
  // Asserts pins + only actually-tested parities; never native-language certification.
  function verifiedModelOnly(page, variant, lang) {
    var proof = variant && variant.proof;
    return !!(page && variant && page.reviewScope === 'veronica-model-only-enabled-tests' &&
      page.sourcePath === 'veronica-giuliani-story.html' &&
      variant.status === 'verified' && VERONICA_MODEL_ONLY_ROUTES[lang] === pathKey(variant.path || '') &&
      Array.isArray(variant.aliases) && variant.aliases.length === 0 &&
      /^[a-f0-9]{64}$/.test(page.sourceSha256 || '') &&
      /^[a-f0-9]{40}$/.test(page.sourceRevision || '') &&
      /^[a-f0-9]{64}$/.test(variant.contentSha256 || '') &&
      variant.sourceSha256 === page.sourceSha256 && proof &&
      proof.contentReviewMode === 'model-only' &&
      proof.nativeReviewStatus === 'not-certified' &&
      proof.scope === 'enabled-tests-only' && !proof.nativeSampleReview &&
      proof.keyedTextComplete === true && proof.mediaParity === true && proof.linkParity === true &&
      typeof proof.editorialReview === 'string' && !!proof.editorialReview &&
      typeof proof.renderedReview === 'string' && !!proof.renderedReview &&
      typeof proof.receipt === 'string' && !!proof.receipt &&
      /^[a-f0-9]{64}$/.test(proof.reviewedContentSha256 || '') &&
      proof.reviewedContentSha256 === variant.contentSha256);
  }
  function verifiedEither(page, variant, lang) { return verified(page, variant) || verifiedModelOnly(page, variant, lang); }
  function resolve(manifest, href, requested, actualLanguage) {
    var url = new URL(href), current = locate(manifest, url.pathname);
    var language = current ? current.language : actualLanguage;
    requested = ((manifest && manifest.aliases || {})[String(requested).toLowerCase()] || requested);
    var result = { available: false, href: href, contentLanguage: language, pageID: current && current.pageID, reason: 'translation-unavailable' };
    if (requested === language) { result.available = true; result.reason = 'same-language'; return result; }
    var homes = manifest && manifest.publishedHomes || {};
    if (Object.values(homes).some(function(path){return pathKey(path) === pathKey(url.pathname);}) && homes[requested]) {
      url.pathname = homes[requested]; url.searchParams.delete('lang'); url.hash = '';
      result.available = true; result.href = url.toString(); result.contentLanguage = requested;
      result.reason = 'published-home'; return result;
    }
    // English is the source escape route, not a claim of translated equivalence.
    var english = manifest && manifest.englishSources && manifest.englishSources[pathKey(url.pathname)];
    if (requested === 'en' && english) {
      var sourceHash = '';
      var englishTarget = current && current.page.variants.en;
      if (url.hash && current && verifiedEither(current.page, current.variant) &&
          verifiedEither(current.page, englishTarget) && pathKey(englishTarget.path) === pathKey(english)) {
        try {
          var sourceKey = decodeURIComponent(url.hash.slice(1));
          var sourceAnchors = current.page.anchorIDs || {};
          var sourceLogical = Object.keys(sourceAnchors).find(function (id) { return sourceAnchors[id][language] === sourceKey; });
          if (sourceLogical && sourceAnchors[sourceLogical].en) sourceHash = sourceAnchors[sourceLogical].en;
        } catch (_) { /* Malformed fragments never block the English source escape. */ }
      }
      url.pathname = english; url.searchParams.delete('lang'); url.hash = sourceHash;
      result.available = true; result.href = url.toString(); result.contentLanguage = 'en';
      result.reason = 'english-source'; return result;
    }
    if (!current || !(manifest.languages || []).includes(requested)) return result;
    var target = current.page.variants[requested];
    if (!travelIdentity(current.page,current.variant,language) || !travelIdentity(current.page,target,requested) ||
        !verifiedEither(current.page, current.variant, language) || !verifiedEither(current.page, target, requested)) return result;
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
