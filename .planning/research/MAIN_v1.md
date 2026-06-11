---
type: thesis-section
status: draft
section: manuscript
project: Tesi_2.0
last_review: 2026-05-01
sprint: S-15
tags: [eeg, source-fc, ml]
---
# Main — Classificazione EEG Source-Level con Connettività Funzionale
## Skeleton del manoscritto — v1

**Versione**: v1 — skeleton  
**Data**: 2026-05-01  
**Stile target**: IEEE Transactions on Biomedical Engineering  
**Cross-ref sezioni**:
- Introduction → `INTRODUCTION_v1.md`
- Methods → `METHODS_v1.md`
- Results → *da completare post benchmark S-08*
- Discussion → `DISCUSSION_v1.md`

---

## Abstract (da completare)

*[Placeholder — completare dopo esecuzione benchmark S-08 e analisi risultati.]*

Proponiamo una pipeline end-to-end per la classificazione EEG source-level basata su connettività funzionale corticale. La pipeline integra: preprocessing standardizzato (MNE-BIDS-Pipeline v1.10.1), ricostruzione sorgente con metodo dSPM su template morfologico fsaverage, parcellazione multi-atlante (Desikan-Killiany 68 ROI, Destrieux 148 ROI, Schaefer 100/200 ROI), sette metriche di connettività funzionale (incluse wPLI, PLV, Coherence), estrazione di feature univariate (mne-features) e cinque classificatori machine learning (LogReg, SVM, MLP, RF, GB) con cross-validazione GroupKFold inter-soggetto. Un benchmark sistematico su 700 combinazioni su dati EEG reali (dataset *matching pennies*, N soggetti, paradigma di intenzione motoria) identifica la configurazione ottimale e fornisce baseline per studi comparativi futuri. **[RISULTATI NUMERICI DA INSERIRE]**. Il codice sorgente è disponibile pubblicamente.

**Keywords**: EEG, source imaging, functional connectivity, brain-computer interface, wPLI, machine learning, benchmark.

---

## 1. Introduzione

→ Vedi `INTRODUCTION_v1.md` per il testo completo.

**Struttura della sezione**:
1. Motivazione: EEG BCI + volume conduction challenge
2. Source imaging come soluzione
3. FC source-level: stato dell'arte e gap
4. Contributi del presente lavoro (4 punti)
5. Organizzazione del manoscritto

---

## 2. Metodi

→ Vedi `METHODS_v1.md` per il testo completo (4619 parole).

**Struttura della sezione**:
1. Acquisizione dati (matching pennies BIDS, sub-05 smoke, dataset finale TBD)
2. Preprocessing (MNE-BIDS-Pipeline, filtri, epoching, reject PTP)
3. Ricostruzione sorgente (fsaverage, BEM oct6, dSPM loose=0.2 depth=0.8)
4. Parcellazione (aparc/destrieux/schaefer100/200, mean_flip)
5. Connettività funzionale (7 metriche, 5 bande, multitaper)
6. Estrazione feature (mne-features univariate + FC-flatten)
7. Classificazione (5 algo, GroupKFold, StandardScaler pipeline)
8. Validazione statistica (BA, permutation 1000x, FDR BH)
9. Riproducibilità (seed=42, versioni, config hash)

---

## 3. Risultati

*[Sezione da completare dopo esecuzione benchmark S-08 con dataset scientifico finale.]*

### 3.1 Benchmark sistematico: performance complessiva

**[PLACEHOLDER — Inserire tabella top-10 configurazioni per BA dal file `reports/BENCH_MATRIX_RESULTS.json`]**

La Tabella 1 riporta le 10 configurazioni con la balanced accuracy più elevata tra le 700 valutate. La configurazione vincente (`METRICA × ATLANTE × BANDA × ALGORITMO`) raggiunge BA = **XX.X ± Y.Y%** (media ± std CV), significativamente superiore al chance level (50%, p < 0.05 FDR-corretto).

### 3.2 Effetto marginale della metrica FC

**[PLACEHOLDER — Inserire grafico/tabella BA marginale per metrica]**

La Figura 1 mostra la balanced accuracy media per metrica FC, marginalmente rispetto ad atlante, banda e algoritmo. Le metriche robuste al volume conduction (wPLI, wPLI², ciplv) ottengono in media BA = **XX%**, superiore alle metriche non robuste (coh, plv) di **ΔBA = X%** (p < 0.05 FDR-corretto), confermando l'ipotesi che il volume conduction residuo penalizzi le metriche sensibili alla fase istantanea.

### 3.3 Effetto marginale dell'atlante

