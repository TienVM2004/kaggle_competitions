# Changelog — ROGII Wellbore Geology Prediction

> **Append-only**, reverse-chronological. One block per work session/phase. For current state see
> [`project-state.md`](project-state.md).

---

## 2026-06-10 — Checkpoint (baselines built → geometry refuted → corrected EDA)

**1. CV harness + baselines built** (plan `plans/01-baseline-cv-harness/`, grounded against raw CSVs first:
0-based `id`, Z negative, `TVT_input == TVT` pre-PS, 14,151 scored-row count reproduced)
- `src/`: `well_io.py` (PS contract + leak firewall: predict-df physically lacks `TVT`/leak cols),
  `cv_folds.py` (deterministic K=5 GroupKFold frozen to `cv-folds.parquet`, overwrite guard),
  `baselines.py` (B1 flat / B2 `−Z+offset` / B3 `+dip`), `eval.py` (single-pass pooled + per-well RMSE).
- **B1 = 15.91** (gate 15–16 passed, matches public flat baseline → harness certified).
  **B2 = 107.49, B3 = 73.08 — catastrophically worse. Stopped per plan rule "investigate, don't assume."**

**2. Refutation verified — no bug**
- Adversarial review agent (all algebra/alignment/pooling cleared; B2 anchor within 0.02 ft at PS) +
  independent numpy re-implementation (same numbers) + exact decomposition (B2 error ≡ drift of `D=TVT+Z`
  to machine precision). Minor fixes: dead fallback guard, docstrings now record the negative result.

**3. Root cause: whole-well EDA**
- eda/02's statistics (corr 0.92, "D small/smooth", "98% free") were dominated by the pre-PS descent
  (~750 ft lockstep swings). Post-PS — the only scored region — steering holds TVT (~26 ft) while Z absorbs
  ~6× structural relief; slope TVT~−Z ≈ 0.01 with zero drilled→predicted transfer.

**4. Corrected EDA** → `notebooks/eda/03-eda-post-ps.ipynb` (773 wells, post-PS rows only; caches
`post-ps-summary.parquet` 773×28)
- Corrected record: corr 0.92→0.09; Δ-corr 0.99→0.67; leftover variance 2%→64%; transfer 0.00.
- Target prior: smooth bounded wander (lag-1 autocorr 0.91, ~170 ft runs, 62% cross back) → continuity
  prior, level must come from GR evidence, never extrapolate trend.
- **GR pinhole discovery:** median gap 1 ft; bridging ≤5 ft gaps: 40 ft → 1,164 ft matchable windows.
- B1 anatomy: error concentrated in high-excursion wells (rank-corr +0.78); GR coverage orthogonal (0.01).

**5. Record corrected** — `modeling/01-baselines.ipynb` (baseline record), supersede banner on eda/02,
README §8 (locked CV) / §9 (refutation arc + alignment direction) / §10 (results table), project-state
overwritten, plan-01 closed.

**Decisions:** geometry spine **dead** · B1 = 15.91 locked floor · alignment-first ·
all future statistics computed post-PS only · eda/02 superseded.
**Next:** plan + build the GR–typewell alignment model vs the 15.91 floor.

---

## 2026-06-09 — Checkpoint (onboarding → EDA complete)

Back-log of all work to date, grouped by phase.

**1. Onboarding & problem reverse-engineering**
- Kaggle competition page is JS-rendered (WebFetch returns only the title) → reverse-engineered the task from the
  raw CSVs + `task-description.pptx` instead.
- Established terminology with operator: lateral/bit/MD/GR/typewell; **Z (below sea level) vs TVT (depth in rock
  stack)**; PS (Prediction Start); why the typewell isn't a lookup table (stretch, scale, missingness, ambiguity).

**2. README authored & data facts corrected**
- Wrote `README.md` §1–7 (problem, physical setting, terminology, data format, why-hard, evaluation, dataset),
  iteratively tone-tuned for a non-drilling, professional reader.
- Corrected early wrong assumptions against real data: **773 train wells (not 64)**; **6 boundary columns
  (not 10)**; Geology = 43 labels (6 common); row range 2,058–12,141; GR missing ~28% (not 43%).

**3. Full data pulled & reorganized; competition type confirmed**
- Downloaded full dataset (817 MB zip), extracted to clean `data/raw/{train,test}/` + `sample_submission.csv`
  (14,151 rows) + `task-description.pptx`. Deleted scratch `_inspect/`. All under gitignored `data/`.
- Found `.venv` and `.kaggle/access_token.txt` live at **repo root** `D:\KAGGLE\`, not the competition folder.
- Confirmed **code competition** via Kaggle API: `is_kernels_submissions_only=True`, 5 subs/day, $50k, 2,464 teams,
  deadline 2026-08-05. Hidden test served by globbing `test/` (folder-swap mechanic, per Deotte starter).

**4. Public-notebook intel digested** (pulls in `data/_kernels/`)
- Read Deotte XGB starter (mechanics + CV) + agent-digest of DWT/ridge/alignment notebooks.
- Winning family = GR↔typewell alignment (PF/DTW/NCC/beam) + geometry prior → GBDT residual-to-anchor → blend →
  smooth. Flat baseline ~15.9; pure-GBDT ~CV15; leaders ~8–9.
- "artifact" = cached features dataset, not geophysics. **Leakage trap**: 3 visible test wells overlap train →
  same-well physical override inflates public LB; private likely unseen. → decision: trust CV, not public LB.

**5. General EDA** → `notebooks/eda/01-eda-general.ipynb` (executed, charts embedded)
- Streaming 773-well summary → `data/processed/well-summary.parquet` (773×33).
- Key: ~74% predicted per well; GR missing ~28% (worse post-PS); per-well GR scale mismatch; TVT span ≈ Z span.

**6. Geometry / increment EDA** → `notebooks/eda/02-eda-geometry.ipynb` (executed)
- Validated operator's derivative instinct + the reframing `TVT = −Z + D`:
  corr(TVT,−Z)=0.92; corr(ΔTVT,−ΔZ)=0.99, ~2% left; D smoothness 0.19; D pre/post-PS slope corr 0.77;
  |corr(ΔGR,ΔTVT)|=0.04. → GR only via typewell alignment; real target is the smooth residual D (~230 ft).

**7. EDA presentation refactor**
- Both notebooks regenerated to a presentation standard: 3-column "meaning" tables (Measurement | Value | What it
  means), annotated histograms (median lines + units), hexbin density for dense scatters, formatted tables
  (killed scientific-notation `describe()` dumps). Numbers unchanged — presentation only.

**Decisions made this checkpoint:** CV = GroupKFold by well, post-PS only · trust CV over public LB ·
geometry-first modeling spine · notebooks via generator + nbconvert · presentation = meaning tables + annotated charts.

**Next:** modeling — baselines (carry-forward, geometry B2/B3) on locked CV, then GR–typewell alignment for D.
