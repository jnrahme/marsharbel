# 2026-09-24 - Mystery page titles: mystery first, brand last (technical SEO lane)

What: the 20 Rosary mystery pages had titles like
"Saint Charbel | Third Glorious Mystery - The Descent of the Holy Spirit".
Seven were 66-71 characters, so Google cut off the end, which is the mystery
name people search for. Titles now read "<mystery> | Saint Charbel". Mystery
names are unchanged. og:title, twitter:title and schema name follow from
apply_seo_tags.py.

Source fix: apply_seo_tags.py has mystery_name(), which reads either order,
so breadcrumbs and generated descriptions don't change. The i18n legacy
baseline entries were renamed to match (same wording, no new text).

Not changed: meta descriptions. All mystery descriptions are 153-158 chars.
The only one over 160 is terms-of-service (172), a legal page I left alone.
The earlier count of "5 long descriptions" was from before PR #65 aligned them.
