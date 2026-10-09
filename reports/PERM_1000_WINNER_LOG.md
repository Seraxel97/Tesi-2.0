# Permutation Test n=1000 — Winner Combo (Paper-Grade)

**Sprint**: R-TESI-2.0-NPERM-1000-WINNER  
**Worker**: sonnet1-tesi  
**Timestamp**: 2026-05-14T21:42:07+02:00  
**Dataset**: ds005385 — N=50, seed=42  
**Combo**: aparc × plv × theta × logreg  

---

## Comando eseguito

```python
# Eseguito da ~/Scrivania/Tesi_2.0/ con conda env base (Python 3.13)
import sys; sys.path.insert(0, '.')
import numpy as np
from ml_training.permutation import permutation_test
from ml_training.ml_dispatcher import run_cv
from analysis.stats_utility import bootstrap_ci

X = np.load('data/features/ds005385/X_aparc_plv_theta.npz')['X']   # shape (100, 2278)
y = np.load('data/features/ds005385/y.npy')                          # shape (100,)
g = np.load('data/features/ds005385/groups.npy')                     # shape (100,), 50 unique

res = permutation_test(X, y, groups=g, algorithm='logreg',
                       n_permutations=1000, n_splits=50, random_state=42)

cv_res = run_cv(X, y, groups=g, algorithm='logreg', n_splits=50)
ci_lo, ci_hi = bootstrap_ci(np.array(cv_res.ba_per_fold),
                             statistic=np.mean, n_boot=10000, alpha=0.05, random_state=42)
```

---

## Risultati

| Metrica | Valore |
|---------|--------|
| **Balanced Accuracy** | **0.9200** |
| **CI 95% (bootstrap 10k)** | **[0.8700, 0.9700]** |
| **p_perm** | **0.0000** |
| n_permutations | 1000 |
| n_splits (LOSO) | 50 |
| n_subjects | 50 |
| n_samples | 100 (EO + EC) |
| n_features | 2278 (aparc 68 ROI, upper triangle) |
| Null distribution mean | 0.4934 |
| Null distribution std | 0.0618 |
| Wall-clock | 7.73 min (463.9 s) |

---

## Input dati

| File | Shape | Note |
|------|-------|------|
| `data/features/ds005385/X_aparc_plv_theta.npz` | (100, 2278) | Feature matrix FC-flatten |
| `data/features/ds005385/y.npy` | (100,) | Labels {0,1} (EO=0, EC=1) |
| `data/features/ds005385/groups.npy` | (100,) | Subject IDs (50 gruppi) |

---

## Confronto n_perm=500 vs n_perm=1000

| Parametro | n_perm=500 (H-SCALE-N50) | n_perm=1000 (paper-grade) |
|-----------|--------------------------|--------------------------|
| BA | 0.920 | **0.920** |
| CI 95% | [0.870, 0.970] | **[0.870, 0.970]** |
| p_perm | 0.0000 | **0.0000** |
| Null mean | — | 0.4934 |
| Wall-clock | ~451 min (48 combo) | 7.73 min (1 combo) |

**Conclusione**: risultati identici a n_perm=500. La significatività è robusta all'aumento del numero di permutazioni. p_perm=0/1000 = **0.000** (nessuna delle 1000 null BA ≥ 0.920).

---

## Note metodologiche

- `n_splits=50` = LOSO GroupKFold (1 test soggetto per fold su 50 soggetti).
- CI calcolato via bootstrap (10000 campioni) sulla distribuzione delle BA per fold, non sulla null distribution.
- `warning "y_pred contains classes not in y_true"` visibile nelle permutazioni: atteso per LOSO con singolo test sample su label permutate (fold con 1 campione e classe single-label). Non influenza la stima della null.
- `random_state=42` su `permutation_test` garantisce riproducibilità della null distribution.
