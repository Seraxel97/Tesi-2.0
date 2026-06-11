# SYNC S-108 — sonnet2-ts

**Sprint**: Pre-flight check scientific outputs S-101+S-103
**Owner**: sonnet2-ts
**Branch**: scientific/preflight-check
**Pre-condizione**: S-101 done.

## Deliverable

1. `scripts/verify_scientific_outputs.py`:
   - CLI args: `--sub-list 007 010 011 026 031`.
   - Per S-101: verifica fwd.fif, inv.fif, *.stc per ogni sub × cond (EO/EC).
   - Per S-103 (waiting): verifica npz quando disponibili.
   - Output table: sub | step | file | exists | size | shape.
2. `reports/SCIENTIFIC_PREFLIGHT.md`:
   - Header timestamp, sub list.
   - Tabella verifica.
   - Verdict CLEAN | MISSING.

## Vincoli
- 2 file output.
- Tempo <10 min.

## Gate
- 2 file deliverable.
- HB sonnet2-ts done verdict=PASS task=S-108.
- Auto-claim post: idle waiting S-103 done.
