"""Estrazione y_age e y_sex da participants.tsv ds004504.

ds004504 usa colonne 'Gender' (F/M) e 'Age' (int) invece di 'sex'/'age'.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

# Percorso (relativo alla radice repo) del participants.tsv di ds004504
DS004504_TSV = Path("data/raw/ds004504/participants.tsv")
# Codifica del sesso: F -> 0, M -> 1
SEX_MAP = {"F": 0, "M": 1}


def load_phenotype_ds004504(
    subjects: list[str],
    tsv_path: Path = DS004504_TSV,
) -> tuple[np.ndarray, np.ndarray]:
    """Carica età e sesso dei soggetti da participants.tsv di ds004504.

    Args:
        subjects: ID BIDS dei soggetti (es. ``["sub-001", ...]``); l'ordine
            dell'output segue quello di questa lista.
        tsv_path: percorso del participants.tsv (colonne ``Age``, ``Gender``).

    Returns:
        Tupla ``(y_age, y_sex)``: età in anni (float64) e sesso codificato con
        ``SEX_MAP`` (int64, F=0, M=1), entrambi di lunghezza ``len(subjects)``.

    Raises:
        ValueError: se mancano soggetti nel TSV o ci sono valori NaN.
    """
    df = pd.read_csv(tsv_path, sep="\t", dtype=str)
    df = df.set_index("participant_id")
    missing = [s for s in subjects if s not in df.index]
    if missing:
        raise ValueError(f"Soggetti mancanti: {missing}")
    sub_df = df.loc[subjects]
    y_age = sub_df["Age"].astype(float).to_numpy(dtype=np.float64)
    y_sex = sub_df["Gender"].map(SEX_MAP).to_numpy(dtype=np.int64)
    if np.any(np.isnan(y_age)):
        raise ValueError("NaN in y_age")
    if np.any(pd.isna(sub_df["Gender"])):
        raise ValueError("NaN in y_sex (Gender)")
    return y_age, y_sex
