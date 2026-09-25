# 2026-09-24 - Article schema and share images for feature pages (technical SEO lane)

Pages with a featured hero image (`<figure class="hero-figure"><img>`),
currently the Saint Charbel Trail, the Saint Charbel Movie, and Pope Leo XIV at
the tomb, used the generic site image for og:image/twitter:image and had
only WebPage schema.

apply_seo_tags.py now, for any page with a hero figure:
- sets og:image and twitter:image to the hero image and og:type to article;
- adds WebPage.mainEntity = Article (headline from the h1, the hero image,
  author and publisher marsharbel.com, datePublished = the date the file
  was first added to the repo).

Decisions: no dateModified, because embedding a git date in the page would
change the page and make the date stale in a loop (the sitemap lastmod
already carries freshness). No NewsArticle: these are evergreen feature
pages, and the dates inside them are event dates, not publication dates.
Author is the site organization because pages have no bylines; inventing
a person would be wrong. New feature pages pick this up automatically.
