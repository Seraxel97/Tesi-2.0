# Tesi_2.0 — Tracking progresso

**Path**: `/home/seraxel/Scrivania/Tesi_2.0/`  
**Ultimo aggiornamento**: 2026-05-01 (S-66, sonnet1-ts)

---

## Stato step pipeline

| Step | Titolo | Stato | Data | Log |
|------|--------|-------|------|-----|
| 1 | Preprocessing (mne-bids-pipeline) | ✅ DONE | 2026-04-27→28 | [reports/STEP1_LOG.md](reports/STEP1_LOG.md) |
| 2 | Source reconstruction (dSPM, sub-05) | ✅ DONE | 2026-05-01 | [reports/STEP2_LOG.md](reports/STEP2_LOG.md) |
| 3 | Parcellazione (aparc, 68 ROI) | ✅ DONE | 2026-05-01 | `parcellation/extract_label_tc.py` |
| 4 | Connettività funzionale (wPLI, bande) | ✅ DONE | 2026-05-01 | `connectivity/fc_dispatcher.py` |
| 5 | Feature extraction (mne-features + FC flatten) | ✅ DONE | 2026-05-01 | `features/dispatcher.py` |
| 6 | ML classification (LOSO GroupKFold, 5 algo) | ✅ DONE | 2026-05-01 | `ml_training/ml_dispatcher.py` |
| 7 | E2E su dataset scientifico | ❌ BLOCKED | — | Attesa Q1 (dataset scientifico) |

**E2E smoke su matchingpennies** (sub-05): ✅ PASS — 8 epoch, aparc, wpli, 10s wall. Vedi `tests/test_integration_final.py`.

---

## Sessione 2026-05-01 — statistiche

| Metrica | Valore |
|---------|--------|
| Sprint completati | **113** |
| Worker attivi | 4 (sonnet1/2/3-ts, haiku1-ts) |
| Batch wave dispatched | ~21 |
| Bug critici risolti | 1 (`run_e2e_matchingpennies.py:141`) |
| Deliverable prodotti | 19+ file (vedi SESSION_SUMMARY) |
| Sprint bloccati (Q1) | 2 (S-07, S-47) |

Vedi `.planning/SESSION_SUMMARY_2026-05-01.md` per il dettaglio completo.

---

## Decisioni aperte

| # | Tema | Stato | Urgenza |
|---|------|-------|---------|
| Q1 | Dataset scientifico finale (ds005385 vs LEMON) | 🔴 APERTA | **URGENTE** — blocca Step 7 |

Tutte le altre decisioni (Q2–Q7) sono state chiuse autonomamente con default reversibili.

---

## Infrastruttura prodotta (2026-05-01)

### Moduli `common/`
- `run_id.py` — run-id standard (timestamp + git_sha + config_hash)
- `logger.py` — JSON structured logger
- `reproducibility.py` — manifest builder per riproducibilità
- `run_schema.py` — JSONSchema + validator per output pipeline
- `paths.py` — path security helpers
- `queue_lib.py` — queue lock/update (fcntl)
- `config_validator.py` — config schema validator

### Moduli `analysis/`
- `stats_utility.py` — ci_bootstrap, cohen_d, power analysis
- `bench_steps.py` — pipeline step benchmarker

### Test (`tests/`)
- `test_integration_final.py` — E2E integration (2/2 PASS)
- `test_perf_regression.py` — perf regression (4/4 PASS in 5s)
- 20+ altri test (244 PASS totali al 2026-05-01)

### Script (`scripts/`)
- `generate_mock_bids.py` — mock ECEO BIDS dataset generator
- `archive_sync_files.sh` — SYNC file archiver
- `archive_full_session.sh` — session history archiver

### Reports notevoli
- `reports/PERF_BASELINE.json` — timing baseline + CI thresholds
- `reports/INTEGRATION_TEST.md` — E2E integration report
- `reports/PERF_BENCHMARK.md` — step-level benchmark (bottleneck: inverse_parcellation 55%)
- `.planning/SESSION_SUMMARY_2026-05-01.md` — session summary completo

### Research/docs
- `.planning/research/citation_style.csl` — IEEE CSL (Zotero/Pandoc)
- `.planning/research/bibliografia.bib` — 27 BibTeX entries
- `.planning/research/CV_STRATEGY.md` — strategia CV + §5 bootstrap BCa

---

## Dataset

| Nome | Ruolo | Path | Dimensione | Stato |
|------|-------|------|------------|-------|
| eeg_matchingpennies | Smoke test tecnico | `data/eeg_matchingpennies/` | 716 MB | ✅ integrato |
| ds005385 (Dortmund Vital) | Candidato scientifico | `~/Scrivania/Tesi/data/ds005385/` | 21 GB | ⏸ attesa Q1 |
| LEMON | Candidato scientifico | `~/Scrivania/Tesi/data/lemon/` | 65 GB | ⏸ attesa Q1 |

---

## Vincoli operatore (invariati)

1. Usare `mne-bids-pipeline` come base reale
2. Librerie: MNE / mne-bids-pipeline / mne-connectivity / mne-features / scikit-learn
3. NO deep learning, NO tool extra
4. Struttura cartelle fissa (10 dir), NO alternative
5. Orchestrazione interna a Tesi_2.0/ (Q3 chiusa autonomamente)

---

## Prossimi passi

1. **Rispondere a Q1** → sblocca S-07 e S-47 → permette Step 7 su dataset scientifico
2. **Performance P0** → refactor `inverse_parcellation` con `apply_inverse_epochs()` batch (riduzione ~40%)
3. Completare sprint finali: S-64 (archive), DR-FINAL-handover, DR-FINAL-validation
