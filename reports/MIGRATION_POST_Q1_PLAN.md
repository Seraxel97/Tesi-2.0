# Migration Plan — Post-Q1 Risolto: Pipeline ds005385

**Sprint**: S-47  
**Data**: 2026-05-01  
**Worker**: sonnet2-ts  
**Timestamp decisione Q1**: 2026-05-01T13:34 (operatore conferma ds005385)

---

## 1. Stato Q1 risolto

| Evento | Timestamp | Dettaglio |
|--------|-----------|-----------|
| Q1 risolto | 2026-05-01T13:34 | Dataset scientifico: **ds005385** (Dortmund Vital Study) |
| Symlink applicato | 2026-05-01T18:30 | `data/raw/ds005385 → ~/Scrivania/Tesi/data/ds005385` |
| Vincolo HARD operatore | 2026-05-01T18:25 | N max=20 sub. NO 200-full run |
| Subset policy | S-100b PASS | N=15, random seed=42 |
| Pilot 5 sub | S-101 in flight | sonnet1-ts — source recon 5 sub iniziale |

**Cross-ref file prodotti**:
- `config/labels_ds005385.py` (S-100) — EO/EC mapping, lista 21 esclusi
- `config/subjects_whitelist.py` (S-100b) — whitelist 15 sub finali
- `reports/DS005385_STRUCTURE.md` (S-100) — analisi BIDS completa
- `reports/SUBSET_POLICY.md` (S-100b) — criterio selezione + demografiche

---

## 2. Decision tree aggiornato

```
Q1 RISOLTO → ds005385 ✅
    │
    ├─ Symlink data/raw/ds005385 ✅ (T18:30)
    ├─ BIDS analysis + EO/EC mapping (S-100) ✅ DONE
    ├─ Subset policy N=15 seed=42 (S-100b) ✅ DONE
    ├─ Config sanity check (S-100c) ✅ DONE
    │
    ├─ PILOT 5 sub source recon (S-101) → IN FLIGHT (sonnet1-ts)
    │       │
    │       ▼  [gate OPERATOR_APPROVE_5SUB]
    │
    ├─ S-102 FULL SCALE (200 sub) → ⛔ DEPRECATED
    │       Motivo: vincolo HARD N max=20 + disco 22 GB critico
    │
    └─ PIPELINE SUBSET (15 sub, post gate operatore)
            ├─ S-103: parcellazione (aparc + schaefer100)
            ├─ S-104: connectivity wPLI + coherence alpha
            ├─ S-105: feature extraction
            ├─ S-106: ML primo run reale
            └─ S-107: esperimenti minimi (2×2×2 matrix)
```

---

## 3. Migration steps dettagliati

### 3.1 Completati (DONE)

| Sprint | Titolo | Stato | Output |
|--------|--------|-------|--------|
| S-100 | BIDS analysis + symlink + EO/EC mapping | DONE | `reports/DS005385_STRUCTURE.md`, `config/labels_ds005385.py` |
| S-100b | Subset policy N=15 seed=42 | DONE | `config/subjects_whitelist.py`, `reports/SUBSET_POLICY.md` |
| S-100c | Config sanity check | DONE | `reports/CONFIG_SANITY.md` |

### 3.2 In corso

| Sprint | Titolo | Owner | Gate |
|--------|--------|-------|------|
| S-101 | Source recon PILOT 5 sub | sonnet1-ts | OPERATOR_APPROVE_5SUB |

**S-101 deliverable attesi**: `data/stcs/ds005385/sub-{007,010,011,026,031}_*-dSPM-{lh,rh}.stc` + `reports/STEP2_DS005385_PILOT.md`.

### 3.3 S-102 DEPRECATED

S-102 (`STEP 2 SCALE: source recon 200 sub`) è **formalmente deprecato**:
- Vincolo HARD operatore: N max=20 (impossibile 200-full).
- Disco: 22 GB liberi su 915 GB (98% usato) — source recon 200 sub richiederebbe ~40-80 GB aggiuntivi.
- Dep `OPERATOR_APPROVE_FULL_SCALE` non verrà mai soddisfatta in questa configurazione.

**Azione richiesta**: queue S-102 → `status=deprecated` (da fare al prossimo orch dispatch).

### 3.4 Pipeline subset (post gate operatore su S-101)

Le dep di S-103..S-107 devono essere aggiornate: `S-102 → S-101` (operare su subset 15 sub, non 200).

| Sprint | Titolo | Dep attuale | Dep corretta | Scope |
|--------|--------|-------------|--------------|-------|
| S-103 | Parcellazione ds005385 | S-102 | **S-101** | 15 sub × 2 atlas (aparc, schaefer100) |
| S-104 | Connectivity wPLI + coh alpha | S-103 | S-103 | 15 sub × 2 atlas × 2 metric |
| S-105 | Feature extraction | S-104 | S-104 | X matrix (15 sub × feature_dim) |
| S-106 | ML primo run reale | S-105 | S-105 | LogReg + RF, GroupKFold(10), permutation |
| S-107 | Esperimenti minimi 2×2×2 | S-106 | S-106 | 8 config cell comparison |

