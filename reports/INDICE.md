# Indice dei report

La cartella `reports/` contiene sia i **risultati scientifici** sia i **log tecnici**
prodotti durante lo sviluppo. I file citati da script e test restano qui; i log di processo sono in `archivio_processo/`. Questa pagina dice da dove iniziare.

## 1. Da leggere per primi (risultati e limiti)

| File | Contenuto |
|---|---|
| `RISULTATI_E_LIMITI.md` | Sintesi unica: cosa regge e cosa no (risultato primario, 3 controlli di robustezza, limiti) |
| `DISCUSSION_v3.md` | Discussione dei risultati e framing finale |
| `STATISTICAL_VALIDITY_NOTES.md` | Note di validità statistica (CV per-soggetto, permutation test) |
| `PIPELINE_LEAKAGE_AUDIT.md` | Audit anti-leakage della pipeline ML |

## 2. Risultati per esperimento

| Tema | File |
|---|---|
| Sesso/età su N=179 | `AGE_SEX_FASE3_N179.md`, `AGE_SEX_VALIDITY.md`, `ml_sex_results*.json`, `ml_age_results*.json` |
| Confound età-sesso | `CONFOUND_AGE_SEX_F3.md`, `CONFOUND_AGE_SEX_REMATCH_F3.md` |
| Sensibilità alla metrica di connettività | `SENSITIVITY_CONN_METRIC_F3.md` |
| Trasferibilità e cross-dataset | `TRANSFERABILITY_N79_F2.md`, `CROSS_DATASET_TRANSFER.md`, `CROSS_DATASET_LEMON_SEX_ALTO2.md` |
| Confronto feature | `feature_comparison_n50.json`, `feature_comparison_n100.json` |
| Permutation test del modello vincente | `PERM_1000_WINNER_LOG.md` |

## 3. Log degli step della pipeline

| Step | Pilota / log |
|---|---|
| 1 Preprocessing | `STEP1_LOG.md` |
| 2 Sorgente | `STEP2_LOG.md`, `STEP2_PROPOSAL.md`, `STEP2_DS005385_PILOT.md`, `STEP2b_DS005385_PER_EPOCH.md` |
| 3 Parcellazione | `STEP3_PROPOSAL.md`, `STEP3_DS005385_PILOT.md`, `STEP3b_DS005385_PER_EPOCH.md` |
| 4 Connettività | `STEP4_DS005385_PILOT.md`, `STEP4b_DS005385_EXTENDED.md`, `FC_CONSOLIDATION.md` |
| 5 Feature | `STEP5_DS005385_FEATURES.md`, `FEATURES_AUDIT.md` |
| 6 ML | `STEP6_DS005385_ML.md`, `BASELINE_COMPARISON.md` |
| E2E (demo) | `E2E_MATCHINGPENNIES.md`, `INTEGRATION_TEST.md` |

## 4. Dataset e protocollo

`DS005385_STRUCTURE.md`, `DATASET_SETUP.md`, `SUBSET_POLICY.md`, `DATA_AUDIT.md`,
`BIDS_VALIDATION.md`, `LEMON_DOWNLOAD_AUDIT.md`, `EXPERIMENTS_N15.md`, `EXPERIMENTS_N30.md`,
`EXPERIMENTS_N50.md`.

## 5. Prestazioni e qualità del codice

`PERF_BENCHMARK.md`, `PERF_PROFILE.md`, `HOT_PATH_OPT.md`, `BENCH_REPLICABILITY.md`,
`COVERAGE.md`, `COVERAGE_THRESHOLDS.md`, `TESTS_DEDUPE.md`.

## 6. Log di processo

Audit, revisioni, SBOM, import da note interne e simili sono in `archivio_processo/`.
Documentano il processo di sviluppo, non i risultati: non servono alla lettura.

## 7. Figure

`figures/` — grafici usati nei report (architettura, balanced accuracy, heatmap, ecc.).
Le figure `*.placeholder` sono segnaposto di figure non generate.
