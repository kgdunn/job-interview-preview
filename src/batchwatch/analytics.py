"""Per-batch curve fitting and the outlier screen.

The pH trace of a healthy batch is a sigmoid: a lag while the culture wakes up,
a fast acidification phase, then a plateau near the target pH. Fitting a
Gompertz to it gives us four numbers per batch that are comparable across sites
and products, which is a lot more useful than "final pH".

Those numbers plus a couple of bulk properties go into a PCA and we look at
whatever sits far from the middle.
"""

from __future__ import annotations

import math

import numpy as np
import pandas as pd
from scipy.optimize import curve_fit

FIT_COLUMNS = ["amplitude", "mu", "lag", "r2"]

DESCRIPTOR_COLUMNS = [
    "ph_start",
    "ph_final",
    "ph_drop",
    "duration_h",
    "od_max",
    "r2",
    "final_yield_kg",
]

MIN_POINTS = 6


def gompertz(t, amplitude, mu, lag):
    """Modified Gompertz, in the usual form: how far the pH has dropped by t.

    amplitude  total drop the batch gets to
    mu         steepest acidification rate, pH units per hour
    lag        hours before acidification really starts
    """
    inner = (mu * math.e / amplitude) * (lag - t) + 1.0
    return amplitude * np.exp(-np.exp(inner))


def fit_ph_curve(hours, ph) -> dict | None:
    """Fit the Gompertz to one batch's pH trace.

    Returns None when there is not enough usable signal to fit at all.
    """
    hours = np.asarray(hours, dtype=float)
    ph = np.asarray(ph, dtype=float)

    keep = ~np.isnan(ph)
    hours = hours[keep]
    ph = ph[keep]
    if hours.size < MIN_POINTS:
        return None

    ph_start = float(ph.max())
    drop = ph_start - ph

    try:
        params, _ = curve_fit(gompertz, hours, drop, maxfev=5000)
    except RuntimeError:
        return None

    fitted = gompertz(hours, *params)
    residual = float(np.sum((drop - fitted) ** 2))
    total = float(np.sum((drop - drop.mean()) ** 2))
    r2 = 1.0 - residual / total if total > 0 else 0.0

    amplitude, mu, lag = (float(p) for p in params)
    return {"amplitude": amplitude, "mu": mu, "lag": lag, "r2": r2}


def readings_to_frame(readings) -> pd.DataFrame:
    """Long reading rows -> a frame with an elapsed-hours column."""
    df = pd.DataFrame(readings)
    if df.empty:
        return df
    df["taken_at"] = pd.to_datetime(df["taken_at"], utc=True)
    start = df["taken_at"].min()
    df["hours"] = (df["taken_at"] - start).dt.total_seconds() / 3600.0
    return df


def describe_batch(batch: dict, readings) -> dict:
    """One row of the descriptor table.

    Two kinds of number in here: things read straight off the trace
    (ph_start, ph_drop, od_max, ...) and the four Gompertz parameters.
    """
    row = {
        "batch_id": batch["batch_id"],
        "site": batch.get("site"),
        "product": batch.get("product"),
        "final_yield_kg": batch.get("final_yield_kg"),
    }
    blank = ["ph_start", "ph_final", "ph_drop", "duration_h", "od_max"] + FIT_COLUMNS
    row.update({key: np.nan for key in blank})

    df = readings_to_frame(readings)
    if df.empty:
        return row

    row["duration_h"] = float(df["hours"].max())

    od = df[df["variable"] == "od600"]["value"].dropna()
    if not od.empty:
        row["od_max"] = float(od.max())

    ph = df[df["variable"] == "pH"].dropna(subset=["value"])
    if not ph.empty:
        ph = ph.sort_values("hours")
        row["ph_start"] = float(ph["value"].max())
        row["ph_final"] = float(ph["value"].iloc[-1])
        row["ph_drop"] = row["ph_start"] - row["ph_final"]

        fit = fit_ph_curve(ph["hours"].to_numpy(), ph["value"].to_numpy())
        if fit is not None:
            row.update(fit)

    return row


def descriptor_table(rows) -> pd.DataFrame:
    df = pd.DataFrame(list(rows))
    if df.empty:
        return df
    for column in DESCRIPTOR_COLUMNS + FIT_COLUMNS:
        if column not in df:
            df[column] = np.nan
    return df


def pca(matrix: np.ndarray, n_components: int = 2):
    """Plain PCA on a 2-D array. Returns (scores, loadings, explained ratio)."""
    matrix = np.asarray(matrix, dtype=float)
    centred = matrix - matrix.mean(axis=0)
    u, s, vt = np.linalg.svd(centred, full_matrices=False)

    n_components = min(n_components, vt.shape[0])
    scores = u[:, :n_components] * s[:n_components]
    loadings = vt[:n_components]

    variance = s**2
    explained = variance[:n_components] / variance.sum() if variance.sum() > 0 else variance[:n_components]
    return scores, loadings, explained


def flag_outliers(descriptors: pd.DataFrame, limit: int = 20):
    """Score every batch by how far it sits from the centre of the PCA.

    Returns the top `limit` rows plus the model summary, so callers can show
    how much of the variance the first two components actually carry.
    """
    empty = descriptors.head(0) if isinstance(descriptors, pd.DataFrame) else pd.DataFrame()
    model = {"n_scored": 0, "explained_variance_ratio": [], "loadings": []}

    if descriptors.empty:
        return empty, model

    usable = descriptors.dropna(subset=DESCRIPTOR_COLUMNS).copy()
    if len(usable) < 3:
        return usable.head(0), model

    scores, loadings, explained = pca(usable[DESCRIPTOR_COLUMNS].to_numpy())

    usable["pc1"] = scores[:, 0]
    usable["pc2"] = scores[:, 1] if scores.shape[1] > 1 else 0.0
    usable["score"] = np.sqrt(usable["pc1"] ** 2 + usable["pc2"] ** 2)

    model = {
        "n_scored": int(len(usable)),
        "explained_variance_ratio": [float(v) for v in explained],
        "loadings": [[float(v) for v in row] for row in loadings],
    }
    return usable.sort_values("score", ascending=False).head(limit), model


def acidity_profile_by_product(frames) -> pd.DataFrame:
    """Mean titratable acidity per product, pooled over every site."""
    usable = [frame for frame in frames if len(frame)]
    if not usable:
        return pd.DataFrame(columns=["product", "mean_titratable_acidity", "n_readings"])

    df = pd.concat(usable, ignore_index=True)
    df = df[["product", "value"]].dropna()

    out = (
        df.groupby("product")["value"]
        .agg(mean_titratable_acidity="mean", n_readings="size")
        .reset_index()
    )
    return out.sort_values("product").reset_index(drop=True)
