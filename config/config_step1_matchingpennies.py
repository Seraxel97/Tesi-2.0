"""
STEP 1 — Matchingpennies EEG, preprocessing base.

Config minimale per verifica end-to-end della pipeline mne-bids-pipeline.
Adattata da: mne_bids_pipeline/tests/configs/config_eeg_matchingpennies.py
(repo ufficiale GitHub mne-tools/mne-bids-pipeline).

NON modificare per source/connectivity/ML: questi step appartengono a STEP 2+.
"""

# ── Percorsi (repo-relativi, riproducibilità F0) ────────────────────────────
from pathlib import Path as _Path  # noqa: E402

_REPO = _Path(__file__).resolve().parents[1]
bids_root = str(_REPO / "data" / "eeg_matchingpennies")
deriv_root = str(_REPO / "data" / "derivatives" / "mne-bids-pipeline")

# ── Soggetti / task ───────────────────────────────────────────────────────
subjects = ["05"]
task = "matchingpennies"
ch_types = ["eeg"]

# ── Esecuzione ────────────────────────────────────────────────────────────
interactive = False

# ── Filtri / preprocessing base ───────────────────────────────────────────
l_freq = None
h_freq = 100
zapline_fline = 50
zapline_iter = False

# Crop runs ai primi 10 minuti (run originali ≈ 31 min) per velocità in test STEP 1
crop_runs = (0, 600)

# ── Reject epochs ─────────────────────────────────────────────────────────
reject = {"eeg": 150e-6}

# ── Condizioni / contrasti ────────────────────────────────────────────────
conditions = ["raised-left", "raised-right"]
contrasts = [("raised-left", "raised-right")]

# ── Decoding (built-in mne-bids-pipeline, NON il nostro ML) ──────────────
decode = True

# ── Group analysis ────────────────────────────────────────────────────────
interpolate_bads_grand_average = False
