# Phase 01 — Frozen CV folds

## Context links
- Parent: [`plan.md`](plan.md) · Grounding: [`reports/01-data-grounding.md`](reports/01-data-grounding.md)
- Dependencies: none (only needs the list of train well_ids from filenames)
- Downstream: Phase 04 (eval reads folds)

## Overview
- Date: 2026-06-09 · Priority: P1 · Impl status: done · Review status: pending
- Build the frozen GroupKFold assignment once and freeze it to disk so every model — now and later — is scored on
  identical folds. The single source of CV truth.

## Key Insights
- Split unit MUST be the whole well; 1-ft neighbor rows are near-duplicates → row-level split leaks.
- Folds must be deterministic and **independent of filesystem glob order**, else a rebuild silently reshuffles and
  invalidates all prior cross-model comparisons. Sort → seed-permute → chunk.
- Baselines are per-well, so for them folds only affect *reporting grouping*, not score — but freezing now makes the
  later cross-well models honest and comparable from day one.

## Requirements
- `src/cv_folds.py` with: `build_folds(well_ids, k=5, seed=42) -> DataFrame[well_id, fold]`;
  `write_folds(df, path, overwrite=False)` (refuse silent overwrite); `load_folds(path) -> DataFrame`.
- Output `data/processed/cv-folds.parquet`: 773 rows, `fold ∈ {0..4}`, balanced.
- well_ids derived from `data/raw/train/*__horizontal_well.csv` basenames (8-char id).

## Architecture
- Pure-stdlib + pandas/numpy. No sklearn GroupKFold needed (it has no seed; ordering-dependent). Deterministic recipe:
  `ids = sorted(well_ids); rng = np.random.RandomState(seed); perm = rng.permutation(ids); fold = index % k` (or
  contiguous chunks). Equal-size, reproducible, seed-controlled.
- Overwrite guard: if path exists and `overwrite=False`, raise with a message telling caller to delete intentionally.

## Related code files
- CREATE `src/cv_folds.py`
- WRITE `data/processed/cv-folds.parquet` (gitignored under `data/`)

## Implementation Steps
1. Glob train laterals → extract sorted unique 8-char well_ids; assert count == 773.
2. `build_folds`: seed-permute sorted ids, assign fold by position; return tidy df.
3. `write_folds` with overwrite guard; `load_folds`.
4. Build + write the parquet; print fold size distribution.

## Todo list
- [ ] `src/cv_folds.py` (build/write/load + guard)
- [ ] generate `cv-folds.parquet`
- [ ] print/verify fold balance + count

## Success Criteria
- 773 rows, 5 folds, sizes ~150–160 each.
- Two consecutive builds with same seed → identical assignment (determinism test).
- Overwrite guard raises when file exists and `overwrite=False`.

## Risk Assessment
- **Fold reshuffle invalidates comparisons** → write-once + overwrite guard + deterministic recipe.
- **Glob-order dependence** → sort ids before permute.
- Wrong well count (≠773) → assert hard-fails early.

## Security Considerations
- Data-integrity analog: folds are the integrity anchor for every future score. Treat the parquet as immutable once
  written; changing it retroactively falsifies historical CV numbers.

## Next steps
→ Phase 02 (well loader) in parallel; both feed Phase 04.
