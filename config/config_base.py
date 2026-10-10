"""
Common configuration for all STEP 1+ processing.

Extracted from config_step1/step2 to avoid duplication.
Contains baseline preprocessing, subject/task, filtering parameters.
Step-specific configs import from here and override as needed.
"""

from common.paths import BIDS_ROOT, DERIV

# ── Percorsi ──────────────────────────────────────────────────────────────
# Radice del dataset BIDS di input (da common.paths)
bids_root = BIDS_ROOT
# Cartella dei derivati prodotti da mne-bids-pipeline
deriv_root = DERIV

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

# Crop runs ai primi 10 minuti (run originali ≈ 31 min) per velocità in test
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

# ── Montage standard EEG 10-20 (per source reconstruction) ─────────────────
# Montage template 10-20: fornisce le posizioni 3D degli elettrodi
eeg_template_montage = "standard_1020"

# ── Group analysis ────────────────────────────────────────────────────────
# False = non interpola i canali cattivi nel grand average
interpolate_bads_grand_average = False
