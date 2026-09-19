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
