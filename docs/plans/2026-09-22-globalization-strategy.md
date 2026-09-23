# Marsharbel international search strategy

Date: 22 September 2026
Status: Proposed roadmap; no new deployment authorized by this document.

## Objective
Help people worldwide discover useful Saint Charbel resources in their preferred language. Measure growth in relevant search impressions, organic visits, and use of prayer resources by country and language. Neither indexing nor rankings or traffic can be guaranteed. A performance score of 100 is not a promise of search visibility.

## Starting point
The deployed site has 44 public sitemap URLs, including Arabic (/ar) and French (/fr) introductions. These are introductory pages, not full translations of the resource library. Runtime translation is available for other content but is not a substitute for dedicated indexable translations. The latest observed Hostinger mobile score was 98; local Lighthouse reached 100.

Google Search Console is verified. Its previously observed sitemap result showed 42 discovered URLs before the two language pages were added; discovery and indexing of those new pages still need confirmation. Bing verification and analytics configuration have not been confirmed.

Historical Google baseline, 21 June–20 September 2026: 38 clicks, 1.36k impressions, 2.8% CTR, average position 11. This is an overall baseline, not a country-specific forecast. Hosting country request counts are not equivalent to human organic visitors and can include crawlers.

## Priority audiences
These are initial hypotheses based on the subject and existing content, not measured keyword demand. Validate with country/query data and available qualified translation reviewers before expanding.

| Wave | Language | Example audiences |
| --- | --- | --- |
| 1 | English | United States, Canada, United Kingdom, Australia, Philippines, and English readers elsewhere |
| 1 | Arabic | Lebanon and Arabic-speaking readers worldwide |
| 1 | French | France, French-speaking Canada, Belgium, Switzerland, and Francophone readers elsewhere |
| 2 | Spanish | Mexico, Spain, Colombia, Argentina, Chile, and Spanish readers worldwide |
| 2 | Portuguese | Brazil and Portugal |
| 3 | Italian, German, Polish, other languages | Prioritize using search demand, engagement, and reviewer availability |

One language version can serve several countries. Create country-specific versions only when the information or language usage materially differs. China, South Korea, and other markets with distinct search ecosystems need a separate feasibility assessment, native-language resources, and checks of local search-engine requirements before promising coverage.

## Recommended architecture
Keep marsharbel.com as the common domain and preserve existing English URLs and /ar and /fr landing URLs. Use language directories for future translated resources, for example /fr/prieres and /ar/prayers; final localized slugs require editorial review and routing tests before implementation.

Each translated resource should contain its complete main content in the initial HTML, with translated navigation, title, description, image descriptions, and correct language/direction attributes. Provide self-referencing canonicals and reciprocal hreflang only among equivalent published pages. Keep a visible language switcher linking equivalent resources, with a clearly labeled fallback when a translation is unavailable. Do not redirect automatically by visitor IP or inferred language. Do not canonicalize translations to English.

Update sitemap entries when pages are published. Keep temporary, incomplete, private, and search/filter utility pages out of the index as appropriate. Do not create near-identical pages for every country or publish unreviewed bulk translations.

## First 90 days

### Weeks 1–2: measurement and editorial preparation
- Export Search Console country, query, and page data for a consistent baseline; separate branded and non-branded searches using reviewed name variants.
- Check Google's discovery and indexing of /ar and /fr and the current sitemap. Investigate actual indexing issues rather than assuming all excluded URLs are errors.
- Verify Bing Webmaster Tools access, submit the sitemap, and evaluate IndexNow for published URL changes. Submission is a discovery signal, not guaranteed inclusion.
- Create a page inventory mapping topic, source, language, URL, reviewer, review date, and publication status.
- Validate search wording for Saint Charbel biography, prayers, novena, rosary, Annaya, and feast day in each priority language. Do not invent search-volume estimates.
- Identify qualified Arabic and French reviewers for language and religious accuracy.

### Weeks 3–6: complete the first language collections
Create or improve five core resources in each of Arabic and French: biography, prayers, novena, rosary guide, and Annaya/feast-day information. This is a proposed ten-page first batch, subject to content inventory and review capacity.

