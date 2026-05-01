# Tesi_2.0 — Tracking progetto

**Path**: `/home/seraxel/Scrivania/Tesi_2.0/`
**Brief operatore**: estendere `mne-bids-pipeline` con parcellation + connectivity + ML, in modo lineare e controllato.
**Modalità lavoro**: step-by-step con conferma operatore, **niente** orchestrazioni cross-session, **niente** worker paralleli, **niente** cron/tmux automation.

---

## Stato step

| Step | Titolo | Stato | Data | Riferimento log |
|------|--------|-------|------|------------------|
| 1 | Setup pipeline (install + dataset test + preprocessing) | ✅ DONE | 2026-04-27 → 2026-04-28 | [reports/STEP1_LOG.md](reports/STEP1_LOG.md) |
| 2 | Source reconstruction (smoke test matchingpennies sub-05) | ✅ DONE | 2026-05-01 | [reports/STEP2_LOG.md](reports/STEP2_LOG.md) |
| 3 | Parcellazione (aparc / Schaefer / neuromaps?) | ⏳ TODO | — | — |
| 4 | Connettività (mne-connectivity) | ⏳ TODO | — | — |
| 5 | Feature extraction (mne-features) | ⏳ TODO | — | — |
| 6 | Machine Learning custom (sklearn) | ⏳ TODO | — | — |
| 7 | Verifica end-to-end | ⏳ TODO | — | — |

Legenda: ✅ DONE · 🔄 IN PROGRESS · 📝 PROPOSAL (in attesa conferma) · ⏳ TODO · ❌ BLOCKED

---

## Asset attuali

### Software installato (env `base`, Python 3.13.12)
- `mne 1.11.0`
- `mne-bids 0.18.0`
- `mne-bids-pipeline 1.10.1` ← installato STEP 1
- `mne-connectivity 0.8`
- `mne-features 0.3.2`
- `mne-icalabel 0.8.1`
- `scikit-learn 1.8.0`

### Dataset scaricati
| Nome | Ruolo | Path | Dim | Stato |
|------|-------|------|-----|-------|
| eeg_matchingpennies | TEST TECNICO pipeline | `data/eeg_matchingpennies/` | 716 MB | ✅ usato STEP 1 |
| ds005385 (Dortmund Vital, EC/EO) | Candidato dataset scientifico | NON scaricato | — | ⏸ blocco — attesa conferma operatore |
| LEMON (EC/EO) | Candidato dataset scientifico | NON scaricato | — | ⏸ blocco — attesa conferma operatore |

### Output prodotti
- `data/derivatives/mne-bids-pipeline/sub-05/eeg/` (epochs, raw filt, report HTML, scores, bads)
- `data/derivatives/mne-bids-pipeline/_cache/` (joblib cache per re-run istantaneo)

### Config esistenti
- `config/config_step1_matchingpennies.py` (preprocessing only)

---

## Vincoli OBBLIGATORI (da brief operatore)

1. NON creare pipeline alternative — usare mne-bids-pipeline come base reale
2. Librerie ammesse: SOLO MNE / mne-bids-pipeline / mne-connectivity / mne-features / scikit-learn
3. NO deep learning, NO modelli non necessari, NO tool extra
4. NO decisioni autonome non giustificate
5. Lavorare per step con conferma esplicita
6. Struttura cartelle fissa (10 dir già create), NO strutture alternative
7. NO orchestrazioni cross-session (decisione operatore 2026-04-28)

---

## Decisioni in sospeso (da confermare)

- [ ] Dataset scientifico finale: `ds005385` vs `LEMON` vs altro EC/EO BIDS
- [ ] STEP 2 — confermare prima dell'esecuzione (proposta in [reports/STEP2_PROPOSAL.md](reports/STEP2_PROPOSAL.md))
