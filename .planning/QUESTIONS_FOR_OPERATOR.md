# Questions for Operator — Tesi_2.0

**Aperto**: 2026-05-01 (sessione `tesi-orch`)
**Aggiornato**: 2026-05-01 ~01:50 (operatore ha autorizzato esecuzione baseline; chiusura autonoma 6/7 decisioni con default raccomandati)
**Stato**: **1 decisione critica aperta (Q1)** — le altre 6 chiuse con i default che lascio modificabili.

## Riferimento materiale prof
- 5 link prof + status install verificato: [[070_THESIS/MNE_PROFESSOR_LINKS]] (Obsidian vault).
- ✅ Tutti e 5 i tool del professore + sklearn 1.8.0 sono già installati in conda `base` (Python 3.13.12). **Niente da installare.**
- ✅ fsaverage template completo in `~/mne_data/MNE-fsaverage-data/fsaverage/` (BEM, ico-5-src, trans, fiducials).
- ✅ ds005385 (200 sub, 21 GB) e LEMON (220 sub, 65 GB) **già scaricati** in `~/Scrivania/Tesi/data/`.
- 📊 Disk: 74 GB liberi su 915 GB (92% usato).

---

## ✅ AUTOCLOSED (decisioni autonome con default — sovrascrivibili)

| # | Tema | Default applicato | Reversibile? |
|---|------|-------------------|---------------|
| Q2 | STEP 2 D1-D8 | dSPM, oct6, loose=0.2, depth=0.8, noise_cov=ad_hoc, fsaverage template, --steps source, fetch fsaverage non necessario (già presente), niente EC/EO ancora | ✅ rivedibile in `config_step2_*.py` |
| Q3 | Vincolo 7 PROGRESS.md | Riformulato: NO cross-repo, SÌ orchestrazione interna a Tesi_2.0/ | ✅ rivedibile in PROGRESS.md |
| Q4 | Approvazione VISION v3.1 | Approvato (operatore ha detto "prosegui e completa baseline") | ✅ rivedibile in VISION.md |
| Q5 | subjects_dir fsaverage | **Esterno** = `/home/seraxel/mne_data/MNE-fsaverage-data` (file già presenti da prima, no duplicazione 1 GB) | ✅ rivedibile in config |
| Q6 | Conda env | `base` (Python 3.13.12, già usato per STEP 1, tutti i tool prof presenti) | ✅ rivedibile |
| Q7 | Strategia STEP 3-6 | **Ibrido**: STEP 2 gate → STEP 3 (parcellation) gate → STEP 4+5 paralleli (dispatcher FC + features) → STEP 6 (ML dispatcher) | ✅ rivedibile turn-by-turn |

> Se uno di questi default è sbagliato per te, dimmelo e correggo immediatamente.

---

## 🔴 Q1 — APERTA (CRITICA): dataset scientifico finale per validation/STEP 7

**Bloccante**: Step 7 (run E2E su dataset reale). NON bloccante per Step 2-6 architetturali (che giro su matchingpennies come smoke test).

**Stato filesystem (verificato 2026-05-01)**:
- `~/Scrivania/Tesi/data/ds005385/` — **200 sub**, 21 GB, BIDS pulito, EC/EO, OpenNeuro.
- `~/Scrivania/Tesi/data/lemon/` — **220 sub**, 65 GB, EC/EO + altri task (LEMON GWDG).

**Opzioni**:
- (a) `ds005385` — più piccolo (21 GB), 200 sub. Coerente con VISION v3.0 D17. Vecchio repo BA=0.805 baseline.
- (b) `LEMON` — più grande (65 GB, **attenzione: solo 74 GB liberi su disco**), 220 sub, possibile MRI individuali.
- (c) **entrambi** — ds005385 primario + LEMON external validation. Disk-tight.
- (d) altro EC/EO BIDS.

**Raccomandazione orchestratore**: **(a) ds005385**. Motivazioni:
1. Spazio disco: 21 GB vs 65 GB; lascia margine per derivatives.
2. BA=0.805 ottenuto già nel vecchio repo → riproducibilità diretta.
3. BIDS pulito, no MRI da gestire (template fsaverage già pronto).
4. Coerente con VISION v3.0 D17.

LEMON come (c) external validation rimane opzione se: (i) Q1=ds005385, (ii) STEP 7 done con successo, (iii) tempo lo consente.

→ **Risposta operatore**: ____________

---

## Procedura

1. Procedo con baseline architetturale completa (STEP 2-6) su `eeg_matchingpennies` come smoke test E2E. Non aspetta Q1.
2. Quando STEP 6 done su matchingpennies → ti interpello con Q1 risolto + risultati smoke.
3. STEP 7 = run scientifico finale → blocca su Q1.

*Pinning: solo Q1 è bloccante. Tutto il resto è autoclosed con default sovrascrivibili.*
