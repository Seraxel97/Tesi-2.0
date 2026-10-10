# ALTO-2 — Validazione esterna SESSO su coorte SANA (ds005385 → LEMON)

Train: **ds005385** N=179. Test: **LEMON** (adulti SANI, 47 sogg/94 sample), stessa pipeline. No leakage (scaler fit solo su train), inference-only. Questo SOSTITUISCE il vecchio transfer confuso su ds004504 (Alzheimer) e i numeri-fantasma dell'ADR-004.

| Metrica | Volume-conduction | BA transfer → LEMON |
|---|---|---|
| plv | sensibile | **0.583** |
| wpli | robusta | **0.508** |
| imcoh | robusta | **0.506** |

Riferimento in-dataset (CV su ds005385): PLV BA = 0.795.

## Verdetto
**GENERALIZZAZIONE DEBOLE/ASSENTE su coorte sana: BA transfer=0.583 (PLV) vicino al caso → la classificazione del sesso è in gran parte specifica di ds005385, non trasferibile; da dichiarare come limite (risultato dataset-specifico).**

> Interpretazione onesta combinata con ALTO-1 (regge age-matching, BA=0.719) e ALTO-3 (volume-conduction: effetto onesto ~0.57): il segnale-sesso è reale entro-dataset; questo test dice se sopravvive anche FUORI dal dataset, su persone sane diverse.
