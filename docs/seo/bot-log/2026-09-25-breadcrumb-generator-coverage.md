# Generated breadcrumbs for new editorial pages, September 25, 2026

The existing SEO generator adds a breadcrumb to an explicit set of navigation pages and Rosary mysteries, but new English feature, prayer-intention, and video pages arrived without one. Content editors' manual WebPage breadcrumb entries were overwritten when generator metadata was reapplied, causing a drift between authored content and CI output.

The generator now gives an otherwise-unmapped, indexable English editorial page a Home > Page trail using its visible H1. New `saint-charbel-prayer-for-*` pages use Home > Prayer > Page, matching the prayer section and avoiding hand-maintained page lists. The existing explicit navigation labels remain unchanged. Pages with a hand-authored Article breadcrumb retain their own trail without a second generated trail; noindex and home pages do not gain a generated trail. The 26 current pages missing breadcrumbs have been regenerated. This adds structured data only; the visible content was not changed. Sitemap lastmod values for touched pages were updated to September 25.

Validation: generator idempotence, SEO unit suite, sitemap/canonical check, i18n checks, and site smoke. An Article whose authored breadcrumb still points at `/miracles` should be fixed by the content owner or a separate schema-normalization pass; this change does not rewrite authored Article blocks.
