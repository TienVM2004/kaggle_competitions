# Phase 03 — Baseline functions (B1/B2/B3)

## Context links
- Parent: [`plan.md`](plan.md) · Grounding: [`reports/01-data-grounding.md`](reports/01-data-grounding.md)
- Dependencies: Phase 02 (`split_ps` contract) · Downstream: Phase 04 (eval), future submission notebook

## Overview
- Date: 2026-06-09 · Priority: P1 · Impl status: done · Review status: pending
- Three per-well geometry predictors, identical signature so the harness loops them uniformly. Inputs only:
  `TVT_input, Z, MD` (all test-present). Each isolates one component of the spine.

## Key Insights
- `D = TVT + Z` (Z negative). `−Z` is free → baselines model only the residual `D`.
- B1→B2→B3 is a strict ladder: each adds exactly one geometric term, so the RMSE drops attribute cleanly to that term.
- Fit D against **MD** (actual), not row index — MD spacing is ~1 ft but not exact.

## Requirements
- `src/baselines.py`, each `fn(known_df, predict_df) -> np.ndarray` (length = len(predict_df), original order):
  - **B1** `carry_forward`: `pred = TVT_input[last_known]` (constant).
  - **B2** `z_anchor`: `D0 = TVT_input[last] + Z[last]`; `pred_i = D0 − Z_i`.
  - **B3** `z_anchor_dip`: lstsq fit `D = a + b·MD` over whole known interval (`D_known = TVT_input + Z`);
    `pred_i = (a + b·MD_i) − Z_i`.
- Fallback ladder: `len(known) < 2` → B3 falls back to B2; `< 1` → B1. Per-row post-PS `Z` NaN → carry-forward that
  row + increment a logged counter.

## Architecture
- Pure numpy; no global/cross-well state (per-well only — keeps spatial-CV question moot for now).
- Shared helper `_known_D(known_df)`; shared `_fallback` wrapper applying the degenerate ladder + NaN-Z patch.
- B3 fit via `np.polyfit(MD, D, 1)` (or `lstsq`); guard near-singular (constant MD) → b=0 ⇒ reduces to B2.

## Related code files
- CREATE `src/baselines.py`

## Implementation Steps
1. `_known_D`, `_fallback` helpers.
2. B1, B2, B3 per math above; wire fallback ladder + NaN-Z handling.
3. Unit-check on `000d7d20`: hand-compute B2 at PS+1 (`D0 − Z[1443]`) and match.

## Todo list
- [ ] `src/baselines.py` (b1/b2/b3 + helpers + fallbacks)
- [ ] hand-computed spot check matches B2
- [ ] assert fns run on test-shaped df (no `TVT`)

## Success Criteria
- All three accept a test-shaped `predict_df` (no `TVT`) and return finite arrays of correct length/order.
- Hand-computed B2 at one row matches harness to ~1e-6.
- Degenerate well (tiny known) returns via fallback, no exception.

## Risk Assessment
- **Reads `TVT` by mistake** → impossible: `predict_df` lacks it (Phase 02 firewall); B-fns only touch `TVT_input,Z,MD`.
- **Fit vs row-index** → fit vs MD explicitly.
- **Sign error on Z** → covered by the hand spot-check landing in the right ballpark + B1≈15.9 global gate.
- Non-monotonic/constant MD → lstsq robust; singular-guard → B2.

## Security Considerations
- Same leakage firewall as Phase 02: baselines structurally cannot see target/leak columns. No external I/O.

## Next steps
→ Phase 04 scores these on the frozen folds.