**Azione richiesta**: orch aggiorna deps S-103 in queue prima del dispatch.

---

## 4. Rischi e mitigazioni

### Rischio 1 — Disco critico (22 GB liberi, 98% usato)

| Stima consumo | Valore |
|---------------|--------|
| STC 15 sub × 2 cond × 2 emisferi | ~3-5 GB |
| Label TC (15 sub × 2 atlas × acq-pre) | ~0.5 GB |
| FC matrices (15 sub × 2 atlas × 2 metric) | ~0.2 GB |
| Feature matrices + risultati ML | ~0.1 GB |
| **Totale stimato (15 sub)** | **~4-6 GB** |

15 sub: **fattibile** con 22 GB disponibili. Margine ~16 GB sufficiente.  
Full scale 200 sub: **impossibile** (~55-80 GB stima, 3.5× lo spazio libero).

**Mitigazione**: dopo S-101 pilot (5 sub) verificare uso disco effettivo prima di procedere a S-103 sui 15 sub completi. Aggiungere check disco in `scripts/repo_sanity.sh`.

### Rischio 2 — Source recon rendering 3D (xvfb)

Ambiente headless: `finalize_inverse.py` già bypassa il rendering MNE (`DISPLAY` non richiesto per source recon numerica). Confermato funzionante su sub-05 matchingpennies.

**Mitigazione**: usare `MNE_3D_OPTION=pyvistaqt` + `import os; os.environ['DISPLAY']=':99'` solo se MNE report HTML richiesto. Per pipeline scientifica: skip HTML report, salvare solo STC file.

### Rischio 3 — Bias demografico nel subset

Subset random seed=42: F=11, M=4 (sbilanciato). Età 23-70, media 47.3.  
Per paper finale il bias non è critico (pilot + esperimenti minimi), ma va menzionato nelle limitazioni.

**Mitigazione**: documentare nelle limitazioni del METHODS. Non richiederebbe re-campionamento per la fase attuale.

### Rischio 4 — EDF format parsing (1000 Hz, 64 ch, ref FCz online)

EDF BrainProducts: lettura via `mne.io.read_raw_edf()` testata su dataset simili.  
Ref FCz online → MNE aggiunge FCz come canale flat durante il caricamento.

**Mitigazione**: `raw.set_eeg_reference('average')` dopo caricamento per rimuovere FCz bias. Già previsto in `config/labels_ds005385.py` note.

---

## 5. Sequenza dispatch raccomandati (post S-101 gate)

```
1. Operatore approva S-101 (STEP 2 pilot 5 sub) → OPERATOR_APPROVE_5SUB
2. Orch: update S-103 deps [S-102 → S-101] in queue
3. Orch: set S-102 status=deprecated in queue
4. Dispatch S-103 (parcellazione 15 sub × 2 atlas) — sonnet2-ts o sonnet3-ts
5. Dispatch S-104 (connectivity) — chain dopo S-103
6. Dispatch S-105 (features) — chain dopo S-104
7. Dispatch S-106 (ML primo run) — chain dopo S-105
8. Dispatch S-107 (esperimenti 2×2×2) — chain dopo S-106
```

Stima tempi:
- S-103: ~15-20 min (15 sub × 2 atlas, source recon su STC già pronti)
- S-104: ~5 min (wPLI + coh su label_tc)
- S-105: ~2 min (flatten upper triangle)
- S-106: ~10-15 min (ML con GroupKFold 10, 15 sub)
- S-107: ~20-30 min (8 config × GroupKFold)

**Stima totale wave scientifica**: ~1-1.5h dopo gate operatore.

---

## 6. Cross-ref file rilevanti

| File | Sprint | Contenuto |
|------|--------|-----------|
| `config/subjects_whitelist.py` | S-100b | Lista 15 sub + SUBSET_POLICY + RANDOM_SEED |
| `config/labels_ds005385.py` | S-100 | EO/EC mapping, 21 esclusi late_ses1, sfreq, n_ch |
| `reports/DS005385_STRUCTURE.md` | S-100 | Analisi BIDS, demografiche, quality flags |
| `reports/SUBSET_POLICY.md` | S-100b | Criterio A, tabella 15 sub, pilot 5-sub plan |
| `reports/STEP2_DS005385_PILOT.md` | S-101 | Output futuro: STC shape + sanity check 5 sub |
| `data/raw/ds005385/` | S-100 | Symlink → `~/Scrivania/Tesi/data/ds005385/` |
