# SYNC S-106 — sonnet1-ts (1 worker mode, claim post-S-105 done + ACK father)

**Sprint**: [WAVE-SCIENTIFIC-007] STEP 6 ML primo run reale ds005385
**Owner**: TBD (sonnet1-ts post-S-105 done)
**Branch**: scientific/step6-ml
**Pre-condizione**: S-105 done. ACK father per dispatch.

## QUOTA MODE

⚠️ 1 worker only.

## CONFIG (da brief operatore)

```python
ALGORITHMS = ["logreg", "rf"]    # solo questi 2 (NO svm/mlp/gb per primo run)
CV = "GroupKFold"
N_SPLITS = 5  # 1 per subject (LOSO equivalente con N=5)
N_PERMUTATIONS = 1000
RANDOM_STATE = 42
METRICS_REPORT = ["balanced_accuracy", "f1_macro", "roc_auc_ovo"]
```

## Cosa fare

1. **Per ogni atlas × metric × algorithm** (2 × 2 × 2 = 8 cells):
   - Carica `data/features/ds005385/X_atlas-XXX_metric-XXX_band-alpha.npz`.
     - `X` shape (10, 2278|4950).
     - `y` shape (10,) binary.
     - `groups` shape (10,) subject_id.
   - Run `ml_training.ml_dispatcher.train_eval(X, y, groups, algorithm=algo, n_splits=5, n_perm=1000, random_state=42)`:
     - GroupKFold(5) inner loop.
     - Permutation testing 1000 shuffles within fold.
     - Metrics: balanced_accuracy, F1 macro, ROC-AUC.
   - Output JSON: BA mean+std+CI, F1, AUC, p_perm, fitted_estimator, confusion_matrix, fold_scores.

2. **Output**:
   - 8 file `results/ds005385/atlas-{aparc|schaefer100}_metric-{wpli|coh}_algo-{logreg|rf}.json`:
     - `balanced_accuracy`: dict mean/std/ci_low/ci_high.
     - `f1_macro`, `roc_auc`.
     - `p_perm`: float (empirical p-value, floor 1/1000=0.001).
     - `confusion_matrix`: (2,2).
     - `fold_scores`: list di 5 BA per fold.
     - `metadata`: atlas, metric, algorithm, n_perm, random_state.

3. **Crea dir** (se non esiste): `mkdir -p results/ds005385`.

4. **Reports**:
   - `reports/STEP6_ML_FIRST_RUN.md`:
     - Header timestamp + config.
     - **Tabella principal**: atlas × metric × algorithm → BA mean ± std, p_perm, F1, AUC.
     - Sezione "Significance": cells con p_perm < 0.05.
     - Sezione "Best config": top BA + p_perm.
     - Note caveat: N=5 sub piccolo, statistiche indicative.

## Vincoli

- 8 file output JSON.
- LogReg + RF solo (no svm/mlp/gb in primo run).
- random_state=42 ovunque.
- Permutation 1000 shuffle (operator brief: "permutation test ATTIVO").
- 1 worker only.

## Gate uscita

- 8 file JSON in `results/ds005385/`.
- `reports/STEP6_ML_FIRST_RUN.md` esiste con tabella + p-value.
- HB sonnet1-ts done verdict=PASS task=S-106.
- Queue S-106 status=done.
- **POST-GATE OBBLIGATORIO**: `.planning/MSG_TO_FATHER_<ts>_S106_DONE.md`:
  - Tempo wall-clock.
  - **Output finale operatore (primary KPI)**: 
    - Dataset: ds005385 (5 sub PILOT).
    - N sub processati: 5.
    - Best config: atlas × metric × algorithm + BA + p_perm.
    - Risultati statistici: tabella completa.
  - Plan S-107 esperimenti minimi (matrice atlas × metric × algo).

## Tempo stimato

10-30 min wall-clock (8 ML runs × GroupKFold(5) × permutation 1000, dipende da algo: logreg veloce, RF medio).
