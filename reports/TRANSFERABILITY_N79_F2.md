# F2 — Transferability check: 79 soggetti held-out (2026-06-30)

> Risposta diretta alla domanda-chiave del relatore sul **double-dipping**: il winner-feature
> (`X_aparc_plv_theta`) è stato selezionato su N=50/N=100 ⊂ N=179, quindi la CV su N=179 non è
> held-out rispetto alla selezione. Questo test isola l'**unico** confronto realmente held-out.

## Metodo
Stessa pipeline dei risultati ufficiali (StandardScaler fit-only-su-train + LogReg-L2
`class_weight=balanced`, C via GridSearchCV con GroupKFold interno), ma:
- **Addestramento SOLO sui 100 soggetti** usati per la selezione-feature.
- **Valutazione sui 79 soggetti NUOVI** = N=179 ∖ N=100 (mai visti né in selezione né in training).
- Significatività: permutation test subject-level sulle label dei 79 (predizioni fisse), `(#≥+1)/(n+1)`.
- Incertezza: cluster-bootstrap a livello soggetto sui 79.

Riproducibile: `python scripts/transferability_n79.py --n-perm 1000 --n-boot 1000` (seed=42).
Logica di split coperta da test (`tests/ml_training/test_transferability_n79.py`).

## Risultato
| Metrica | Valore |
|---------|--------|
| BA held-out (79 nuovi) | **0.776** |
| CI95 (cluster-bootstrap) | [0.700, 0.839] |
| p_perm (held-out) | **0.0010** |
| C selezionata | 0.01 |
| BA CV-N=179 (riferimento) | 0.795 |
| **Gap di ottimismo** (CV − held-out) | **+0.019** |

## Interpretazione
- Il modello addestrato **solo sui 100** classifica il sesso sui **79 mai-visti** con BA=0.776,
  **significativo** (p=0.001) e con CI95 ben **sopra il caso (0.5)**.
- Il gap tra CV-N=179 (0.795) e held-out puro (0.776) è di **soli ~0.02**: il double-dipping ha
  gonfiato la stima in modo **trascurabile**. La feature non è un artefatto della selezione.
- **Conseguenza per la tesi**: la possibile obiezione sul double-dipping si **ribalta in un punto
  di forza** — il risultato sul sesso generalizza a soggetti held-out dello stesso dataset.
- ⚠️ Resta valida la distinzione (vedi `STATISTICAL_VALIDITY_NOTES.md`): held-out *entro-dataset*
  ≠ generalizzazione *cross-dataset* (che richiederebbe LEMON, non ancora disponibile).
