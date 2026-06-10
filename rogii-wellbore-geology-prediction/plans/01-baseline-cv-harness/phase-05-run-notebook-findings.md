# Phase 05 — Run notebook + findings

## Context links
- Parent: [`plan.md`](plan.md) · Grounding: [`reports/01-data-grounding.md`](reports/01-data-grounding.md)
- Dependencies: Phases 01–04 (imports all `src/` modules) · Downstream: README §10, `docs/log/`

## Overview
- Date: 2026-06-09 · Priority: P1 · Impl status: done · Review status: pending
- The committed, executed artifact: imports `src/`, runs B1/B2/B3 on the frozen folds, renders the comparison table +
  per-well RMSE distribution, and writes plain-English findings. The run log of this phase.

## Key Insights
- Notebook authored via generator script → `nbconvert --execute --inplace` (locked convention; committed executed
  `.ipynb` is the artifact). Notebook imports from `src/`, never the reverse.
- Presentation standard (from EDA notebooks): 3-col meaning tables, annotated charts, no sci-notation dumps.
- This is where the global gate (B1≈15.9) is visually confirmed and the floor is published.

## Requirements
- `notebooks/modeling/01-baselines.ipynb` (executed, outputs committed):
  - imports `cv_folds`, `well_io`, `baselines`, `eval`.
  - **Comparison table**: B1/B2/B3 pooled RMSE + "isolates" column (meaning-table style).
  - **Per-well RMSE distribution** chart (histogram, annotated median; matplotlib, no seaborn) — ideally B2 or B3.
  - Findings markdown at bottom: concise, plain English, claims + numbers (gate hit? B2/B3 deltas? blow-up wells?).
- Generator script kept ephemeral (jobs tmp), `py_compile`-checked before execution (avoids the prior docstring bug).

## Architecture
- Self-contained: `find_data_root()` walk (as in EDA notebooks) to locate `data/raw`.
- Cells: setup/import → load folds → run `compare` → table → per-well chart → findings md.
- Headless exec with `PYTHONIOENCODING=utf-8` (cp1258 chokes on `−`/`Δ`).

## Related code files
- CREATE `notebooks/modeling/01-baselines.ipynb` (+ ephemeral generator)
- UPDATE `README.md` §10 results row; `docs/log/project-state.md`; `docs/log/changelog.md`

## Implementation Steps
1. Generator script (nbformat) → cells above; `py_compile` check.
2. `nbconvert --execute --inplace` via repo-root venv `python.exe`, `PYTHONIOENCODING=utf-8`.
3. Read back: confirm B1 gate, table renders, chart embedded.
4. Write findings md; update README §10 + `docs/log/`.

## Todo list
- [ ] generator script (+ py_compile)
- [ ] execute notebook headless, outputs embedded
- [ ] findings markdown at bottom
- [ ] README §10 + project-state + changelog updated

## Success Criteria
- Notebook executes clean end-to-end; table + chart embedded in committed `.ipynb`.
- B1≈15–16 visible; B2<B1, B3≤B2 shown with deltas.
- Findings answer: gate hit? per-component lift? worst-well behavior?
- README §10 has the first real CV numbers.

## Risk Assessment
- Generator docstring-in-string bug → `#` comments + `py_compile` precheck (known fix).
- Unicode `−`/`Δ` on Windows → `PYTHONIOENCODING=utf-8`.
- Stale outputs (edit without re-exec) → always `--execute --inplace`, verify on read-back.

## Security Considerations
- None beyond the leakage firewall already enforced in `src/`. Notebook surfaces only train CV — no submission here.

## Next steps
- Phase boundary: update `docs/log/`. Then next plan: GR–typewell alignment to correct D's far-tail drift (the lift
  from floor → single digits).
