# Tesi_2.0 — Pipeline EEG source-space: connettività funzionale e ML

Estensione modulare di `mne-bids-pipeline` che, a partire da registrazioni EEG in formato
BIDS, ricostruisce l'attività alla sorgente, la parcellizza con atlanti standard, calcola
la connettività funzionale (FC) e addestra classificatori con validazione per-soggetto e
permutation test. Progetto di tesi magistrale.

**Per il relatore**: [docs/GUIDA_PROFESSORE.md](docs/GUIDA_PROFESSORE.md) (avvio in 1 minuto) e
[reports/RISULTATI_E_LIMITI.md](reports/RISULTATI_E_LIMITI.md)
(risultati e limiti, cosa regge e cosa no).

## Indice

1. [Pipeline](#1-pipeline)
2. [Installazione](#2-installazione)
3. [Uso rapido](#3-uso-rapido)
4. [Struttura del repository](#4-struttura-del-repository)
5. [Dataset](#5-dataset)
6. [Test e qualità del codice](#6-test-e-qualità-del-codice)
7. [Dashboard interattiva](#7-dashboard-interattiva)
8. [Documentazione e riferimenti](#8-documentazione-e-riferimenti)

---

## 1. Pipeline

```
STEP 1  preprocessing            (mne-bids-pipeline)            -> *_clean_epo.fif
STEP 2  ricostruzione sorgente   (dSPM, fsaverage)              -> *-inv.fif, *.stc
STEP 3  parcellazione            (aparc / destrieux / schaefer) -> serie temporali per ROI
STEP 4  connettività spettrale   (wPLI, PLV, coh, imCoh, ...)   -> matrici FC per banda
STEP 5  estrazione feature       (mne-features + FC + grafo)    -> matrice X
STEP 6  classificazione ML       (5 algoritmi, GroupKFold)      -> metriche + CI
STEP 7  verifica end-to-end      (dataset demo)                 -> report
```

Diagramma dettagliato con input/output di ogni step: [docs/PIPELINE_OVERVIEW.md](docs/PIPELINE_OVERVIEW.md).

## 2. Installazione

Richiede Python 3.13.

```bash
conda env create -f environment.yml   # crea l'ambiente `tesi_baseline`
conda activate tesi_baseline
make install                          # dipendenze + strumenti di sviluppo
make data-demo                        # scarica dataset demo e fsaverage (necessari a demo e a parte dei test)
python -c "import mne, mne_bids, mne_connectivity, mne_features, sklearn; print('ok')"
```

Le versioni delle librerie sono fissate in `requirements.txt` (mne 1.11.0,
mne-bids-pipeline 1.10.1, scikit-learn 1.8.0, ...). Per la dashboard servono anche i
pacchetti in `dashboard/requirements.txt`.

## 3. Uso rapido

I comandi comuni sono raccolti nel `Makefile` (`make help` per l'elenco):

```bash
make run-step1    # STEP 1 sul dataset demo (sub-05)
make run-step2    # STEP 2: sorgente + inverso
python -m pipeline_mne_bids.run_e2e_matchingpennies   # STEP 3-6 in sequenza sul demo
make test         # suite di test (i test che richiedono data/ vengono saltati se mancano)
make lint         # ruff check + format --check
```

Note importanti:

- Gli script che importano pacchetti del repository vanno lanciati come modulo
  (`python -m ...`) dalla radice, altrimenti si ottiene `ModuleNotFoundError`.
- Con `noise_cov="ad-hoc"`, `mne-bids-pipeline==1.10.1` non scrive il file
  `<sub>_proc-adhoc_rank.json` richiesto dallo step `source` (bug upstream). Il comando
  `python -m cli.main step2` applica il workaround in automatico
  (`source_reconstruction/adhoc_rank.py`).
- Su server o sessioni senza display (o se `make run-step2` si interrompe con `X Error ... BadWindow`) eseguire con `DISPLAY= PYVISTA_OFF_SCREEN=true make run-step2`: il rendering 3D dei report va fatto offscreen.
- Il CLI unificato espone gli stessi step: `python -m cli.main --help`.

Esecuzione dei singoli step sul dataset demo:

```bash
mne_bids_pipeline --config config/config_step1_matchingpennies.py --steps preprocessing
python -m cli.main step2
python -m cli.main bench --output reports/BENCH_MATRIX_RESULTS.json   # matrice di benchmark
```

**Attenzione**: molti script sovrascrivono i risultati in `data/features/` e `reports/`; fare una copia prima di rieseguirli (vedi CONTRIBUTING.md).

Gli esperimenti sul dataset scientifico si lanciano con gli script in `scripts/`
(es. `scripts/run_pipeline_ds004504.py`, `scripts/run_ml_age_sex_n179.py`); ogni script
riporta nel docstring iniziale scopo, input, output ed esempio di uso.

## 4. Struttura del repository

```
Tesi_2.0/
|-- pipeline_mne_bids/       STEP 1 e orchestratore E2E (run_e2e_matchingpennies.py)
|-- source_reconstruction/   STEP 2: forward, inverso, STC, workaround rank ad-hoc
|-- parcellation/            STEP 3: serie temporali per ROI (4 atlanti), neuromaps
|-- connectivity/            STEP 4: dispatcher delle metriche FC (mne-connectivity)
|-- features/                STEP 5: feature (mne-features, FC, teoria dei grafi, FOOOF)
|-- ml_training/             STEP 6: classificatori, GroupKFold, permutation test, età/sesso
|-- analysis/                statistica di supporto (CI, effect size, valutazione cross-dataset)
|-- common/                  utilità condivise (logger, run id, stato, helper)
|-- config/                  configurazioni per step, dataset, whitelist soggetti, etichette
|-- cli/                     CLI unificato (`python -m cli.main`)
|-- scripts/                 pipeline sui dataset scientifici, validazioni, figure
|-- dashboard/               dashboard Streamlit (app.py, pages/, components/, utils/)
|-- tests/                   suite pytest (unitari, integrazione, smoke)
|-- reports/                 risultati e log (indice in reports/INDICE.md)
|-- docs/                    documentazione (guida relatore, overview, API HTML)
|-- data/                    dataset e derivati (non versionati, vedi §5)
`-- .github/workflows/       CI: lint, test, smoke EEG
```

## 5. Dataset

| Dataset | Ruolo | Note |
|---|---|---|
| `ds005385` (Dortmund Vital Study) | **scientifico principale**, N=179 | task RestingState, EO/EC; risultati sesso/età |
| LEMON | validazione esterna su coorte sana | il segnale del sesso non generalizza |
| `ds004504` | fenotipo clinico (config etichette) | vedi `config/labels_phenotype_ds004504.py` |
| `eeg_matchingpennies` | **demo tecnica** (7 soggetti, 61 canali) | usata da test e smoke E2E |

I dati (circa 50 GB tra raw e derivati) **non sono nel repository** (`.gitignore`): il dataset demo si scarica con `make data-demo`; i dataset scientifici vanno scaricati da OpenNeuro (vedi `scripts/setup_scientific_dataset.py`). Le
whitelist dei soggetti usati sono in `config/subjects_whitelist_*.py`. La struttura del
dataset principale è descritta in `reports/DS005385_STRUCTURE.md`.

## 6. Test e qualità del codice

```bash
make test                                 # suite completa
pytest tests/test_e2e_smoke_minimal.py    # smoke sintetico, senza dataset
make lint                                 # ruff (regole E, F, W, I, UP; riga max 100)
pre-commit install                        # hook ruff a ogni commit
```

I test che richiedono `data/` vengono saltati se mancano; per eseguirli tutti serve `make data-demo`.
La CI (`.github/workflows/`) esegue lint, test e uno smoke EEG.

## 7. Dashboard interattiva

La dashboard **legge risultati già calcolati** (non esegue gli step 1-4): servono le feature in
`data/features/` e i risultati in `data/results/`, che non sono nel repository. Vengono
consegnate a parte in `Tesi_2.0_dati_dashboard.zip` (174 MB): decomprimerlo nella radice del
progetto (`unzip Tesi_2.0_dati_dashboard.zip`).

```bash
pip install -r dashboard/requirements.txt
streamlit run dashboard/app.py --server.port 8501
```

Sei pagine (coorte, preprocessing, sorgente/parcellazione, grafo di connettività,
predizioni ML, cross-dataset). Dettagli in [dashboard/README.md](dashboard/README.md).

## 8. Documentazione e riferimenti

- Guida per il relatore: [docs/GUIDA_PROFESSORE.md](docs/GUIDA_PROFESSORE.md)
- Panoramica pipeline: [docs/PIPELINE_OVERVIEW.md](docs/PIPELINE_OVERVIEW.md)
- Indice dei report: [reports/INDICE.md](reports/INDICE.md)
- Contribuire: [CONTRIBUTING.md](CONTRIBUTING.md)
- API (HTML generato con pdoc): `docs/api/index.html`

| Libreria | Documentazione |
|---|---|
| MNE-Python | https://mne.tools/stable/ |
| mne-bids-pipeline | https://mne-bids-pipeline.readthedocs.io/ |
| mne-connectivity | https://mne.tools/mne-connectivity/ |
| mne-features | https://mne.tools/mne-features/ |
| neuromaps | https://netneurolab.github.io/neuromaps/ |
| scikit-learn | https://scikit-learn.org/stable/ |

**Parole chiave**: eeg, source-reconstruction, functional-connectivity, machine-learning,
mne-python, mne-bids-pipeline, wpli, plv, group-kfold, permutation-testing, schaefer-atlas, dspm.
