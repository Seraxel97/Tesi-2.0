# FC Dispatcher — Consolidamento WARN/FAIL (BAND-5-9-T06)

**Sprint**: BAND-5-9-T06  
**Data**: 2026-05-01  
**Dipende da**: BAND-5-9-T02 (sweep 252 combo)  

---

## Sorgente WARN/FAIL

Dal sweep BAND-5-9-T02: **168 PASS, 84 WARN, 0 FAIL, 0 ERROR** su 252 combinazioni.

---

## Tabella WARN → Fix

| ID | Pattern | Causa | Fix applicato | File modificato |
|----|---------|-------|---------------|-----------------|
| WARN-01 | `delta` band (1-4 Hz) + epoch 2.048s | Cicli insufficienti: 2.05 < 5 richiesti da multitaper | `UserWarning` proattiva in `compute_fc()` prima di chiamare mne, con raccomandazione fmin/durata | `connectivity/fc_dispatcher.py` |

### Dettaglio fix WARN-01

**Dove**: `compute_fc()`, loop pre-computazione bande.

**Logica**: per ogni banda, se `(n_times / sfreq) * fmin < 5` → emette `UserWarning` con:
- nome della banda problematica
- cicli effettivi vs richiesti
- fmin minima raccomandata (`5 / epoch_duration_s`)
- durata minima raccomandata (`5 / fmin`)

**Codice aggiunto** (in `connectivity/fc_dispatcher.py`):
```python
epoch_duration_s = label_tc.shape[2] / sfreq
_MIN_CYCLES = 5
for band_name, (fmin, _) in bands.items():
    if fmin > 0 and epoch_duration_s * fmin < _MIN_CYCLES:
        warnings.warn(
            f"Band '{band_name}' (fmin={fmin} Hz): epoch duration {epoch_duration_s:.3f}s "
            f"gives {epoch_duration_s * fmin:.2f} cycles < {_MIN_CYCLES} required. "
            f"Use fmin >= {_MIN_CYCLES / epoch_duration_s:.1f} Hz or epochs >= "
            f"{_MIN_CYCLES / fmin:.1f}s for reliable spectrum. (BAND-5-9-T06 fix)",
            UserWarning,
            stacklevel=2,
        )
```

**Rationale**: il `RuntimeWarning` interno di mne viene ancora emesso, ma ora l'utente riceve
anche un `UserWarning` esplicito a livello di `compute_fc()` — piu' facile da filtrare/loggare
nel codice chiamante senza dover parsare il messaggio di mne.

---

## Tabella FAIL → xfail

| ID | Pattern | Causa | Azione |
|----|---------|-------|--------|
| — | — | — | **Nessun FAIL** nel sweep T02 |

Il sweep 252 combo non ha prodotto FAIL (NaN silenti, asimmetrie, crash non catturati).
Non sono necessari xfail test.

---

## Test di regressione

**File**: `tests/test_fc_consolidate.py` — 12 test:

| Test | Verifica |
|------|----------|
| `test_delta_short_epoch_emits_user_warning` | UserWarning emesso per delta + epoch corta |
| `test_delta_long_epoch_no_user_warning` | Nessun UserWarning con epoch 6s (5 cicli ok) |
| `test_alpha_band_no_user_warning` | Nessun UserWarning per alpha band |
| `test_fix_output_still_correct_after_warn[×7]` | Output finito e simmetrico nonostante il warning |
| `test_warning_message_contains_recommendation` | Messaggio include raccomandazione actionable |
| `test_no_fail_cases_in_sweep` | Combo estreme del sweep T02 confermano 0 FAIL |

**Risultato**: 12/12 PASS.

---

## Regressione suite completa post-fix

| Suite | N test | Risultato |
|-------|--------|-----------|
| test_fc_dispatcher.py | 34 | PASS |
| test_fc_edge.py | 37 | PASS |
| test_fc_edge_extreme.py | 259 | PASS |
| test_fc_consolidate.py | 12 | PASS |
| **Totale FC** | **342** | **PASS** |

---

## Conclusione

Un solo fix puntuale applicato (WARN-01). Nessun FAIL noto. Il comportamento di
`fc_dispatcher.compute_fc()` e' ora piu' difensivo rispetto a bande con cicli insufficienti.

**Priorita' future** (non bloccanti):
- Aggiungere stesso check per `theta` (4-8 Hz) con epoch molto brevi (< 0.63s).
- Considerare `fmax > nyquist` warning esplicito (attualmente silente — accettabile).
