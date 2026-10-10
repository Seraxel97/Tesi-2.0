# Lesson Learned — wPLI Collapse (S-104 → S-101b fix)

**Data**: 2026-05-01T19:22:00+02:00  
**Sprint origine**: S-104 (connectivity wPLI ds005385)  
**Sprint fix**: S-101b (per-epoch source recon)  
**Documentato in**: S-114 (sonnet2-ts)  
**Cross-ref METHODS**: `.planning/research/METHODS_v1.md §5.4`

---

## Issue

Durante S-104 (calcolo connettività wPLI su ds005385 pilot 5 sub), tutte le
matrici FC prodotte presentavano valori **costanti ≈ 1.0** su tutte le coppie ROI:

```
wpli_alpha[sub-007, aparc]:  min=0.998  max=1.000  mean=0.999
wpli_beta[sub-007, aparc]:   min=0.997  max=1.000  mean=0.999
```

Range fisiologico atteso: **[0.05, 0.50]**. Il collasso a 1.0 è artefactuale
e non riflette connettività reale.

---

## Root cause

**Pattern difettoso** nel codice di source recon (S-101 originale):

```python
evoked = epochs.average()                     # media su N_epochs → 1 osservazione
stc = mne.minimum_norm.apply_inverse(evoked, inv_op, ...)  # STC shape (N_src, N_t)
label_tc = mne.extract_label_time_course(stc, labels, src)  # (N_ROI, N_t)
# ↓ passato a spectral_connectivity_epochs con N=1 "epoch"
```

`spectral_connectivity_epochs` riceveva un tensore `(1, N_ROI, N_t)`.
Con N=1 osservazione, Im(S_xy) ha varianza zero e il wPLI collassa:

**wPLI = E[|Im(S_xy)| · sign(Im(S_xy))] / E[|Im(S_xy)|] = 1.0**

per qualsiasi coppia (i, j) — la media su un singolo valore della propria
magnitudine è sempre 1.

### Perché non impatta tutte le metriche allo stesso modo

| Metrica | Dipende da variabilità trial? | Collassa con N=1? |
|---------|------------------------------|-------------------|
| wPLI | Sì (stima pesata di lag di fase) | **Sì — sempre 1.0** |
| wPLI2_debiased | Sì | **Sì** |
| PLI | Sì (sign medio) | Sì (≈ ±1) |
| imcoh | Parzialmente | Instabile ma non 1.0 |
| coh, plv, ciplv | No (magnitudine) | No, ma stima instabile |

---

## Fix (S-101b)

Sostituire `apply_inverse` su evoked con `apply_inverse_epochs` su ogni
singola epoch, producendo variabilità inter-trial reale:

```python
# Corretto (S-101b):
stcs = mne.minimum_norm.apply_inverse_epochs(
    epochs, inv_op, lambda2=1.0 / 9.0, method="dSPM", verbose=False
)
label_tc = np.stack([
    mne.extract_label_time_course(stc, labels, src, mode="mean_flip")
    for stc in stcs
], axis=0)  # shape: (N_epochs, N_ROI, N_t) — variabilità corretta
```

Il tensore `(N_epochs, N_ROI, N_t)` fornisce a `spectral_connectivity_epochs`
N_epochs osservazioni indipendenti, consentendo una stima cross-spettrale
stabile.

### Trade-off computazionale

`apply_inverse_epochs` è più lento di `apply_inverse` su evoked:

| Approccio | N operazioni inverse | Tempo stimato (5 sub × 120 epoch) |
|-----------|---------------------|-----------------------------------|
| Su evoked | 1 per condizione | ~1s/sub |
| Per-epoch (S-101b) | N_epochs per condizione | ~2-5min/sub |

Il costo è accettabile per il pilot (5 sub) e per il subset (15 sub).
Per scale maggiori (N > 50 sub), considerare parallelizzazione con `n_jobs`.

---

## Criteri di validazione post-fix

Dopo S-101b, il check obbligatorio per ogni matrice wPLI prodotta:

| Criterio | Soglia | Tool |
|----------|--------|------|
| Range valori | 0.0 ≤ wPLI ≤ 1.0 | `validate_connectivity_outputs.py` |
| Max < 0.95 (no collasso) | max < 0.95 | idem |
| Media nell'intervallo fisiologico | 0.05 ≤ mean ≤ 0.50 | idem |
| No NaN / Inf | count = 0 | idem |
| Simmetria numerica | \|M - M.T\|.max() < 1e-5 | idem |

Il range fisiologico [0.05, 0.50] è derivato da:
- Vinck et al. (2011): wPLI tipicamente < 0.5 in dati EEG intracrania e scalp
- Nagy et al. (2024): wPLI residuo dopo inversione dSPM su dataset resting-state
  presenta valori medi < 0.3 per coppie ROI non direttamente connesse

---

## Impatto su altri script

| Script | Stato prima | Stato dopo S-101b |
|--------|-------------|-------------------|
| `scripts/pilot_step2_ds005385.py` | `apply_inverse` su evoked | `apply_inverse_epochs` |
| `analysis/bench_steps.py` | loop su epochs[i] (corretto) | invariato |
| `pipeline_mne_bids/run_e2e_matchingpennies.py` | evoked (smoke ok) | da verificare se si aggiunge wPLI |

---

## Riferimenti

- Vinck, M., et al. (2011). An improved index of phase-synchronization for
  electrophysiological data in the presence of volume-conduction, noise and
  sample-size bias. *NeuroImage*, 55(4), 1548-1565.
  doi:10.1016/j.neuroimage.2011.01.055
- Nagy, Z., et al. (2024). Disentangling spurious from genuine source-level
  functional connectivity in EEG. *Human Brain Mapping*, 45(3), e26650.
  doi:10.1002/hbm.26650
