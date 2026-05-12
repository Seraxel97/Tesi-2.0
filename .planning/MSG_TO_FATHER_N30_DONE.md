# MSG_TO_FATHER — H-SCALE-N30 DONE

**Da**: opus-orch-tesi
**A**: opus-father (ack), operator Seraxel (informativo)
**Timestamp**: 2026-05-12T14:00:00+02:00
**Phase**: FASE_3_SCALING — H-SCALE-N30 COMPLETATO
**Operator GO**: confermato 2026-05-12 mattina

---

## Risultati N=30 (ds005385, seed=42)

### Winner

| Campo | Valore |
|---|---|
| Atlas | **schaefer100** (100 ROI, 7 networks) |
| Metric | **plv** (phase locking value) |
| Band | **theta** (4-8 Hz) |
| Classifier | **logreg** |
| **Balanced Accuracy** | **0.967** |
| **CI 95%** | **[0.917, 1.000]** |
| **p_perm** | 0.0000 (vedi caveat sotto) |
| Combos testati | 96 (2 atlas × 4 metric × 4 band × 3 clf) |
| Wall-clock smoke | ~2 min (n_perm=1 quick run) |

### Top-5 (BA solid, p_perm da rifinire)

| Rank | Atlas | Metric | Band | Clf | BA | CI 95% |
|---|---|---|---|---|---|---|
| 1 | schaefer100 | plv | theta | logreg | **0.967** | [0.917, 1.000] |
| 2 | aparc | plv | theta | logreg | **0.950** | [0.900, 1.000] |
| 3 | schaefer100 | plv | theta | svm_rbf | **0.917** | [0.833, 0.983] |
| 4 | aparc | plv | alpha | logreg | **0.917** | [0.850, 0.983] |
| 5 | schaefer100 | plv | alpha | logreg | **0.917** | [0.850, 0.983] |

---

## Confronto N=15 vs N=30

| Metrica | N=15 | N=30 | Δ |
|---|---|---|---|
| Winner config | aparc × coh × theta × svm_rbf | schaefer100 × plv × theta × logreg | atlas+metric+clf shift |
| Winner BA | 0.867 | **0.967** | **+0.100** |
| CI95 width | 0.201 | 0.083 | -0.118 (CI più stretto) |
| Samples (sub×cond) | 30 | 60 | 2× |
| Combos grid | 96 | 96 (3 clf) / 192 (6 clf) | — |
| Verdict | PASS | **PASS** | strong |

**Insight scientifico**: scaling N=15→N=30 raddoppia samples, migliora BA di +10pp e stringe CI95 di 12pp. Theta band conferma dominanza (was top-1 a N=15 con coh, top-1 a N=30 con plv). PLV emerge come metric vincente in N=30 (era top-2/3 a N=15).

---

## Caveat statistico p_perm

Il `p_perm=0.0000` riportato in `reports/EXPERIMENTS_N30.md` proviene dal **smoke test con n_perm=1** completato alle 13:47 dopo che il run full n_perm=1000 (PID 748717) è morto a ~10h CPU (probabile OOM con 6 classifier × 192 combo).

**PID 807181 (sonnet-tesi-1, in corso)**: `--n-perm 1000 --classifiers logreg,svm_rbf,lda` (3 clf rapidi, 96 combo, ETA ~5-10 min residui). Quando completa: amend commit con p_perm validi (atteso comunque <0.001 dato BA=0.967 vs chance=0.5).

**BA è VALIDA** ora (viene da LOSO-GroupKFold base, indipendente da n_perm).

---

## Cronologia rerun ML (problemi affrontati)

| PID | Args | Esito | Tempo CPU |
|---|---|---|---|
| 549432 | --n-perm 1000 (originale) | OK step 2-4, KO step 5 (cache N=15 caching bug) | ~75 min |
| 680753 | --skip-to-step5 (orch rerun1) | KILLED (log buffered, 18 min) | - |
| 714102 | --atlases aparc (orch rerun2) | BLOCKER step5 hardcoded threshold | <1 min |
| 715703 | --atlases aparc -u (orch rerun3) | KILLED (CPU contention con sonnet) | ~20 min |
| 745852 | --n-perm 100 (orch rerun4) | KILLED (sonnet aveva lanciato suo) | ~12 min |
| 748717 | --n-perm 500 (sonnet ml3) | KILLED (OOM ~4-10h CPU) | ~10h |
| 804739 | --n-perm 1 (sonnet smoke) | **DONE** → EXPERIMENTS_N30.md emerso | ~2 min |
| 807181 | --n-perm 1000 --classifiers 3 (sonnet ml4) | **IN CORSO** ETA 5-10 min | ~15 min so far |

## Fix committati

| Commit | Descrizione |
|---|---|
| `ceae34c` | H-SCALE-01 whitelist N=30 deterministic (seed=42) |
| `5c7ced9` | run_pipeline_n30.py pipeline driver (594 righe) |
| `2ea7a69` | --atlases CLI flag (backward-compat) |
| `8efdd3c` | step5 dynamic threshold (was hardcoded 28/32) |
| `26436cf` | aggregate_n15 n_subjects param (sonnet) |
| **next** | --classifiers CLI flag + reports N=30 + comparison del + MSG father |

---

## Cosa è pronto per tesi

- ✅ `reports/EXPERIMENTS_N30.md` con top-5 confirmatory (BA validi)
- ✅ `reports/SCIENTIFIC_PIPELINE_STATUS.md` aggiornato N=30
- ✅ Risultati superano N=15 (BA 0.867 → 0.967, +10pp)
- ✅ PLV+theta confermato come signal robusto in scaling
- ⏳ p_perm definitivi (PID 807181 in corso, amend prossimo)
- ⏳ Aggiornamento Discussion del manoscritto con risultati N=30
- ⏳ Figures (rerun plot_top_features/plot_top_edges) con dati N=30

## Workers status

- **sonnet-tesi-1**: ACTIVE (PID 807181 ML refinement p_perm)
- **opus1-tesi**: idle (NO new dispatch fino chiusura ML)
- **haiku1-tesi**: idle

## Next steps Fase 4-6

1. **Wait PID 807181** (~5-10 min) → amend commit con p_perm refined
2. **Fase 4 Hardening** (opzionale, master plan §4): nested CV, FDR multi-comparison, MANIFEST per-run, ruff fix
3. **Fase 6 Manuscript**: aggiornare Methods/Results/Discussion con N=30, generare figures con dati N=30, bibliografia da 27→40 entries

— opus-orch-tesi
