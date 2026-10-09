# FASE 3 — Risultati ML Età + Sesso N=179

**Data**: 2026-06-05T00:03:56+00:00
**Coorte**: ds005385 N=179 (whitelist completa locale, late_ses1==0; nessun campionamento, il seed 43 riguarda solo la N=100)
**Feature winner**: X_aparc_plv_theta (2278-dim PLV theta aparc)
**Protocollo**: GroupKFold K=5 outer / K=3 inner (solo sesso; età: RF senza tuning), perm subject-level n=1000, boot cluster-subject n=1000

## 1. Classificazione Sesso — baseline 2278-dim

| Metrica | Valore | CI95 | p_perm |
|---------|--------|------|--------|
| BA | **0.795** | [0.744, 0.843] | 0.0010 |
| Null BA (mean) | 0.499 | — | — |

Significativo (α=0.05): **SÌ**
Letteratura (Kollia 2022, N=100): BA≈0.70-0.75. N=100 FASE 1: BA=0.713.

## 2. Regressione Età — baseline 2278-dim

| Metrica | Valore | CI95 |
|---------|--------|------|
| MAE (anni) | **12.26** | [11.31, 13.32] |
| R² | **0.082** | [-0.014, 0.154] |
| Brain-age gap (mean) | 0.27 anni | — |
| p_perm (R²) | 0.0010 | — |

Significativo al permutation test (α=0.05): **SÌ** (p_perm=0.0010).

> ⚠️ **Nota di rigore (F1) — effetto DEBOLE, da non sovra-interpretare:**
> - Il **CI95 di R² = [-0.014, 0.154] include 0 (e valori negativi)**: il permutation test
>   (p=0.001) e il CI95 cluster-bootstrap divergono → il segnale è ai **limiti della rilevabilità**.
>   La divergenza va dichiarata, non nascosta.
> - **R²=0.082 spiega <9% della varianza dell'età**: significatività *statistica* ≠ rilevanza
>   *pratica*. MAE=12.26 anni è al limite superiore della letteratura (Franck 2019: 8-12 anni).
> - Conclusione onesta: l'età è **debolmente** predicibile dalle feature FC (segnale presente ma
>   piccolo), non un predittore clinicamente utile.

Letteratura (Franck 2019, N>200): MAE≈8-12 anni. N=100 FASE 1: MAE=12.52.

## 3. Graph-Theory 8-dim vs Baseline — FDR-BH

| Confronto | Score | p_raw | p_fdr | Sig? |
|-----------|-------|-------|-------|------|
| sex_baseline | BA=0.795 | 0.0010 | 0.0013 | ✅ |
| sex_gt | BA=0.656 | 0.0010 | 0.0013 | ✅ |
| age_baseline | R²=0.082 | 0.0010 | 0.0013 | ✅ |
| age_gt | R²=-0.194 | 0.9061 | 0.9061 | ❌ |

## 4. Confronto N=100 vs N=179

| Target | Metrica | N=100 FASE 1 | N=179 FASE 3 | Δ |
|--------|---------|-------------|-------------|---|
| Sesso | BA | 0.713 | 0.795 | +0.082 |
| Età | MAE (anni) | 12.52 | 12.26 | -0.26 |
| Età | R² | 0.097 | 0.082 | -0.015 |

## 5. Limitazioni

- Sorgenti su fsaverage (no MRI individuale): distorsione spaziale per-soggetto.
- PLV sensibile a volume conduction residuo (mitigato da parcellazione aparc).
- schaefer100 non utilizzato (incompleto su N=100, non ripetuto su N=179).
- n_perm=1000: p_perm ≥ 1/(n_perm+1) = 0.00100.

---
*Generato da scripts/run_ml_age_sex_n179.py — 2026-06-05T00:03:56+00:00*
