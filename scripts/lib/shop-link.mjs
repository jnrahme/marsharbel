// Disabled by default. This helper only changes source-composed English pages.
export function shopLinkConfig(env) {
  if (env.SHOP_LINK_ENABLED !== '1') return null;
  if (!env.SHOP_LINK_URL) throw new Error('SHOP_LINK_URL is required when SHOP_LINK_ENABLED=1');
  let url;
  try { url = new URL(env.SHOP_LINK_URL); } catch { throw new Error('SHOP_LINK_URL must be an absolute HTTPS URL'); }
  if (url.protocol !== 'https:' || url.username || url.password) throw new Error('SHOP_LINK_URL must be HTTPS without credentials');
  return { url: url.href };
}
const escape = value => String(value).replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;');
export function composeShopLink(html, config, fragment, copy) {
  if (!config) return html;
  if (!copy || typeof copy['shop.link.label'] !== 'string' || !copy['shop.link.label'].trim()) throw new Error('Missing shop.link.label copy');
  if ((html.match(/<\/footer>/g) || []).length !== 1) throw new Error('Shop link requires exactly one composed footer');
  if (html.includes('data-shop-link')) throw new Error('Shop link already present');
  const link = fragment.replace('{{url}}', escape(config.url)).replace('{{label}}', escape(copy['shop.link.label']));
  if (/\{\{/.test(link)) throw new Error('Unfilled shop-link fragment slot');
  return html.replace('</footer>', link + '\n</footer>');
}
