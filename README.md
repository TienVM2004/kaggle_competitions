# Kaggle Portfolio

A working repository of Kaggle competition entries. Each competition lives in its own self-contained subfolder with a dedicated README, source code, notebooks, and submission artifacts. The objective across all entries is the same: strong leaderboard performance grounded in a trustworthy cross-validation scheme, with the reasoning behind every modeling decision documented as it is made.

---

## Competitions

| Competition | Domain | Metric | CV | Public LB | Private LB | Status |
|---|---|---|---|---|---|---|
| _Pending first entry_ | — | — | — | — | — | — |

Entries are added here as competitions reach stable milestones. Each row links to the competition's own subfolder for the full writeup.

---

## How This Repository Is Organized

```
KAGGLE/
  README.md                     # this file
  CLAUDE.md                     # working agreement for AI-assisted development
  {competition-slug}/           # one folder per competition
    README.md                   # problem, approach, results, reproduction steps
    docs/                       # deeper tech-decision writeups (on demand)
    notebooks/                  # EDA, exploration, error analysis
    src/                        # data, model, train, predict modules
    data/                       # raw/, processed/ (not committed)
    models/                     # weights and checkpoints (not committed)
    submissions/                # *.csv outputs (committed)
```

Each competition subfolder is fully self-contained — no shared utilities, no cross-competition imports. The repository is intentionally structured so that any single competition can be opened, understood, and reproduced on its own.

---

## What Each Competition Writeup Covers

- The problem in one sentence and the link to the original competition.
- The evaluation metric and what optimizing it means in practice.
- A summary of the data — shape, splits, notable characteristics.
- The cross-validation scheme and the reasoning behind it.
- The modeling approach: features, model family, ensembling if any.
- Results across CV, public leaderboard, and private leaderboard.
- Instructions to reproduce the submission.
- Key takeaways and what would be done differently next time.

---

## Skills Demonstrated

This section is populated as the body of work grows. Expected coverage areas:

- **Tabular modeling** — gradient boosting (LightGBM, XGBoost, CatBoost), feature engineering, target encoding, cross-validation discipline.
- **Computer vision** — PyTorch, `timm`, transfer learning, augmentation strategies.
- **Natural language processing** — HuggingFace transformers, tokenization, fine-tuning.
- **Time series** — lag features, rolling statistics, validation under temporal splits.
- **Cross-cutting** — robust CV design, leakage prevention, ensembling, reproducibility practices.

---

## Reproducibility

Every submitted result is committed before submission. Each competition's README documents the exact entry point to reproduce its result from raw data. Raw competition data is not committed — download instructions are provided per competition.
