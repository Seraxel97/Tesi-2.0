# SYNC S-116 — haiku1-ts

**Sprint**: Vault CONNECTIVITY_METRICS lesson per-epoch wPLI
**Owner**: haiku1-ts
**Branch**: vault/lesson-wpli

## Deliverable

Aggiungi a `~/Documenti/ObsidianVault/050_METHODS/CONNECTIVITY_METRICS.md` sezione warning:

```markdown
## ⚠️ Common pitfall: wPLI single-epoch collapse

wPLI è undefined per single-epoch input (n_epochs=1):
- Phase difference variance = 0 → wPLI = 1.0 spurious.
- Best practice: usare apply_inverse_epochs (NOT apply_inverse on evoked) prima di compute wPLI.
- Validation range fisiologico atteso: 0.05-0.50.

Fonte: Tesi_2.0 S-104 issue → S-101b fix (2026-05-01).
```

## Gate
- 1 file aggiornato in vault.
- HB haiku1-ts done verdict=PASS task=S-116.
- Auto-claim post: idle.
