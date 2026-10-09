# Connectivity Outputs Pre-flight Check

**Sprint**: S-111  **Data**: 2026-05-01T18:17:42Z  **Worker**: sonnet2-ts
**Verdict**: WAITING  CLEAN=0  FAIL=0  WAITING=5

---

## Tabella verifica

| Sub | Atlas | Cond | Metric | Band | Verdict | Shape | NaN | Range | Symmetry |
|-----|-------|------|--------|------|---------|-------|-----|-------|----------|
| sub-007 | aparc | EO | wpli | alpha | **WAITING** | - | - | - | - |
| sub-010 | aparc | EO | wpli | alpha | **WAITING** | - | - | - | - |
| sub-011 | aparc | EO | wpli | alpha | **WAITING** | - | - | - | - |
| sub-026 | aparc | EO | wpli | alpha | **WAITING** | - | - | - | - |
| sub-031 | aparc | EO | wpli | alpha | **WAITING** | - | - | - | - |

---

## Note lifecycle FC

- **FC_DIR**: `data/connectivity/ds005385/`
- **Pattern file**: `{sub}_atlas-{atlas}_cond-{cond}_metric-{metric}.npz`
- **Chiave npz**: `fc_{band}` (es. `fc_alpha`, `fc_beta`)
- **Metriche signed** [-1,1]: wpli, imcoh, ciplv, pli
- **Metriche positive** [0,1]: wpli2_debiased, plv, coh
- **Simmetria**: |M - M.T|.max() < 1e-5
- **S-104 status**: IN FLIGHT (waiting)

S-104 in flight (sonnet1-ts). Ri-eseguire dopo completamento per aggiornare il report.
