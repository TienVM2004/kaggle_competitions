---
title: "CV harness + geometry baselines (B1/B2/B3)"
description: "Frozen GroupKFold ruler + 3 geometry baselines producing the honest CV floor every alignment model must beat."
status: completed
priority: P1
effort: 4h
branch: main
tags: [modeling, cross-validation, baseline, geometry]
created: 2026-06-09
---

# Plan 01 — CV harness + geometry baselines

First modeling step. Build the **measuring stick** (frozen CV) and the **floor** (three geometry baselines, no GR,
no cross-well learning). Every later GR-alignment model is judged against this. Design fully brainstormed + decided;
all data-level assumptions verified against raw CSVs — see [`reports/01-data-grounding.md`](reports/01-data-grounding.md).

## Spine
`TVT = −Z + D`, `D = TVT + Z` (Z stored negative). `−Z` is free everywhere → baselines spend their effort only on
the smooth residual `D`. B1 ignores geometry; B2 adds the −Z anchor; B3 adds D's linear dip.

## Phases
| # | Phase | File | Status | Deps |
|---|---|---|---|---|
| 01 | Frozen CV folds | [`phase-01-frozen-cv-folds.md`](phase-01-frozen-cv-folds.md) | done | — |
| 02 | Well loader + PS contract | [`phase-02-well-loader-ps-contract.md`](phase-02-well-loader-ps-contract.md) | done | — |
| 03 | Baseline functions | [`phase-03-baseline-functions.md`](phase-03-baseline-functions.md) | done | 02 |
| 04 | Eval harness | [`phase-04-eval-harness.md`](phase-04-eval-harness.md) | done | 01,02,03 |
| 05 | Run notebook + findings | [`phase-05-run-notebook-findings.md`](phase-05-run-notebook-findings.md) | done | 01–04 |

## Deliverable
| Baseline | Pooled CV RMSE | Isolates |
|---|---|---|
| B1 carry-forward | **15.91** | do-nothing floor (~15.9 expected) ✓ gate passed |
| B2 −Z + offset | 107.49 | value of Z anchor — **refuted** |
| B3 + dip | 73.08 | value of D persistence — **refuted** |

**Outcome (2026-06-10):** B1 = 15.91 is the locked floor (harness certified). B2/B3 refuted the geometry
spine — code review confirmed no bug; root cause was whole-well EDA statistics. Corrected analysis:
`notebooks/eda/03-eda-post-ps.ipynb`; record: `notebooks/modeling/01-baselines.ipynb`. Next: alignment model.

## Global gate
**B1 pooled RMSE must land ≈ 15–16.** Anything else ⇒ PS-detection or row-index bug; stop and fix before trusting
any other number. (Verified: `id` index is 0-based row position; `sample_submission` starts at the PS row.)

## Out of scope
Kaggle submission notebook (glob `test/`, write `submission.csv`), GR/typewell alignment, GBDT, spatial-holdout CV,
metric-confirmation submission. Baseline fns written test-portable so the future submission notebook just wraps them.

## On completion
Update `docs/log/project-state.md` (phase → "baselines done"), append `docs/log/changelog.md`, fill README §10 results row.

## Open questions (non-blocking)
1. B3 slope window: whole pre-PS (default) vs last-N-ft. Ship whole, A/B later.
2. Confirm PS detection reproduces the official 14,151 scored rows across the 3 test wells.
