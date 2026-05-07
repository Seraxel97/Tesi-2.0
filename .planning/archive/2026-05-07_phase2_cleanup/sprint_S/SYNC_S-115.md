# SYNC S-115 — sonnet3-ts

**Sprint**: SCIENTIFIC_PIPELINE_STATUS update fix S-101b in flight
**Owner**: sonnet3-ts
**Branch**: docs/pipeline-status-update

## Deliverable

Aggiorna `reports/SCIENTIFIC_PIPELINE_STATUS.md` (S-112) con sezione:

```markdown
## Fix S-101b (per-epoch STC) — in flight 2026-05-01

**Issue identified S-104**: wPLI valori collassati a 1.0 (range atteso 0.05-0.50).

**Root cause**: S-101 ha applicato apply_inverse(evoked, ...) → 1 STC per condizione (single sample), no phase variability.

**Fix**: S-101b applica apply_inverse_epochs → list[STC] per epoch, ripristina phase variance.

**Pipeline status post-fix atteso**:
- S-101b: 5 sub × 2 cond = 10 file per-epoch STC.
- S-103b: 5 sub × 2 atlas × 2 cond = 20 file per-epoch label_tc (n_epochs, n_labels, n_times).
- S-104b: 40 FC matrix con valori fisiologici.
```

## Gate
- File aggiornato.
- HB sonnet3-ts done verdict=PASS task=S-115.
- Auto-claim post: idle.
