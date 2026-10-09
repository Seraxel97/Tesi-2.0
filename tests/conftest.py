"""Fixtures condivise per test suite Tesi_2.0.

Puntano ai dati reali sub-05 matchingpennies (read-only).
I test che richiedono file reali vengono skippati se il file non esiste.
"""

import os
from pathlib import Path

import pytest

pytest_plugins = ["tests.fixtures.synthetic"]


# Path repo-relativi + env-override (riproducibilità F0): i test girano su qualsiasi macchina.
_REPO = Path(__file__).resolve().parents[1]
_BIDS_ROOT = Path(
    os.environ.get("TESI_BIDS_ROOT", "").strip() or _REPO / "data" / "eeg_matchingpennies"
)
_DERIV = Path(
    os.environ.get("TESI_DERIV", "").strip() or _REPO / "data" / "derivatives" / "mne-bids-pipeline"
)
_SUB05 = _DERIV / "sub-05" / "eeg"
_SUBJECTS_DIR = Path(
    os.environ.get("TESI_SUBJECTS_DIR", "").strip()
    or Path.home() / "mne_data" / "MNE-fsaverage-data"
)


@pytest.fixture(scope="session")
def bids_root() -> Path:
    if not _BIDS_ROOT.exists():
        pytest.skip(f"BIDS root non trovato: {_BIDS_ROOT}")
    return _BIDS_ROOT


@pytest.fixture(scope="session")
def deriv_root() -> Path:
    if not _DERIV.exists():
        pytest.skip(f"Derivati non trovati: {_DERIV}")
    return _DERIV


@pytest.fixture(scope="session")
def subjects_dir() -> Path:
    if not _SUBJECTS_DIR.exists():
        pytest.skip(f"subjects_dir non trovato: {_SUBJECTS_DIR}")
    return _SUBJECTS_DIR


@pytest.fixture(scope="session")
def sub_id() -> str:
    return "05"


@pytest.fixture(scope="session")
def task_name() -> str:
    return "matchingpennies"


@pytest.fixture(scope="session")
def stc_path() -> Path:
    """Stem STC sub-05 (senza -lh/-rh suffix), primo match via glob."""
    matches = sorted(_SUB05.glob("*_inv-dSPM-lh.stc"))
    if not matches:
        pytest.skip(f"Nessun STC trovato in: {_SUB05}")
    lh_file = matches[0]
    return Path(str(lh_file).removesuffix("-lh.stc"))


@pytest.fixture(scope="session")
def fwd_path() -> Path:
    p = _SUB05 / "sub-05_fwd.fif"
    if not p.exists():
        pytest.skip(f"Forward non trovato: {p}")
    return p


@pytest.fixture(scope="session")
def inv_path() -> Path:
    p = _SUB05 / "sub-05_inv.fif"
    if not p.exists():
        pytest.skip(f"Inverse non trovato: {p}")
    return p


@pytest.fixture(scope="session")
def evoked_path() -> Path:
    p = _SUB05 / "sub-05_task-matchingpennies_ave.fif"
    if not p.exists():
        pytest.skip(f"Evoked non trovato: {p}")
    return p


@pytest.fixture(scope="session")
def epochs_path() -> Path:
    p = _SUB05 / "sub-05_task-matchingpennies_proc-clean_epo.fif"
    if not p.exists():
        pytest.skip(f"Epochs non trovato: {p}")
    return p


# ── Marker needs_data: skip se mancano i dati reali (data/ e' gitignored) ────
_NEEDS_DATA_SENTINELS = (
    _REPO / "data" / "features" / "ds005385" / "y.npy",
    _REPO / "data" / "raw" / "ds005385" / "participants.tsv",
)


def pytest_collection_modifyitems(config, items):
    missing = [str(p.relative_to(_REPO)) for p in _NEEDS_DATA_SENTINELS if not p.exists()]
    if not missing:
        return
    skip = pytest.mark.skip(reason=f"richiede data/ (mancano: {', '.join(missing)})")
    for item in items:
        if "needs_data" in item.keywords:
            item.add_marker(skip)
