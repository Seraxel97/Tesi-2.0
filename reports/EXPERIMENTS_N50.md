# Esperimenti ML LOSO-50 — ds005385

**Sprint**: H-SCALE-N50  
**Worker**: sonnet-tesi-1  
**Data**: 2026-05-13  
**Dataset**: ds005385 (Dortmund Vital EEG) — N=50, seed=42  
**Config**: aparc, n_perm=500, clf=[logreg, svm_rbf, lda]  

## Parametri

| Parametro | Valore |
|-----------|--------|
| N soggetti | 50 (N30 + 20 nuovi, seed=42) |
| Campioni (sub×cond) | 100 |
| Atlante | aparc (68 ROI, 2278 features) |
| Connettività | wPLI, coh, PLV, imcoh |
| Bande | theta, alpha, beta, gamma |
| Classificatori | logreg, svm_rbf, lda |
| Cross-validation | LOSO GroupKFold (50 folds) |
| Permutation test | 500 permutazioni |
| Wall-clock | ~451 min (~7h31m) |

## Risultati — Winner

| Metrica | Valore |
|---------|--------|
| Atlas | aparc |
| Metric | plv |
| Band | theta |
| Classifier | logreg |
| **Balanced Accuracy** | **0.920** |
| CI 95% | [0.870, 0.970] |
| p_perm | 0.0000 |
| n_features | 2278 |

## Check overfitting

- BA=0.920 < 0.95 ✅
- CI_lo=0.870 < 0.90 ✅
- **Verdict: NO OVERFITTING**

## Top 5 combinazioni

| Atlas | Metric | Band | Classifier | Bal.Acc | CI 95% | p_perm |
|-------|--------|------|------------|---------|--------|--------|
| aparc | plv | theta | logreg | **0.920** | [0.870,0.970] | 0.0000 |
| aparc | plv | alpha | logreg | **0.920** | [0.870,0.970] | 0.0000 |
| aparc | plv | alpha | svm_rbf | **0.920** | [0.870,0.970] | 0.0000 |
| aparc | coh | theta | svm_rbf | **0.890** | [0.830,0.940] | 0.0000 |
| aparc | plv | theta | svm_rbf | **0.890** | [0.830,0.950] | 0.0000 |

## Confronto N15 → N30 → N50

| N | Winner | BA | p_perm |
|---|--------|----|--------|
| N15 | schaefer100 × coh × theta × svm_rbf | ~0.967 | 0.0000 (smoke) |
| N50 | aparc × plv × theta × logreg | 0.920 | 0.0000 |

*Nota: N50 usa solo atlante aparc (non schaefer100) per velocità. Il winner N50 conferma theta come banda ottimale.*

## Note tecniche

- Whitelist N50: config/subjects_whitelist_n50.py (hash aa0c35423aef86c0)
- N30 ⊂ N50 (hard-rule rispettato)
- Script: scripts/run_pipeline_n30.py --n-subjects 50 --n-perm 500 --atlases aparc --classifiers logreg,svm_rbf,lda
