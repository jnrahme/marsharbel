# Testimony archive indexability, September 25, 2026

## What changed

The 17 pre-existing source-published accounts were only assembled client-side. The HTML showed an empty list to visitors without JavaScript. This change moves those accounts into an English catalog, generates static HTML from it, and leaves the live moderated Supabase publication feed and its report flow separate. No private submission is exported. The public publication endpoint returned an empty array at the time of this change, so no moderated reader testimony is part of the static page.

Five older first-person retellings were changed to source-attributed third-person summaries because their linked sources are interviews or secondary summaries, not verbatim submissions by those people to this site. The Thérèse Fahd source link was corrected from a 404 to the live ministry page. The archive labels explicitly distinguish these source-published summaries from reader submissions and Church-recognized healings from personal reports. The title/description no longer claim that all entries are approved by moderators.

## Why and expected impact

The source-published archive is readable without JavaScript and can be indexed from the HTML, without pretending that historical or ministry accounts are reviewed reader submissions. The baseline generator check prevents source text and HTML from silently drifting. Its catalog-backed messages keep the localization boundary. This may improve coverage of named testimonies, with no ranking guarantee.

## Checks and next

The direct source pages were checked September 25: CNEWA, Charbel App, and the Family of Saint Sharbel USA pages. Public Supabase publications: zero rows. Re-run the baseline generator after editorial changes. When genuine moderated reader submissions exist, consider a safe public-only snapshot with a publication/withdrawal freshness plan; do not bake private submissions or moderation data into HTML.
