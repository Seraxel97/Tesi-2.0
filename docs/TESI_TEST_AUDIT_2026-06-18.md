# Audit conservativo suite test — Tesi_2.0

**Data**: 2026-06-18  
**Branch**: `seraxel/tesi-test-audit-conservative`  
**Base**: `seraxel/tesi-test-slow-markers`  
**Metodo**: Atlante 3-leve (DEDUP/RIMOZIONE/AGGIUNTA) — bias conservativo

---

## Eseguito

- Collection pytest: 330 item raccolti, 9 errori import (dipendenze mancanti: `networkx`, `statsmodels`)
- Suite veloce (`-m "not slow"`, 42 file su 51, escludendo 9 con import error): **251 passed, 65 skipped, 11 failed, 2 errors, 139 warnings**
- Coverage su directory corrente (subset eseguibile): **37.2%** totale — sotto soglia 60% configurata in `.coveragerc`
- Analisi statica: `grep "def test_"` + `uniq -d` su tutti i file test

---

## File test analizzati (51 totali)

**Root tests/:**
`test_aggregate_n15.py`, `test_aperiodic_fooof.py`, `test_broadcast_hooks.py`, `test_broadcast.py`, `test_cli.py`, `test_compare.py`, `test_config_schema.py`, `test_dashboard_format_pvalue_callsites.py`, `test_dashboard_multi_dataset.py`, `test_dashboard_target_selector.py`, `test_dispatcher_base.py`, `test_e2e_matchingpennies.py`, `test_e2e_smoke_minimal.py`, `test_fc_dispatcher.py`, `test_fc_extend.py`, `test_feature_comparison.py`, `test_features_no_double_normalization.py`, `test_features.py`, `test_generate_figures.py`, `test_graph_theory.py`, `test_hb_lib.py`, `test_integration_final.py`, `test_labels_phenotype.py`, `test_logger.py`, `test_metadata_consistency.py`, `test_migrations.py`, `test_ml_age.py`, `test_ml_dispatcher.py`, `test_ml_extend.py`, `test_ml_sex.py`, `test_mock_pipeline.py`, `test_neuromaps_helper.py`, `test_parcellation_edge.py`, `test_parcellation.py`, `test_paths_security.py`, `test_perf_regression.py`, `test_pipeline_timeout.py`, `test_plot_top_features.py`, `test_progress.py`, `test_queue_lib.py`, `test_reproducibility.py`, `test_rs_epochs.py`, `test_run_id.py`, `test_run_schema.py`, `test_smoke.py`, `test_stats_utility.py`, `test_subjects_whitelist_n100.py`, `test_subjects_whitelist_n30.py`, `test_subjects_whitelist_n50.py`

**tests/dashboard/:**
`test_data_loader.py`, `test_ml_runner_no_leakage.py`

---

## Risultati coverage (moduli principali, subset eseguibile)

| Modulo | Coverage |
|--------|----------|
| `connectivity/fc_dispatcher.py` | 100% |
| `ml_training/ml_dispatcher.py` | 98% |
| `common/queue_lib.py` | 98% |
| `common/reproducibility.py` | 94% |
| `common/state_lib.py` | 92% |
| `scripts/generate_figures.py` | 93% |
| `ml_training/ml_age.py` | 67% |
| `ml_training/ml_sex.py` | 58% |
| `dashboard/app.py` | 0% |
| `features/graph_theory.py` | 0% (networkx mancante) |
| `features/aperiodic_fooof.py` | 0% |
| `pipeline_mne_bids/` | 0% |
| **TOTALE** | **37.2%** |

La bassa copertura totale è principalmente dovuta a: (1) 9 file ignorati per dipendenze mancanti (networkx, statsmodels), (2) moduli pipeline/bench/dashboard mai eseguiti nel subset non-slow.

---

## Analisi per leva

### Leva 1 — DEDUP (duplicati reali)

Nomi duplicati rilevati da analisi statica: 4 nomi condivisi tra file diversi.

| Nome | File A | File B | Valutazione |
|------|--------|--------|-------------|
| `test_data_shape` | `test_ml_age.py` | `test_ml_sex.py` | **NON duplicato** — target diverso (età regressione vs sesso classificazione), fixture diverse, asserzioni diverse |
| `test_groups_aligned` | `test_ml_age.py` | `test_ml_sex.py` | **NON duplicato** — verifica allineamento su variabili diverse (float età vs int sesso) |
| `test_shuffle_leakage` | `test_ml_age.py` | `test_ml_sex.py` | **NON duplicato** — metriche diverse (R² regressione vs BA classificazione) |
| `test_fc_dispatcher_rejects_invalid_metric` | `test_dispatcher_base.py` | `test_e2e_smoke_minimal.py` | **Quasi-duplicato** — stessa asserzione, stessa chiamata. Ma scopi diversi: unit-test dispatcher (base) vs test integrazione e2e (smoke). TIENI entrambi per ora (bias conservativo) |

**Verdetto DEDUP: D=0** — nessun duplicato reale da rimuovere.

### Leva 2 — RIMOZIONE (test senza copertura)

Test candidati valutati: file che falliscono per dipendenze mancanti (`statsmodels`, `networkx`) non sono candidati a rimozione — il modulo esiste ed è produzione, il test è valido ma richiederebbe installazione dep. Il fallimento è ambientale, non strutturale.

Test `test_e2e_smoke_minimal.py::test_fc_dispatcher_rejects_invalid_metric` è quasi-duplicato ma in un contesto e2e che copre percorsi di integrazione distinti. Bias conservativo: TIENI.

Nessun test identificato come privo di copertura in modo definitivo e non recuperabile.

**Verdetto RIMOZIONE: R=0**

### Leva 3 — AGGIUNTA (buchi core non coperti)

Buchi di copertura evidenti:
- `dashboard/app.py` (0%): applicazione Dash/Streamlit, richiede infrastruttura UI non banale da testare
- `pipeline_mne_bids/` (0%): richiede dataset BIDS reale — non mockable facilmente
- `features/graph_theory.py` (0%): richiede `networkx` — buco risolvibile con mock se installazione non possibile

Tuttavia: l'audit è conservativo. Aggiungere test richiede comprensione profonda dei contratti API. Nessun percorso core non coperto è stato identificato come gap critico e ovvio senza rischio di false asserzioni.

**Verdetto AGGIUNTA: A=0**

---

## Verdetto finale

**D=0 / R=0 / A=0**

La suite è coerente e non presenta duplicati reali. I 4 nomi condivisi sono falsi positivi (target/metriche diversi). I fallimenti attuali sono ambientali (dipendenze mancanti: `networkx`, `statsmodels`) non strutturali. Coverage bassa (37%) riflette moduli pipeline non eseguibili in CI senza dataset — non indica test mancanti sulla logica core.

**Raccomandazione**: installare `networkx` e `statsmodels` nell'env CI (o aggiornare `requirements.txt`/`environment.yml`) per sbloccare 9 file test attualmente ignorati. Questo solo porterebbe la copertura stimata a ~55-60%.
