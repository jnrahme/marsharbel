(function () {
  if (window.__scTranslateInitialized) return;
  window.__scTranslateInitialized = true;

  var runtimeLabelNode = document.getElementById('sc-runtime-labels');
  var runtimeLabels = runtimeLabelNode ? JSON.parse(runtimeLabelNode.textContent) : null;
  function runtimeText(key, fallback) { return runtimeLabels && runtimeLabels[key] || fallback; }

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

    var hasAccessibilityLink = Array.prototype.some.call(
      footerShell.querySelectorAll('a[href]'),
      function (anchor) {
        return /\/accessibility(?:\.html)?$/.test(anchor.getAttribute('href') || '');
      }
    );

    var linksToAdd = [];

    if (!hasPrivacyLink) {
      linksToAdd.push({
        href: '/privacy-policy',
        text: runtimeText('footer.privacy', 'Privacy Policy'),
        isCurrent: isPrivacyPolicyPath(window.location.pathname || ''),
      });
    }

    if (!hasTermsLink) {
      linksToAdd.push({
        href: '/terms-of-service',
        text: runtimeText('footer.terms', 'Terms of Service'),
        isCurrent: isTermsOfServicePath(window.location.pathname || ''),
      });
    }

    if (!hasAccessibilityLink) {
      linksToAdd.push({
        href: '/accessibility',
        text: runtimeText('footer.accessibility', 'Accessibility'),
        isCurrent: /\/accessibility(?:\.html)?$/.test(window.location.pathname || ''),
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
    var existingImage = document.head.querySelector('meta[property="og:image"]');
    var imageUrl = existingImage && existingImage.getAttribute('content') || new URL('/saint-charbel.jpg', window.location.origin).toString();

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
        showHint(runtimeText('install.ios', "On iPhone: tap Share, then 'Add to Home Screen'."));
      } else {
        showHint(runtimeText('install.browser', "If no popup appears, open browser menu and choose 'Install app' or 'Add to Home screen'."));
      }
    };
    window.__scInstallApp = handleInstallClick;
    window.__scInstallLabel = runtimeText('install.label', 'Install App');

    var footerHost = document.querySelector('.footer .site-shell') || document.querySelector('.footer') || document.querySelector('main');
    if (footerHost) {
      var installLinkWrap = document.createElement('p');
      installLinkWrap.className = 'notranslate';
      installLinkWrap.style.marginTop = '0.7rem';
      installLinkWrap.style.fontSize = '0.9rem';
      installLinkWrap.style.color = '#d9d4c8';

      var installLink = document.createElement('a');
      installLink.href = '#install-app';
      installLink.textContent = runtimeText('install.link', 'Click here to install this app');
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

  // Language routing belongs to the authored same-page resolver.
  // Keep install/legal/SEO capabilities; never rewrite content or ordinary links.
  ensureSeoHeadAssets();
  ensurePwaHeadAssets();
  registerServiceWorker();
  ensureLegalFooterLinks();
  setupInstallAppPrompt();
})();
