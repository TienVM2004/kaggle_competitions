# Phase 02 — Well loader + PS contract

## Context links
- Parent: [`plan.md`](plan.md) · Grounding: [`reports/01-data-grounding.md`](reports/01-data-grounding.md)
- Dependencies: none · Downstream: Phases 03, 04 (every model + eval share this contract)

## Overview
- Date: 2026-06-09 · Priority: P1 · Impl status: done · Review status: pending
- One module owning how a well is loaded and split at PS. The single definition of "known vs predict" so no model
  re-implements (and re-bugs) it. The **test-portability firewall** lives here.

## Key Insights
- **`TVT` and the 6 leak columns are train-only.** Loader must hand models a `predict_df` that *physically lacks*
  `TVT` and leak cols → a baseline cannot accidentally read the target. `TVT` is returned on a separate channel used
  only by the eval harness (train scoring), never by models.
- PS = first NaN `TVT_input`; verified contiguous tail. Known = rows before PS; predict = PS→end.
- `id` row index = 0-based position in the file → models/eval must preserve original row order for id alignment.

## Requirements
- `src/well_io.py`:
  - `load_lateral(path) -> DataFrame` (preserve row order; parse blanks as NaN).
  - `split_ps(df) -> (known_df, predict_df, ps_idx)` where `predict_df` excludes `TVT` + leak cols; `known_df` keeps
    `TVT_input` (== TVT pre-PS).
  - `true_tvt(df) -> Series` — train-only target accessor for the harness (raises if `TVT` absent).
  - `well_id_from_path(path) -> str` (8-char).
  - constants: `LEAK_COLS = [ANCC,ASTNU,ASTNL,EGFDU,EGFDL,BUDA]`, `TARGET='TVT'`.

## Architecture
- `predict_df` columns restricted to the test-present set `{MD,X,Y,Z,GR,TVT_input}` → identical shape for train and
  test wells, guaranteeing a baseline that runs in CV also runs in the hidden test.
- `ps_idx` returned for id construction + scored-row counting.
- Degenerate handling deferred to baselines, but loader exposes `len(known_df)` cleanly.

## Related code files
- CREATE `src/well_io.py`

## Implementation Steps
1. `load_lateral`: `pd.read_csv`, keep order, ensure numeric coercion leaves blanks as NaN.
2. `split_ps`: `ps_idx = first index where TVT_input.isna()`; slice; drop `TARGET`+`LEAK_COLS` from `predict_df`.
3. `true_tvt`, `well_id_from_path`.
4. Smoke-test on `000d7d20` (train) + its test twin → assert `predict_df` lacks `TVT`/leak in both; `ps_idx==1442`.

## Todo list
- [ ] `src/well_io.py` with loader, `split_ps`, accessors, constants
- [ ] smoke test train + test twin (cols, ps_idx)

## Success Criteria
- `predict_df` never contains `TVT` or any leak col (assert in tests).
- `ps_idx==1442` for `000d7d20`; predict rows = total − 1442.
- Same function returns coherent split on a test well (no `TVT`) without error.

## Risk Assessment
- **TVT-vs-TVT_input leak** → loader strips `TVT` from `predict_df`; the firewall is structural, not a convention.
- **id off-by-one** → preserve original 0-based order; verified against sample_submission.
- Blank parsed as string not NaN → explicit numeric coercion + test.

## Security Considerations
- Leakage prevention is the core security concern of the whole competition. This module is the enforcement point:
  the target and target-encoding columns are removed at the boundary so downstream code cannot leak them.

## Next steps
→ Phase 03 consumes `(known_df, predict_df)`.
