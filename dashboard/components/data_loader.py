"""Data loader component — accesso ai dati reali della pipeline ds005385.

Carica dati da:
  - data/raw/ds005385/participants.tsv  → fenotipi (età, sesso)
  - data/features/ds005385/            → matrici feature X_*.npz
  - data/connectivity/ds005385/        → matrici FC per-soggetto per-condizione
  - reports/                           → risultati ML precomputed
"""

from __future__ import annotations

import json
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

_ROOT = Path(__file__).parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

_FEAT_DIR = _ROOT / "data" / "features" / "ds005385"
_CONN_DIR = _ROOT / "data" / "connectivity" / "ds005385"
_PARTICIPANTS_TSV = _ROOT / "data" / "raw" / "ds005385" / "participants.tsv"
_REPORTS_DIR = _ROOT / "reports"
_META_FILE = _FEAT_DIR / "metadata.json"


@lru_cache(maxsize=1)
def load_metadata() -> dict[str, Any]:
    if not _META_FILE.exists():
        return {}
    return json.loads(_META_FILE.read_text())


@lru_cache(maxsize=1)
def load_cohort_df(n_subjects: int | None = None) -> pd.DataFrame:
    """Carica DataFrame cohort con età, sesso dai soggetti N=100 whitelist.

    Se participants.tsv non disponibile, restituisce un DataFrame con solo subject_id.
    """
    meta = load_metadata()
    subjects: list[str] = meta.get("subjects", [])
    if not subjects:
        from config.subjects_whitelist_n100 import WHITELIST_N100

        subjects = list(WHITELIST_N100)

    if n_subjects is not None:
        subjects = subjects[:n_subjects]

    rows: list[dict[str, Any]] = []
    pheno: dict[str, dict] = {}

    if _PARTICIPANTS_TSV.exists():
        tsv = pd.read_csv(_PARTICIPANTS_TSV, sep="\t", dtype=str)
        tsv = tsv.set_index("participant_id")
        for sub in subjects:
            if sub in tsv.index:
                row = tsv.loc[sub]
                pheno[sub] = {
                    "sex": row.get("sex", "?"),
                    "age": _safe_float(row.get("age", "")),
                    "handedness": row.get("handedness", "?"),
                }

    for sub in subjects:
        p = pheno.get(sub, {})
        rows.append(
            {
                "participant_id": sub,
                "age": p.get("age", float("nan")),
                "sex": p.get("sex", "?"),
                "handedness": p.get("handedness", "?"),
                "has_EO": _has_conn(sub, "EO"),
                "has_EC": _has_conn(sub, "EC"),
            }
        )

    return pd.DataFrame(rows)


def _safe_float(val: str) -> float:
    try:
        return float(val)
    except (ValueError, TypeError):
        return float("nan")


def _has_conn(subject: str, cond: str, atlas: str = "aparc", metric: str = "plv", band: str = "theta") -> bool:
    fname = f"{subject}_atlas-{atlas}_cond-{cond}_metric-{metric}_band-{band}_per-epoch.npz"
    return (_CONN_DIR / fname).exists()


def list_subjects_with_connectivity(
    atlas: str = "aparc", metric: str = "plv", band: str = "theta", cond: str = "EC"
) -> list[str]:
    """Elenco soggetti con file connectivity per la combo data."""
    pattern = f"*_atlas-{atlas}_cond-{cond}_metric-{metric}_band-{band}_per-epoch.npz"
    files = sorted(_CONN_DIR.glob(pattern))
    return [f.name.split("_")[0] for f in files]


def load_connectivity_matrix(
    subject: str,
    atlas: str = "aparc",
    metric: str = "plv",
    band: str = "theta",
    cond: str = "EC",
) -> np.ndarray:
    """Carica matrice FC (n_roi × n_roi) per un soggetto.

    Raises FileNotFoundError se il file non esiste.
    """
    fname = f"{subject}_atlas-{atlas}_cond-{cond}_metric-{metric}_band-{band}_per-epoch.npz"
    path = _CONN_DIR / fname
    if not path.exists():
        raise FileNotFoundError(f"Connectivity file non trovato: {path}")
    data = np.load(path, allow_pickle=True)
    return data["fc_matrix"]


def load_feature_matrix(
    atlas: str,
    metric: str,
    band: str,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, list[str] | None]:
    """Carica X, y, groups, roi_names per la combo data."""
    from dashboard.utils.data_loader import load_feature_matrix as _load

    return _load(atlas, metric, band, dataset_id="ds005385")


def list_available_combos() -> list[dict[str, str]]:
    """Elenco combo (atlas, metric, band) con file feature disponibili."""
    from dashboard.utils.data_loader import list_available_combos as _list

    return _list(dataset_id="ds005385")


def load_ml_sex_results(n100: bool = True) -> dict[str, Any]:
    """Carica risultati ML sesso (N=100 se disponibili, altrimenti N=50)."""
    fname = "ml_sex_results_n100.json" if n100 else "ml_sex_results.json"
    path = _REPORTS_DIR / fname
    if not path.exists():
        path = _REPORTS_DIR / "ml_sex_results.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def load_ml_age_results(n100: bool = True) -> dict[str, Any]:
    """Carica risultati ML età (N=100 se disponibili, altrimenti N=50)."""
    fname = "ml_age_results_n100.json" if n100 else "ml_age_results.json"
    path = _REPORTS_DIR / fname
    if not path.exists():
        path = _REPORTS_DIR / "ml_age_results.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def load_bench_matrix() -> dict[str, Any]:
    """Carica BENCH_MATRIX_RESULTS.json (tutte le combo ML)."""
    path = _REPORTS_DIR / "BENCH_MATRIX_RESULTS.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text())
