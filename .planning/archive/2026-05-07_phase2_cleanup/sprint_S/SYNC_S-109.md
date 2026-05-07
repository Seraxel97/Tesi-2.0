# SYNC S-109 — sonnet3-ts

**Sprint**: Documentation update post-Q1 ds005385
**Owner**: sonnet3-ts
**Branch**: docs/post-q1-update
**Pre-condizione**: S-100, S-100b done.

## Deliverable

1. **README.md** sezione "Current dataset":
   - ds005385 (Dortmund Vital Study), 200 sub totali, **subset N=15** (operator hard constraint).
   - PILOT 5 sub: sub-007/010/011/026/031.
   - Path symlink: `data/raw/ds005385` → `~/Scrivania/Tesi/data/ds005385/`.
   - Cross-ref `config/subjects_whitelist.py`, `config/labels_ds005385.py`, `reports/DS005385_STRUCTURE.md`.

2. **docs/PIPELINE_OVERVIEW.md**: aggiornare cross-ref ds005385 task=RestingState, conditions=EO/EC.

3. **PROGRESS.md** (se serve aggiungi sezione "Current scientific run") — verifica se già aggiornato da S-66.

## Vincoli
- 2-3 file aggiornati.
- NO emoji.

## Gate
- File aggiornati.
- HB sonnet3-ts done verdict=PASS task=S-109.
- Auto-claim post: idle.
