# SYNC S-101b — sonnet1-ts

**Sprint**: [FIX] STEP 2 PER-EPOCH STC ds005385 (apply_inverse_epochs)
**Owner**: sonnet1-ts
**Branch**: scientific/step2-per-epoch
**Pre-condizione**: S-101 done (forward + inverse + evoked STC esistenti).
**OPERATOR DECISION**: OPZIONE A T20:38 — fix wPLI collapse via per-epoch STC.

## ROOT CAUSE

S-101 ha applicato `apply_inverse(evoked, ...)` → 1 STC per condizione (single sample). wPLI su `(1, n_labels, n_times)` collassa a 1.0 perché phase non varia tra epoch (n_epochs=1).

**Fix**: usare `mne.minimum_norm.apply_inverse_epochs(epochs, inverse_operator, lambda2, method='dSPM')` → ritorna `list[SourceEstimate]` (uno per epoch). wPLI su `(n_epochs, n_labels, n_times)` produce valori fisiologici (range 0.05-0.50).

## SUB LIST + PARAMETRI (invariati da S-101)

```python
PILOT_SUBJECTS = ["sub-007", "sub-010", "sub-011", "sub-026", "sub-031"]
INVERSE_METHOD = "dSPM"
LAMBDA2 = 1.0 / 9.0  # snr=3
LOOSE = 0.2
DEPTH = 0.8
L_FREQ = 1.0
H_FREQ = 40.0
SFREQ = 250.0
```

## Cosa fare

1. **Riusa forward + inverse esistenti**:
   - `data/derivatives/mne-bids-pipeline/sub-XXX/eeg/sub-XXX_fwd.fif`
   - `data/derivatives/mne-bids-pipeline/sub-XXX/eeg/sub-XXX_inv.fif`

2. **Carica epochs cleaned** (output STEP 1 preprocessing):
   - `data/derivatives/mne-bids-pipeline/sub-XXX/eeg/sub-XXX_task-RestingState_proc-clean_epo.fif`
   - Filtra epochs per condition tag (EO vs EC).

3. **Apply inverse per-epoch**:
   ```python
   import mne
   from pathlib import Path

   inv_op = mne.minimum_norm.read_inverse_operator(str(inv_path))

   for sub in PILOT_SUBJECTS:
       epochs = mne.read_epochs(epochs_path)
       for cond in ['EO', 'EC']:
           epo_cond = epochs[cond]  # filter by condition
           stcs = mne.minimum_norm.apply_inverse_epochs(
               epo_cond, inv_op,
               lambda2=LAMBDA2,
               method='dSPM',
               return_generator=False,  # tieni list per ora
               verbose=False
           )
           # stcs è list[SourceEstimate], len = n_epochs della condition
           # Salva in HDF5 (formato MNE nativo per list di STC)
           output_path = Path(f"data/derivatives/mne-bids-pipeline/sub-{sub}/eeg/sub-{sub}_task-RestingState_cond-{cond}_inv-dSPM-stcs.h5")
           # mne ha mne.externals.h5io.write_hdf5 o salviamo come npz con concatenazione
           # Alternativa: salva come npz con stack array (n_epochs, n_sources, n_times)
           import numpy as np
           data = np.stack([s.data for s in stcs])  # (n_epochs, n_sources, n_times)
           vertices = stcs[0].vertices  # invariate per tutte le epoch
           tmin = stcs[0].tmin
           tstep = stcs[0].tstep
           np.savez_compressed(
               output_path.with_suffix('.npz'),
               data=data,
               vertices_lh=vertices[0],
               vertices_rh=vertices[1],
               tmin=tmin,
               tstep=tstep,
               n_epochs=len(stcs),
           )
   ```

4. **Output**:
   - 5 sub × 2 cond = 10 file `.npz` (formato salvato come stack np.array invece di HDF5 per riusare extract_label_tc patterns):
     - `data/derivatives/mne-bids-pipeline/sub-XXX/eeg/sub-XXX_task-RestingState_cond-{EO|EC}_inv-dSPM-stcs.npz`
     - Keys: `data` (n_epochs, n_sources, n_times), `vertices_lh`, `vertices_rh`, `tmin`, `tstep`, `n_epochs`.

5. **Reports**:
   - `reports/STEP2b_DS005385_PER_EPOCH.md`:
     - Header timestamp + sub list + parametri.
     - Tabella per (sub × cond): n_epochs, shape per-epoch STC, tempo wall-clock.
     - Disk delta reale (df -h pre/post).
     - Esempio output 1 sub × 1 cond × primi 3 epochs (data shape, mean, std).

## Vincoli

- 5 sub × 2 cond = 10 file output.
- Disk delta atteso: ~1.5-3 GB (n_epochs ~125 × n_sources 8196 × n_times ~250 × 4 bytes ≈ 1 GB per cond × 5 sub × 2 cond, compressed ~1.5-3 GB).
- Verifica `df -h` pre/post per validare delta atteso.
- NIENTE altri sub.

## Gate uscita

- 10 file `.npz` (per-epoch STC).
- `reports/STEP2b_DS005385_PER_EPOCH.md` esiste.
- HB sonnet1-ts done verdict=PASS task=S-101b.
- Queue S-101b status=done.
- **POST-GATE OBBLIGATORIO**: scrivi `.planning/MSG_TO_FATHER_<ts>_S101b_DONE.md` con:
  - Tempo wall-clock per-sub.
  - Disk delta reale (es. da X GB a Y GB liberi).
  - Esempio output 1 sub × 1 cond: file path + shape (n_epochs, n_sources, n_times) + primi 3 epochs valori (mean/std).
  - Eventuali warning (epoch dropped, shape mismatch).
  - Plan S-103b parcellation + S-104b connectivity rerun.
- Auto-claim post: NIENTE (S-103b parcellation rerun gated dopo questo).

## Tempo stimato

15-30 min wall-clock (5 sub × 2 cond × ~125 epochs × inverse compute).
