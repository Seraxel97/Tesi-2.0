# Scientific Pipeline Status — ds005385 PILOT

**Timestamp**: 2026-05-01T19:08:00+02:00
**Sprint**: S-112 (sonnet3-ts)
**Dataset**: ds005385 (Dortmund Vital Study) — subset N=15, seed=42
**PILOT subjects**: sub-007, sub-010, sub-011, sub-026, sub-031
**Atlases**: aparc (68 ROI), schaefer100 (100 ROI)
**Conditions**: EO (Eyes Open), EC (Eyes Closed)

---

## Stato step — overview

| Step | Descrizione | Soggetti | Stato | Sprint | Note |
|------|-------------|----------|-------|--------|------|
| 1 | Preprocessing raw BIDS | 5 PILOT | completato | S-100, S-100b | Dati raw accessibili via symlink, EO/EC mapping validato |
| 2 | Source reconstruction (dSPM) | 5 PILOT | completato | S-101 | 20 STC file, 415 MB |
| 3 | Parcellazione atlastica | 5 x 2 atlas x 2 cond | completato | S-103 | 20 .npz file, 3.1 MB |
| 4 | FC spettrale (wPLI + coh) | 5 x 2 atlas x 2 cond | in corso | S-104 | claimed sonnet1-ts |
| 5 | Feature extraction | — | in attesa | S-105 | gate: S-104 done |
| 6 | ML classification | — | in attesa | S-106 | gate: S-105 done |
| 7 | E2E validation + report | — | in attesa | S-107 | gate: S-106 done |

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

## Summary statistics

| Metrica | Valore |
|---------|--------|
| Soggetti PILOT completati (STEP 1-3) | 5 / 5 |
| Atlases | 2 (aparc, schaefer100) |
| Condizioni | 2 (EO, EC) |
| STC file prodotti (STEP 2) | 20 (5 sub x 2 cond x 2 emisferi) |
| .npz label_ts prodotti (STEP 3) | 20 / 20 |
| Disk usage STEP 2 (STC) | ~415 MB (5 x 83 MB) |
| Disk usage STEP 3 (label_ts) | 3.1 MB |
| Disk usage totale PILOT (STEP 2+3) | ~418 MB |
| Wall-clock STEP 2 | 28.7s |
| Wall-clock STEP 3 | 5.2s |
| Step 4 | in corso (S-104) |
| Step 5-7 | pending gate operatore |
