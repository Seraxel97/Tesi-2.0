# SYNC S-103b — sonnet1-ts (UNICO worker attivo, quota ridotta)

**Sprint**: [FIX] STEP 3 parcellation per-epoch label_tc (rerun S-103 con per-epoch STC)
**Owner**: sonnet1-ts
**Branch**: scientific/step3-per-epoch
**Pre-condizione**: S-101b done (per-epoch STC `*_stcs.npz` esistenti).
**OPERATOR APPROVAL**: 2026-05-02 T00:18 OPZIONE 2 (S-103b + cleanup STC post-done).

## QUOTA MODE: 1 WORKER ONLY

⚠️ **NESSUN parallelismo workers fino alle 05:00** (quota Claude ridotta).
Tu sei l'UNICO worker attivo. Heartbeat regolare ogni 5-7 min essenziale.

## SUB LIST + ATLASES + CONFIG (invariati)

```python
PILOT_SUBJECTS = ["sub-007", "sub-010", "sub-011", "sub-026", "sub-031"]
ATLASES = ["aparc", "schaefer100"]
CONDITIONS = ["EO", "EC"]
MODE = "mean_flip"
```

## Cosa fare

1. **Per ogni sub × atlas × cond** (5 × 2 × 2 = 20 estrazioni):
   - Carica per-epoch STC: `data/derivatives/mne-bids-pipeline/sub-XXX/eeg/sub-XXX_task-RestingState_cond-{EO|EC}_inv-dSPM-stcs.npz`.
     - Keys: `data` (n_epochs, n_sources, n_times), `vertices_lh`, `vertices_rh`, `tmin`, `tstep`.
   - Carica forward: `sub-XXX_fwd.fif` per source space.
   - Estrai labels: `parcellation.extract_label_tc.get_labels(atlas, subject='fsaverage')`.
   - Per ogni epoch (loop su `data` axis 0):
     - Ricostruisci STC: `mne.SourceEstimate(data=data_epoch, vertices=[vertices_lh, vertices_rh], tmin=tmin, tstep=tstep, subject='fsaverage')`.
     - Estrai label_tc: `mne.extract_label_time_course(stc, labels, src=fwd['src'], mode='mean_flip', allow_empty=True)`.
   - Stack: `label_tc_per_epoch` shape `(n_epochs, n_labels, n_times)`.

2. **Output**:
   - 20 file `data/label_ts/ds005385/sub-XXX_atlas-{aparc|schaefer100}_cond-{EO|EC}_per-epoch.npz`:
     - `label_tc`: shape `(n_epochs, n_labels, n_times)`.
     - `label_names`: array str.
     - `metadata`: subject, condition, atlas, mode, n_epochs, sfreq.

3. **Crea dir output** (se non esiste):
   ```bash
   mkdir -p data/label_ts/ds005385
   ```
   I file precedenti S-103 (single-epoch, naming senza `_per-epoch`) NON vanno cancellati ora — overwrite con `_per-epoch` suffix per separazione.

4. **Reports**:
   - `reports/STEP3b_DS005385_PER_EPOCH.md`:
     - Header timestamp + sub list + atlas + mode.
     - Tabella per (sub × atlas × cond): n_epochs, shape `(n_epochs, n_labels, n_times)`, eventuali warning.
     - Wall-clock totale.
     - Esempio output 1 sub × 1 atlas: file path + shape + label_names primi 5 + first 3 epochs mean.

## Vincoli

- 20 file output.
- mode = `mean_flip`.
- NIENTE altri sub.
- 1 worker only (no parallelismo).

## Gate uscita

- 20 file `.npz` con suffix `_per-epoch.npz`.
- `reports/STEP3b_DS005385_PER_EPOCH.md` esiste.
- HB sonnet1-ts done verdict=PASS task=S-103b.
- Queue S-103b status=done.
- **POST-GATE OBBLIGATORIO**: scrivi `.planning/MSG_TO_FATHER_<ts>_S103b_DONE.md` con:
  - Tempo wall-clock totale.
  - Output esempio: 1 sub × 1 atlas × 1 cond (file path + shape + label_names primi 5 + esempio epochs).
  - Eventuali warning.
  - **Cleanup richiesta**: lista file STC per-epoch (10 file `*_stcs.npz`) da rimuovere post-done per recuperare ~17.9 GB disk.
  - Plan S-104b connectivity rerun (config invariata: wpli + coh banda alpha aparc + schaefer100).
- Auto-claim post: NIENTE. Aspetta ACK father per cleanup STC + S-104b dispatch.

## Tempo stimato

10-20 min wall-clock (5 sub × 2 atlas × 2 cond × ~125 epochs × extract_label_time_course light operation).
