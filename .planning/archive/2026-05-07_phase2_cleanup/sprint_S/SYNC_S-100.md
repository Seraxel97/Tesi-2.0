# SYNC S-100 — sonnet1-ts

**Sprint**: [WAVE-SCIENTIFIC-001] STEP 1 dataset prep ds005385
**Owner**: sonnet1-ts
**Branch**: scientific/step1-dataset
**Pre-condizione**: ds005385 symlink ✅ (data/raw/ds005385/ → ~/Scrivania/Tesi/data/ds005385/, 200 sub, 21 GB).

## Cosa fare

1. **Verifica symlink + struttura BIDS**:
   ```bash
   ls -la data/raw/ds005385/
   python -c "from mne_bids import print_dir_tree; print_dir_tree('data/raw/ds005385', max_depth=3)"
   ```

2. **Analizza struttura BIDS**:
   - `participants.tsv`: read + count, age/sex distribution, group filter.
   - `events.tsv` per 1 sub random: identifica codifica EO/EC (run_label vs event_value).
   - `task-*_eeg.json`: sfreq, channel count, montage type.

3. **Identifica condizioni EO vs EC**:
   - Scan `sub-*/eeg/sub-*_task-*_events.tsv` per pattern.
   - Output: dict `{condition: ["sub-001_run-1", "sub-001_run-2", ...]}`.

4. **Output**:
   - `reports/DS005385_STRUCTURE.md`:
     - Header: timestamp, dataset name, source path symlink.
     - Tabella: n_subjects=200, n_channels, sfreq, n_runs/sub, conditions encoding.
     - Sezione "EO/EC label mapping" con codifica decisa.
     - Sezione "Quality flags" (es. sub esclusi se README menziona).
   - `config/labels_ds005385.py`:
     ```python
     """Label mapping ds005385 EO vs EC."""
     LABEL_EO = "eyes-open"
     LABEL_EC = "eyes-closed"
     # Mapping derivato da events.tsv analysis
     CONDITION_MAP = {
         "EO": [...],
         "EC": [...],
     }
     ```

## Vincoli

- NIENTE preprocess vero (è solo analisi struttura).
- NIENTE multi-sub processing (rimando S-101 PILOT).
- 2 file output: report MD + config Python.
- Tempo previsto: 15-30 min.

## Gate

- 2 file deliverable.
- HB sonnet1-ts done verdict=PASS task=S-100.
- Queue S-100 status=done.
- **POST-GATE OBBLIGATORIO**: scrivi `.planning/MSG_TO_FATHER_<ts>_S100_DONE.md` con summary BIDS + EO/EC codifica per sblocco S-100b.
- Auto-claim post: NON fare auto-claim S-101 (gated OPERATOR_APPROVE_5SUB). Resta idle.
