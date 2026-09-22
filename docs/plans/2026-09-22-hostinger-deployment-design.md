# Hostinger deployment verification

Hostinger deploys `stage` independently through its existing GitHub push webhook.
The GitHub workflow previously only ran QA and printed a success message, even
when Hostinger failed because `public_html` was not a Git checkout.

Keep the existing deployment integration. After QA, fetch each root HTML, JS,
CSS and web manifest file, plus the mystery HTML pages, and compare its bytes
with the checkout. Use a fresh query parameter and bounded retries to allow
deployment and cache propagation. Fail on missing files, network errors, or
different contents. Cancel superseded workflow runs when another stage push
arrives. This verifies frontend content, not PHP execution or every media file.

Alternatives were a timestamp-only marker (can miss partial deployments) or a
new upload pipeline (unnecessary replacement of the existing Git integration).

Validate against matching local content, deliberately stale content, missing
files, and the live website. Keep the normal site QA suite before pushing.

Operational repair: preserve the current site outside `public_html`, recreate
the Git checkout using Hostinger's existing stage repository configuration,
retain server-only files, clear cache, and verify public file contents. Do not
replace this checkout with archive uploads that remove Git metadata.
