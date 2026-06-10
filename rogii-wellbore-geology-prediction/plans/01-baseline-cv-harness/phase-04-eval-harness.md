# Phase 04 — Eval harness

## Context links
- Parent: [`plan.md`](plan.md) · Grounding: [`reports/01-data-grounding.md`](reports/01-data-grounding.md)
- Dependencies: Phases 01 (folds), 02 (loader), 03 (baselines) · Downstream: Phase 05 (notebook renders this)

## Overview
- Date: 2026-06-09 · Priority: P1 · Impl status: done · Review status: pending
- Score any baseline fn on the frozen folds: predict each held-out well's post-PS tail, pool all rows, one RMSE.
  Mirrors the LB's global pooling exactly.

## Key Insights
- **Pooled** RMSE (concat all post-PS rows, then RMSE) is the LB-matching headline; long wells weigh more — correct.
- **Per-well** RMSE distribution is the diagnostic — catches a model that's good on average but detonates on a few
  wells (the failure mode geometry baselines may hide).
- Truth comes from `true_tvt` (train-only channel), never from anything a model saw.

## Requirements
- `src/eval.py`:
  - `score_baseline(fn, folds, data_root) -> {pooled_rmse: float, per_well: DataFrame[well_id, fold, rmse, n_rows]}`.
  - For each well: `split_ps` → `pred = fn(known, predict)` → align to `true_tvt[ps_idx:]` → accumulate.
  - `rmse(pred, true)` helper.
  - Optional `compare(fns: dict) -> DataFrame` building the B1/B2/B3 comparison table.

## Architecture
- Iterate folds only for grouping/reporting; pooled RMSE computed over the concatenation of every held-out post-PS
  `(pred, true)` pair across all folds (== over all 773 wells, since every well is held out exactly once).
- Accumulate sum-of-squared-error + row count for pooled (memory-light), plus per-well rmse list.
- Log: total scored rows (gate vs official count on test), NaN-Z fallback counts surfaced from baselines.

## Related code files
- CREATE `src/eval.py`

## Implementation Steps
1. `rmse`, `score_baseline` (SSE accumulation + per-well list).
2. `compare` over `{B1,B2,B3}`.
3. Run; assert pooled RMSE finite; print comparison table + per-well summary stats.

## Todo list
- [ ] `src/eval.py` (rmse, score_baseline, compare)
- [ ] B1 pooled RMSE check (global gate)
- [ ] per-well distribution computed + summarized

## Success Criteria
- **B1 pooled RMSE ≈ 15–16** (global gate; else PS/index bug → stop).
- B2 < B1 and B3 ≤ B2 (investigate if not — do not assume).
- Per-well df has 773 rows, no NaN rmse.
- Total scored rows = sum of post-PS rows over all train wells (sane, deterministic).

## Risk Assessment
- **Pooled vs per-well metric mismatch with LB** → pooled is headline (matches LB), per-well diagnostic only.
- **Misalignment of pred↔true** (off-by-one at PS) → align both from `ps_idx`; covered by B1 gate.
- Silent NaN in pred → assert finite before RMSE.

## Security Considerations
- Truth (`TVT`) enters only here, via the dedicated `true_tvt` channel, strictly for scoring — never passed back to a
  model. Keeps the train-only target out of the prediction path.

## Next steps
→ Phase 05 renders results + per-well chart in the run notebook.
