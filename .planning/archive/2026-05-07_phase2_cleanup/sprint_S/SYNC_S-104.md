# SYNC S-104 — sonnet1-ts

**Sprint**: [WAVE-SCIENTIFIC-005] STEP 4 connectivity wPLI + coherence banda alpha
**Owner**: sonnet1-ts
**Branch**: scientific/step4-connectivity
**Pre-condizione**: S-103 done (20 npz label_tc). **OPERATOR APPROVAL**: "Yes" T20:14 via TG.

## CONFIG CONFERMATA OPERATORE

```python
SUBJECTS = ["sub-007", "sub-010", "sub-011", "sub-026", "sub-031"]
ATLASES = ["aparc", "schaefer100"]
CONDITIONS = ["EO", "EC"]
METRICS = ["wpli", "coh"]            # solo questi 2 (NO beta gamma altri)
BAND = {"alpha": (8.0, 13.0)}        # SOLO alpha
MODE = "multitaper"
```

## Cosa fare

1. **Per ogni sub × atlas × cond × metric** (5 × 2 × 2 × 2 = 40 file):
   - Carica `data/label_ts/ds005385/sub-XXX_atlas-{aparc|schaefer100}_cond-{EO|EC}.npz`.
   - Estrai `label_tc` array (shape (n_labels, n_times) o (n_epochs, n_labels, n_times)).
   - Se shape è `(n_labels, n_times)` → reshape a `(1, n_labels, n_times)` per fc_dispatcher (richiede 3D).
   - Compute FC: `connectivity.fc_dispatcher.compute_fc(label_tc, sfreq, metric=metric, bands={'alpha': (8.0, 13.0)}, mode='multitaper')`.
   - Output dict {'alpha': matrix shape (n_labels, n_labels)}.

2. **Output**:
   - `data/connectivity/ds005385/sub-XXX_atlas-{aparc|schaefer100}_metric-{wpli|coh}_band-alpha.npz`:
     - `fc_matrix`: shape (n_labels, n_labels) simmetrica.
     - `label_names`: array str.
     - `metadata`: subject, condition, atlas, metric, band, sfreq.
   - **Note**: brief operatore dice "matrici parcels × parcels". Naming `sub-<id>_atlas-<a>_cond-<c>_metric-<m>_band-alpha.npz` (4 nomi per axis).

3. **Crea dir**:
   ```bash
   mkdir -p data/connectivity/ds005385
   ```

4. **Tool**:
   - `connectivity.fc_dispatcher.compute_fc()` (già hardenato S-02 + DR-REVIEW-fc-symmetrize).
   - `connectivity.fc_dispatcher.save_fc()` per salvataggio npz.

5. **Reports**:
   - `reports/STEP4_DS005385_PILOT.md`:
     - Header timestamp + parametri.
     - Tabella per (sub × atlas × cond × metric): shape, mean upper triangle, eventuali NaN.
     - Wall-clock totale.
     - Esempio output 1 sub × 1 atlas × 1 metric (npz keys + matrix mean/std).

## Vincoli

- 40 file output.
- BAND = SOLO alpha (no beta/gamma/theta/delta).
- METRICS = SOLO wpli + coh (no plv/pli/altri).
- mode = multitaper.
- NIENTE altri sub.

## Gate uscita

- 40 file `.npz` in `data/connectivity/ds005385/`.
- `reports/STEP4_DS005385_PILOT.md` esiste.
- HB sonnet1-ts done verdict=PASS task=S-104.
- Queue S-104 status=done.
- **POST-GATE OBBLIGATORIO**: scrivi `.planning/MSG_TO_FATHER_<ts>_S104_DONE.md` con:
  - Tempo wall-clock totale.
  - Output esempio: 1 sub × 1 atlas × 1 metric (file path + shape FC matrix + mean upper triangle + range valori).
  - Eventuali warning (NaN, simmetria persa, ecc).
  - Plan STEP 5 features (S-105) da chiedere ACK operatore: upper-triangle flatten → X matrix per ML.
- Auto-claim post: NIENTE. STEP 5 (S-105) gated, attendi ACK operatore.

## Tempo stimato

5-10 min wall-clock totali (40 spectral_connectivity_epochs su matrici piccole, multitaper alpha singolo).
