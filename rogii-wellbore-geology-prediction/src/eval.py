"""Score baselines on the frozen folds.

Pooled RMSE over every held-out post-PS row (matches the leaderboard's global row pooling) is the
headline metric; the per-well RMSE distribution is the diagnostic that catches a model good on
average but exploding on a few wells. Truth (``TVT``) enters only here, via ``true_tvt``, strictly
for scoring — never on a model's prediction path.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from well_io import load_lateral, split_ps, true_tvt


def rmse(pred, true) -> float:
    """Root-mean-square error between two equal-length arrays."""
    pred = np.asarray(pred, float)
    true = np.asarray(true, float)
    return float(np.sqrt(np.mean((pred - true) ** 2)))


def _lateral_path(data_root, well_id) -> Path:
    return Path(data_root) / "train" / f"{well_id}__horizontal_well.csv"


def score_baselines(fns: dict, folds: pd.DataFrame, data_root) -> dict:
    """Score every named baseline in a single pass over the wells (one file read per well).

    Returns ``{name: {pooled_rmse, per_well DataFrame[well_id,fold,rmse,n_rows], n_rows,
    n_nan_patched}}``. Non-finite predictions (e.g. a NaN ``Z`` post-PS) are patched to the last
    known TVT and counted, so the pooled RMSE is always well defined.
    """
    acc = {name: {"sse": 0.0, "n": 0, "rows": [], "patched": 0} for name in fns}
    for well_id, fold in zip(folds["well_id"], folds["fold"]):
        df = load_lateral(_lateral_path(data_root, well_id))
        known, predict, ps = split_ps(df)
        if len(predict) == 0:
            continue
        truth = true_tvt(df).to_numpy(float)[ps:]
        for name, fn in fns.items():
            pred = np.asarray(fn(known, predict), float)
            bad = ~np.isfinite(pred)
            if bad.any():
                pred[bad] = float(known["TVT_input"].iloc[-1])
                acc[name]["patched"] += int(bad.sum())
            err2 = (pred - truth) ** 2
            a = acc[name]
            a["sse"] += float(err2.sum())
            a["n"] += len(err2)
            a["rows"].append((well_id, int(fold), float(np.sqrt(err2.mean())), len(err2)))
    out = {}
    for name, a in acc.items():
        per_well = pd.DataFrame(a["rows"], columns=["well_id", "fold", "rmse", "n_rows"])
        out[name] = {"pooled_rmse": float(np.sqrt(a["sse"] / a["n"])), "per_well": per_well,
                     "n_rows": a["n"], "n_nan_patched": a["patched"]}
    return out


def comparison_table(results: dict) -> pd.DataFrame:
    """Flatten ``score_baselines`` output into a table sorted by pooled RMSE (best first)."""
    rows = [{"baseline": name, "pooled_rmse": r["pooled_rmse"], "n_rows": r["n_rows"],
             "n_nan_patched": r["n_nan_patched"]} for name, r in results.items()]
    return pd.DataFrame(rows).sort_values("pooled_rmse").reset_index(drop=True)
