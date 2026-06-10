"""Well loading + Prediction-Start (PS) split contract.

Single source of truth for how a lateral well is read and partitioned into the known (pre-PS)
and to-predict (post-PS) segments. Enforces the test-portability firewall: the predict segment is
stripped of the training-only target (``TVT``) and the six layer-boundary leak columns, so a
downstream model physically cannot read them — any model that runs in CV also runs on the hidden
test set, whose wells lack those columns entirely.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

TARGET = "TVT"
LEAK_COLS = ["ANCC", "ASTNU", "ASTNL", "EGFDU", "EGFDL", "BUDA"]
TRAIN_ONLY = [TARGET, *LEAK_COLS]


def well_id_from_path(path) -> str:
    """Return the 8-char well id from a ``{id}__horizontal_well.csv`` path."""
    return Path(path).name.split("__", 1)[0]


def load_lateral(path) -> pd.DataFrame:
    """Load a lateral well CSV preserving row order; blank cells parse as NaN (float64)."""
    return pd.read_csv(path)


def find_ps(df: pd.DataFrame) -> int:
    """Row position of Prediction Start = first row with blank ``TVT_input``.

    Returns ``len(df)`` when ``TVT_input`` is fully populated (nothing to predict).
    """
    mask = df["TVT_input"].isna()
    if not mask.any():
        return len(df)
    return int(mask.to_numpy().argmax())


def split_ps(df: pd.DataFrame):
    """Split a lateral at PS into ``(known_df, predict_df, ps_idx)``.

    ``known_df`` keeps ``TVT_input`` (== ``TVT`` pre-PS). ``predict_df`` excludes the training-only
    target and leak columns, so it is identical in shape for train and test wells — the leakage
    firewall. ``ps_idx`` is the 0-based row position, matching the ``{well}_{i}`` submission id.
    """
    ps = find_ps(df)
    known = df.iloc[:ps].copy()
    drop = [c for c in TRAIN_ONLY if c in df.columns]
    predict = df.iloc[ps:].drop(columns=drop).copy()
    return known, predict, ps


def true_tvt(df: pd.DataFrame) -> pd.Series:
    """Return the train-only target column; raises if absent (e.g. a test well).

    Scoring-only accessor — the target must never reach a model's prediction path.
    """
    if TARGET not in df.columns:
        raise KeyError(f"{TARGET!r} absent: true_tvt is train-only and must never feed a model")
    return df[TARGET]
