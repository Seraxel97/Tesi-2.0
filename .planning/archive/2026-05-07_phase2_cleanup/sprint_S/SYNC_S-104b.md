# SYNC S-104b — sonnet1-ts (1 worker mode, claim post-S-103b done + ACK father)

**Sprint**: [FIX] STEP 4 connectivity wpli + coh banda alpha PER-EPOCH (rerun S-104 post fix)
**Owner**: TBD (sonnet1-ts post-S-103b done)
**Branch**: scientific/step4-per-epoch
**Pre-condizione**: S-101b + S-103b done. ACK father per dispatch (gate operatore via father).

## QUOTA MODE

⚠️ 1 worker only. NO parallelismo (fino 09:00).

## CONFIG (invariata da S-104, ma input diverso = per-epoch)

```python
SUBJECTS = ["sub-007", "sub-010", "sub-011", "sub-026", "sub-031"]
ATLASES = ["aparc", "schaefer100"]
CONDITIONS = ["EO", "EC"]
METRICS = ["wpli", "coh"]
BAND = {"alpha": (8.0, 13.0)}
MODE = "multitaper"
SFREQ = 250.0  # post-preprocessing resample
```

## Cosa fare

1. **Per ogni sub × atlas × cond × metric** (5 × 2 × 2 × 2 = 40 file):
   - Carica `data/label_ts/ds005385/sub-XXX_atlas-{aparc|schaefer100}_cond-{EO|EC}_per-epoch.npz`.
     - Keys: `label_tc` shape `(n_epochs, n_labels, n_times)`, `label_names`.
   - Verifica `n_epochs ≥ 10` (validation pre-FC, evita wPLI collapse).
   - Compute FC: `connectivity.fc_dispatcher.compute_fc(label_tc, sfreq=250.0, metric=metric, bands={'alpha': (8.0, 13.0)}, mode='multitaper', n_jobs=1)`.
   - Output: `dict {'alpha': matrix shape (n_labels, n_labels)}` simmetrica.
   - **Validation post-compute**: per metric=wpli, mean upper triangle deve essere in range fisiologico [0.05, 0.50]. Se >0.7 → error log (regression test failure).

2. **Output**:
   - 40 file `data/connectivity/ds005385/sub-XXX_atlas-{aparc|schaefer100}_cond-{EO|EC}_metric-{wpli|coh}_band-alpha_per-epoch.npz`:
     - `fc_matrix`: shape `(n_labels, n_labels)`.
     - `label_names`: array str.
     - `metadata`: subject, condition, atlas, metric, band, sfreq, n_epochs, mean_upper_triangle, std_upper_triangle.

3. **Crea dir** (se non esiste): `mkdir -p data/connectivity/ds005385`.

4. **Reports**:
   - `reports/STEP4b_DS005385_RERUN.md`:
     - Header timestamp + parametri + suffix `_per-epoch`.
     - Tabella per (sub × atlas × cond × metric): n_epochs, mean upper triangle, std, range, PASS/WARN.
     - **Confronto S-104 vs S-104b**: wPLI mean S-104 (~1.0 collapse) vs wPLI mean S-104b (~0.10-0.30 fisiologico).
     - Wall-clock totale.

## Vincoli

- 40 file output con suffix `_per-epoch.npz`.
- Validation range wPLI [0.05, 0.50] obbligatoria.
- 1 worker only.

## Gate uscita

- 40 file `.npz` con suffix `_per-epoch.npz`.
- `reports/STEP4b_DS005385_RERUN.md` esiste con confronto pre/post-fix.
- HB sonnet1-ts done verdict=PASS task=S-104b (warning se mean wpli >0.5 → flag).
- Queue S-104b status=done.
- **POST-GATE OBBLIGATORIO**: `.planning/MSG_TO_FATHER_<ts>_S104b_DONE.md`:
  - Tempo wall-clock.
  - Output esempio: 1 sub × 1 atlas × 1 metric (file path + shape FC + mean upper triangle + range).
  - Confronto wPLI S-104 vs S-104b: validation fisiologica.
  - Plan S-105 features upper-triangle flatten.

## Tempo stimato

10-20 min wall-clock (40 spectral_connectivity_epochs su matrici piccole, n_epochs ~125).
