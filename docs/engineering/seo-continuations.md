# Fixed SEO continuation foundation

This is a delta verifier, not approval, and not an enabled pin exception.

The November 19 requests require FAQ JSON-LD removal and consolidation of the
English prayer URL. Some affected files have historical C2 pins. Those historical
records and the B-to-C2 proof must remain intact.

## What this change does

- Adds four fixed operations: internal prayer anchor href replacement,
  winner-only robots metadata, standalone FAQPage JSON-LD removal and minimal Article addition from existing metadata.
- Restricts receipts to a literal set of 37 HTML inputs already covered by the
  citation table or its derived master inputs. Unknown paths and arbitrary
  replacement instructions are rejected.
- A receipt contains exact before/after SHA-256 values and a fixed operation list.
  The expected after bytes are recomputed, not trusted from the receipt.
- Every receipt preimage must equal the actual historical C2 blob. Naming a newer
  ancestor cannot absorb an unrelated edit. The base must be an ancestor of HEAD.
- Binds receipt, module and affected content to native HEAD and current disk.
  Missing objects, symlinks, dirty inputs and editable exports fail closed.
- Does not cache a proof. No stale-memo acceptance exists in this foundation.
- Adds 35 positive and negative controls to the existing citation CI command,
  without adding or displacing a shard-inventory slot.

The foundation PR stays inactive. This dependent integration wires the owning guards but adds no receipt or content changes. Original records, artifacts and pins remain unchanged. No FAQ or prayers page change is claimed by this integration alone.

## Owning-guard integration required before use

This integration wires the operation into the owning guards and requires independent exact-head review. A dependent content PR still must add finite receipts, regenerate, prove and review its resulting exact head. `pinned_preimage` returns
only a proven preimage. The caller must compare that preimage to its ORIGINAL
historical pin, not treat successful delta verification as sufficient.

Integration must cover:

1. Original B-to-C2 historical proof and unchanged historical records/bundle.
2. N1: historical finite graph identity retained, current differences accepted
   only through the fixed receipt and original C2 preimage check.
3. Effective body hashes and candidate bytes, with a separate continuation
   record so historical citation evidence is never relabeled as a new review.
4. Keyed/exact master and frozen prayer-main formulas, checked against preimages.
5. All proof inputs in HEAD/worktree and memo keys, including receipt/module.
6. Exports: no continuation can self-certify in an editable export. Fail closed
   or emit explicitly unverified build data without reviewed/approved claims.
7. Deterministic source and locale generation. The same fixed transformation
   must be applied at the owning generation stage, not by hand-editing output.
8. Native controls for combined FAQ + prayer operations and each owning guard,
   including tampered prose, changed links outside the approved aliases,
   catalog drift, removed receipt and warm-memo tampering.

The preimage must stay at C2 for cumulative operations. A later content PR adds
its fixed class to the same row and reconstructs the combined candidate from
that unchanged preimage. It must not replace the baseline with the first patch.

## Narrow limits

FAQ removal only supports complete standalone FAQPage script blocks. A mixed
JSON-LD graph is rejected, never dropped or reserialized. If a pinned mixed graph
exists, a new exact fixed graph transform must be designed and independently
reviewed. The separate article-add operation creates a minimal Article from the existing canonical, og:title, description, language and optional og:image. It invents no dates or author and leaves an existing Article unchanged. All pinned FAQ inputs already have BreadcrumbList, so no pinned breadcrumb addition is needed. The content patch still must add breadcrumbs to the one unpinned page lacking them through its owning serializer.

Prayer href replacement changes only real quoted `a[href]` values resolving to
the three retired aliases on marsharbel.com. Text, comments, scripts, raw-text
containers, non-anchor attributes, other hosts and prefix lookalikes stay intact.
Query and fragment values are preserved. It does not change the other English
mirror pairs. Robots edits are limited to saint-charbel-prayers.html and the exact
approved value. Redirects, sitemaps and llms.txt remain owning content work.

## Verification

- Direct invocation: `python3 scripts/qa/test_seo_continuations.py`, 35 tests.
- Module invocation: `python3 -m unittest scripts.qa.test_seo_continuations`,
  the same 35 tests.
- CI wrapper: `python3 scripts/qa/check_citation_amendment.py`, calls these
  controls inside its existing slot, after the original controls.

Independent review is required before release. No owner approval is inferred
from a receipt, a passing test, a path name or this document.


## Integration proof and limits

The integration extends the current native proof with a separate C2-to-current
leg. It leaves the original B-to-C2 ancestry, reconstruction, derived-pin,
evidence-record and isolated historical-chain checks in place. Every current
finite file must equal C2 or pass the fixed receipt with the exact C2 preimage.
The receipt bytes, module, expanded inputs and owning renderer files enter the
memo/W0 closure. Removing a receipt cannot preserve a warm cached pass.

Effective main-body and candidate APIs use continued current bytes only after
that proof. The citation addendum keeps its original C2 fields and adds a
separate technical continuation sibling. It does not invent a new native,
editorial or rendered review.

Keyed/exact renderers compare preimages against original master pins and render
those original master bytes. Fixed operations are reapplied after localized
metadata composition and before final manifest/body checks. Thus an English
Article headline is not copied into localized output. Frozen prayer-main checks
compare the original preimage formula and require generated current main bytes
to equal the continued disk main.

The 31-test suite includes native current-leg fixtures. Those fixtures replace
only the expensive isolated historical command with an explicit unit fixture.
They are not historical qualification. The original citation wrapper still runs
the real historical chain separately and must pass on the exact candidate in
native CI. No full-wrapper success is inferred from these unit fixtures.

No receipt is active yet. The dependent FAQ/prayers changes still need complete
source generation, output parity, URL behavior, live verification and independent
exact-head review. Any missing owning path remains a blocker, never a reason to
refresh or disable a pin.


Accuracy review correction: file content hashes alone cannot establish path
identity. Every citation proof call now checks regular-file and parent-directory
identity before its memo lookup, including unchanged-byte content, receipt and
module symlink swaps. Controls cover these swaps after a warm pass and symlinked
ar, locales and scripts/i18n directories. Additional controls combine all four
real effects in a synthetic winner and exercise the frozen-prayer composer with
a continued en/prayers body, including rejection of generated body drift.
