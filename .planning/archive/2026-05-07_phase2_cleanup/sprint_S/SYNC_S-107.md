# SYNC S-107 — sonnet1-ts (1 worker mode, claim post-S-106 done + ACK father)

**Sprint**: [WAVE-SCIENTIFIC-008] STEP 7 esperimenti minimi (matrice confronto)
**Owner**: TBD (sonnet1-ts post-S-106 done)
**Branch**: scientific/step7-experiments
**Pre-condizione**: S-106 done. ACK father per dispatch.

## QUOTA MODE

⚠️ 1 worker only.

## CONFRONTI MINIMI (da brief operatore)

```
1. aparc vs schaefer100 (atlas effect)
2. wPLI vs coherence (metric effect)
3. LogReg vs RF (algorithm effect)
```

## Cosa fare

1. **Riusa results JSON da S-106** (già 2 atlas × 2 metric × 2 algo = 8 cells).

2. **Comparison matrix**:
   - Carica 8 JSON da `results/ds005385/`.
   - Costruisci DataFrame con colonne: atlas, metric, algorithm, BA, p_perm, F1, AUC.
   - Salva `results/ds005385/comparison_matrix.json`:
     ```json
     {
       "cells": [{"atlas": "aparc", "metric": "wpli", "algorithm": "logreg", "BA": 0.XX, "p_perm": 0.XXX, ...}, ...],
       "summary": {
         "atlas_effect": {"aparc_mean_BA": 0.XX, "schaefer100_mean_BA": 0.YY},
         "metric_effect": {"wpli_mean_BA": 0.XX, "coh_mean_BA": 0.YY},
         "algo_effect": {"logreg_mean_BA": 0.XX, "rf_mean_BA": 0.YY}
       },
       "best_cell": {...},
       "worst_cell": {...}
     }
     ```

3. **Statistical significance**:
   - Apply FDR (analysis/fdr_helper.py S-16) sui 8 p_perm.
   - Output `p_fdr` corretti.

4. **Reports**:
   - `reports/STEP7_EXPERIMENTS_MINIMAL.md`:
     - Header timestamp + scope.
     - **Tabella principale**: 8 cells con BA, p_perm, p_fdr, F1, AUC.
     - **Sezione "Atlas effect"**: confronto aparc vs schaefer100 (paired su metric × algo).
     - **Sezione "Metric effect"**: confronto wpli vs coh.
     - **Sezione "Algorithm effect"**: confronto logreg vs rf.
     - **Sezione "Winner config"**: best cell + raccomandazione.
     - **Sezione "Limitazioni"**: N=5 sub, smoke run, no full-scale (operator constraint).
     - **Sezione "Next steps"**: scale a N=15 subset post-validation, oppure expand a 5 algorithms.

5. **Crea visualizations** (se time permits, riusa `dashboard/plot_top_features.py` S-11):
   - PNG bar chart BA per cell (8 bars).
   - PNG matrix heatmap atlas × metric × algorithm.
   - Output: `reports/figures/step7_BA_comparison.png`, `reports/figures/step7_matrix_heatmap.png`.

## Vincoli

- 1-3 file output (comparison_matrix.json + report MD + figures opzionali).
- NIENTE re-run ML (solo aggregazione + analysis).
- 1 worker only.

## Gate uscita

- `results/ds005385/comparison_matrix.json` esiste.
- `reports/STEP7_EXPERIMENTS_MINIMAL.md` esiste con 4 sezioni effect + winner.
- HB sonnet1-ts done verdict=PASS task=S-107.
- Queue S-107 status=done.
- **POST-GATE OBBLIGATORIO** (FINAL OUTPUT TESI):
  - `.planning/MSG_TO_FATHER_<ts>_S107_DONE_FINAL.md` con:
    - **Output finale tesi (operatore brief)**:
      1. Dataset usato: ds005385 (Dortmund Vital Study), 5 sub PILOT.
      2. N soggetti processati: 5.
      3. Metriche ML ottenute: tabella completa atlas × metric × algorithm.
      4. Risultati statistici: p_perm + p_fdr per ogni cell.
      5. Stato pipeline: 7 step completi su PILOT 5 sub.
      6. Prossimi step: scale a N=15 subset (operator decision), expand altri algorithm/banda, replicate ds005385.
    - Effect sizes (atlas/metric/algorithm).
    - Best config + razionale.
    - Plan post-S-107 (handover/manuscript update).

## Tempo stimato

10-20 min wall-clock (load JSON + aggregate + report MD + opt. visualizations).
