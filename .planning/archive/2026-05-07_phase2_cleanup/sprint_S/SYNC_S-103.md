# SYNC S-103 — sonnet1-ts

**Sprint**: [WAVE-SCIENTIFIC-004] STEP 3 parcellation ds005385 PILOT
**Owner**: sonnet1-ts
**Branch**: scientific/step3-parcellation
**Pre-condizione**: S-101 done (5 sub STC). **OPERATOR APPROVAL**: "Si" T19:43 via TG.

## SUB LIST + ATLASES (confermati operatore)

```python
PILOT_SUBJECTS = ["sub-007", "sub-010", "sub-011", "sub-026", "sub-031"]
ATLASES = ["aparc", "schaefer100"]
TASK = "RestingState"
CONDITIONS = ["EO", "EC"]
```

## Cosa fare

1. **Per ogni sub × ogni atlas × ogni condizione** (5 × 2 × 2 = 20 estrazioni):
   - Carica STC: `data/derivatives/mne-bids-pipeline/sub-XXX/eeg/sub-XXX_task-RestingState_cond-{EO|EC}_inv-dSPM-{lh,rh}.stc`.
   - Carica forward (per source space): `sub-XXX_fwd.fif`.
   - Estrai label time courses: `parcellation.extract_label_tc.extract_tc(stc, atlas, src=fwd['src'], mode='mean_flip')`.

2. **Output**:
   - `data/label_ts/ds005385/sub-XXX_task-RestingState_cond-{EO|EC}_atlas-{aparc|schaefer100}.npz`:
     - `label_tc`: shape `(n_labels, n_times)` per condizione singola epoch (evoked) **OPPURE** `(n_epochs, n_labels, n_times)` se STC contiene più epoch.
     - `label_names`: array str.
     - `atlas`, `subject`, `condition`, `task` come metadata.
   - **Note**: brief operatore dice `<sub>_<atlas>_<run>.npz`. Se STC è single-epoch (evoked-style), naming `sub-XXX_atlas-XXX_cond-XXX.npz`. Per "run" interpreta come "condition" (EO/EC).

3. **Crea dir output**:
   ```bash
   mkdir -p data/label_ts/ds005385
   ```

4. **Tool da usare**:
   - `parcellation/extract_label_tc.py` (già hardenato S-01 + DR-REVIEW fix).
   - API: `extract_tc_from_files(stc_path, fwd_path=..., atlas=..., mode='mean_flip')`.

5. **Reports**:
   - `reports/STEP3_DS005385_PILOT.md`:
     - Header timestamp + sub list + atlases.
     - Tabella per (sub × atlas): n_labels effettivi, shape label_tc, n_times, eventuali warning (label vuote, medial wall filtrate).
     - Wall-clock totale.
     - Esempio output 1 sub × 1 atlas (npz keys).

## Vincoli

- SOLO 5 sub × 2 atlas × 2 cond = 20 file output.
- NIENTE altri sub.
- mode = `mean_flip` (default sicuro per FC, da CV_STRATEGY).
- Tempo previsto: 5-15 min wall-clock (operazione veloce, no compute pesante).

## Gate uscita

- 20 file `.npz` in `data/label_ts/ds005385/`.
- `reports/STEP3_DS005385_PILOT.md` esiste.
- HB sonnet1-ts done verdict=PASS task=S-103.
- Queue S-103 status=done.
- **POST-GATE OBBLIGATORIO**: scrivi `.planning/MSG_TO_FATHER_<ts>_S103_DONE.md` con:
  - Tempo wall-clock totale.
  - Output esempio: 1 sub × 1 atlas (file path + shape + label_names primi 5).
  - Eventuali warning.
  - Plan STEP 4 connectivity (S-104) da chiedere ACK operatore: parametri (wpli + coherence, banda alpha 8-13 Hz, multitaper).
- Auto-claim post: NIENTE. STEP 4 (S-104) gated, attendi ACK operatore.
