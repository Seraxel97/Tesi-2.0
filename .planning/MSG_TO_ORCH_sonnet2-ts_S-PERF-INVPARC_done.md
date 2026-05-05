# MSG S-PERF-INVPARC DONE — sonnet-tesi-2 → opus-orch-tesi

**Timestamp**: 2026-05-05T19:35  
**Sprint**: S-PERF-INVPARC  
**Worker**: sonnet-tesi-2  
**Verdict**: ✅ PASS

---

## Risultati benchmark

| Metrica | Prima (S-48) | Dopo (S-PERF-INVPARC) | Delta |
|---------|-------------|----------------------|-------|
| `inverse_parcellation` | 5.490s | **1.533s** | **-3.58x (-72%)** |
| Pipeline totale | 9.857s | **5.976s** | -1.65x (-39%) |

Target era ≥30% (-40% target) → **SUPERATO** (72% di riduzione).

---

## Modifiche

### File modificati
- **`analysis/bench_steps.py`**: loop `apply_inverse` per-epoch → `apply_inverse_epochs` batch + `extract_tc_batch`
- **`parcellation/extract_label_tc.py`**: aggiunta `extract_tc_batch(stcs, atlas, src)` → `(n_stcs, n_labels, n_times)`
- **`connectivity/fc_dispatcher.py`**: aggiunta validazione esplicita `metric` (ValueError con messaggio leggibile)
- **`ml_training/ml_dispatcher.py`**: aggiunta validazione esplicita `algorithm` (ValueError invece di KeyError)
- **`tests/conftest.py`**: registrato `pytest_plugins = ["tests.fixtures.synthetic"]` (fix preesistente)
- **`tests/test_parcellation.py`**: aggiunti 3 test batch (`shape`, `finite`, `consistent_with_per_epoch`)
- **`tests/test_perf_regression.py`**: aggiunto `test_inverse_parcellation_batch_speed` con soglia 2.5s
- **`tests/test_e2e_smoke_minimal.py`**: rimosso import `_validate_cli_path` mai implementato (fix preesistente)
- **`reports/PERF_BASELINE.json`**: aggiornato `inverse_parcellation: 1.533s`, `total: 5.976s`, threshold 2.5s
- **`reports/PERF_BENCHMARK.md`**: tabella pre/post-refactor con speedup dettagliato
- **`PROGRESS.md`**: aggiornato data e nota bottleneck risolto

### Fix preesistenti (non in SYNC ma bloccavano la suite)
4 bug mai scoperti finora (fixture non registrata, import inesistente, error message mismatch ×2).

---

## Test
- **283/283 PASS** (era 282 pre-sprint, +1 nuovo test `inverse_parcellation`)
- `test_perf_regression.py`: 5/5 PASS

---

## Note
- `scripts/pilot_step*` NON toccati (per policy SYNC, in uso da sonnet-tesi-1)
- MCP rule: refactor codice multi-file → Claude; docs/reports → Claude (task breve, Codex non necessario)
- Branch: `scientific/step7-experiments` (modifiche non committate, in attesa conferma operator per commit)
