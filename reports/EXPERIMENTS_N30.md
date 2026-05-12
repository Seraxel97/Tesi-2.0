# Scientific Pipeline Status — ds005385 N=30 FULL RUN

**Timestamp**: 2026-05-12T11:47:47+00:00
**Sprint**: H-SCALE-N30 (sonnet-tesi-1)
**Dataset**: ds005385 — N=30, seed=42

## Stato step — N=30

| Step | Soggetti | Stato |
|------|----------|-------|
| 2 (fwd+inv) | 30/30 | ✅ |
| 2b (stcs per-epoch) | 30/30 | ✅ (cleanup post-3b) |
| 3b (label_ts) | 30/30 | ✅ |
| 4b (FC) | 30/30 | ✅ |
| 5 (features) | 30/30 | ✅ |
| 6+7 (ML LOSO-30) | 30/30 | ✅ |

## Risultati finali — N=30

| Metrica | Valore |
|---------|--------|
| Soggetti totali | 30 |
| Campioni (sub×cond) | 60 |
| Combos ML testati | 96 |
| **Winner** | **schaefer100 × plv × theta × logreg** |
| **Best bal_acc** | **0.967** CI=[0.917,1.000] |
| **p_perm** | **0.0000** |
| Wall-clock totale | ~2 min |
| Verdict pipeline | **PASS** ✅ |

## Best combos (top 5)

| Atlas | Metric | Band | Classifier | Bal.Acc | CI 95% | p_perm |
|-------|--------|------|------------|---------|--------|--------|
| schaefer100 | plv | theta | logreg | **0.967** | [0.917,1.000] | 0.0000 |
| aparc | plv | theta | logreg | **0.950** | [0.900,1.000] | 0.0000 |
| schaefer100 | plv | theta | svm_rbf | **0.917** | [0.833,0.983] | 0.0000 |
| aparc | plv | alpha | logreg | **0.917** | [0.850,0.983] | 0.0000 |
| schaefer100 | plv | alpha | logreg | **0.917** | [0.850,0.983] | 0.0000 |

