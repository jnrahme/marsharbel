/*
 * Shopify Storefront Web Components integration boundary.
 * Keep the QA page in its honest empty state until the store domain and
 * Storefront access token are supplied by the store owner.
 */
(() => {
  const config = window.MARSHARBEL_SHOPIFY || {};
  const host = document.getElementById('shopify-storefront');
  const empty = document.getElementById('souvenir-empty');

  if (!host || !empty || !config.storeDomain || !config.publicAccessToken) return;

  const script = document.createElement('script');
  script.type = 'module';
  script.src = 'https://cdn.shopify.com/storefront/web-components.js';
  script.onload = () => {
    const store = document.createElement('shopify-store');
    store.setAttribute('store-domain', config.storeDomain);
    store.setAttribute('public-access-token', config.publicAccessToken);
    store.innerHTML = `
      <shopify-context type="collection" handle="${config.collectionHandle || 'souvenirs'}">
        <template>
          <div class="souvenir-product-grid">
            <shopify-list-context type="product" query="products(first: 24)">
              <template>
                <shopify-product-card></shopify-product-card>
              </template>
            </shopify-list-context>
          </div>
        </template>
      </shopify-context>
      <shopify-cart></shopify-cart>`;
    host.replaceChildren(store);
    host.hidden = false;
    empty.hidden = true;
  };
  script.onerror = () => {
    host.hidden = true;
    empty.hidden = false;
  };
  document.head.appendChild(script);
})();

/*
 * Catalog preview. Renders store/catalog.json as a gallery. While the
 * catalog status is "preview" or checkout is disabled, cards never expose a
 * buy path: no prices, no links out, no cart.
 */
(() => {
  const grid = document.getElementById('souvenir-catalog');
  if (!grid) return;
  const el = (tag, cls, text) => {
    const node = document.createElement(tag);
    if (cls) node.className = cls;
    if (text) node.textContent = text;
    return node;
  };
  fetch('/store/catalog.json', { credentials: 'omit' })
    .then(res => (res.ok ? res.json() : Promise.reject(new Error('catalog'))))
    .then(catalog => {
      const live = catalog.status === 'live' && catalog.checkout && catalog.checkout.enabled;
      const cards = catalog.products.map(product => {
        const card = el('article', 'souvenir-card');
        const frame = el('div', 'souvenir-card-frame');
        const img = document.createElement('img');
        img.src = product.art;
        img.alt = product.alt;
        img.loading = 'eager';
        img.decoding = 'async';
        frame.append(img);
        const body = el('div', 'souvenir-card-body');
        body.append(el('span', 'kicker', product.kind));
        body.append(el('h3', '', product.title));
        body.append(el('p', '', product.blurb));
        const foot = el('div', 'souvenir-card-foot');
        if (live && product.checkoutUrl && product.priceCents != null) {
          const buy = el('a', '', catalog.labels.order);
          buy.classList.add('btn', 'primary');
          buy.href = product.checkoutUrl;
          buy.rel = 'noopener';
          foot.append(el('span', 'souvenir-price', '$' + (product.priceCents / 100).toFixed(2)), buy);
        } else {
          foot.append(el('span', 'souvenir-pill', catalog.labels.preview));
        }
        body.append(foot);
        card.append(frame, body);
        return card;
      });
      grid.replaceChildren(...cards);
      grid.hidden = false;
    })
    .catch(() => { grid.hidden = true; });

  const fine = window.matchMedia(['(hover:hover)', '(pointer:fine)'].join(' and ')).matches;
  const calm = window.matchMedia('(prefers-reduced-motion:' + 'reduce)').matches;
  if (fine && !calm) {
    grid.addEventListener('pointermove', event => {
      const card = event.target.closest('.souvenir-card');
      if (!card) return;
      const r = card.getBoundingClientRect();
      const x = (event.clientX - r.left) / r.width - 0.5;
      const y = (event.clientY - r.top) / r.height - 0.5;
      card.style.setProperty('--tilt-x', (y * -6).toFixed(2) + 'deg');
      card.style.setProperty('--tilt-y', (x * 8).toFixed(2) + 'deg');
    });
    grid.addEventListener('pointerout', event => {
      const card = event.target.closest('.souvenir-card');
      if (card) { card.style.removeProperty('--tilt-x'); card.style.removeProperty('--tilt-y'); }
    });
  }
})();
