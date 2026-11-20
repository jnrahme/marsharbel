# Fixed SEO continuation foundation

This is a delta verifier, not approval, and not an enabled pin exception.

The November 19 requests require FAQ JSON-LD removal and consolidation of the
English prayer URL. Some affected files have historical C2 pins. Those historical
records and the B-to-C2 proof must remain intact.

## What this change does

- Adds three fixed operations: internal prayer anchor href replacement,
  winner-only robots metadata, standalone FAQPage JSON-LD removal.
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
- Adds 23 positive and negative controls to the existing citation CI command,
  without adding or displacing a shard-inventory slot.

No receipt is added. No page, generator, historical record, historical artifact,
existing pin or original guard is changed. No active call site invokes this
module outside the tests. This PR alone cannot make the FAQ or prayers patch
pass a pin guard.

## Owning-guard integration required before use

A dependent content PR must wire the operation into each owning guard, then
receive independent review of the resulting exact head. `pinned_preimage` returns
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
reviewed. Article and BreadcrumbList additions are outside this operation and
must be evaluated separately where a pinned file needs them.

Prayer href replacement changes only real quoted `a[href]` values resolving to
the three retired aliases on marsharbel.com. Text, comments, scripts, raw-text
containers, non-anchor attributes, other hosts and prefix lookalikes stay intact.
Query and fragment values are preserved. It does not change the other English
mirror pairs. Robots edits are limited to saint-charbel-prayers.html and the exact
approved value. Redirects, sitemaps and llms.txt remain owning content work.

## Verification

- Direct invocation: `python3 scripts/qa/test_seo_continuations.py`, 23 tests.
- Module invocation: `python3 -m unittest scripts.qa.test_seo_continuations`,
  the same 23 tests.
- CI wrapper: `python3 scripts/qa/check_citation_amendment.py`, calls these
  controls inside its existing slot, after the original controls.

Independent review is required before release. No owner approval is inferred
from a receipt, a passing test, a path name or this document.
