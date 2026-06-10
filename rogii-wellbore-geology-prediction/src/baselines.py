"""Geometry baselines B1/B2/B3 (per-well, no GR, no cross-well learning).

Decomposition ``TVT = -Z + D`` with ``D = TVT + Z`` (Z is stored negative, so ``-Z`` is a large
positive number known everywhere). The baselines model only the smooth residual D; each adds
exactly one geometric term, so the RMSE drop between them attributes cleanly to that term. Inputs
are restricted to test-present columns (``TVT_input``, ``Z``, ``MD``) — never the target.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def _known_md_d(known: pd.DataFrame):
    """Return (MD, D) arrays over the known interval, with ``D = TVT_input + Z``."""
    md = known["MD"].to_numpy(float)
    d = known["TVT_input"].to_numpy(float) + known["Z"].to_numpy(float)
    return md, d


def b1_carry_forward(known: pd.DataFrame, predict: pd.DataFrame) -> np.ndarray:
    """B1 — hold the last known TVT flat across the predict interval (the do-nothing floor)."""
    if len(known) < 1:
        raise ValueError("empty known interval: no anchor to carry forward")
    last = float(known["TVT_input"].iloc[-1])
    return np.full(len(predict), last)


def b2_z_anchor(known: pd.DataFrame, predict: pd.DataFrame) -> np.ndarray:
    """B2 — anchor on -Z, hold the structural residual D flat at its PS value.

    ``D0 = TVT_input[last] + Z[last]``; prediction ``= D0 - Z_i``. REFUTED on post-PS data
    (pooled RMSE 107 vs B1's 15.9): in the lateral, -Z swings ~6x more than TVT, so riding -Z
    at unit slope imports that swing as error. Kept as a documented negative result.
    """
    if len(known) < 1:
        return b1_carry_forward(known, predict)
    d0 = float(known["TVT_input"].iloc[-1] + known["Z"].iloc[-1])
    return d0 - predict["Z"].to_numpy(float)


def b3_z_anchor_dip(known: pd.DataFrame, predict: pd.DataFrame) -> np.ndarray:
    """B3 — B2 plus a linear dip: let D drift along MD at the slope seen pre-PS.

    Fits ``D ~ a + b*MD`` over the whole known interval. REFUTED on post-PS data (pooled RMSE 73):
    the pre-PS slope of D does not persist past PS (corr ~0 on post-PS slopes). Kept as a
    documented negative result. Falls back to B2 with <2 known points or constant MD.
    """
    if len(known) < 2:
        return b2_z_anchor(known, predict)
    md, d = _known_md_d(known)
    if np.ptp(md) == 0:
        return b2_z_anchor(known, predict)
    slope, intercept = np.polyfit(md, d, 1)
    md_p = predict["MD"].to_numpy(float)
    z_p = predict["Z"].to_numpy(float)
    return (intercept + slope * md_p) - z_p


BASELINES = {"B1 carry-forward": b1_carry_forward,
             "B2 -Z+offset": b2_z_anchor,
             "B3 -Z+offset+dip": b3_z_anchor_dip}
