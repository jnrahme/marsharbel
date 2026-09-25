# Checklist ARIA and stacking checks, September 25, 2026

A CI run during the R3 merge briefly reported failures in the unrelated rosary/story ARIA and sticky-controls stacking checks. The checklist browser suite reused a single page across many routes and read computed styles after `DOMContentLoaded` plus a fixed 300 ms sleep. That event does not promise the stylesheet has loaded, while a sleep does not establish page readiness on a busy CI worker.

The focused checks now wait for each route's load event, assert a successful response, wait for the target control, and check that the page stylesheet exists before inspecting ARIA references or computed z-index. ARIA validation now checks every ID in both `aria-labelledby` and `aria-describedby` whitespace-separated lists, rather than only the first attribute's entire value. It still rejects missing references and z-index below 80. Other interactive checklist tests remain unchanged.

The full checklist suite passed on the current stage base. A separate delayed-stylesheet browser probe confirmed both controls reach z-index 90 after stylesheet load. This does not prove the prior CI failure's exact cause because its debug artifact was not available, but it removes one plausible timing failure and strengthens the assertion.
