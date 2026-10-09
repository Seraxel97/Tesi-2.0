# Coverage Thresholds — Tesi_2.0

**Sprint**: DR-VAULT-test-coverage-import
**Data**: 2026-05-01
**Pattern**: importato da Vesta CI (Vesta/.github/workflows/ci.yml, `--cov=. --cov-report=xml`)

---

## Soglia attuale

| Threshold | Valore | Stato |
|-----------|--------|-------|
| `fail_under` | 60% | ATTIVO (warm-up) |

Configurazione: `.coveragerc` + `pyproject.toml [tool.coverage.report]`.
CI gate: `.github/workflows/test.yml` passo `--cov-fail-under=60`.

---

## Scope di misura

I seguenti package sono inclusi nel calcolo della coverage:

| Package | Scope |
|---------|-------|
| `parcellation/` | STEP 3: extract_label_tc, neuromaps_helper |
| `connectivity/` | STEP 4: fc_dispatcher, run_fc_on_epochs |
| `features/` | STEP 5: dispatcher |
| `ml_training/` | STEP 6: ml_dispatcher, permutation |
| `source_reconstruction/` | STEP 2: finalize_inverse, apply_inverse_epochs_rs |
| `common/` | paths, hb_lib, queue_lib, state_lib, dispatcher_base |
| `analysis/` | compare_runs, fdr_helper, profile_bench |
| `pipeline_mne_bids/` | run_e2e, bench/, run_with_timeout |
| `dashboard/` | plot_top_features |

Esclusi: `tests/`, `.planning/`, `__pycache__/`.

---

## Linee escluse dal conteggio

Le seguenti tipologie di righe sono escluse dalla coverage report:

- `pragma: no cover` — righe marcate esplicitamente
- `def __repr__` — metodi repr di classe
- `if __name__ == "__main__":` — blocchi CLI
- `raise NotImplementedError` — metodi astratti
- Righe `pass` isolate

---

## Roadmap incrementale

| Fase | Threshold | Trigger |
|------|-----------|---------|
| Baseline (attuale) | 60% | warm-up, 500+ test su 9 package |
| Post-benchmark | 70% | dopo esecuzione S-08 e aggiunta test di integrazione |
| Post-dataset scientifico | 80% | dopo S-07 (dataset finale) e test multi-soggetto |

### Motivazione soglie graduali

La soglia 60% riflette lo stato attuale della test suite che copre:
- Tutti i moduli core con test unitari (dispatcher, CV, FC, parcellation)
- Smoke test sintetico E2E (`test_e2e_smoke_minimal.py`)
- Test infrastruttura (migrations, hb_lib, queue_lib)

I moduli `analysis/` e `dashboard/` hanno coverage bassa perche' le loro
funzioni principali richiedono dati di benchmark reali non disponibili durante
il CI senza dataset. La soglia 70% sara' raggiungibile aggiungendo test con
dati sintetici per `compare_runs.py` e `fdr_helper.py` (sprint post-S-08).

---

## Comandi locali

```bash
# Coverage report locale
pytest tests/ --cov --cov-report=html:htmlcov --cov-report=term-missing

# Apri report HTML
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux

# Coverage solo su un modulo
pytest tests/test_fc_edge.py --cov=connectivity --cov-report=term-missing
```
