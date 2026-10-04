// JSON-LD serializers. Each reproduces the exact bytes the pages carried when the
// block was pasted by hand, so extraction cannot change served output. String
// values are passed through verbatim (already JSON-escaped in the source).
const SITE_NAMES = ['Mar Charbel', 'Saint Charbel Makhlouf', 'Sharbel', 'St Charbel', 'Saint Sharbel', 'Charbel Makhlouf'];

// args: name, description, url, then pairs of (crumb name, crumb url).
export function renderWebPage([name, description, url, ...crumbs], article = null, beforeBreadcrumb = null) {
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
${beforeBreadcrumb === null ? '' : beforeBreadcrumb}  "breadcrumb": {
    "@type": "BreadcrumbList",
    "itemListElement": [
${items.join(',\n')}
    ]
  }${article === null ? '' : `,
  "mainEntity": ${article}`}
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

// args: article headline, image URL, publication date, then renderWebPage args.
export function renderWebPageArticle([headline, image, datePublished, ...page], dateModified = null) {
  if (typeof headline !== 'string' || typeof image !== 'string' || typeof datePublished !== 'string' || page.length < 5) {
    throw new Error('ld-webpage-article needs headline, image, date and webpage arguments');
  }
  return renderWebPage(page, `{
    "@type": "Article",
    "headline": "${headline}",
    "image": [
      "${image}"
    ],
    "author": {
      "@type": "Organization",
      "name": "marsharbel.com",
      "url": "https://marsharbel.com/"
    },
    "publisher": {
      "@type": "Organization",
      "name": "marsharbel.com",
      "url": "https://marsharbel.com/"
    },
    "datePublished": "${datePublished}"
  }`, dateModified === null ? null : `  "dateModified": "${dateModified}",\n`);
}

// args: language, audience label, min/max age, then renderWebPage args.
// Values remain JSON-escaped strings; ages are validated before numeric emission.
export function renderWebPageAudience([language, audienceType, minAge, maxAge, ...page]) {
  if (typeof language !== 'string' || typeof audienceType !== 'string' || page.length < 5) {
    throw new Error('ld-webpage-audience needs language, audience, ages and webpage arguments');
  }
  if (!/^(0|[1-9]\d*)$/.test(minAge) || !/^(0|[1-9]\d*)$/.test(maxAge) || Number(minAge) > Number(maxAge)) {
    throw new Error('ld-webpage-audience needs ordered non-negative integer ages');
  }
  return renderWebPage(page, null, `  "inLanguage": "${language}",
  "isAccessibleForFree": true,
  "audience": {
    "@type": "PeopleAudience",
    "audienceType": "${audienceType}",
    "suggestedMinAge": ${minAge},
    "suggestedMaxAge": ${maxAge}
  },
`);
}