Use reliable sources, distinguish reported testimonies from verified facts, and label the site's independent status accurately. Confirm permission to reproduce any modern copyrighted prayer translation. Keep audio language and availability clear. Publish only pages whose main content and navigation have been reviewed.

Strengthen related-topic links and provide genuinely useful answers, including prayer instructions and readable mobile layouts. Validate Arabic right-to-left display, mixed numerals, navigation, and keyboard access.

### Weeks 7–12: evaluate and expand
Review indexing, impressions, clicks, and reader engagement. Begin Spanish and Portuguese collections when evidence and review capacity support them; otherwise deepen existing languages. Prepare relevant resources that parishes, Maronite communities, and Catholic publishers may choose to share. External outreach requires separate authorization before sending messages. Avoid purchased links and unsupported affiliation claims.

Assess overseas loading behavior from representative regions and real-user field data when available. Change CDN or caching settings only when measurements justify the change; a single local Lighthouse run does not establish worldwide speed.

## Acceptance criteria for every release
- Each intended indexable page returns 200, has complete localized HTML, accurate metadata, a self-canonical, valid reciprocal language links, and a sitemap entry.
- Links and language switching work with JavaScript disabled where applicable; translations do not depend on browser storage to be discovered.
- Native-language and factual review completed; source and review ownership recorded.
- Mobile navigation, Arabic RTL, text overflow, keyboard interaction, and prayer flows pass checks at representative sizes.
- Performance measured repeatedly under consistent mobile conditions; no unexplained regression from the prior release. Track field Core Web Vitals when sufficient data exists.
- Joey tests the batch locally before any new push to stage. Stage currently publishes the public website, so it is a production-impacting action.
- After authorized deployment, verify the actual published files and live routes, then check indexing over time. Search-engine inclusion is outside deployment verification.

## Measurement and decision rules
Compare consecutive 28-day windows and retain a 90-day view. Track impressions, clicks, CTR, queries, and landing pages by country and language. Treat average position as contextual because query mix changes. Report how many countries generate relevant impressions and clicks, alongside absolute counts so isolated events do not look like established traction.

Where suitable analytics and consent are configured, measure organic visits, engaged reading, and prayer starts using aggregate events. Do not collect prayer text or sensitive testimony details in analytics. Hosting request totals alone cannot establish this.

The first milestone is a reviewed, technically sound Arabic/French collection and confirmed search-engine discovery. Set numeric traffic targets after the country baseline is available. If impressions grow but clicks do not, review search intent and titles. If indexed pages receive no relevant impressions, improve topic fit and internal discovery before adding more languages. If indexing fails, investigate technical and content causes first.

## Sources
- Google multilingual and multi-regional guidance: https://developers.google.com/search/docs/specialty/international/managing-multi-regional-sites
- Google Search Console performance reporting: https://support.google.com/webmasters/answer/7576553?hl=en
- Bing Webmaster Guidelines: https://www.bing.com/webmasters/help/webmaster-guidelines-30fba23a

## Immediate next implementation batch
Prepare the Arabic/French page inventory, establish country-level measurement, and draft the first complete translated resources for local review. This plan does not authorize new publication, external outreach, or paid services.

## Implementation update — 22 September 2026

The first ten Arabic/French guides are now implemented locally with SEO and responsive checks. Per Joey’s subsequent instruction, the assistant performs source-based editorial review; external reviewers are not a publication requirement. The separate local-review-before-push rule remains. See docs/seo/international-publishing.md for current status, measured checks, and search-engine setup steps. Spanish/Portuguese expansion and longitudinal measurement remain later work.

## Eight-language implementation update — 22 September 2026

Joey subsequently authorized all eight proposed languages immediately: English, Arabic, French, Spanish, Portuguese, Italian, German and Polish. Earlier phased language priorities are superseded by this instruction. The implementation now contains five equivalent reading guides per language, seven localized homepages, a shared template, keyed catalogs, a central route registry and mandatory localization checks. See `locales/README.md` and `AGENTS.md`. This does not claim full translation of legacy interactive experiences; their affected strings must migrate when changed. External reviewers are not a release gate under Joey's instruction; researched wording and assistant judgment are used. Local review and explicit approval remain required before pushing this batch to stage.
