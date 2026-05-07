# Tesi_2.0 — STATE snapshot

**Generato**: 2026-05-01 (sessione tesi-orch / opus-orch-ts)
**Path repo**: `/home/seraxel/Scrivania/Tesi_2.0/`
**Sorgente**: derivato da analisi `PROGRESS.md`, `reports/STEP1_LOG.md`, `reports/STEP2_PROPOSAL.md` + diff con vecchio repo `~/Scrivania/Tesi/.planning/core/VISION.md` v3.0.

---

## 0. Recovery + Fase 1 + Fase 2 (2026-05-07)

- **Recovery** (18:15): repo ripristinata da Trash a HEAD `21bba74` da opus-father. Master plan, test, derivatives intatti.
- **Fase 1 Audit** (18:15→18:50): 5/5 H-AUDIT sprint completati. Dataset 179 validi, bench 96/96 REPLICABLE.
- **Fase 2 Cleanup** (18:50→19:10): ~4.9 GB recuperati, 22 SYNC archiviati, pytest GREEN. HEAD: `cb29346`.
- **HEAD attuale**: `cb29346` (2026-05-07T19:10)

## 1. Status step-by-step

| Step | Titolo | Stato | Output disponibile |
|------|--------|-------|---------------------|
| 1 | Setup pipeline (install + dataset test + preprocessing) | ✅ DONE 2026-04-28 | `data/derivatives/mne-bids-pipeline/sub-05/eeg/` (epochs, raw filt, report HTML, scores, bads, joblib cache) |
| 2 | Source reconstruction (dSPM, fsaverage, N=15) | ✅ DONE 2026-05-01 | `reports/STEP2_DS005385_PILOT.md`, STC files |
| 3 | Parcellazione (aparc + Schaefer100, N=15) | ✅ DONE 2026-05-01 | `parcellation/extract_label_tc.py` |
| 4 | Connettività FC (4 metric × 4 band, N=15) | ✅ DONE 2026-05-05 | `data/connectivity/ds005385/` 960 files |
| 5 | Feature extraction (32 X matrices N=15) | ✅ DONE 2026-05-05 | `data/features/ds005385/X_*.npz` (30, 2278/4950) |
| 6 | ML classification (96 combo LOSO, N=15) | ✅ DONE 2026-05-06 | `data/results/ds005385/comparison_matrix_N15.json` |
| 7 | E2E N=15 full pipeline | ✅ DONE 2026-05-06 | Winner: `aparc×coh×theta×svm_rbf` BA=0.867, p=0.0 |

## 2. Asset confermati

- **Env**: conda `base`, Python 3.13.12, GPU MSI RTX 4060 (non sfruttata, MNE è CPU-bound). ✅ verificato live 2026-05-01 da VS (tutti import OK).
- **Pacchetti chiave (5 tool prof + sklearn, all installed)**: mne 1.11.0, mne-bids 0.18.0, mne-bids-pipeline 1.10.1, **neuromaps 0.0.5**, mne-connectivity 0.8, mne-features 0.3.2, sklearn 1.8.0.
- **Bonus transitive**: mne-icalabel 0.8.1, nibabel 5.4.2, nilearn 0.13.1, python-picard, pyvista[qt], dask/distributed, meegkit, statsmodels.
- **Niente da installare**. ✅
- **5 link prof canonici**: salvati in vault Obsidian `[[070_THESIS/MNE_PROFESSOR_LINKS]]`.
- **Dataset test (smoke)**: `eeg_matchingpennies` (716 MB, 7 sub BrainVision, BIDS pulito, task 2-class). Solo `sub-05` è stato processato.
- **Dataset scientifico finale**: ⏸ NON SCELTO — candidati `ds005385` (Dortmund Vital, EC/EO, 608 sub, 64 ch) vs `LEMON` (228 sub, 62 ch + MRI). DECISIONE BLOCCANTE.
- **Config**: `config/config_step1_matchingpennies.py` (preprocessing-only, 192 parametri pipeline esposti, override Python).
- **Output STEP 1**: 146 MB derivatives + joblib cache → re-run istantaneo.

## 3. Vincoli operatore (da PROGRESS.md §Vincoli OBBLIGATORI)

1. NON creare pipeline alternative — `mne-bids-pipeline` come base reale.
2. Librerie ammesse: SOLO MNE / mne-bids-pipeline / mne-connectivity / mne-features / sklearn.
3. NO deep learning, NO modelli non necessari, NO tool extra.
4. NO decisioni autonome non giustificate.
5. Step lineari con conferma esplicita.
6. Struttura cartelle fissa (10 dir già create), NO strutture alternative.
7. NO orchestrazioni cross-session (decisione operatore 2026-04-28).

⚠️ **Conflitto operativo**: il prompt corrente abilita orchestrazione tramite `.planning/DISPATCH_QUEUE_tesi.jsonl` + workers Sonnet → contraddice vincolo 7. Ipotesi: vincolo 7 era valido per la fase pre-restart; il restart `Tesi_2.0` con orchestratore `tesi-orch` rilassa quel vincolo. **Da confermare con operatore prima della prima ondata.**

## Fase 1 Audit DONE — 5/5 sprint

