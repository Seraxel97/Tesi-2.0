# Deep Review FC — Edge Sweep Estremo (BAND-5-9-T02)

**Sprint**: BAND-5-9-T02  
**Data**: 2026-05-01  
**Owner**: sonnet2-ts  
**Pre-condizione**: S-02 done, DR-REVIEW-edge-cases done  

---

## Metodologia

Sweep parametrico: **7 metriche × 4 n_epochs × 3 n_labels × 3 bande = 252 combinazioni**.

| Parametro | Valori testati |
|-----------|---------------|
| metric | coh, imcoh, plv, ciplv, pli, wpli, wpli2_debiased |
| n_epochs | 1, 2, 5, 10 |
| n_labels | 2, 5, 50 |
| band / config | alpha 8-13 Hz (normale), delta 1-4 Hz (cicli insufficienti), hf 80-200 Hz (fmax > nyquist=125) |
| sfreq | 250 Hz |
| n_times | 512 (2.048 s) |

Detector per ogni combo: NaN/Inf nel risultato, simmetria persa, RuntimeWarning, eccezioni.

**Tempo sweep**: 6.5s totale.

---

## Risultati aggregati

| Outcome | Count | % |
|---------|-------|---|
| **PASS** | 168 | 66.7% |
| **WARN** | 84 | 33.3% |
| FAIL | 0 | 0% |
| ERROR | 0 | 0% |

**Nessun FAIL né ERROR.** Tutti i 252 output sono finiti e simmetrici.

---

## Matrice outcome per banda

### Banda alpha (8–13 Hz) — normale

| Metrica | ne=1 | ne=2 | ne=5 | ne=10 |
|---------|------|------|------|-------|
| coh | PASS | PASS | PASS | PASS |
| imcoh | PASS | PASS | PASS | PASS |
| plv | PASS | PASS | PASS | PASS |
| ciplv | PASS | PASS | PASS | PASS |
| pli | PASS | PASS | PASS | PASS |
| wpli | PASS | PASS | PASS | PASS |
| wpli2_debiased | PASS | PASS | PASS | PASS |

> Tutti i n_labels (2, 5, 50) danno lo stesso outcome. n_epochs=1 produce risultati finiti e simmetrici.

### Banda delta (1–4 Hz) — cicli insufficienti @ 2.048s

| Metrica | ne=1..10 | n_labels=2..50 |
|---------|----------|----------------|
| coh | **WARN** | **WARN** |
| imcoh | **WARN** | **WARN** |
| plv | **WARN** | **WARN** |
| ciplv | **WARN** | **WARN** |
| pli | **WARN** | **WARN** |
| wpli | **WARN** | **WARN** |
| wpli2_debiased | **WARN** | **WARN** |

**Warning**: `RuntimeWarning: fmin=1.000 Hz corresponds to 2.048 < 5 cycles based on the epoch length 2.048 sec, need at least 5.000 sec epochs or fmin=2.500. Spectrum estimate will be unreliable.`

**Caratteristiche**: warning SEMPRE emesso per tutte le 7 metriche (84/84 combos), indipendente da n_epochs e n_labels. Il risultato e' finito e simmetrico ma **inaffidabile spettralmente**.

### Banda hf (80–200 Hz, fmax > nyquist=125 Hz)

| Metrica | ne=1..10 | n_labels=2..50 |
|---------|----------|----------------|
| coh | **PASS** | **PASS** |
| imcoh | **PASS** | **PASS** |
| plv | **PASS** | **PASS** |
| ciplv | **PASS** | **PASS** |
| pli | **PASS** | **PASS** |
| wpli | **PASS** | **PASS** |
| wpli2_debiased | **PASS** | **PASS** |

mne_connectivity clamppa automaticamente fmax al nyquist (125 Hz). Output finito, simmetrico, nessun warning.

---

## Dettaglio WARN: delta band cicli insufficienti

**Pattern**: costante per tutte le metriche e tutte le combo (n_epochs, n_labels).

**Causa**: la banda delta (1–4 Hz) richiede almeno 5 cicli completi nell'epoch. Con epoch di 2.048s, il periodo di 1 Hz = 1s, quindi 2.048 cicli < 5 richiesti.

**Impatto**: lo spettro multitaper stimato e' inaffidabile per fmin=1 Hz a questa durata. Il risultato **non e' NaN** ma ha alta varianza.

**Mitigazione raccomandata** (in ordine di priorita'):
1. **Validazione input** in `compute_fc()`: aggiungere check `if n_times / sfreq * fmin < 5: warnings.warn(...)` PRIMA della chiamata a mne — per dare un warning piu' specifico al codice utente.
2. **Epoch piu' lunghe**: per delta band (1-4 Hz), usare epoch ≥ 5s (1250 sample @ 250 Hz).
3. **Limite fmin**: ignorare delta nella pipeline se le epoch sono < 5s.

**Priorita' fix**: **LOW** — il warning e' gia' emesso da mne_connectivity. Non e' un bug di fc_dispatcher, ma un limite fisico.

---

## n_epochs=1 — analisi specifica

Con n_epochs=1 (banda alpha, tutte le metriche):
- Output shape: (n_labels, n_labels) ✓
- Tutti i valori finiti ✓
- Matrice simmetrica ✓
- Nessun warning ✓

**Conclusione**: fc_dispatcher gestisce correttamente n_epochs=1. La stima e' piu' rumorosa per natura statistica (single-trial), ma non produce NaN silenti.

---

## n_labels estremi

| n_labels | Comportamento |
|----------|---------------|
| 2 | PASS — matrice 2×2, diag=0, off-diag finito |
| 5 | PASS — matrice 5×5 |
| 50 | PASS — matrice 50×50, ~0.3s per metric/banda |

Nessun problema di scalabilita' rilevato fino a 50 ROI.

---

## Conclusione priorita' fix

| Finding | Severity | Stato |
|---------|----------|-------|
| delta band cycles warning (sempre emesso) | LOW | Comportamento corretto di mne; nessun fix richiesto in fc_dispatcher |
| n_epochs=1 nessun warning | INFO | Accettabile — stima rumorosa ma valida |
| fmax > nyquist clamp silente | INFO | mne_connectivity gestisce internamente |

**Nessun fix urgente.** Unica azione raccomandata (OPTIONAL): aggiungere validazione proattiva `n_times / sfreq * fmin` in `compute_fc()` per messaggi piu' user-friendly.
