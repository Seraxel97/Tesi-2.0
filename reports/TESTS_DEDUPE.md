# Tests Deduplication Report

**Data**: 2026-05-01  **Sprint**: S-61  **Worker**: sonnet2-ts
**Suite**: `tests/` — 31 file, 196 funzioni test

---

## 1. Duplicati cross-file (stesso nome in file diversi)

**2 funzioni duplicate** (stesso nome, file diversi):

| Funzione | File |
|----------|------|
| `test_build_X_fc_only` | test_e2e_smoke_minimal.py, test_features.py |
| `test_fc_dispatcher_rejects_invalid_metric` | test_dispatcher_base.py, test_e2e_smoke_minimal.py |

## 2. Duplicati intra-file (stesso nome nello stesso file)

Nessun duplicato intra-file trovato.

## 3. Quasi-duplicati (stem identico, suffisso numerico/variante)

Nessun quasi-duplicato trovato.

## 4. Test senza asserzioni (possibili placeholder)

**3 funzioni** senza `assert`/`raises`:

**test_dispatcher_base.py**: `test_validate_valid_keys`
**test_e2e_smoke_minimal.py**: `test_imports_all_modules` *(import-only — assertion implicita via ImportError)*
**test_smoke.py**: `test_imports_smoke` *(import-only — assertion implicita via ImportError)*

> Nota: `test_imports_*` sono test di smoke validi: falliscono per `ImportError` se un modulo e' rotto.
> Non richiedono `assert` esplicito. `test_validate_valid_keys` invece non verifica output — considerare
> di aggiungere `assert True` o convertire a test parametrizzato con assert sul risultato.

---

## Riepilogo

| Categoria | Count |
|-----------|-------|
| Duplicati cross-file | 2 |
| Duplicati intra-file | 0 |
| Quasi-duplicati (coppie) | 0 |
| Test senza asserzioni | 3 |

### Raccomandazioni

- **Duplicati cross-file**: consolidare nel file piu' specifico; rimuovere la copia generica (es. test_smoke.py vs test_<modulo>.py).
- **test_imports_***: validi come smoke test (fail per ImportError) — nessuna azione richiesta.
- **test_validate_valid_keys**: aggiungere assert esplicito o convertire a `@pytest.mark.parametrize`.
