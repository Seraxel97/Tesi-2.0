"""
STEP 2 — Matchingpennies EEG, source reconstruction su fsaverage template.

Eredita la config STEP 1 (preprocessing, già validato) e aggiunge i parametri
per BEM + forward + inverse. Niente parcellazione, niente connettività.
Smoke test della source reconstruction end-to-end.
"""

# ── Percorsi (repo-relativi + env-override fsaverage, riproducibilità F0) ────
import os as _os  # noqa: E402
from pathlib import Path as _Path  # noqa: E402

_REPO = _Path(__file__).resolve().parents[1]
bids_root = str(_REPO / "data" / "eeg_matchingpennies")
deriv_root = str(_REPO / "data" / "derivatives" / "mne-bids-pipeline")
subjects_dir = _os.environ.get(
    "TESI_SUBJECTS_DIR", str(_Path.home() / "mne_data" / "MNE-fsaverage-data")
)

# ── Soggetti / task ───────────────────────────────────────────────────────
# Soggetti da processare (qui il solo sub-05: smoke test end-to-end)
subjects = ["05"]
# Nome del task BIDS (dataset pubblico eeg_matchingpennies)
task = "matchingpennies"
# Tipi di canale usati: solo EEG
ch_types = ["eeg"]

# ── Montage: i canali (FC5, FC1, C3, CP5, CP1, FC2, FC6, C4, CP2, CP6) sono
# nomi 10-20 standard ma il BIDS dataset non include posizioni → applichiamo il
# template standard_1020 prima del forward computation. (Necessario per source recon.)
# Montage template 10-20: fornisce le posizioni 3D degli elettrodi
eeg_template_montage = "standard_1020"

# ── Esecuzione ────────────────────────────────────────────────────────────
# False = esecuzione batch, nessuna finestra interattiva
interactive = False

# ── Filtri / preprocessing base (eredita STEP 1) ──────────────────────────
# Passa-alto [Hz]: None = nessun filtro passa-alto in questo step
l_freq = None
# Passa-basso [Hz]: 100 Hz elimina il rumore ad alta frequenza
h_freq = 100
# Frequenza di rete [Hz] da rimuovere con Zapline (50 Hz in Europa)
zapline_fline = 50
# False = Zapline in singolo passaggio (senza iterazioni)
zapline_iter = False
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

# ── Decoding sensor (built-in) ────────────────────────────────────────────
# True = esegue il decoding sensor-level interno della pipeline
decode = True

# ── Group analysis ────────────────────────────────────────────────────────
# False = non interpola i canali cattivi nel grand average
interpolate_bads_grand_average = False

# ── Source reconstruction (NUOVI parametri STEP 2) ────────────────────────
# True = abilita BEM + forward + inverse
run_source_estimation = True
# MRI template al posto di MRI individuali (non disponibili)
use_template_mri = "fsaverage"

# Metodo inverso: dSPM (rumore-normalizzato, stabile con EEG)
inverse_method = "dSPM"
# Spaziatura delle sorgenti: oct6 (~4000 vertici per emisfero)
spacing = "oct6"
# Vincolo di orientamento dipoli: 0.2 = quasi normali alla corteccia (default MNE)
loose = 0.2
# Peso di profondita: 0.8 compensa il bias verso sorgenti superficiali (default MNE)
depth = 0.8

# Covarianza del rumore ad-hoc (nessuna baseline/empty-room disponibile)
noise_cov = "ad-hoc"

# Su cosa applicare l'inverso: solo gli evocati
inverse_targets = ["evoked"]
