# SYNC S-112 — sonnet3-ts

**Sprint**: SCIENTIFIC_PIPELINE_STATUS.md tabella step × completion
**Owner**: sonnet3-ts
**Branch**: docs/pipeline-status

## Deliverable

`reports/SCIENTIFIC_PIPELINE_STATUS.md`:
- Header timestamp.
- Tabella step × sub × atlas × cond × completion (✅/⏳/❌):
  - STEP 1 preprocessing: 5 sub ✅
  - STEP 2 source recon: 5 sub ✅ (S-101)
  - STEP 3 parcellation: 5 sub × 2 atlas × 2 cond ✅ (S-103, 20 npz)
  - STEP 4 connectivity: in flight (S-104)
  - STEP 5-7: pending operator gate
- Summary statistics: file count, disk usage delta.

## Gate
- 1 file output.
- HB sonnet3-ts done verdict=PASS task=S-112.
- Auto-claim post: idle.
