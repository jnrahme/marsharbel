// JSON-LD serializers. Each reproduces the exact bytes the pages carried when the
// block was pasted by hand, so extraction cannot change served output. String
// values are passed through verbatim (already JSON-escaped in the source).
const SITE_NAMES = ['Mar Charbel', 'Saint Charbel Makhlouf', 'Sharbel', 'St Charbel', 'Saint Sharbel', 'Charbel Makhlouf'];

// args: name, description, url, then pairs of (crumb name, crumb url).
export function renderWebPage([name, description, url, ...crumbs]) {
  if (crumbs.length === 0 || crumbs.length % 2) throw new Error('ld-webpage needs breadcrumb name/url pairs');
  const items = [];
  for (let i = 0; i < crumbs.length; i += 2) {
    items.push(`      {
        "@type": "ListItem",
        "position": ${i / 2 + 1},
        "name": "${crumbs[i]}",
        "item": "${crumbs[i + 1]}"
      }`);
  }
  return `<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "WebPage",
  "name": "${name}",
  "description": "${description}",
  "url": "${url}",
  "isPartOf": {
    "@type": "WebSite",
    "name": "Saint Charbel",
    "alternateName": [
${SITE_NAMES.map(n => `      "${n}"`).join(',\n')}
    ],
    "url": "https://marsharbel.com/",
    "publisher": {
      "@type": "Organization",
      "name": "marsharbel.com",
      "url": "https://marsharbel.com/"
    }
  },
  "breadcrumb": {
    "@type": "BreadcrumbList",
    "itemListElement": [
${items.join(',\n')}
    ]
  }
}
  </script>`;
}

// args: pairs of (question, answer). FAQPage block.
export function renderFaq(pairs) {
  if (pairs.length === 0 || pairs.length % 2) throw new Error('ld-faq needs question/answer pairs');
  const items = [];
  for (let i = 0; i < pairs.length; i += 2) {
    items.push(`    {
      "@type": "Question",
      "name": "${pairs[i]}",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "${pairs[i + 1]}"
      }
    }`);
  }
  return `<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
${items.join(',\n')}
  ]
}
  </script>`;
}
