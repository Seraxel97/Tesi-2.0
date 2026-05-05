---
type: manuscript
status: draft
section: appendix
project: Tesi_2.0
last_review: 2026-05-01
sprint: S-32
tags: [eeg, source-fc, ml]
version: v1
language: italiano
target_journal: Journal of Neural Engineering
date: 2026-05-01
---
# Appendice A — Configurazione della pipeline e parametri di riproducibilita'

Questa appendice documenta la configurazione completa adottata per tutti gli esperimenti
descritti nel presente lavoro, con l'obiettivo di garantire la riproducibilita' dei
risultati. I file di configurazione elencati sono distribuiti insieme al codice sorgente
e non richiedono modifiche per replicare l'analisi sul dataset *matching pennies*.

---

## A.1 Ambiente software

### A.1.1 Interprete e ambiente

| Parametro | Valore |
|-----------|--------|
| Sistema operativo | Linux (Ubuntu 22.04 / 24.04) |
| Gestore environment | conda (base env) |
| Versione Python | 3.13.12 |
| Backend numerico | CPU-only; GPU RTX 4060 presente ma non utilizzata (MNE e' CPU-bound) |

### A.1.2 Dipendenze principali

File `requirements.txt` filtrato alle librerie scientifiche rilevanti
(generato con `pip freeze` e fissato alla data 2026-05-01):

```text
mne==1.11.0
mne-bids==0.18.0
mne-bids-pipeline==1.10.1
mne-connectivity==0.8
mne-features==0.3.2
mne-icalabel==0.8.1
neuromaps==0.0.5
nibabel==5.4.2
nilearn==0.13.1
scikit-learn==1.8.0
numpy==2.4.4
scipy==1.17.1
pandas==3.0.2
matplotlib==3.10.8
joblib==1.5.3
pyvista==0.47.3
meegkit==0.1.9
python-picard==0.8.2
```

Nessun pacchetto aggiuntivo e' necessario oltre a quelli elencati. Il file completo
`requirements.txt` e' incluso nella radice del repository.

---

## A.2 Configurazione STEP 1 — Preprocessing

La configurazione del preprocessing e' suddivisa in due livelli:

- `config/config_base.py` — parametri condivisi tra tutti gli step (percorsi, filtri,
  soggetti, condizioni). E' la sorgente di verita' per i parametri di base.
- `config/config_step1_matchingpennies.py` — eredita `config_base.py` tramite
  `from config.config_base import *`; per il dataset *matching pennies* non aggiunge
  override (la configurazione base e' sufficiente).

### `config/config_base.py`

```python
"""
Common configuration for all STEP 1+ processing.

Extracted from config_step1/step2 to avoid duplication.
Contains baseline preprocessing, subject/task, filtering parameters.
Step-specific configs import from here and override as needed.
"""

from common.paths import BIDS_ROOT, DERIV

# ── Percorsi ──────────────────────────────────────────────────────────────
bids_root = BIDS_ROOT
deriv_root = DERIV

# ── Soggetti / task ───────────────────────────────────────────────────────
subjects = ["05"]
task = "matchingpennies"
ch_types = ["eeg"]

# ── Esecuzione ────────────────────────────────────────────────────────────
interactive = False

# ── Filtri / preprocessing base ───────────────────────────────────────────
l_freq = None       # nessun filtro passa-alto (preserva componenti lente)
h_freq = 100        # filtro passa-basso 100 Hz
zapline_fline = 50  # rimozione rumore rete (ZapLine, 50 Hz)
zapline_iter = False

# Crop runs ai primi 10 minuti (run originali ~31 min)
crop_runs = (0, 600)

# ── Reject epochs ─────────────────────────────────────────────────────────
reject = {"eeg": 150e-6}   # 150 uV peak-to-peak

# ── Condizioni / contrasti ────────────────────────────────────────────────
conditions = ["raised-left", "raised-right"]
contrasts = [("raised-left", "raised-right")]

# ── Decoding (mne-bids-pipeline built-in, NON il nostro ML) ──────────────
decode = True

# ── Montage standard EEG 10-20 (per source reconstruction) ───────────────
eeg_template_montage = "standard_1020"

# ── Group analysis ────────────────────────────────────────────────────────
interpolate_bads_grand_average = False
```

### `config/config_step1_matchingpennies.py`

```python
"""
STEP 1 — Matchingpennies EEG, preprocessing base.

Inherits common settings from config_base.py.
Config minimale per verifica end-to-end della pipeline mne-bids-pipeline.
NON modificare per source/connectivity/ML: questi step appartengono a STEP 2+.
"""

from config.config_base import *  # noqa: F401, F403
```

---

## A.3 Configurazione STEP 2 — Source reconstruction

### `config/config_step2_source_matchingpennies.py`

```python
"""
STEP 2 — Matchingpennies EEG, source reconstruction su fsaverage template.

Inherits common settings from config_base.py and extends with source-specific
parameters (BEM + forward + inverse). Niente parcellazione, niente connettivita'.
Smoke test della source reconstruction end-to-end.
"""

from config.config_base import *  # noqa: F401, F403

# ── Percorso MRI template (source reconstruction) ─────────────────────────
subjects_dir = "/home/seraxel/mne_data/MNE-fsaverage-data"

# ── Source reconstruction (STEP 2 parametri specifici) ────────────────────
run_source_estimation = True
use_template_mri = "fsaverage"

inverse_method = "dSPM"   # Dynamic Statistical Parametric Mapping
spacing = "oct6"          # ~4098 sorgenti per emisfero
loose = 0.2               # orientamento libero parziale (0=fixed, 1=free)
depth = 0.8               # depth weighting exponent

noise_cov = "ad-hoc"      # covarianza rumore stimata analiticamente

inverse_targets = ["evoked"]   # applica inverse agli averaged evoked
```

**Parametri chiave e motivazione:**

| Parametro | Valore | Motivazione |
|-----------|--------|-------------|
| `inverse_method` | `"dSPM"` | Default mne-bids-pipeline; unita' z-score, robusto a variabilita' SNR |
| `spacing` | `"oct6"` | Bilancio risoluzione spaziale / costo computazionale |
| `loose` | `0.2` | Orientamento semi-libero: standard per EEG su superficie corticale |
| `depth` | `0.8` | Depth weighting: compensa bias verso sorgenti superficiali |
| `noise_cov` | `"ad-hoc"` | *Matching pennies* non ha baseline pre-stimolo sufficientemente lungo |
| `use_template_mri` | `"fsaverage"` | Nessuna MRI individuale disponibile nel dataset |

Il comando CLI completo per STEP 2:

```bash
python source_reconstruction/finalize_inverse.py \
    --subject 05 --task matchingpennies \
    --method dSPM --loose 0.2 --depth 0.8 --lambda2 0.1111
```

---

## A.4 Seeds e determinismo

Tutti i componenti stocastici della pipeline usano il seed fisso `42` per garantire
la riproducibilita' bit-for-bit dei risultati:

| Componente | Parametro | Valore | Modulo |
|------------|-----------|--------|--------|
| Classificatori sklearn | `random_state` | 42 | `ml_training/ml_dispatcher.py` |
| StratifiedKFold (smoke) | `random_state` | 42 | `ml_training/ml_dispatcher.py` |
| Permutation test | `rng = np.random.default_rng(42)` | 42 | `ml_training/permutation.py` |
| Benchmark matrix | `rng = np.random.default_rng(42)` | 42 | `pipeline_mne_bids/bench/matrix.py` |

Non vengono usati seed globali di numpy o random a livello di processo, per evitare
interferenze con librerie MNE che gestiscono internamente il proprio stato RNG. Ogni
componente e' inizializzato con il seed locale sopra indicato.

---

## A.5 Convenzioni di path e variabili d'ambiente

I percorsi di progetto sono centralizzati in `common/paths.py` e configurabili tramite
variabili d'ambiente (introdotto da sprint DR-SIMPL-path-helpers, DR-REVIEW-paths-env):

| Variabile | Default | Descrizione |
|-----------|---------|-------------|
| `TESI_BIDS_ROOT` | `<repo>/data/eeg_matchingpennies` | Root del dataset BIDS |
| `TESI_DERIV` | `<repo>/data/derivatives/mne-bids-pipeline` | Root derivatives |
| `TESI_SUBJECTS_DIR` | `~/mne_data/MNE-fsaverage-data` | Directory fsaverage FreeSurfer |

Il valore di default per `TESI_SUBJECTS_DIR` assume che `fsaverage` sia stato scaricato
tramite `mne.datasets.fetch_fsaverage()` nel path standard di MNE
(`~/mne_data/MNE-fsaverage-data`). Il download e' necessario solo alla prima esecuzione
e richiede circa 1.5 GB di spazio disco.

Per eseguire la pipeline con path personalizzati:

```bash
export TESI_BIDS_ROOT=/data/miei_dati/eeg_dataset
export TESI_DERIV=/data/miei_dati/derivatives
export TESI_SUBJECTS_DIR=/opt/freesurfer/subjects
python pipeline_mne_bids/run_e2e_matchingpennies.py
```