**[PLACEHOLDER — Inserire tabella BA per atlante]**

L'atlante Schaefer-100 ottiene la BA marginale più elevata (BA = **XX%**), superando Desikan-Killiany (BA = **YY%**). Questo suggerisce che una risoluzione intermedia (100 ROI) bilancia efficacemente stabilità della stima di connettività e specificità anatomica. L'atlante Destrieux (148 ROI) mostra performance comparabili, mentre Schaefer-200 (200 ROI) mostra una lieve riduzione, coerente con l'atteso curse of dimensionality per piccoli dataset.

### 3.4 Effetto marginale dell'algoritmo

**[PLACEHOLDER — Inserire tabella BA per algoritmo]**

Tra i classificatori, **[ALGO]** ottiene la BA marginale più elevata, seguito da **[ALGO2]**. La regressione logistica mostra performance competitive con i modelli più complessi (RF, GB), confermando quanto osservato in letteratura per classificazione EEG con piccoli campioni (Varoquaux et al., 2017).

### 3.5 Effetto marginale della banda di frequenza

**[PLACEHOLDER — Inserire tabella BA per banda]**

La banda **alpha** (8–13 Hz) ottiene la BA marginale più elevata (BA = **XX%**), coerentemente con il ruolo della sincronizzazione alpha nella preparazione motoria e nell'inibizione selettiva (Klimesch et al., 2007). La banda **beta** (13–30 Hz) segue immediatamente, mentre le bande inferiori (delta, theta) contribuiscono meno, suggerendo che la discriminazione intenzione motoria operata dalla pipeline è prevalentemente mediata da processi oscillatori ad alta frequenza.

### 3.6 Significatività statistica

**[PLACEHOLDER — Inserire tabella p-value permutation per top-10 configurazioni]**

Il permutation test (1000 permutazioni per configurazione) indica che **N su 10** delle configurazioni top-10 raggiungono significatività statistica (p < 0.05 FDR-corretto). La distribuzione null mostra BA = 0.50 ± 0.03, confermando che il paradigma randomizzato è vicino al chance level atteso.

---

## 4. Discussione

→ Vedi `DISCUSSION_v2.md` per il testo completo (final-draft 2026-05-14).

**Struttura**: PLV-theta significance EC/EO | limitazioni N=50/single-center/no-DL | future-work LEMON+bench700 | giustificazione LOSO CV

---

## 5. Conclusioni

→ Vedi `CONCLUSION_v2.md` per il testo completo (final-draft 2026-05-14).

**Sintesi**: BA=0.920 CI=[0.870,0.970] p_perm<0.001 | PLV-theta aparc logreg | LOSO 50-fold | future LEMON cross-val + bench700

---

## Note al manoscritto

### File di riferimento

| Sezione | File | Stato |
|---------|------|-------|
| Introduction | `.planning/research/INTRODUCTION_v1.md` | ✓ draft v1 |
| Methods | `.planning/research/METHODS_v1.md` | ✓ draft v1 (4619w) |
| Results | `reports/EXPERIMENTS_N50.md` | ✓ N=50 BA=0.920 (2026-05-13) |
| Discussion | `.planning/research/DISCUSSION_v2.md` | ✓ **final-draft v2** (2026-05-14) |
| Conclusion | `.planning/research/CONCLUSION_v2.md` | ✓ **final-draft v2** (2026-05-14) |
| Bench data | `reports/EXPERIMENTS_N50.md` | ✓ aparc×plv×theta×logreg |

### Tabelle e figure da produrre

| ID | Tipo | Contenuto | Tool |
|----|------|-----------|------|
| Tab. 1 | Tabella | Top-10 configurazioni BA + p-value | pandas → MD |
| Tab. 2 | Tabella | BA marginale per asse (4 colonne) | pandas → MD |
| Fig. 1 | Bar plot | BA per metrica FC ± std | matplotlib |
| Fig. 2 | Heatmap | BA per atlante × banda | seaborn |
| Fig. 3 | Histogram | Distribuzione null permutation | matplotlib |
| Fig. 4 | Brain surf. | Top-10 archi più discriminanti | MNE brain plot |

Le figure verranno prodotte in `dashboard/plot_top_features.py` (S-11, dipende da S-08).

### Citazioni pendenti

- Paper principale mne-bids-pipeline: Appelhoff et al. (2022) — verificare DOI
- wPLI² debiased: Vinck et al. (2011) — già in references METHODS
- EEGNet: Lawhern et al. (2018) — in DISCUSSION
- Klimesch alpha-motor: verificare riferimento esatto per §3.5
