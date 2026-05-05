# Esperimenti N=15 — ds005385 Full Run

**Timestamp**: 2026-05-05T19:17:38+00:00
**Sprint**: S-FULL-N15 (sonnet-tesi-1)
**Dataset**: ds005385 — N=15, seed=42
**Campioni**: 30 (EO + EC)
**CV**: LOSO GroupKFold-15
**Modulo**: ml_training.aggregate_n15.aggregate_classify_n15 (S-AGG-N15 commit 4995662)
**n_permutations**: 100

---

## STEP 6+7 — LOSO-15 + Bootstrap CI + Permutation Test

| Atlas | Metric | Classifier | Bal.Acc | CI 95% | p_perm | Sig |
|-------|--------|------------|---------|--------|--------|-----|
| aparc | wpli | logreg | **0.667** ±0.298 | [0.500, 0.833] | 0.030 | ✅ |
| aparc | wpli | svm_rbf | **0.667** ±0.350 | [0.467, 0.833] | 0.000 | ✅ |
| aparc | wpli | lda | **0.700** ±0.245 | [0.567, 0.833] | 0.000 | ✅ |
| aparc | coh | logreg | **0.767** ±0.249 | [0.633, 0.900] | 0.010 | ✅ |
| aparc | coh | svm_rbf | **0.833** ±0.236 | [0.700, 0.933] | 0.000 | ✅ |
| aparc | coh | lda | **0.800** ±0.245 | [0.667, 0.900] | 0.000 | ✅ |
| schaefer100 | wpli | logreg | **0.700** ±0.245 | [0.567, 0.833] | 0.000 | ✅ |
| schaefer100 | wpli | svm_rbf | **0.767** ±0.249 | [0.633, 0.900] | 0.000 | ✅ |
| schaefer100 | wpli | lda | **0.633** ±0.221 | [0.533, 0.767] | 0.020 | ✅ |
| schaefer100 | coh | logreg | **0.833** ±0.298 | [0.667, 0.967] | 0.000 | ✅ |
| schaefer100 | coh | svm_rbf | **0.700** ±0.305 | [0.533, 0.833] | 0.010 | ✅ |
| schaefer100 | coh | lda | **0.633** ±0.287 | [0.500, 0.767] | 0.110 | ❌ |

---

## Best configuration

**Winner**: `aparc × coh × svm_rbf`
**Balanced Accuracy**: 0.833  CI=[0.700, 0.933]
**p_perm**: 0.000 (p<0.05 ✅)

### PILOT (n=10) → Full (N=15) — schaefer100 × coh × logreg

| Config | PILOT bal_acc | N=15 bal_acc |
|--------|--------------|--------------|
| schaefer100 × coh × logreg | 0.900 | 0.833 |

---

## Summary

| Metrica | Valore |
|---------|--------|
| Soggetti | 15 |
| Campioni | 30 |
| Combos testati | 12 |
| Combos significativi (p<0.05) | 11/12 |
| Winner | aparc × coh × svm_rbf |
| Best bal_acc | 0.833 CI=[0.700,0.933] |
| Best p_perm | 0.000 |
| Verdict | **PASS** ✅ |

