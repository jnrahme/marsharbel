(() => {
  const script = document.currentScript;
  const mode = (script && script.dataset.shareMode) || 'page';
  const canonical = document.querySelector('link[rel="canonical"]');
  const baseUrl = canonical ? canonical.href : location.origin + location.pathname;
  const pageTitle = (document.querySelector('meta[property="og:title"]')?.content || document.title || '').split('|')[0].trim();
  const ogImage = document.querySelector('meta[property="og:image"]')?.content || '';
  const clean = text => (text || '').replace(/\s+/g, ' ').trim();

  const urlFor = (hash, source) => {
    const url = new URL(baseUrl);
    if (source) {
      url.searchParams.set('utm_source', source);
      url.searchParams.set('utm_medium', 'share');
    }
    url.hash = hash ? '#' + hash : '';
    return url.toString();
  };

  // Brand glyphs: Simple Icons (CC0), 24x24 viewBox. Inline SVG, no external requests.
  const icons = {
    facebook: 'M9.101 23.691v-7.98H6.627v-3.667h2.474v-1.58c0-4.085 1.848-5.978 5.858-5.978.401 0 .955.042 1.468.103a8.68 8.68 0 0 1 1.141.195v3.325a8.623 8.623 0 0 0-.653-.036 26.805 26.805 0 0 0-.733-.009c-.707 0-1.259.096-1.675.309a1.686 1.686 0 0 0-.679.622c-.258.42-.374.995-.374 1.752v1.297h3.919l-.386 2.103-.287 1.564h-3.246v8.245C19.396 23.238 24 18.179 24 12.044c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.628 3.874 10.35 9.101 11.647Z',
    x: 'M14.234 10.162 22.977 0h-2.072l-7.591 8.824L7.251 0H.258l9.168 13.343L.258 24H2.33l8.016-9.318L16.749 24h6.993zm-2.837 3.299-.929-1.329L3.076 1.56h3.182l5.965 8.532.929 1.329 7.754 11.09h-3.182z',
    whatsapp: 'M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413Z',
    telegram: 'M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z',
    pinterest: 'M12.017 0C5.396 0 .029 5.367.029 11.987c0 5.079 3.158 9.417 7.618 11.162-.105-.949-.199-2.403.041-3.439.219-.937 1.406-5.957 1.406-5.957s-.359-.72-.359-1.781c0-1.663.967-2.911 2.168-2.911 1.024 0 1.518.769 1.518 1.688 0 1.029-.653 2.567-.992 3.992-.285 1.193.6 2.165 1.775 2.165 2.128 0 3.768-2.245 3.768-5.487 0-2.861-2.063-4.869-5.008-4.869-3.41 0-5.409 2.562-5.409 5.199 0 1.033.394 2.143.889 2.741.099.12.112.225.085.345-.09.375-.293 1.199-.334 1.363-.053.225-.172.271-.401.165-1.495-.69-2.433-2.878-2.433-4.646 0-3.776 2.748-7.252 7.92-7.252 4.158 0 7.392 2.967 7.392 6.923 0 4.135-2.607 7.462-6.233 7.462-1.214 0-2.354-.629-2.758-1.379l-.749 2.848c-.269 1.045-1.004 2.352-1.498 3.146 1.123.345 2.306.535 3.55.535 6.607 0 11.985-5.365 11.985-11.987C23.97 5.39 18.592.026 11.985.026L12.017 0z',
    line: 'M19.365 9.863c.349 0 .63.285.63.631 0 .345-.281.63-.63.63H17.61v1.125h1.755c.349 0 .63.283.63.63 0 .344-.281.629-.63.629h-2.386c-.345 0-.627-.285-.627-.629V8.108c0-.345.282-.63.63-.63h2.386c.346 0 .627.285.627.63 0 .349-.281.63-.63.63H17.61v1.125h1.755zm-3.855 3.016c0 .27-.174.51-.432.596-.064.021-.133.031-.199.031-.211 0-.391-.09-.51-.25l-2.443-3.317v2.94c0 .344-.279.629-.631.629-.346 0-.626-.285-.626-.629V8.108c0-.27.173-.51.43-.595.06-.023.136-.033.194-.033.195 0 .375.104.495.254l2.462 3.33V8.108c0-.345.282-.63.63-.63.345 0 .63.285.63.63v4.771zm-5.741 0c0 .344-.282.629-.631.629-.345 0-.627-.285-.627-.629V8.108c0-.345.282-.63.63-.63.346 0 .628.285.628.63v4.771zm-2.466.629H4.917c-.345 0-.63-.285-.63-.629V8.108c0-.345.285-.63.63-.63.348 0 .63.285.63.63v4.141h1.756c.348 0 .629.283.629.63 0 .344-.282.629-.629.629M24 10.314C24 4.943 18.615.572 12 .572S0 4.943 0 10.314c0 4.811 4.27 8.842 10.035 9.608.391.082.923.258 1.058.59.12.301.079.766.038 1.08l-.164 1.02c-.045.301-.24 1.186 1.049.645 1.291-.539 6.916-4.078 9.436-6.975C23.176 14.393 24 12.458 24 10.314',
    vk: 'm9.489.004.729-.003h3.564l.73.003.914.01.433.007.418.011.403.014.388.016.374.021.36.025.345.03.333.033c1.74.196 2.933.616 3.833 1.516.9.9 1.32 2.092 1.516 3.833l.034.333.029.346.025.36.02.373.025.588.012.41.013.644.009.915.004.98-.001 3.313-.003.73-.01.914-.007.433-.011.418-.014.403-.016.388-.021.374-.025.36-.03.345-.033.333c-.196 1.74-.616 2.933-1.516 3.833-.9.9-2.092 1.32-3.833 1.516l-.333.034-.346.029-.36.025-.373.02-.588.025-.41.012-.644.013-.915.009-.98.004-3.313-.001-.73-.003-.914-.01-.433-.007-.418-.011-.403-.014-.388-.016-.374-.021-.36-.025-.345-.03-.333-.033c-1.74-.196-2.933-.616-3.833-1.516-.9-.9-1.32-2.092-1.516-3.833l-.034-.333-.029-.346-.025-.36-.02-.373-.025-.588-.012-.41-.013-.644-.009-.915-.004-.98.001-3.313.003-.73.01-.914.007-.433.011-.418.014-.403.016-.388.021-.374.025-.36.03-.345.033-.333c.196-1.74.616-2.933 1.516-3.833.9-.9 2.092-1.32 3.833-1.516l.333-.034.346-.029.36-.025.373-.02.588-.025.41-.012.644-.013.915-.009ZM6.79 7.3H4.05c.13 6.24 3.25 9.99 8.72 9.99h.31v-3.57c2.01.2 3.53 1.67 4.14 3.57h2.84c-.78-2.84-2.83-4.41-4.11-5.01 1.28-.74 3.08-2.54 3.51-4.98h-2.58c-.56 1.98-2.22 3.78-3.8 3.95V7.3H10.5v6.92c-1.6-.4-3.62-2.34-3.71-6.92Z',
    viber: 'M11.4 0C9.473.028 5.333.344 3.02 2.467 1.302 4.187.696 6.7.633 9.817.57 12.933.488 18.776 6.12 20.36h.003l-.004 2.416s-.037.977.61 1.177c.777.242 1.234-.5 1.98-1.302.407-.44.972-1.084 1.397-1.58 3.85.326 6.812-.416 7.15-.525.776-.252 5.176-.816 5.892-6.657.74-6.02-.36-9.83-2.34-11.546-.596-.55-3.006-2.3-8.375-2.323 0 0-.395-.025-1.037-.017zm.058 1.693c.545-.004.88.017.88.017 4.542.02 6.717 1.388 7.222 1.846 1.675 1.435 2.53 4.868 1.906 9.897v.002c-.604 4.878-4.174 5.184-4.832 5.395-.28.09-2.882.737-6.153.524 0 0-2.436 2.94-3.197 3.704-.12.12-.26.167-.352.144-.13-.033-.166-.188-.165-.414l.02-4.018c-4.762-1.32-4.485-6.292-4.43-8.895.054-2.604.543-4.738 1.996-6.173 1.96-1.773 5.474-2.018 7.11-2.03zm.38 2.602c-.167 0-.303.135-.304.302 0 .167.133.303.3.305 1.624.01 2.946.537 4.028 1.592 1.073 1.046 1.62 2.468 1.633 4.334.002.167.14.3.307.3.166-.002.3-.138.3-.304-.014-1.984-.618-3.596-1.816-4.764-1.19-1.16-2.692-1.753-4.447-1.765zm-3.96.695c-.19-.032-.4.005-.616.117l-.01.002c-.43.247-.816.562-1.146.932-.002.004-.006.004-.008.008-.267.323-.42.638-.46.948-.008.046-.01.093-.007.14 0 .136.022.27.065.4l.013.01c.135.48.473 1.276 1.205 2.604.42.768.903 1.5 1.446 2.186.27.344.56.673.87.984l.132.132c.31.308.64.6.984.87.686.543 1.418 1.027 2.186 1.447 1.328.733 2.126 1.07 2.604 1.206l.01.014c.13.042.265.064.402.063.046.002.092 0 .138-.008.31-.036.627-.19.948-.46.004 0 .003-.002.008-.005.37-.33.683-.72.93-1.148l.003-.01c.225-.432.15-.842-.18-1.12-.004 0-.698-.58-1.037-.83-.36-.255-.73-.492-1.113-.71-.51-.285-1.032-.106-1.248.174l-.447.564c-.23.283-.657.246-.657.246-3.12-.796-3.955-3.955-3.955-3.955s-.037-.426.248-.656l.563-.448c.277-.215.456-.737.17-1.248-.217-.383-.454-.756-.71-1.115-.25-.34-.826-1.033-.83-1.035-.137-.165-.31-.265-.502-.297zm4.49.88c-.158.002-.29.124-.3.282-.01.167.115.312.282.324 1.16.085 2.017.466 2.645 1.15.63.688.93 1.524.906 2.57-.002.168.13.306.3.31.166.003.305-.13.31-.297.025-1.175-.334-2.193-1.067-2.994-.74-.81-1.777-1.253-3.05-1.346h-.024zm.463 1.63c-.16.002-.29.127-.3.287-.008.167.12.31.288.32.523.028.875.175 1.113.422.24.245.388.62.416 1.164.01.167.15.295.318.287.167-.008.295-.15.287-.317-.03-.644-.215-1.178-.58-1.557-.367-.378-.893-.574-1.52-.607h-.018z',
    copy: 'M16 1H4a2 2 0 0 0-2 2v14h2V3h12V1Zm3 4H8a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h11a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2Zm0 16H8V7h11v14Z',
    email: 'M20 4H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2Zm0 4-8 5-8-5V6l8 5 8-5v2Z',
    native: 'M18 16.1c-.8 0-1.5.3-2 .8l-7.1-4.2c.1-.2.1-.5.1-.7s0-.5-.1-.7L16 7.2c.5.5 1.2.8 2 .8a3 3 0 1 0-3-3c0 .2 0 .5.1.7L8 9.8A3 3 0 1 0 6 15c.8 0 1.5-.3 2-.8l7.2 4.2c0 .2-.1.4-.1.6a2.9 2.9 0 1 0 2.9-2.9Z'
  };
  const svg = key => {
    const ns = 'http://www.w3.org/2000/svg';
    const el = document.createElementNS(ns, 'svg');
    el.setAttribute('viewBox', '0 0 24 24');
    el.setAttribute('width', '18');
    el.setAttribute('height', '18');
    el.setAttribute('aria-hidden', 'true');
    el.setAttribute('focusable', 'false');
    const path = document.createElementNS(ns, 'path');
    path.setAttribute('d', icons[key]);
    path.setAttribute('fill', 'currentColor');
    el.appendChild(path);
    return el;
  };
  const setIcon = (el, key, label) => {
    el.textContent = '';
    el.appendChild(svg(key));
    const text = document.createElement('span');
    text.className = 'share-text';
    text.textContent = label;
    el.appendChild(text);
    el.title = label;
  };

  const targets = [
    { id: 'facebook', label: 'Facebook', href: (u, t) => 'https://www.facebook.com/sharer/sharer.php?u=' + encodeURIComponent(u) },
    { id: 'x', label: 'X', href: (u, t) => 'https://twitter.com/intent/tweet?url=' + encodeURIComponent(u) + '&text=' + encodeURIComponent(t) },
    { id: 'whatsapp', label: 'WhatsApp', href: (u, t) => 'https://wa.me/?text=' + encodeURIComponent(t + ' ' + u) },
    { id: 'pinterest', label: 'Pinterest', href: (u, t, m) => 'https://www.pinterest.com/pin/create/button/?url=' + encodeURIComponent(u) + '&media=' + encodeURIComponent(m || '') + '&description=' + encodeURIComponent(t) },
    { id: 'telegram', label: 'Telegram', href: (u, t) => 'https://t.me/share/url?url=' + encodeURIComponent(u) + '&text=' + encodeURIComponent(t) },
    { id: 'line', label: 'LINE', href: (u, t) => 'https://social-plugins.line.me/lineit/share?url=' + encodeURIComponent(u) },
    { id: 'vk', label: 'VK', href: (u, t) => 'https://vk.com/share.php?url=' + encodeURIComponent(u) + '&title=' + encodeURIComponent(t) },
    { id: 'viber', label: 'Viber', href: (u, t) => 'viber://forward?text=' + encodeURIComponent(t + ' ' + u) },
    { id: 'email', label: 'Email', href: (u, t) => 'mailto:?subject=' + encodeURIComponent(t) + '&body=' + encodeURIComponent(t + '\n\n' + u) }
  ];

  const makeBar = ({ title, hash, image }) => {
    const bar = document.createElement('div');
    bar.className = 'share-bar';
    bar.setAttribute('role', 'group');
    bar.setAttribute('aria-label', 'Share: ' + title);
    const label = document.createElement('span');
    label.className = 'share-label';
    label.textContent = 'Share';
    bar.appendChild(label);

    if (navigator.share) {
      const native = document.createElement('button');
      native.type = 'button';
      native.className = 'btn subtle share-btn share-native';
      setIcon(native, 'native', 'Share');
      native.setAttribute('aria-label', 'Share ' + title + ' with another app');
      native.addEventListener('click', async () => {
        try {
          await navigator.share({ title, text: title, url: urlFor(hash, 'native') });
        } catch (error) {
          if (error && error.name !== 'AbortError') status.textContent = 'Sharing was not available. Use a link below.';
        }
      });
      bar.appendChild(native);
    }

    const media = image || ogImage;
    const list = targets;
    list.forEach(target => {
      const a = document.createElement('a');
      a.className = 'btn subtle share-btn share-' + target.id;
      setIcon(a, target.id, target.label);
      a.href = target.href(urlFor(hash, target.id), title, media);
      if (target.id !== 'viber' && target.id !== 'email') {
        a.target = '_blank';
        a.rel = 'noopener noreferrer';
      }
      a.setAttribute('aria-label', 'Share ' + title + ' on ' + target.label);
      bar.appendChild(a);
    });

    const copy = document.createElement('button');
    copy.type = 'button';
    copy.className = 'btn subtle share-btn share-copy';
    setIcon(copy, 'copy', 'Copy link');
    copy.setAttribute('aria-label', 'Copy link to ' + title);
    copy.addEventListener('click', async () => {
      const link = urlFor(hash, 'copy');
      try {
        await navigator.clipboard.writeText(link);
        status.textContent = 'Link copied. Paste it into Instagram or any app.';
      } catch (error) {
        window.prompt('Copy this link:', link);
      }
    });
    bar.appendChild(copy);

    const status = document.createElement('span');
    status.className = 'share-status';
    status.setAttribute('role', 'status');
    status.setAttribute('aria-live', 'polite');
    bar.appendChild(status);
    return bar;
  };

  const slug = text => clean(text).toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').slice(0, 60);

  const init = () => {
    if (mode === 'gallery') {
      document.querySelectorAll('.gallery-card').forEach((card, index) => {
        const img = card.querySelector('img');
        const link = card.querySelector('.gallery-item');
        const caption = clean(card.querySelector('figcaption')?.textContent).split(/(?<=\.)\s/)[0];
        const title = (caption || clean(img?.alt) || 'Saint Charbel gallery image').slice(0, 140);
        card.id = card.id || 'gallery-image-' + (index + 1);
        const src = link ? new URL(link.getAttribute('href'), location.href).href : ogImage;
        const imageUrl = src.startsWith(location.origin) ? 'https://marsharbel.com' + new URL(src).pathname : src;
        card.appendChild(makeBar({ title, hash: card.id, image: imageUrl }));
      });
    } else if (mode === 'news') {
      document.querySelectorAll('main article.update').forEach(card => {
        const heading = card.querySelector('h2, h3');
        const title = clean(heading?.textContent) || pageTitle;
        if (!card.id && heading) card.id = 'news-' + slug(title);
        card.appendChild(makeBar({ title, hash: card.id }));
      });
    } else {
      const h1 = document.querySelector('main h1');
      if (h1) {
        const host = h1.closest('.hero') || h1.parentElement;
        host.appendChild(makeBar({ title: pageTitle, hash: '' }));
      }
    }
    if (location.hash.length > 1) {
      let id = location.hash.slice(1);
      try { id = decodeURIComponent(id); } catch (_) { /* Ignore malformed external fragment encoding. */ }
      const target = document.getElementById(id);
      if (target) setTimeout(() => target.scrollIntoView({ block: 'start' }), 150);
    }
  };

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
