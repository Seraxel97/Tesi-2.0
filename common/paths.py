"""Percorsi di progetto centralizzati — Tesi_2.0.

Tutti i path sono configurabili via env var con default relativi al repo.
Variabili d'ambiente:
  TESI_BIDS_ROOT     : root dataset BIDS (default: <repo>/data/eeg_matchingpennies)
  TESI_DERIV         : root derivatives mne-bids-pipeline (default: <repo>/data/derivatives/...)
  TESI_SUBJECTS_DIR  : directory fsaverage (default: ~/mne_data/MNE-fsaverage-data)

Posizione nella pipeline: infrastruttura trasversale agli STEP 1-7 (non appartiene a un singolo step).
"""

from __future__ import annotations

import os
from pathlib import Path

_REPO_ROOT = Path(__file__).parent.parent


def _validate_env_path(env_var: str, default: Path, must_exist: bool = True) -> Path:
    """Validate environment variable path for security.

    Parameters
    ----------
    env_var : str
        Environment variable name.
    default : Path
        Default path if env_var not set.
    must_exist : bool, optional
        If True, path must exist (default: True).

    Returns
    -------
    Path
        Validated absolute path.

    Raises
    ------
    ValueError
        If path is not absolute.
    FileNotFoundError
        If must_exist=True and path does not exist.
    """
    raw = os.environ.get(env_var, str(default))
    p = Path(raw).expanduser()

    if not p.is_absolute():
        raise ValueError(f"{env_var} must be absolute path, got: {p}")

    p = p.resolve()
    if must_exist and not p.exists():
        raise FileNotFoundError(f"{env_var} not found: {p}")

    return p


_DEFAULTS = {
    "BIDS_ROOT": ("TESI_BIDS_ROOT", _REPO_ROOT / "data" / "eeg_matchingpennies"),
    "DERIV": ("TESI_DERIV", _REPO_ROOT / "data" / "derivatives" / "mne-bids-pipeline"),
    "SUBJECTS_DIR": ("TESI_SUBJECTS_DIR", Path.home() / "mne_data" / "MNE-fsaverage-data"),
}


def __getattr__(name: str) -> Path:
    """Risolve BIDS_ROOT/DERIV/SUBJECTS_DIR al primo accesso (lazy).

    Il controllo di esistenza avviene qui e non all'import, cosi' un clone
    senza data/ resta importabile; FileNotFoundError solo se il path serve.
    """
    if name in _DEFAULTS:
        env_var, default = _DEFAULTS[name]
        return _validate_env_path(env_var, default, must_exist=True)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
