# Scientific Pipeline Status — ds005385 PILOT

**Timestamp**: 2026-05-02T15:28:00Z  
**Sprint**: S-107 (sonnet1-ts) — AGGIORNAMENTO FINALE  
**Dataset**: ds005385 (Dortmund Vital Study) — subset N=15, seed=42  
**PILOT subjects**: sub-007, sub-010, sub-011, sub-026, sub-031  
**Atlases**: aparc (68 ROI), schaefer100 (100 ROI)  
**Conditions**: EO (Eyes Open), EC (Eyes Closed)

---

## Stato step — overview (AGGIORNATO)

| Step | Descrizione | Soggetti | Stato | Sprint | Note |
|------|-------------|----------|-------|--------|------|
| 1 | Preprocessing raw BIDS | 5 PILOT | ✅ completato | S-100, S-100b | EO/EC mapping validato |
| 2b | Source reconstruction per-epoch (dSPM) | 5 PILOT | ✅ completato | S-101b | 10 stcs.npz → cleanup post S-103b |
| 3b | Parcellazione per-epoch | 5×2×2 | ✅ completato | S-103b | 20 label_tc (n_ep,n_lbl,n_t) |
| 4b | FC spettrale per-epoch (wPLI+coh) | 5×2×2×2 | ✅ completato | S-104b | 40 fc_matrix, wPLI 0.12-0.21 |
| 5 | Feature extraction upper-triangle | 4 atlas×metric | ✅ completato | S-105 | X(10,2278/4950), NaN=0 |
| 6 | ML classification LOSO | 4×3 combos | ✅ completato | S-106 | best: schaefer100×coh×LogReg 0.90 |
| 7 | Esperimenti confronto | aggregazione | ✅ completato | S-107 | comparison_matrix.json + report |

---

## STEP 1 — Preprocessing raw BIDS

Dati raw ds005385 accessibili via `data/raw/ds005385` (symlink → `~/Scrivania/Tesi/data/ds005385/`).
Analisi BIDS (S-100, sonnet1-ts) e subset policy (S-100b, sonnet2-ts) completate.
Mapping condizioni EO/EC in `config/labels_ds005385.py`.

| Soggetto | EO raw | EC raw | Stato |
|----------|--------|--------|-------|
| sub-007 | disponibile | disponibile | completato |
| sub-010 | disponibile | disponibile | completato |
| sub-011 | disponibile | disponibile | completato |
| sub-026 | disponibile | disponibile | completato |
| sub-031 | disponibile | disponibile | completato |

---

## STEP 2 — Source Reconstruction (dSPM)

Sprint S-101 (sonnet1-ts). Metodo: dSPM, fsaverage oct6, lambda2=0.111, loose=0.2, depth=0.8.
Preprocessing: 1.0-40.0 Hz, 250 Hz, epoche 2.0s.

| Soggetto | Cond | Epoche | STC shape | Wall (s) | Stato |
|----------|------|--------|-----------|----------|-------|
| sub-007 | EO | 122 | (8196, 501) | 0.68 | completato |
| sub-007 | EC | 124 | (8196, 501) | 0.97 | completato |
| sub-010 | EO | 122 | (8196, 501) | 0.62 | completato |
| sub-010 | EC | 122 | (8196, 501) | 0.72 | completato |
| sub-011 | EO | 121 | (8196, 501) | 0.61 | completato |
| sub-011 | EC | 120 | (8196, 501) | 0.89 | completato |
| sub-026 | EO | 122 | (8196, 501) | 0.67 | completato |
| sub-026 | EC | 124 | (8196, 501) | 0.76 | completato |
| sub-031 | EO | 120 | (8196, 501) | 0.62 | completato |
| sub-031 | EC | 120 | (8196, 501) | 0.62 | completato |

Wall-clock totale: 28.7s. Verdict: PASS.
File: `data/derivatives/mne-bids-pipeline/sub-XXX/eeg/sub-XXX_task-RestingState_cond-YY_inv-dSPM-{lh,rh}.stc`

---

## STEP 3 — Parcellazione Atlastica

Sprint S-103 (sonnet1-ts). Mode: `mean_flip`.
File output: `data/label_ts/ds005385/sub-XXX_atlas-ATLAS_cond-COND.npz`

| Soggetto | Atlas | Cond | n_labels | n_times | Wall (s) | Stato |
|----------|-------|------|----------|---------|----------|-------|
| sub-007 | aparc | EO | 68 | 501 | 0.888 | completato |
| sub-007 | aparc | EC | 68 | 501 | 0.176 | completato |
| sub-007 | schaefer100 | EO | 100 | 501 | 0.197 | completato |
| sub-007 | schaefer100 | EC | 100 | 501 | 0.195 | completato |
| sub-010 | aparc | EO | 68 | 501 | 0.172 | completato |
| sub-010 | aparc | EC | 68 | 501 | 0.171 | completato |
| sub-010 | schaefer100 | EO | 100 | 501 | 0.195 | completato |
| sub-010 | schaefer100 | EC | 100 | 501 | 0.195 | completato |
| sub-011 | aparc | EO | 68 | 501 | 0.170 | completato |
| sub-011 | aparc | EC | 68 | 501 | 0.169 | completato |
| sub-011 | schaefer100 | EO | 100 | 501 | 0.197 | completato |
| sub-011 | schaefer100 | EC | 100 | 501 | 0.195 | completato |
| sub-026 | aparc | EO | 68 | 501 | 0.171 | completato |
| sub-026 | aparc | EC | 68 | 501 | 0.168 | completato |
| sub-026 | schaefer100 | EO | 100 | 501 | 0.199 | completato |
| sub-026 | schaefer100 | EC | 100 | 501 | 0.367 | completato |
| sub-031 | aparc | EO | 68 | 501 | 0.340 | completato |
| sub-031 | aparc | EC | 68 | 501 | 0.181 | completato |
| sub-031 | schaefer100 | EO | 100 | 501 | 0.516 | completato |
| sub-031 | schaefer100 | EC | 100 | 501 | 0.197 | completato |

