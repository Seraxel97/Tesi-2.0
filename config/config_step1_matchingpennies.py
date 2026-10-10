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
# Soggetti da processare (qui il solo sub-05: smoke test end-to-end)
subjects = ["05"]
# Nome del task BIDS (dataset pubblico eeg_matchingpennies)
task = "matchingpennies"
# Tipi di canale usati: solo EEG
ch_types = ["eeg"]

# ── Esecuzione ────────────────────────────────────────────────────────────
# False = esecuzione batch, nessuna finestra interattiva
interactive = False

# ── Filtri / preprocessing base ───────────────────────────────────────────
# Passa-alto [Hz]: None = nessun filtro passa-alto in questo step
l_freq = None
# Passa-basso [Hz]: 100 Hz elimina il rumore ad alta frequenza
h_freq = 100
# Frequenza di rete [Hz] da rimuovere con Zapline (50 Hz in Europa)
zapline_fline = 50
# False = Zapline in singolo passaggio (senza iterazioni)
zapline_iter = False

# Crop runs ai primi 10 minuti (run originali ≈ 31 min) per velocità in test STEP 1
# (inizio, fine) in secondi: tiene solo i primi 600 s
crop_runs = (0, 600)

# ── Reject epochs ─────────────────────────────────────────────────────────
# Soglia peak-to-peak [V] per scartare epoche: 150 uV, valore standard EEG
reject = {"eeg": 150e-6}

# ── Condizioni / contrasti ────────────────────────────────────────────────
# Condizioni sperimentali (alzata mano sinistra / destra)
conditions = ["raised-left", "raised-right"]
# Contrasto da analizzare: sinistra vs destra
contrasts = [("raised-left", "raised-right")]

# ── Decoding (built-in mne-bids-pipeline, NON il nostro ML) ──────────────
# True = esegue il decoding sensor-level interno della pipeline
decode = True

# ── Group analysis ────────────────────────────────────────────────────────
# False = non interpola i canali cattivi nel grand average
interpolate_bads_grand_average = False
