# Tesi_2.0 — EEG Source-Level Functional Connectivity for Cognitive Task Classification

Estensione modulare di `mne-bids-pipeline` con parcellazione atlastica, connettivita funzionale
e classificazione ML. Progetto di tesi magistrale.

Stato corrente: vedi [PROGRESS.md](PROGRESS.md).

---

## Overview

Pipeline in 7 step sequenziali che parte da dati EEG BIDS e produce classificatori ML
con valutazione LOSO (Leave-One-Subject-Out) e permutation testing:

```
STEP 1  → preprocessing (mne-bids-pipeline)
STEP 2  → source reconstruction (dSPM, fsaverage)
STEP 3  → parcellazione (aparc / destrieux / schaefer100 / schaefer200)
STEP 4  → connettivita spettrale (wpli, plv, coh, imcoh, ciplv, pli, wpli2_debiased)
STEP 5  → feature extraction (mne-features + FC flatten)
STEP 6  → ML classification (LogReg / SVM / MLP / RF / GB, GroupKFold)
STEP 7  → verifica E2E + risultati finali
```

Diagramma dettagliato: [docs/PIPELINE_OVERVIEW.md](docs/PIPELINE_OVERVIEW.md).

---

## Stato

| Step | Stato |
|------|-------|
| STEP 1 — Preprocessing | DONE (2026-04-28) |
| STEP 2 — Source reconstruction | DONE (2026-05-01) |
| STEP 3 — Parcellazione | DONE (sprint S-01, 2026-05-01) |
| STEP 4 — Connettivita | DONE (sprint S-02, 2026-05-01) |
| STEP 5 — Features | DONE (sprint S-03, 2026-05-01) |
| STEP 6 — ML | DONE (sprint S-04, 2026-05-01) |
| STEP 7 — E2E | DONE (sprint S-05, 2026-05-01) |

Log dettagliato: [PROGRESS.md](PROGRESS.md).

---

## Developer setup

### Pre-commit hooks

Il repository usa [pre-commit](https://pre-commit.com/) per garantire qualità del codice ad ogni commit:

```bash
pip install pre-commit
pre-commit install          # installa hook pre-commit (ruff check + format)
pre-commit install --hook-type pre-push   # installa hook pre-push (pytest smoke)
```

I hook configurati in `.pre-commit-config.yaml`:

| Hook | Trigger | Azione |
|------|---------|--------|
| `ruff` | pre-commit | Linting + autofix (`--fix`) |
| `ruff-format` | pre-commit | Formattazione stile |
| `pytest-fast` | pre-push | Smoke test `tests/test_smoke.py` |

Esecuzione manuale su tutti i file:

```bash
pre-commit run --all-files
```

### Installazione

#### Prerequisiti

- conda env `base`, Python 3.13.12
- Nessun pacchetto aggiuntivo da installare: tutto e' gia' presente nell'env.

Verifica:

```bash
python -c "import mne, mne_bids, mne_connectivity, mne_features, sklearn; print('ok')"
```

Versioni attese:

| Pacchetto | Versione |
|-----------|----------|
| mne | 1.11.0 |
| mne-bids | 0.18.0 |
| mne-bids-pipeline | 1.10.1 |
| mne-connectivity | 0.8 |
| mne-features | 0.3.2 |
| scikit-learn | 1.8.0 |
| neuromaps | 0.0.5 |

---

## Quick start

### STEP 1 — Preprocessing (matchingpennies sub-05)

```bash
mne_bids_pipeline --config config/config_step1_matchingpennies.py --steps preprocessing
```

Output: `data/derivatives/mne-bids-pipeline/sub-05/eeg/`

### STEP 2 — Source reconstruction

```bash
python source_reconstruction/finalize_inverse.py --subject 05 --task matchingpennies
```

Output: `data/derivatives/mne-bids-pipeline/sub-05/eeg/*-stc-*.stc`

I passi successivi (STEP 3-7) vengono eseguiti tramite i moduli in
`parcellation/`, `connectivity/`, `features/`, `ml_training/`. Vedere
[docs/PIPELINE_OVERVIEW.md](docs/PIPELINE_OVERVIEW.md) per i comandi specifici.

---

## Struttura cartelle

```
Tesi_2.0/
|-- config/                 configurazioni per ogni step (override mne-bids-pipeline)
|-- connectivity/           fc_dispatcher.py: 7 metriche spettrali via mne-connectivity
|-- dashboard/              plot_top_features.py: visualizzazioni figure paper (PNG headless)
|-- data/                   dataset BIDS + derivatives (NON versionato, .gitignore)
|   |-- eeg_matchingpennies/  dataset test tecnico (716 MB)
|   `-- derivatives/          output pipeline (epochs, STC, report HTML)
|-- docs/                   documentazione developer-facing
|-- features/               dispatcher.py: mne-features + FC flatten -> vettore X
|-- ml_training/            ml_dispatcher.py: 5 algoritmi + GroupKFold + permutation
|-- parcellation/           extract_label_tc.py: 4 atlasi + neuromaps_helper.py
|-- pipeline_mne_bids/      run_e2e_matchingpennies.py: orchestratore step 1-6
|-- reports/                log esecuzione, risultati benchmark, figure
|-- source_reconstruction/  finalize_inverse.py: forward + inverse + STC
`-- tests/                  pytest suite (test unitari + smoke)
```

---

## Riferimenti

- Vault Obsidian: `[[070_THESIS/MNE_PROFESSOR_LINKS]]` (5 link professorali canonici).
- MNE-Python docs: https://mne.tools/stable/
- mne-bids-pipeline docs: https://mne-bids-pipeline.readthedocs.io/
- mne-connectivity: https://mne.tools/mne-connectivity/
- mne-features: https://mne.tools/mne-features/
- neuromaps: https://netneurolab.github.io/neuromaps/

Progetto sviluppato come **estensione modulare** di mne-bids-pipeline, non come pipeline standalone.
Ogni step usa esclusivamente le librerie del vincolo 2 (PROGRESS.md §Vincoli OBBLIGATORI).
