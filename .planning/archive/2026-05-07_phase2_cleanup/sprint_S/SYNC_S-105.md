# SYNC S-105 — sonnet1-ts (1 worker mode, claim post-S-104b done + ACK father)

**Sprint**: [WAVE-SCIENTIFIC-006] STEP 5 features upper-triangle flatten ds005385
**Owner**: TBD (sonnet1-ts post-S-104b done)
**Branch**: scientific/step5-features
**Pre-condizione**: S-104b done. ACK father per dispatch.

## QUOTA MODE

⚠️ 1 worker only.

## Cosa fare

1. **Per ogni sub × atlas × cond × metric** (5 × 2 × 2 × 2 = 40 input):
   - Carica `data/connectivity/ds005385/sub-XXX_atlas-XXX_cond-XXX_metric-XXX_band-alpha_per-epoch.npz`.
   - `fc_matrix` shape (n_labels, n_labels).
   - Estrai upper triangle (off-diagonal) flatten:
     ```python
     import numpy as np
     iu = np.triu_indices(n_labels, k=1)
     features_vector = fc_matrix[iu]  # shape (n_labels*(n_labels-1)/2,)
     ```
   - Per aparc (68 ROI): 68*67/2 = 2278 features.
   - Per schaefer100 (100 ROI): 100*99/2 = 4950 features.

2. **Aggrega per (sub, atlas, metric)** combinando EO + EC (label = condition):
   - X matrix shape `(n_samples, n_features)` dove `n_samples = 2 conds (EO+EC) × n_subjects = 10`.
   - y array binary (0=EO, 1=EC) shape `(10,)`.
   - groups array `subject_id` per GroupKFold.
   - **Note**: con 5 sub × 2 cond, X = (10, n_features). Per LOSO/GroupKFold n_splits=5 (1 per subject).

3. **Output** (per atlas × metric → 4 file):
   - `data/features/ds005385/X_atlas-{aparc|schaefer100}_metric-{wpli|coh}_band-alpha.npz`:
     - `X`: shape `(10, 2278|4950)`.
     - `y`: shape `(10,)` binary.
     - `groups`: shape `(10,)` subject_id.
     - `feature_names`: array str (`"label_i--label_j"` for each pair).
     - `metadata`: subjects, atlases, metric, band.

4. **Reports**:
   - `reports/STEP5_DS005385.md`:
     - Header timestamp.
     - Tabella per (atlas × metric): X.shape, y unique, groups unique.
     - Verdict.

## Vincoli

- 4 file output (1 per atlas × metric).
- NIENTE altri sub.
- Cleanup: NIENTE delete connectivity npz (servono per re-runs).

## Gate uscita

- 4 file `.npz`.
- `reports/STEP5_DS005385.md` esiste.
- HB sonnet1-ts done verdict=PASS task=S-105.
- Queue S-105 status=done.
- **POST-GATE OBBLIGATORIO**: `.planning/MSG_TO_FATHER_<ts>_S105_DONE.md`:
  - Tempo wall-clock.
  - Output esempio: X shape, y values, groups values per 1 atlas × 1 metric.
  - Plan S-106 ML primo run reale.

## Tempo stimato

5 min wall-clock (operazione veloce, no compute pesante).
