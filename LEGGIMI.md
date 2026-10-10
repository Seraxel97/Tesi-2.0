# Tesi_2.0 — da dove iniziare

Codice e documentazione. I dati già calcolati per la dashboard NON sono nel repository: arrivano a parte in `Tesi_2.0_dati_dashboard.zip` (da decomprimere nella radice del progetto con `unzip`).
Richiede Python 3.13 (consigliato conda).

## A. Vedere i risultati (2 minuti, richiede lo zip dei dati)

```bash
conda env create -f environment.yml && conda activate tesi_baseline
pip install -r dashboard/requirements.txt
streamlit run dashboard/app.py --server.port 8501     # poi aprire http://localhost:8501
```

I risultati e i limiti sono riassunti in `reports/RISULTATI_E_LIMITI.md` (indice: `reports/INDICE.md`).

## B. Verificare che il codice funzioni

```bash
make install && make test       # circa 390 test; quelli che richiedono dati esterni vengono saltati
```

## C. Rieseguire la pipeline sul dataset demo

```bash
make data-demo                  # scarica il dataset demo (una tantum)
make run-step1 && make run-step2
python -m pipeline_mne_bids.run_e2e_matchingpennies
```

Dettagli: `README.md` e `docs/GUIDA_PROFESSORE.md`.
