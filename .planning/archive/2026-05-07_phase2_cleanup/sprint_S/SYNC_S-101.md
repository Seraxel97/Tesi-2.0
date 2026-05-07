# SYNC S-101 — sonnet1-ts

**Sprint**: [WAVE-SCIENTIFIC-002] STEP 2 SOURCE RECON PILOT 5 sub
**Owner**: sonnet1-ts
**Branch**: scientific/step2-source-pilot
**Pre-condizione**: S-100 done (BIDS analysis), S-100b done (subset policy + sub list).
**OPERATOR APPROVAL**: Yes (T19:14 via TG).

## SUB LIST CONFERMATA OPERATORE

```python
PILOT_SUBJECTS = ["sub-007", "sub-010", "sub-011", "sub-026", "sub-031"]
```

## PARAMETRI STEP 2 (da brief operatore)

- `inverse_method = "dSPM"`
- `snr = 3` → `lambda2 = 1 / snr**2 = 1/9 ≈ 0.111`
- `loose = 0.2`
- `depth = 0.8`
- `noise_cov = "ad-hoc"` (resting-state, no empty room)
- `subjects_dir = "/home/seraxel/mne_data/MNE-fsaverage-data"` (esterno)
- `use_template_mri = "fsaverage"`
- `eeg_template_montage` da inferire da channels.tsv ds005385 (probabilmente standard_1020 o easycap-M1)
- `spacing = "oct6"` (consistente con STEP 2 matchingpennies)

## Cosa fare

1. **Crea config dedicato** `config/config_step2_ds005385_pilot.py`:
   - Eredita da `config/config_base.py` (post DR-SIMPL-config-validate).
   - Override: `subjects = PILOT_SUBJECTS`, `bids_root = "data/raw/ds005385"`, `task = <da BIDS, vedi S-100 output>`, source recon params come sopra.

2. **Esegui pipeline mne-bids-pipeline** sui 5 sub:
   ```bash
   mne_bids_pipeline --config config/config_step2_ds005385_pilot.py \
       --steps preprocessing,sensor,source 2>&1 | tee reports/STEP2_DS005385_PILOT_run.log
   ```
   Forwarding probabile fail su rendering 3D (xvfb missing) → bypass via `source_reconstruction/finalize_inverse.py` (post DR-SIMPL-path-helpers).

3. **Finalize inverse + STC** per ogni sub via:
   ```bash
   for sub in 007 010 011 026 031; do
       python source_reconstruction/finalize_inverse.py --subject "$sub" --task <task_name> \
           --method dSPM --loose 0.2 --depth 0.8 --lambda2 0.111
   done
   ```

4. **Output**:
   - `data/derivatives/mne-bids-pipeline/sub-{007,010,011,026,031}/eeg/sub-XXX_fwd.fif`
   - `data/derivatives/mne-bids-pipeline/sub-XXX/eeg/sub-XXX_inv.fif`
   - `data/derivatives/mne-bids-pipeline/sub-XXX/eeg/sub-XXX_task-XXX_cond-{EO,EC}_inv-dSPM-{lh,rh}.stc`
   - **Note**: brief operatore suggerisce `data/stcs/ds005385/<sub>_<run>.npz`. Adatta naming se serve, ma format STC nativo MNE è preferibile (riusa `mne.read_source_estimate`).

5. **Reports**:
   - `reports/STEP2_DS005385_PILOT.md`:
     - Header timestamp + sub list.
     - Per ogni sub: tempo wall-clock, shape STC, vertices, condizioni (EO/EC), warning.
     - Wall-clock totale + disk delta reale.

## Vincoli

- SOLO 5 sub (S-007/010/011/026/031). NIENTE altri sub.
- DISK: ~5-15 GB delta atteso (5 sub × ~2-3 GB derivatives). Verifica `df -h` pre/post.
- NIENTE source recon su altri sub anche se workers hanno tempo.
- Heartbeat ogni 5-7 min con progress (es. "sub-010 done, sub-011 in progress").

## Gate uscita

- 5 sub × 5+ file output (fwd, inv, ≥2 STC per condizione).
- `reports/STEP2_DS005385_PILOT.md` esiste con verdict.
- HB sonnet1-ts done verdict=PASS task=S-101.
- Queue S-101 status=done.
- **POST-GATE OBBLIGATORIO**: scrivi `.planning/MSG_TO_FATHER_<ts>_S101_DONE.md` con:
  - Tempo wall-clock totale + per-sub.
  - Disk delta reale (df -h pre/post).
  - Esempio output 1 sub (file paths + STC shape).
  - Eventuali warning/errori.
  - Plan STEP 3 parcellation (S-103) da chiedere ACK operatore.
- Auto-claim post: NIENTE. Step 3-7 gated, attendi father ACK.

## Tempo stimato

15-30 min wall-clock per 5 sub (forward+inverse light, STC su evoked/condition).
