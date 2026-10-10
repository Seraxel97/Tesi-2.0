# F3 — Confound check età↔sesso (N=179, 2026-06-30)

> Controllo richiesto da qualsiasi revisore di neuroimaging: la classificazione del **sesso**
> potrebbe in parte sfruttare differenze legate all'**età**, se età e sesso sono confusi nel campione.

## Risultato (HONEST — finding positivo di confound)
| | F | M |
|---|---|---|
| N | 112 | 67 |
| Età mediana | 42.5 | 50.0 |
| Età media | 42.0 | 48.1 |

**Mann-Whitney U = 2832, p = 0.0061** → l'età **differisce in modo significativo** tra i sessi
nel campione (i maschi sono in media ~6 anni più anziani).

## Interpretazione (da dichiarare in tesi — limitazione)
- C'è un **confound età↔sesso**: il classificatore del sesso (BA=0.776 held-out) potrebbe
  sfruttare **in parte** pattern EEG correlati all'età, non solo il segnale biologico del sesso.
- Questo **non invalida** il risultato (il sesso resta predicibile e significativo), ma ne
  **qualifica l'interpretazione**: «BA=0.776 per la classificazione del sesso» va accompagnato da
  «il campione ha M più anziani delle F (p=0.006), quindi parte del segnale potrebbe essere
  età-mediato».
- **Follow-up consigliato** (non ancora eseguito): ri-stimare la classificazione del sesso
  (a) regredendo l'età dalle feature, oppure (b) su un sottocampione **age-matched** M/F, per
  isolare il contributo del sesso al netto dell'età. Da pianificare con il relatore.

## Riproducibilità
`python scripts/confound_age_sex.py` (deterministico, solo phenotype). Statistica coperta da
test (`tests/ml_training/test_confound_age_sex.py`). Output: `data/results/ds005385/confound_age_sex.json`.
