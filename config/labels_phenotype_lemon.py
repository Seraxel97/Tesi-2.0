"""Estrazione y_age e y_sex da participants.tsv (LEMON).

LEMON usa colonne 'gender' (F/M) e 'age (5-year bins)' (es. "55-60").
- gender  → F→0, M→1 (coerente con SEX_MAP ds005385/ds004504)
- età     → midpoint del bin 5-anni (es "55-60" → 57.5)
"""

from __future__ import annotations

import os
from pathlib import Path

import numpy as np
import pandas as pd

_TSV_ENV = os.environ.get("TESI_LEMON_TSV", "").strip()
LEMON_TSV = (
    Path(_TSV_ENV).expanduser()
    if _TSV_ENV
    else Path(__file__).resolve().parents[1] / "data" / "raw" / "lemon" / "participants.tsv"
)

SEX_MAP = {"F": 0, "M": 1}
_AGE_COL = "age (5-year bins)"


def _bin_midpoint(bin_str: str) -> float:
    """Converte un bin '55-60' nel midpoint 57.5."""
    s = str(bin_str).strip()
    if "-" not in s:
        raise ValueError(f"Bin età non valido: {bin_str!r}")
    lo_str, hi_str = s.split("-", 1)
    lo, hi = float(lo_str), float(hi_str)
    return (lo + hi) / 2.0


def load_phenotype_lemon(
    subjects: list[str],
    tsv_path: Path = LEMON_TSV,
) -> tuple[np.ndarray, np.ndarray]:
    """Ritorna (y_age float64, y_sex int64) allineati a `subjects`.

    Parameters
    ----------
    subjects:
        Lista ordinata di subject ID (es. ["sub-010002", ...]).
    tsv_path:
        Path a participants.tsv LEMON.

    Returns
    -------
    y_age : np.ndarray float64, shape (n,)  — midpoint del bin 5-anni
    y_sex : np.ndarray int64,   shape (n,)  — F→0, M→1
    """
    df = pd.read_csv(tsv_path, sep="\t", dtype=str)
    df = df.set_index("participant_id")

    missing = [s for s in subjects if s not in df.index]
    if missing:
        raise ValueError(f"Soggetti mancanti nel TSV LEMON: {missing}")

    sub_df = df.loc[subjects]

    if sub_df["gender"].isna().any():
        raise ValueError("NaN in gender LEMON")
    y_sex = sub_df["gender"].map(SEX_MAP).to_numpy(dtype=np.int64)
    if np.any(np.isnan(y_sex.astype(float))):
        raise ValueError(f"gender non mappabile (attesi F/M): {sub_df['gender'].unique()}")

    y_age = sub_df[_AGE_COL].map(_bin_midpoint).to_numpy(dtype=np.float64)
    if np.any(np.isnan(y_age)):
        raise ValueError("NaN in y_age LEMON")

    return y_age, y_sex
