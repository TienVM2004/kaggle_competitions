# Project State — ROGII Wellbore Geology Prediction

> **Living snapshot.** Overwritten at each checkpoint. Read this first when resuming. For chronology see
> [`changelog.md`](changelog.md).

- **Last updated:** 2026-06-11
- **Current phase:** baselines + post-PS EDA done → **alignment model next** (planning not started)
- **Status:** CV harness built and certified (B1 reproduces the public flat-baseline score). Geometry
  hypothesis **refuted** by its own baselines; root cause found (whole-well EDA statistics); corrected
  post-PS EDA done. No alignment model or submission yet. Checkpoint committed and **pushed to origin/main**
  (`d240b9d`…`31bc8ee`); working tree clean.

---

## Problem
Predict `TVT` (depth within the rock-layer stack) for the post-PS portion of each horizontal well, from the
lateral gamma-ray (`GR`) log + a per-well vertical reference (`typewell`). This is ML geosteering.
→ full framing in [`../../README.md`](../../README.md).

## Hard facts locked
*(measured/verified; see [`README.md`](../../README.md), [`eda/01`](../../notebooks/eda/01-eda-general.ipynb),
[`eda/03`](../../notebooks/eda/03-eda-post-ps.ipynb))*
- **773 train wells, 3 visible test wells** (the 3 are byte-identical to train wells — the public-LB leak).
- **Code competition**: hidden larger test set, discovered by globbing `test/` (folder swap at scoring);
  5 subs/day; deadline 2026-08-05. Metric RMSE (API says MSE — equivalent; confirm scale on 1st sub).
- **PS contract verified end-to-end:** PS = first NaN `TVT_input` (contiguous tail); `id = {well}_{i}`,
  i = 0-based row position; submission rows = post-PS only; sum over the 3 visible test wells = **14,151**
  = official scored count, reproduced exactly.
- **B1 flat carry-forward = 15.91 pooled RMSE** (3,783,989 scored rows) — the locked floor, matches the
  publicly known flat-baseline score → harness/folds/PS contract certified.
- `Z` stored negative; `TVT_input == TVT` pre-PS; `Z` complete post-PS; MD ~1 ft spacing (not exact).
- Leak columns (`ANCC…BUDA`) + `TVT` are train-only; the loader strips them from every model's input.

## Corrected picture (post-PS, the scored region) — supersedes the old "geometry spine"
*(measured in [`eda/03`](../../notebooks/eda/03-eda-post-ps.ipynb) §8; old whole-well numbers were dominated
by the pre-PS descent section)*
- **Steering holds TVT nearly constant** (~26 ft median excursion; end drift 11 ft median / 32 p90) while
  **Z absorbs ~6× larger structural swings**. corr(TVT,−Z): 0.92 whole-well → **0.09** post-PS; slope
  TVT~−Z ≈ **0.01**; ΔTVT variance left after −ΔZ: 2% → **64%**; drilled→predicted slope transfer **0.00**.
  → **Z is noise for this task; no geometry shortcut exists.**
- **The deviation `TVT − anchor` is a smooth bounded wander:** lag-1 autocorr of ΔTVT 0.91; direction
  persists ~170 ft; 62% of wells cross back through the anchor → locally persistent, globally direction-less.
  Departure from anchor: ~10.5 ft median / ~30 p90 at 5,000 ft past PS.
- **GR missingness is pinholes, not chasms:** 70% median coverage, median gap 1 ft; bridging gaps ≤5 ft
  turns ~40 ft raw runs into **1,164 ft** median matchable windows (~3 windows ≥200 ft per well).
  Coverage uncorrelated with well difficulty (rank-corr 0.01).
- **B1's error is concentrated:** per-well median 10.7, worst 70.6; hardness tracks TVT excursion
  (rank-corr **+0.78**), not length/GR/geometry. The 15.9 → ~9 gap lives in high-excursion wells deep past PS.

