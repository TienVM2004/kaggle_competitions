"""Frozen GroupKFold assignment over wells.

Builds a deterministic well->fold map (independent of filesystem order) and freezes it to disk so
every model — now and later — is scored on identical folds. Whole wells go to a single fold;
splitting at row level would leak across 1-ft-spaced neighbours. The frozen parquet is the CV
integrity anchor: once written it is immutable, since changing it retroactively falsifies every
historical CV number.
"""
from __future__ import annotations

import glob
from pathlib import Path

import numpy as np
import pandas as pd

from well_io import well_id_from_path

N_FOLDS = 5
SEED = 42


def train_well_ids(data_root) -> list[str]:
    """Sorted unique 8-char well ids from the train laterals under ``{data_root}/train``."""
    paths = glob.glob(str(Path(data_root) / "train" / "*__horizontal_well.csv"))
    return sorted({well_id_from_path(p) for p in paths})


def build_folds(well_ids, k: int = N_FOLDS, seed: int = SEED) -> pd.DataFrame:
    """Assign each well a fold via sort -> seeded permutation -> round-robin.

    Deterministic given (well_ids set, seed) and independent of input order, so a rebuild can never
    silently reshuffle. Round-robin on the shuffled order keeps fold sizes balanced.
    """
    ids = sorted(set(well_ids))
    rng = np.random.RandomState(seed)
    order = rng.permutation(np.asarray(ids))
    fold_of = {w: i % k for i, w in enumerate(order)}
    return pd.DataFrame({"well_id": ids, "fold": [fold_of[w] for w in ids]})


def write_folds(df: pd.DataFrame, path, overwrite: bool = False) -> None:
    """Freeze folds to parquet. Refuses to overwrite unless explicitly told to.

    Overwriting invalidates all prior CV comparisons — gated behind ``overwrite=True`` on purpose.
    """
    path = Path(path)
    if path.exists() and not overwrite:
        raise FileExistsError(
            f"{path} exists; folds are frozen. Pass overwrite=True only if you intend to "
            "invalidate every prior CV number."
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=False)


def load_folds(path) -> pd.DataFrame:
    """Load the frozen well->fold map."""
    return pd.read_parquet(path)