Wall-clock totale: 5.2s. Verdict: PASS.

---

## STEP 4 — FC Spettrale

Sprint S-104 (sonnet1-ts) — in corso al momento di questo report.
Metriche pianificate: wPLI, coherence. Bande: alpha (8-13 Hz), theta (4-8 Hz).
Input: 20 .npz da STEP 3.

| Combinazione | Stato |
|--------------|-------|
| 5 sub x 2 atlas x 2 cond x 2 metriche | in corso |

Risultati in: `reports/STEP4_DS005385_PILOT.md` (non ancora prodotto).

---

## STEP 5-7 — In attesa

| Step | Gate | Stato |
|------|------|-------|
| 5 — Feature extraction | S-104 done | in attesa |
| 6 — ML classification (LogReg, RF, GroupKFold-10) | S-105 done | in attesa |
| 7 — Esperimenti atlas x metric x algo | S-106 done | in attesa |

---

## Fix S-101b (per-epoch STC) — in flight 2026-05-01

**Issue identificato da S-104**: valori wPLI collassati a 1.0 (range fisiologico atteso: 0.05-0.50).

**Root cause**: S-101 ha applicato `apply_inverse(evoked, ...)` producendo 1 STC per condizione
(single evoked sample). Con un singolo campione non vi e' varianza di fase tra epoch, e la
wPLI risulta sempre 1.0 per definizione.

**Fix (S-101b)**: applicare `apply_inverse_epochs(epochs, ...)` → `list[STC]` per epoch,
ripristinando la varianza di fase necessaria al calcolo di metriche di connettivita' funzionale.

**Pipeline status post-fix atteso**:

| Sprint | Descrizione | Output | Stato |
|--------|-------------|--------|-------|
| S-101b | Per-epoch STC su 5 PILOT sub | 5 sub x 2 cond = 10 file per-epoch STC | in flight |
| S-103b | Parcellazione su per-epoch STC | 5 sub x 2 atlas x 2 cond = 20 file label_tc (n_epochs, n_labels, n_times) | pending S-101b |
| S-104b | FC su per-epoch label_tc | 40 FC matrix con valori fisiologici (0.05-0.50) | pending S-103b |

**Impatto**: i risultati di S-101/S-103/S-104 (STC evoked, label_ts evoked, wPLI=1.0) sono
da considerare preliminari/non validi per l'analisi scientifica. Il fix S-101b produce output
compatibili con il resto della pipeline.

---

## STEP 5-7 — Feature Extraction + ML + Esperimenti (COMPLETATI)

### STEP 5 — Feature Extraction (S-105)

Upper-triangle flatten su fc_matrix (n_labels, n_labels).

| File | Shape | NaN | Range |
|------|-------|-----|-------|
| X_aparc_wpli_alpha.npz | (10, 2278) | 0 | [0.016, 0.808] |
| X_aparc_coh_alpha.npz | (10, 2278) | 0 | [0.010, 0.979] |
| X_schaefer100_wpli_alpha.npz | (10, 4950) | 0 | [0.011, 0.878] |
| X_schaefer100_coh_alpha.npz | (10, 4950) | 0 | [0.009, 0.992] |

y=[0,1,0,1,0,1,0,1,0,1] (EO=0, EC=1), groups=[0,0,1,1,2,2,3,3,4,4] LOSO-ready.

### STEP 6 — ML Classification LOSO (S-106)

LogReg / SVM-RBF / LDA. 5-fold LOSO. n=10 — INDICATIVO.

| Atlas | Metric | Best clf | Bal.Acc |
|-------|--------|----------|---------|
| aparc | wpli | pari 0.700 | 0.700 |
| aparc | coh | logreg/svm_rbf | 0.800 |
| schaefer100 | wpli | logreg/lda | 0.700 |
| schaefer100 | coh | **logreg** | **0.900** |

### STEP 7 — Esperimenti confronto (S-107)

Aggregazione in `data/results/ds005385/comparison_matrix.json`.
Report completo: `reports/EXPERIMENTS_MINIMAL.md`.

**Winning config**: schaefer100 × coh × LogisticRegression (bal_acc=0.900).

---

## Summary statistics — FINALE

| Metrica | Valore |
|---------|--------|
| Soggetti PILOT | 5 (sub-007/010/011/026/031) |
| Atlases | 2 (aparc 68 ROI, schaefer100 100 ROI) |
| Condizioni | 2 (EO, EC) |
| label_tc .npz (STEP 3b) | 20 / 20 |
| FC matrices (STEP 4b) | 40 / 40 |
| Feature matrices X | 4 (aparc/schaefer100 × wpli/coh) |
| ML combos testati | 12 (4 × 3 clf) |
| Best config | schaefer100 × coh × LogReg bal=0.90 |
| Wall-clock totale pipeline | ~6 min (S-101b→S-107) |
| Verdict pipeline | **PASS** ✅ |
| Next step | full run N=15→179 con best config |
