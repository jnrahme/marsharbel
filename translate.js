(function () {
  if (window.__scTranslateInitialized) return;
  window.__scTranslateInitialized = true;

  var SUPPORTED_LANGUAGES = [
    { code: 'en', api: 'en', label: 'English' },
    { code: 'ar', api: 'ar', label: 'Arabic', rtl: true },
    { code: 'zh-cn', api: 'zh-CN', label: 'Chinese (Simplified)' },
    { code: 'zh-tw', api: 'zh-TW', label: 'Chinese (Traditional)' },
    { code: 'es', api: 'es', label: 'Spanish' },
    { code: 'fr', api: 'fr', label: 'French' },
    { code: 'de', api: 'de', label: 'German' },
    { code: 'pt', api: 'pt', label: 'Portuguese' },
    { code: 'ru', api: 'ru', label: 'Russian' },
    { code: 'hi', api: 'hi', label: 'Hindi' },
    { code: 'ja', api: 'ja', label: 'Japanese' },
    { code: 'ko', api: 'ko', label: 'Korean' },
    { code: 'it', api: 'it', label: 'Italian' },
    { code: 'tr', api: 'tr', label: 'Turkish' },
    { code: 'el', api: 'el', label: 'Greek' },
    { code: 'he', api: 'he', label: 'Hebrew', rtl: true },
    { code: 'af', api: 'af', label: 'Afrikaans' },
    { code: 'sq', api: 'sq', label: 'Albanian' },
    { code: 'am', api: 'am', label: 'Amharic' },
    { code: 'hy', api: 'hy', label: 'Armenian' },
    { code: 'az', api: 'az', label: 'Azerbaijani' },
    { code: 'eu', api: 'eu', label: 'Basque' },
    { code: 'be', api: 'be', label: 'Belarusian' },
    { code: 'bn', api: 'bn', label: 'Bengali' },
    { code: 'bs', api: 'bs', label: 'Bosnian' },
    { code: 'bg', api: 'bg', label: 'Bulgarian' },
    { code: 'ca', api: 'ca', label: 'Catalan' },
    { code: 'ceb', api: 'ceb', label: 'Cebuano' },
    { code: 'ny', api: 'ny', label: 'Chichewa' },
    { code: 'co', api: 'co', label: 'Corsican' },
    { code: 'hr', api: 'hr', label: 'Croatian' },
    { code: 'cs', api: 'cs', label: 'Czech' },
    { code: 'da', api: 'da', label: 'Danish' },
    { code: 'nl', api: 'nl', label: 'Dutch' },
    { code: 'eo', api: 'eo', label: 'Esperanto' },
    { code: 'et', api: 'et', label: 'Estonian' },
    { code: 'tl', api: 'tl', label: 'Filipino (Tagalog)' },
    { code: 'fi', api: 'fi', label: 'Finnish' },
    { code: 'fy', api: 'fy', label: 'Frisian' },
    { code: 'gl', api: 'gl', label: 'Galician' },
    { code: 'ka', api: 'ka', label: 'Georgian' },
    { code: 'gu', api: 'gu', label: 'Gujarati' },
    { code: 'ht', api: 'ht', label: 'Haitian Creole' },
    { code: 'ha', api: 'ha', label: 'Hausa' },
    { code: 'haw', api: 'haw', label: 'Hawaiian' },
    { code: 'hmn', api: 'hmn', label: 'Hmong' },
    { code: 'hu', api: 'hu', label: 'Hungarian' },
    { code: 'is', api: 'is', label: 'Icelandic' },
    { code: 'ig', api: 'ig', label: 'Igbo' },
    { code: 'id', api: 'id', label: 'Indonesian' },
    { code: 'ga', api: 'ga', label: 'Irish' },
    { code: 'jw', api: 'jw', label: 'Javanese' },
    { code: 'kn', api: 'kn', label: 'Kannada' },
    { code: 'kk', api: 'kk', label: 'Kazakh' },
    { code: 'km', api: 'km', label: 'Khmer' },
    { code: 'ku', api: 'ku', label: 'Kurdish (Kurmanji)' },
    { code: 'ky', api: 'ky', label: 'Kyrgyz' },
    { code: 'lo', api: 'lo', label: 'Lao' },
    { code: 'la', api: 'la', label: 'Latin' },
    { code: 'lv', api: 'lv', label: 'Latvian' },
    { code: 'lt', api: 'lt', label: 'Lithuanian' },
    { code: 'lb', api: 'lb', label: 'Luxembourgish' },
    { code: 'mk', api: 'mk', label: 'Macedonian' },
    { code: 'mg', api: 'mg', label: 'Malagasy' },
    { code: 'ms', api: 'ms', label: 'Malay' },
    { code: 'ml', api: 'ml', label: 'Malayalam' },
    { code: 'mt', api: 'mt', label: 'Maltese' },
    { code: 'mi', api: 'mi', label: 'Maori' },
    { code: 'mr', api: 'mr', label: 'Marathi' },
    { code: 'mn', api: 'mn', label: 'Mongolian' },
    { code: 'my', api: 'my', label: 'Myanmar (Burmese)' },
    { code: 'ne', api: 'ne', label: 'Nepali' },
    { code: 'no', api: 'no', label: 'Norwegian' },
    { code: 'or', api: 'or', label: 'Odia' },
    { code: 'ps', api: 'ps', label: 'Pashto', rtl: true },
    { code: 'fa', api: 'fa', label: 'Persian', rtl: true },
    { code: 'pl', api: 'pl', label: 'Polish' },
    { code: 'pa', api: 'pa', label: 'Punjabi' },
    { code: 'ro', api: 'ro', label: 'Romanian' },
    { code: 'sm', api: 'sm', label: 'Samoan' },
    { code: 'gd', api: 'gd', label: 'Scots Gaelic' },
    { code: 'sr', api: 'sr', label: 'Serbian' },
    { code: 'st', api: 'st', label: 'Sesotho' },
    { code: 'sn', api: 'sn', label: 'Shona' },
    { code: 'sd', api: 'sd', label: 'Sindhi', rtl: true },
    { code: 'si', api: 'si', label: 'Sinhala' },
    { code: 'sk', api: 'sk', label: 'Slovak' },
    { code: 'sl', api: 'sl', label: 'Slovenian' },
    { code: 'so', api: 'so', label: 'Somali' },
    { code: 'su', api: 'su', label: 'Sundanese' },
    { code: 'sw', api: 'sw', label: 'Swahili' },
    { code: 'sv', api: 'sv', label: 'Swedish' },
    { code: 'tg', api: 'tg', label: 'Tajik' },
    { code: 'ta', api: 'ta', label: 'Tamil' },
    { code: 'te', api: 'te', label: 'Telugu' },
    { code: 'th', api: 'th', label: 'Thai' },
    { code: 'uk', api: 'uk', label: 'Ukrainian' },
    { code: 'ur', api: 'ur', label: 'Urdu', rtl: true },
    { code: 'ug', api: 'ug', label: 'Uyghur', rtl: true },
    { code: 'uz', api: 'uz', label: 'Uzbek' },
    { code: 'vi', api: 'vi', label: 'Vietnamese' },
    { code: 'cy', api: 'cy', label: 'Welsh' },
    { code: 'xh', api: 'xh', label: 'Xhosa' },
    { code: 'yi', api: 'yi', label: 'Yiddish', rtl: true },
    { code: 'yo', api: 'yo', label: 'Yoruba' },
    { code: 'zu', api: 'zu', label: 'Zulu' }
  ];

  var POPULAR_LANGUAGE_CODES = [
    'en', 'ar', 'zh-cn', 'es', 'fr', 'de', 'pt', 'ru', 'hi', 'ja', 'ko', 'it', 'tr', 'el', 'he'
  ];

  var LANG_BY_CODE = {};
  SUPPORTED_LANGUAGES.forEach(function (lang) {
    LANG_BY_CODE[lang.code] = lang;
  });
  var POPULAR_SET = {};
  POPULAR_LANGUAGE_CODES.forEach(function (code) {
    POPULAR_SET[code] = true;
  });

  var EXCLUDED_SELECTOR = [
    'script',
    'style',
    'noscript',
    'textarea',
    'input',
    'select',
    'option',
    'code',
    'pre',
    '.notranslate',
    '.lang-switcher'
  ].join(',');
  var STORAGE_KEY = 'sc_lang_pref';

  function readStoredLang() {
    try {
      var stored = (localStorage.getItem(STORAGE_KEY) || '').toLowerCase();
      return LANG_BY_CODE[stored] ? stored : '';
    } catch (_) {
      return '';
    }
  }

  function writeStoredLang(langCode) {
    try {
      localStorage.setItem(STORAGE_KEY, langCode || 'en');
    } catch (_) {
      // no-op
    }
  }

  function getRequestedLang() {
    var params = new URLSearchParams(window.location.search);
    var fromQuery = (params.get('lang') || '').toLowerCase();
    var lang = fromQuery || readStoredLang() || 'en';
    return LANG_BY_CODE[lang] ? lang : 'en';
  }

  function buildUrlForLang(langCode) {
    var url = new URL(window.location.href);
    if (['/', '/index', '/index.html'].indexOf(url.pathname) !== -1 && (langCode === 'ar' || langCode === 'fr')) {
      url.pathname = '/' + langCode;
      url.searchParams.delete('lang');
      url.hash = '';
      return url.toString();
    }
    if (!langCode || langCode === 'en') {
      url.searchParams.delete('lang');
    } else {
      url.searchParams.set('lang', langCode);
    }
    return url.toString();
  }

  function rewriteInternalLinks(langCode) {
    var links = document.querySelectorAll('a[href]');
    links.forEach(function (anchor) {
      var rawHref = anchor.getAttribute('href');
      if (!rawHref) return;
      if (rawHref.startsWith('#')) return;
      if (/^(mailto:|tel:|javascript:)/i.test(rawHref)) return;
      var url;
      try {
        url = new URL(rawHref, window.location.href);
      } catch (_) {
        return;
      }
      if (url.origin !== window.location.origin) return;
      if (langCode && langCode !== 'en') {
        url.searchParams.set('lang', langCode);
      } else {
        url.searchParams.delete('lang');
      }
      anchor.setAttribute('href', url.pathname + url.search + url.hash);
    });
  }

  function isPrivacyPolicyPath(pathname) {
    return /\/privacy-policy(?:\.html)?$/.test(pathname || '');
  }

  function isTermsOfServicePath(pathname) {
    return /\/terms-of-service(?:\.html)?$/.test(pathname || '');
  }

  function isPrivacyPolicyHref(href) {
    if (!href) return false;
    try {
      return isPrivacyPolicyPath(new URL(href, window.location.href).pathname);
    } catch (_) {
      return false;
    }
  }

  function isTermsOfServiceHref(href) {
    if (!href) return false;
    try {
      return isTermsOfServicePath(new URL(href, window.location.href).pathname);
    } catch (_) {
      return false;
    }
  }

  function ensureLegalFooterLinks() {
    var footer = document.querySelector('footer.footer');
    if (!footer) {
      footer = document.createElement('footer');
      footer.className = 'footer';
      document.body.appendChild(footer);
    }

    var footerShell = footer.querySelector('.site-shell');
    if (!footerShell) {
      footerShell = document.createElement('div');
      footerShell.className = 'site-shell';
      while (footer.firstChild) {
        footerShell.appendChild(footer.firstChild);
      }
      footer.appendChild(footerShell);
    }

    if (!footerShell.textContent.trim()) {
      footerShell.textContent = 'Author: Please pray for the person who made this website.';
    }

    var hasPrivacyLink = Array.prototype.some.call(
      footerShell.querySelectorAll('a[href]'),
      function (anchor) {
        return isPrivacyPolicyHref(anchor.getAttribute('href'));
      }
    );

    var hasTermsLink = Array.prototype.some.call(
      footerShell.querySelectorAll('a[href]'),
      function (anchor) {
        return isTermsOfServiceHref(anchor.getAttribute('href'));
      }
    );

    var linksToAdd = [];

    if (!hasPrivacyLink) {
      linksToAdd.push({
        href: '/privacy-policy.html',
        text: 'Privacy Policy',
        isCurrent: isPrivacyPolicyPath(window.location.pathname || ''),
      });
    }

    if (!hasTermsLink) {
      linksToAdd.push({
        href: '/terms-of-service.html',
        text: 'Terms of Service',
        isCurrent: isTermsOfServicePath(window.location.pathname || ''),
      });
    }

    if (!linksToAdd.length) return;

    if (footerShell.childNodes.length) {
      footerShell.appendChild(document.createTextNode(' '));
    }

    linksToAdd.forEach(function (link, index) {
      if (index > 0) {
        footerShell.appendChild(document.createTextNode(' · '));
      }

      var legalLink = document.createElement('a');
      legalLink.href = link.href;
      legalLink.textContent = link.text;
      if (link.isCurrent) {
        legalLink.setAttribute('aria-current', 'page');
      }

      footerShell.appendChild(legalLink);
    });

    footerShell.appendChild(document.createTextNode('.'));
  }

  function ensureHeadTag(tagName, attrs) {
    var selector = tagName;
    if (attrs.name) selector += '[name="' + attrs.name + '"]';
    if (attrs.rel) selector += '[rel="' + attrs.rel + '"]';
    if (attrs.property) selector += '[property="' + attrs.property + '"]';
    var existing = document.head.querySelector(selector);
    if (!existing) {
      existing = document.createElement(tagName);
      document.head.appendChild(existing);
    }
    Object.keys(attrs).forEach(function (key) {
      existing.setAttribute(key, attrs[key]);
    });
    return existing;
  }

  function ensurePwaHeadAssets() {
    ensureHeadTag('link', { rel: 'manifest', href: '/manifest.webmanifest' });
    ensureHeadTag('meta', { name: 'theme-color', content: '#0a1622' });
    ensureHeadTag('meta', { name: 'apple-mobile-web-app-capable', content: 'yes' });
    ensureHeadTag('meta', { name: 'apple-mobile-web-app-status-bar-style', content: 'black-translucent' });
    ensureHeadTag('meta', { name: 'apple-mobile-web-app-title', content: 'Saint Charbel' });
    ensureHeadTag('link', { rel: 'apple-touch-icon', href: '/pwa/apple-touch-icon.png' });
    ensureHeadTag('link', { rel: 'icon', type: 'image/png', sizes: '32x32', href: '/favicon-32x32.png' });
    ensureHeadTag('link', { rel: 'icon', type: 'image/png', sizes: '16x16', href: '/favicon-16x16.png' });
  }

  function cleanCanonicalPath(pathname) {
    if (!pathname) return '/';
    if (pathname === '/index.html' || pathname === '/index') return '/';
    if (pathname.endsWith('.html')) return pathname.slice(0, -5);
    return pathname.length > 1 ? pathname.replace(/\/$/, '') : pathname;
  }

  function inferDescription() {
    var existing = document.head.querySelector('meta[name="description"]');
    if (existing && existing.getAttribute('content')) {
      return existing.getAttribute('content');
    }
    var firstParagraph = document.querySelector('main p, article p, section p');
    var raw = firstParagraph ? (firstParagraph.textContent || '') : '';
    var normalized = raw.replace(/\s+/g, ' ').trim();
    if (!normalized) {
      normalized = 'Explore Saint Charbel: history, story, miracles, testimonies, and guided Rosary prayer resources.';
    }
    if (normalized.length > 160) {
      normalized = normalized.slice(0, 157).trimEnd() + '...';
    }
    return normalized;
  }

  function ensureSeoHeadAssets() {
    var url = new URL(window.location.href);
    url.hash = '';
    url.search = '';
    url.pathname = cleanCanonicalPath(url.pathname);
    // Published HTML owns canonicalization, including aliases and the preferred
    // production hostname. Do not replace it with a preview or www origin.
    var canonicalTag = document.head.querySelector('link[rel="canonical"]');
    var canonical = canonicalTag && canonicalTag.getAttribute('href') || url.toString();
    var title = document.title || 'Saint Charbel';
    var description = inferDescription();
    var imageUrl = new URL('/saint-charbel.jpg', window.location.origin).toString();

    ensureHeadTag('meta', { name: 'description', content: description });
    if (!document.head.querySelector('meta[name="robots"]')) {
      ensureHeadTag('meta', { name: 'robots', content: 'index,follow,max-image-preview:large' });
    }
    ensureHeadTag('link', { rel: 'canonical', href: canonical });
    ensureHeadTag('meta', { property: 'og:type', content: 'website' });
    ensureHeadTag('meta', { property: 'og:site_name', content: 'Saint Charbel' });
    ensureHeadTag('meta', { property: 'og:title', content: title });
    ensureHeadTag('meta', { property: 'og:description', content: description });
    ensureHeadTag('meta', { property: 'og:url', content: canonical });
    ensureHeadTag('meta', { property: 'og:image', content: imageUrl });
    ensureHeadTag('meta', { name: 'twitter:card', content: 'summary_large_image' });
    ensureHeadTag('meta', { name: 'twitter:title', content: title });
    ensureHeadTag('meta', { name: 'twitter:description', content: description });
    ensureHeadTag('meta', { name: 'twitter:image', content: imageUrl });
  }

  function registerServiceWorker() {
    if (!('serviceWorker' in navigator)) return;
    window.addEventListener('load', function () {
      navigator.serviceWorker.register('/service-worker.js', { updateViaCache: 'none' }).catch(function () {
        // no-op
      });
    }, { once: true });
  }

  function setupInstallAppPrompt() {
    var isStandalone = window.matchMedia('(display-mode: standalone)').matches || window.navigator.standalone === true;
    if (isStandalone) return;

    var ua = (window.navigator.userAgent || '').toLowerCase();
    var isIOS = /iphone|ipad|ipod/.test(ua);
    var deferredPrompt = null;
    var hint = document.createElement('div');
    hint.id = 'sc-install-hint';
    hint.className = 'notranslate';
    hint.style.position = 'fixed';
    hint.style.left = '50%';
    hint.style.right = 'auto';
    hint.style.bottom = 'calc(14px + env(safe-area-inset-bottom))';
    hint.style.transform = 'translateX(-50%)';
    hint.style.zIndex = '9999';
    hint.style.display = 'none';
    hint.style.maxWidth = 'min(92vw, 380px)';
    hint.style.padding = '10px 12px';
    hint.style.borderRadius = '10px';
    hint.style.border = '1px solid rgba(211,178,110,.28)';
    hint.style.background = 'rgba(10,18,28,.96)';
    hint.style.color = '#ece8df';
    hint.style.fontSize = '12px';
    hint.style.lineHeight = '1.45';
    hint.style.fontFamily = 'Manrope, system-ui, sans-serif';
    document.body.appendChild(hint);

    var hintTimer = null;
    function showHint(message) {
      if (!message) return;
      hint.textContent = message;
      hint.style.display = 'block';
      hint.setAttribute('role', 'status');
      hint.setAttribute('aria-live', 'polite');
      if (hintTimer) clearTimeout(hintTimer);
      hintTimer = setTimeout(function () {
        hint.style.display = 'none';
      }, 6000);
    }

    var handleInstallClick = function () {
      if (deferredPrompt) {
        deferredPrompt.prompt();
        deferredPrompt.userChoice.finally(function () {
          deferredPrompt = null;
        });
        return;
      }

      if (isIOS) {
        showHint("On iPhone: tap Share, then 'Add to Home Screen'.");
      } else {
        showHint("If no popup appears, open browser menu and choose 'Install app' or 'Add to Home screen'.");
      }
    };
    window.__scInstallApp = handleInstallClick;
    window.__scInstallLabel = isIOS ? 'Add App' : 'Install App';

    var footerHost = document.querySelector('.footer .site-shell') || document.querySelector('.footer') || document.querySelector('main');
    if (footerHost) {
      var installLinkWrap = document.createElement('p');
      installLinkWrap.className = 'notranslate';
      installLinkWrap.style.marginTop = '0.7rem';
      installLinkWrap.style.fontSize = '0.9rem';
      installLinkWrap.style.color = '#d9d4c8';

      var installLink = document.createElement('a');
      installLink.href = '#install-app';
      installLink.textContent = 'Click here to install this app';
      installLink.style.color = '#ddbf80';
      installLink.style.textDecoration = 'underline';
      installLink.addEventListener('click', function (event) {
        event.preventDefault();
        handleInstallClick();
      });

      installLinkWrap.appendChild(installLink);
      footerHost.appendChild(installLinkWrap);
    }

    window.addEventListener('beforeinstallprompt', function (event) {
      event.preventDefault();
      deferredPrompt = event;
    });

    window.addEventListener('appinstalled', function () {
      hint.style.display = 'none';
      var headerBtn = document.getElementById('sc-install-app-btn');
      if (headerBtn) {
        headerBtn.style.display = 'none';
      }
    });

  }

  function createSwitcher(currentCode) {
    if (document.getElementById('sc-language-switcher')) return;

    var container = document.createElement('div');
    container.id = 'sc-language-switcher';
    container.className = 'lang-switcher notranslate';

    var label = document.createElement('label');
    label.setAttribute('for', 'sc-language-select');
    label.textContent = 'Language';

    var select = document.createElement('select');
    select.id = 'sc-language-select';
    select.setAttribute('aria-label', 'Choose language');

    var popular = SUPPORTED_LANGUAGES.filter(function (lang) {
      return POPULAR_SET[lang.code];
    });
    var allSorted = SUPPORTED_LANGUAGES.filter(function (lang) {
      return !POPULAR_SET[lang.code];
    }).sort(function (a, b) {
      return a.label.localeCompare(b.label);
    });

    var popularGroup = document.createElement('optgroup');
    popularGroup.label = 'Popular';
    popular.forEach(function (lang) {
      var opt = document.createElement('option');
      opt.value = lang.code;
      opt.textContent = lang.label;
      popularGroup.appendChild(opt);
    });
    select.appendChild(popularGroup);

    var allGroup = document.createElement('optgroup');
    allGroup.label = 'All Languages (A-Z)';
    allSorted.forEach(function (lang) {
      var opt = document.createElement('option');
      opt.value = lang.code;
      opt.textContent = lang.label;
      allGroup.appendChild(opt);
    });
    select.appendChild(allGroup);

    select.value = currentCode;
    select.addEventListener('change', function () {
      writeStoredLang(select.value);
      window.location.assign(buildUrlForLang(select.value));
    });

    container.appendChild(label);
    container.appendChild(select);

    if (!document.getElementById('sc-install-app-btn') && typeof window.__scInstallApp === 'function') {
      var installBtn = document.createElement('button');
      installBtn.id = 'sc-install-app-btn';
      installBtn.type = 'button';
      installBtn.className = 'sc-install-app-btn';
      installBtn.textContent = window.__scInstallLabel || 'Install App';
      installBtn.addEventListener('click', function () {
        window.__scInstallApp();
      });
      container.appendChild(installBtn);
    }

    var nav = document.querySelector('.topbar .nav');
    if (nav) {
      var slot = nav.querySelector('.lang-switcher-slot');
      if (slot) slot.replaceWith(container);
      else nav.appendChild(container);
    } else {
      container.classList.add('lang-switcher-floating');
      document.body.appendChild(container);
    }
  }

  function collectTextNodes() {
    var list = [];
    var walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    var node;
    while ((node = walker.nextNode())) {
      if (!node.nodeValue) continue;
      if (!node.nodeValue.trim()) continue;

      var parent = node.parentElement;
      if (!parent) continue;
      if (parent.closest(EXCLUDED_SELECTOR)) continue;
      if (parent.isContentEditable) continue;

      var trimmed = node.nodeValue.trim();
      if (!/[A-Za-z]/.test(trimmed)) continue;
      if (/^[0-9\W_]+$/.test(trimmed)) continue;

      if (!node.__scOriginalText) {
        node.__scOriginalText = node.nodeValue;
      }
      list.push({ node: node, original: node.__scOriginalText });
    }
    return list;
  }

  function splitByWhitespaceEdges(text) {
    var leading = (text.match(/^\s*/) || [''])[0];
    var trailing = (text.match(/\s*$/) || [''])[0];
    var core = text.substring(leading.length, text.length - trailing.length);
    return { leading: leading, core: core, trailing: trailing };
  }

  function parseTranslationPayload(payload) {
    if (!Array.isArray(payload) || !Array.isArray(payload[0])) return '';
    return payload[0].map(function (part) {
      return Array.isArray(part) ? (part[0] || '') : '';
    }).join('');
  }

  var translationCache = new Map();

  async function translateCoreText(coreText, targetLangApi) {
    var key = targetLangApi + '::' + coreText;
    if (translationCache.has(key)) return translationCache.get(key);

    var url =
      'https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&dt=t&tl=' +
      encodeURIComponent(targetLangApi) +
      '&q=' +
      encodeURIComponent(coreText);

    var response = await fetch(url, { credentials: 'omit' });
    if (!response.ok) throw new Error('translate API error: ' + response.status);
    var payload = await response.json();
    var translated = parseTranslationPayload(payload) || coreText;
    translationCache.set(key, translated);
    return translated;
  }

  async function translatePage(langCode) {
    var target = LANG_BY_CODE[langCode];
    if (!target) return;

    var html = document.documentElement;
    if (langCode === 'en') {
      setEnglishDocumentDefaults();
      var englishNodes = collectTextNodes();
      englishNodes.forEach(function (item) {
        item.node.nodeValue = item.original;
      });
      return;
    }

    html.setAttribute('lang', target.api);
    html.setAttribute('dir', target.rtl ? 'rtl' : 'ltr');

    var nodes = collectTextNodes();
    if (!nodes.length) return;

    var uniqueCore = new Map();
    nodes.forEach(function (item) {
      var parts = splitByWhitespaceEdges(item.original);
      if (parts.core) uniqueCore.set(parts.core, true);
    });

    var keys = Array.from(uniqueCore.keys());
    var workers = 5;
    var index = 0;

    async function runWorker() {
      while (index < keys.length) {
        var currentIndex = index++;
        var core = keys[currentIndex];
        try {
          await translateCoreText(core, target.api);
        } catch (err) {
          console.warn('Translation skipped for segment:', core, err);
        }
      }
    }

    var pool = [];
    for (var i = 0; i < workers; i += 1) pool.push(runWorker());
    await Promise.all(pool);

    nodes.forEach(function (item) {
      var parts = splitByWhitespaceEdges(item.original);
      var translatedCore = translationCache.get(target.api + '::' + parts.core);
      if (!translatedCore) return;
      item.node.nodeValue = parts.leading + translatedCore + parts.trailing;
    });
  }

  function setEnglishDocumentDefaults() {
    var html = document.documentElement;
    html.setAttribute('lang', 'en');
    html.setAttribute('dir', 'ltr');
  }

  var requestedLang = getRequestedLang();
  ensureSeoHeadAssets();
  ensurePwaHeadAssets();
  registerServiceWorker();
  ensureLegalFooterLinks();
  setupInstallAppPrompt();
  writeStoredLang(requestedLang);
  createSwitcher(requestedLang);
  rewriteInternalLinks(requestedLang);

  var translationTicking = false;
  var translationQueued = false;
  function runRequestedTranslation() {
    if (translationTicking) {
      translationQueued = true;
      return;
    }
    translationTicking = true;
    translatePage(requestedLang).catch(function (err) {
      console.error('Page translation failed', err);
    }).finally(function () {
      rewriteInternalLinks(requestedLang);
      translationTicking = false;
      if (translationQueued) {
        translationQueued = false;
        runRequestedTranslation();
      }
    });
  }

  window.__scApplyTranslation = runRequestedTranslation;

  var boot = function () {
    if (requestedLang === 'en') {
      setEnglishDocumentDefaults();
      return;
    }
    runRequestedTranslation();
  };

  if (document.readyState === 'loading') {
    window.addEventListener('DOMContentLoaded', boot, { once: true });
  } else {
    boot();
  }

  window.addEventListener('sc:content-updated', function () {
    if (requestedLang === 'en') return;
    runRequestedTranslation();
  });
})();
