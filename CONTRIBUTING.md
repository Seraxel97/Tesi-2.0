# Contributing — Tesi_2.0

Guida per chi vuole eseguire, modificare o estendere il codice.

## Setup

```bash
conda env create -f environment.yml && conda activate tesi_baseline
make install        # requirements.txt + requirements-dev.txt (pytest, ruff, ...)
make data-demo      # scarica il dataset demo e fsaverage (necessari a una parte dei test)
```

## Test e stile

```bash
make test           # pytest; i test che richiedono data/ vengono saltati se mancano
make lint           # ruff check + ruff format --check
make format         # applica ruff (regole E, F, W, I, UP; riga max 100)
pre-commit install  # hook ruff a ogni commit
```

Regole:

- Ogni funzione e modulo ha una docstring in italiano (scopo, Args, Returns).
- Commenti in italiano sui passaggi non ovvi (formule, shape degli array, scelte di metodo).
- Nessuna modifica che alteri i risultati scientifici senza rieseguire gli esperimenti
  interessati e aggiornare i report in `reports/`.
- Commit atomici, messaggio nel formato `tipo(ambito): descrizione`.

## Struttura dei moduli

Una cartella per step della pipeline (vedi README §4). Gli script in `scripts/` sono
gli entrypoint per i dataset scientifici; la logica riusabile sta nei package.

## Come estendere la pipeline

- **Nuova metrica di connettività**: aggiungere il nome al tipo `Metric` in
  `connectivity/fc_dispatcher.py` e gestirlo in `compute_fc`; aggiungere un test in
  `tests/test_fc_dispatcher.py`.
- **Nuovo atlante**: aggiungere la voce a `ATLAS_TO_PARC` e al tipo `AtlasName` in
  `parcellation/extract_label_tc.py`; test in `tests/test_parcellation.py`.
- **Nuovo classificatore**: registrarlo in `ml_training/ml_dispatcher.py` (`Algorithm`,
  `_make_pipeline`); test in `tests/test_ml_dispatcher.py`.
- **Nuovo dataset**: aggiungere configurazione e mapping delle etichette in `config/`
  (vedi `config/dataset_lemon.py` e `config/labels_*.py`) e una whitelist soggetti.

## Attenzione: i risultati si sovrascrivono

Alcuni script scrivono in `data/features/ds005385/` (`y.npy`, `groups.npy`, `X_*.npz`) e
rigenerano file in `reports/` (es. `run_pipeline_n15.py`, `compute_features.py`,
`make bench`). Prima di rieseguirli su dati reali fare una copia dei risultati esistenti.