| Sprint | Commit | Report |
|--------|--------|--------|
| H-AUDIT-01 | opus1-tesi | `reports/PIPELINE_AUDIT.md` |
| H-AUDIT-02 | 9241452 | `reports/PIPELINE_LEAKAGE_AUDIT.md` |
| H-AUDIT-03 | 25125e1 | `reports/DATASET_SUBJECT_AUDIT.md` — 179 valid sub |
| H-AUDIT-04 | ca2f88e | `reports/BENCH_REPLICABILITY.md` — 96/96 REPLICABLE |
| H-AUDIT-05 | haiku1-tesi | pipeline structure audit |

## Fase 2 Cleanup DONE

| Metrica | Valore |
|---------|--------|
| Cache rimossa | ~700 MB |
| Shadow archiviato (father) | ~4.2 GB |
| SYNC archiviati | 22 (→ `.planning/archive/2026-05-07_phase2_cleanup/sprint_S/`) |
| HEAD post-cleanup | cb29346 |
| pytest post-cleanup | 247 PASS / 63 skip / 0 FAIL |
| Ruff | 25 errori pre-esistenti (task H-HARD-RUFF) |
| Pre-commit | binary missing (task H-HARD-PRECOMMIT) |

## 4. Decisioni in sospeso

| # | Decisione | Bloccante per |
|---|-----------|----------------|
| Q1 | Dataset scientifico finale (ds005385 vs LEMON vs altro) — ↔ VS-2 | Step 3+ su dato reale |
| Q2 | Approvazione STEP 2 PROPOSAL (8 decisioni in `reports/STEP2_PROPOSAL.md` §5) — ↔ VS-1 (go aggregato) | Step 2 esecuzione |
| Q3 | Riallineamento vincolo 7 (orchestrazione cross-session) | Wave 1 workers |
| Q4 | `subjects_dir` esterno vs interno per fsaverage (D5 di STEP2_PROPOSAL) | Step 2 |
| Q5 | Refresh VISION (vecchia v3.0 in repo Tesi/ vs nuovo scope minimal restart) | Tutto |
| Q6 | Conda env `base` vs `tradingai` — VS-3 | Wave 1 esecuzione |
| Q7 | Strategia STEP 3-4-5-6: dispatcher one-shot vs step-by-step vs ibrido — VS-4 | Wave 2+ |

## 5. Diff repo Tesi (vecchio) vs Tesi_2.0 (nuovo)

| Aspetto | Tesi/ (vecchio) | Tesi_2.0/ (nuovo) |
|---------|-----------------|---------------------|
| Pipeline base | `neuro_ml_starter` custom (634 LOC, 8 moduli) | `mne-bids-pipeline` ufficiale come motore |
| Dataset | LEMON download in corso (PID 528009, 220 sub) | matchingpennies test only, scientifico TBD |
| Sprint completati | S01-S13c, S15, S16 (best BA=0.870 aparc×wPLI2×RF FDR-significant) | STEP 1 only |
| Connectivity | wPLI2/PLI/COH/PLV già in produzione, FDR done | Nessuna run |
| Riemannian | Pianificato (coffeine/PyRiemann), non implementato | ❌ ESCLUSO da vincolo 2 |
| Experiment tracking | Custom JSON (D5 v2.1) | Nessuno (TBD) |
| neuromaps | Sprint S-10 READY (richiesta prof) | Cartella `parcellation/` vuota |
| Mne-bids-pipeline | Sprint S-11 BLOCKED da S-10 | ✅ già installata + in uso |
| Stato Q4 dataset | LEMON in download | LEMON candidato non scelto |
| Inferenza statistica | INFERENCE_RULES.md congelato 2026-04-19 | Da riportare |
| Vision | v3.0 riallineata professore (D15 neuromaps prio, D16 wrapper) | DA RISCRIVERE per nuovo scope |

## 6. Background jobs / processi

Nessuno attivo nel repo Tesi_2.0. (PID 528009 LEMON download appartiene a Tesi/ — non riavviato qui.)

## 7. Stato infrastruttura .planning (aggiornato 2026-05-07)

- `.planning/core/` — MASTER_PLAN_THESIS_READY.md, STATE.md, VISION_PROPOSAL_v3.1.md
- `.planning/heartbeats_tesi/` — sonnet1-tesi.json, haiku1-tesi.json, opus1-tesi.json (attivi)
- `.planning/DISPATCH_QUEUE_tesi.jsonl` — 121+ task, queue operativa
- `.planning/archive/2026-05-07_phase2_cleanup/sprint_S/` — 22 SYNC archiviati
- `.planning/research/` — bibliografia.bib (27 entry), draft manuscript sections, CV_STRATEGY.md

## 8. Next actions (post Fase 2)

1. **Gate Fase 3**: ack opus-father per Path A/B (N=30 vs paper N=15)
2. **Symlink fix**: `ln -s ~/Scrivania/Tesi/data/ds005385 data/raw/ds005385` (confermato disponibile)
3. **Fase 3 N=30**: whitelist expansion + rerun Step 4b+5+6+7 con n_perm=1000
4. **Fase 4 hardening**: H-HARD-RUFF + H-HARD-PRECOMMIT
5. **Manuscript**: completare draft Methods + Results con N=15 results definitivi
