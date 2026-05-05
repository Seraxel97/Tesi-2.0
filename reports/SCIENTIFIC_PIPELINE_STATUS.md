# Scientific Pipeline Status — ds005385 N=15 FULL RUN

**Timestamp**: 2026-05-05T19:17:38+00:00
**Sprint**: S-FULL-N15 (sonnet-tesi-1) — FINALE
**Dataset**: ds005385 (Dortmund Vital Study) — N=15, seed=42

## Stato step — FINALE

| Step | Descrizione | Soggetti | Stato | Sprint |
|------|-------------|----------|-------|--------|
| 2 | Forward + inverse operator | 15/15 | ✅ | S-101, S-FULL-N15 |
| 2b | Source reconstruction per-epoch (dSPM) | 15/15 | ✅ | S-101b, S-FULL-N15 |
| 3b | Parcellazione per-epoch | 15×2×2=60 file | ✅ | S-103b, S-FULL-N15 |
| 4b | FC spettrale per-epoch (wPLI+coh) | 120/120 file | ✅ | S-104b, S-FULL-N15 |
| 5 | Feature extraction upper-triangle | X (30,*) × 4 combos | ✅ | S-FULL-N15 |
| 6+7 | ML LOSO-15 + perm test | 12 combos | ✅ | S-FULL-N15, S-AGG-N15 |

## Risultati finali — N=15

| Metrica | Valore |
|---------|--------|
| Soggetti totali | 15 |
| Campioni (sub×cond) | 30 |
| FC matrices | 120/120 |
| Combos ML testati | 12 |
| Combos significativi | 11/12 |
| **Winner** | **aparc × coh × svm_rbf** |
| **Best bal_acc** | **0.833** CI=[0.700,0.933] |
| **p_perm** | **0.000** (p<0.05 ✅) |
| Confronto PILOT | schaefer100×coh×logreg: 0.900→0.833 |
| Verdict pipeline | **PASS** ✅ |
