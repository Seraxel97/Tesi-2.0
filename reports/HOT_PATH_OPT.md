# Hot Path Optimization Report — BAND-5-9-T07

**Data**: 2026-05-01  
**Pre-condizione**: PERF_PROFILE.md (S-17)  
**Strumento**: `analysis/optimize_hot_path.py`  
**Soggetto benchmark**: sub-05 matchingpennies, N=20 epoch, sfreq 5000 Hz (non decimato)

---

## Bottleneck identificati (da PERF_PROFILE.md)

| Rank | Funzione | % tempo totale | Causa |
|------|----------|----------------|-------|
| 1 | `_prepare_label_extraction` + `intersect1d` | 38% | Ricalcolo vertici per-epoch (invariante) |
| 2 | `prepare_inverse_operator` | 24% | Ricalcolo decomposizione inv per-epoch (invariante) |
| 3 | `label_sign_flip` | 19.5% | SVD flip per-epoch (invariante) |
| 4 | `compute_fc` | 6% | FC spettrale — trascurabile |

**Nota**: Bottleneck #1/#2/#3 sono tutti invarianti tra epoch — le label, l'operatore inverso
e le sorgenti non cambiano tra un'epoch e l'altra. Il costo è O(N_epochs) dove dovrebbe essere O(1).

---

## Ottimizzazione OPT-1: Batch apply_inverse_epochs

### Principio

L'implementazione baseline nel pipeline E2E chiama `mne.minimum_norm.apply_inverse` su ogni epoch
singolarmente tramite `iter_evoked`. Internamente, ad ogni chiamata MNE esegue `prepare_inverse_operator`
che calcola decomposizioni costose (SVD, whitening) anche se l'operatore non è cambiato.

**Soluzione**: sostituire il loop con `mne.minimum_norm.apply_inverse_epochs` (batch), che:
1. Chiama `prepare_inverse_operator` **una sola volta** per tutte le epoch
2. Applica la stessa decomposizione a tutte le epoch
3. Gestisce anche il sign-flip in batch

### Risultati benchmark (N=20 epoch reali, sub-05)

| Metrica | Baseline (loop) | OPT-1 (batch) | Miglioramento |
|---------|----------------|----------------|---------------|
| Tempo totale (s) | 16.005 | 2.174 | **−13.83s** |
| Speedup | 1.00x | **7.36x** | +636% |
| Risparmio (%) | — | **86.4%** | — |
| N chiamate `prepare_inverse` | 20 | 1 | -95% |

### Proiezione su benchmark completo (700 run)

| Scenario | Baseline (stima) | OPT-1 (stima) | Risparmio |
|----------|-----------------|----------------|-----------|
| 700 run × 20 epoch, 1 atlas | ~1540 s (26 min) | ~210 s (3.5 min) | ~22 min |
| 700 run × 20 epoch, 4 atlas | ~6160 s (103 min) | ~840 s (14 min) | ~89 min |

---

## Implementazione

**File**: `analysis/optimize_hot_path.py`

```python
from analysis.optimize_hot_path import optimized_batch_inverse, benchmark_compare

# Uso diretto
stcs = optimized_batch_inverse(epochs, inv_op, method='dSPM')

# Benchmark comparativo
results = benchmark_compare(epochs, inv_op, n_repeat=3)
# → {'speedup': 7.36, 'saved_pct': 86.4, ...}
```

---

## Bottleneck #1 — _prepare_label_extraction (38%): analisi

Il ricalcolo dei vertici label × source space (`numpy.intersect1d` × 2732 chiamate per 20 epoch)
è invariante: le label e il source space non cambiano tra epoch. MNE non implementa
caching interno per questo.

**Fix potenziale** (non implementato — richiederebbe patch MNE):
Pre-computare `_prepare_label_extraction(labels, src)` una volta e passare il risultato pre-calcolato.
Stima risparmio aggiuntivo: ~38% del tempo residuo (~0.8s su 2.17s OPT-1).

**Stato**: rimandato — richiederebbe accesso a API interne MNE non pubbliche.

---

## Verdict

| Ottimizzazione | Severity | Stato | Speedup |
|----------------|----------|-------|---------|
| OPT-1: batch apply_inverse_epochs | **HIGH** | **IMPLEMENTATA** | **7.36x** |
| OPT-2: pre-cache label indices | MEDIUM | Rinviata (API interne MNE) | ~1.5x aggiuntivo stima |

**Raccomandazione**: adottare OPT-1 nel pipeline E2E (modificare `exec.py` step 3).
Il cambio riduce il benchmark completo da ore a minuti.