## Competitive landscape
*(reference pulls in `data/_kernels/`, gitignored)*
- Winning family: unsupervised GR↔typewell alignment (particle filter / DTW / NCC / beam) + geometry prior →
  GBDT residual-to-anchor → blend → smooth. Flat ≈ 15.9 (= our B1); pure-GBDT-on-row-features ≈ CV 15
  (now explained: local features carry no signal); leaders ≈ 8–9.
- "artifact" in public titles = ravaghi's cached-features dataset, not geophysics.
- **Leakage trap:** 3 visible test wells overlap train → public LB inflated by same-well overrides; private
  set (the $50k) likely unseen wells. → trust local CV.

## Decisions locked
| Decision | Why | Status |
|---|---|---|
| CV = GroupKFold by well, K=5, frozen `data/processed/cv-folds.parquet`, post-PS pooled RMSE | mirrors test protocol; row splits leak | firm |
| Trust local CV over public LB | overlap exploit contaminates public | firm |
| ~~Geometry-first spine (predict D)~~ | **REFUTED 2026-06-10** — B2/B3 RMSE 107/73; code review confirmed no bug; see eda/03 | dead |
| B1 = 15.91 is the floor; alignment-first is the direction | only GR carries geology; EDA leaves no other channel | firm |
| eda/02 conclusions superseded (banner added) | whole-well stats dominated by descent section | firm |
| Methodology: compute every statistic on post-PS rows only | the EDA failure mode that caused the refutation | firm |
| Compute free-only via Kaggle kernels | see `compute-bridge` memory | firm |
| Notebooks = generator script → `nbconvert --execute`; meaning tables + annotated charts | committed executed `.ipynb` is the artifact | firm |

## Artifacts map
- [`README.md`](../../README.md) — framing + §8 CV (locked), §9 approach arc (geometry refuted → alignment),
  §10 results table (B1/B2/B3).
- `src/` — `well_io.py` (PS contract + leak firewall), `cv_folds.py` (frozen folds), `baselines.py`
  (B1/B2/B3, docstrings record the refutation), `eval.py` (pooled+per-well RMSE harness).
- [`notebooks/modeling/01-baselines.ipynb`](../../notebooks/modeling/01-baselines.ipynb) — baseline record
  (table, B1 error anatomy, findings).
- [`notebooks/eda/03-eda-post-ps.ipynb`](../../notebooks/eda/03-eda-post-ps.ipynb) — **the corrected EDA**;
  findings §8 is the reference for all post-PS statistics. eda/01 general; eda/02 superseded (banner).
- `data/processed/` — `cv-folds.parquet` (frozen, immutable), `post-ps-summary.parquet` (773×28),
  `well-summary.parquet`.
- [`plans/01-baseline-cv-harness/`](../../plans/01-baseline-cv-harness/plan.md) — completed plan (incl.
  data-grounding report). `data/_kernels/` reference pulls. `submissions/` empty yet.

## Open threads / next
- **Plan + build the GR–typewell alignment model**: start from flat, bend smoothly where the GR sequence
  matched against the typewell indicates drift; anchor at PS; continuity as hard constraint; bridge GR gaps
  ≤5 ft; per-well GR normalization (scale mismatch, eda/01). Score on the frozen folds vs the 15.91 floor.
- Then: Kaggle submission notebook (glob `test/`, write `submission.csv`); confirm MSE-vs-RMSE on 1st sub.
- Deferred: spatial-holdout CV stress test (only once a model learns across wells via X,Y).

## Operator working preferences
- Peer engineer; hard pushback expected; sycophancy is the worst failure; concede only on evidence.
- Brainstorm jointly, **operator decides**; **plan-first** before non-trivial execution.
- Explanations **plain-English**: no unexplained jargon, no childish analogies; define every measure
  introduced (e.g. "variance left after removing X" needed defining).
- Rebuilding ML reflexes — favor clear reasoning over name-dropping methods.
