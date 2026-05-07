# SYNC S-111 — sonnet2-ts

**Sprint**: Pre-flight S-104 connectivity output validation
**Owner**: sonnet2-ts
**Branch**: scientific/preflight-step4

## Deliverable

1. `scripts/validate_connectivity_outputs.py`:
   - CLI: `--sub 007 --atlas aparc --cond EO --metric wpli --band alpha`.
   - Verifica file `.npz` esiste, carica, check shape simmetrica, no NaN, range [-1,1] o [0,1] per metric.
   - Output table verifica.

2. `reports/CONN_PREFLIGHT.md`: verbose check lifecycle FC output.

## Gate
- 2 file output.
- HB sonnet2-ts done verdict=PASS task=S-111.
- Auto-claim post: idle waiting S-104 done.
