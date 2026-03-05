# QA and Bug-Fix Loop

This repository uses a hybrid loop:

1. Deterministic QA (required): `npm run qa`
2. Exploratory agentic QA (optional): `npm run qa:agentic:smoke`

## Deterministic Gate

Run before every push:

```bash
npm run qa
```

This runs:
- `test:site-smoke`: high-value page navigation/runtime checks
- `test:rosary-all`: existing rosary regression tests

CI runs the same gate using `.github/workflows/qa.yml`.

## Bug-Fix Protocol

When a bug is found:

1. Reproduce it locally with the smallest reliable steps.
2. Add or extend a failing test first (site smoke or rosary suite).
3. Fix the code.
4. Re-run `npm run qa` until green.
5. Push and confirm GitHub Actions QA passes.

## Optional Agentic Pass

Use this for fast exploratory UI checks:

```bash
npm run qa:agentic:smoke
```

This captures browser evidence in `output/playwright/`.

Agentic runs are useful for discovery, but merge decisions should rely on deterministic `npm run qa` results.
