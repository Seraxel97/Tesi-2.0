# SYNC S-114 — sonnet2-ts

**Sprint**: Lesson learned wPLI collapse — METHODS_v1.md update
**Owner**: sonnet2-ts
**Branch**: manuscript/lesson-learned

## Deliverable

1. Aggiungi a `.planning/research/METHODS_v1.md` sezione 5 (Functional connectivity) **subsezione "Methodological note: per-epoch vs evoked STC for wPLI"**:
   - wPLI is undefined for single-epoch (n=1) data: phase difference variance = 0 → collapse to 1.0.
   - Best practice: apply inverse PER-EPOCH (mne.minimum_norm.apply_inverse_epochs) before computing wPLI.
   - Validation: range fisiologico atteso 0.05-0.50.
   - Cite: Vinck 2011 (wPLI mathematical framework) + observation Tesi_2.0 S-104 → S-101b fix.

2. `reports/LESSON_LEARNED_WPLI.md`:
   - Header timestamp.
   - Issue (S-104 wPLI=1.0 col).
   - Root cause (single-epoch evoked STC).
   - Fix (per-epoch S-101b).
   - Validation criteria post-fix (range 0.05-0.50).

## Vincoli
- 1-2 file output.

## Gate
- 2 file deliverable.
- HB sonnet2-ts done verdict=PASS task=S-114.
- Auto-claim post: idle.
