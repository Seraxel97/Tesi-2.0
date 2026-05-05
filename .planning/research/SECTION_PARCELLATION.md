---
type: thesis-section
status: draft
section: methods
project: Tesi_2.0
last_review: 2026-05-01
sprint: DR-RESEARCH-parcellation
tags: [eeg, source-fc, ml]
---
# Literature Evidence — Parcellazione Corticale per EEG Source-Level Connectivity

**Sezione**: Methods — Parcellazione  
**Per**: STEP3_PROPOSAL.md / METHODS_v1.md  
**Data**: 2026-05-01  
**Parole**: ~750

---

## Literature Evidence: Granularità Ottimale per EEG Source FC

### 1. Vincolo fisico: risoluzione spaziale dell'EEG sorgente

La risoluzione spaziale della ricostruzione sorgente EEG dipende da tre fattori:
il numero di canali (64 nel presente studio), il modello di testa (fsaverage template,
senza MRI individuale), e il metodo di inverse (dSPM con regolarizzazione λ²=1/9).
Con 64 canali, il numero di gradi di libertà spaziali effettivi è stimato tra 50 e 100
sorgenti indipendenti, compatibile con atlanti di 68--100 ROI [[1]](#ref-farahibozorg2018).

### 2. Scelta dell'atlante primario: aparc (Desikan-Killiany, 68 ROI)

L'atlante Desikan-Killiany [[2]](#ref-desikan2006), implementato come `aparc` in FreeSurfer e MNE,
suddivide la corteccia in 68 regioni basate su anatomia macroscopica (gyri). Con 34 regioni
per emisfero, rappresenta la granularità tipicamente raccomandata per studi EEG sorgente.

Farahibozorg et al. (2018) [[1]](#ref-farahibozorg2018) dimostrano mediante simulazioni che
parcellazioni nella fascia 68--80 ROI massimizzano il Signal-to-Noise Ratio (SNR) della
connettività funzionale sorgente. Parcellazioni più fini (>150 ROI) incrementano
significativamente il **source leakage** inter-ROI: regioni adiacenti appaiono artificialmente
correlate anche in assenza di connettività reale. Metriche FC immaginarie (wPLI, PLI, imCoh)
riducono questo effetto, ma non lo eliminano completamente con atlanti oltre 100--150 ROI.

### 3. Atlanti di confronto

**Schaefer2018 (100/200 parcels)** [[3]](#ref-schaefer2018) è il candidato moderno per il confronto:
le ROI sono definite su base funzionale (resting-state fMRI intrinsica) e appartengono
a uno dei 7 network di Yeo (Default, Frontoparietal, Limbic, ecc.). Questo permette
di interpretare i risultati FC in termini di network theory. Con 100 parcels è comparabile
ad aparc in termini di granularità; con 200 parcels si avvicina al limite superiore per EEG.

**Destrieux a2009s (148 ROI)** [[4]](#ref-destrieux2010) usa nomenclatura anatomica gyri/sulci,
fornendo maggiore dettaglio sub-lobare rispetto ad aparc. Rimane nel range accettabile
per EEG, sebbene vicino al limite superiore.

**HCP MMP1 (360 aree)** [[5]](#ref-glasser2016) è il gold standard per neuroimaging multimodale
ad alta risoluzione (strutturale + funzionale + mielinico). Con 360 parcelle è eccessivamente
fine per EEG con 64 canali: il leakage renderebbe le stime FC non affidabili. Escluso
dal benchmark baseline; eventuale utilizzo futuro con MEG ad alta densità.

### 4. Strategia benchmark (Tesi_2.0)

In linea con le raccomandazioni della letteratura, il benchmark S-08 testa:

| Atlante | N ROI | Motivazione |
|---------|-------|-------------|
| aparc | 68 | Standard EEG, ottimale per SNR (Farahibozorg 2018) |
| destrieux | 148 | Confronto granularità intermedia |
| schaefer100 | 100 | Network-aware, confrontabile con aparc |
| schaefer200 | 200 | Limite superiore, valuta degradazione leakage |

La modalità di aggregazione **`mean_flip`** (default MNE) è raccomandata per source-level FC:
compensa il flip di segno delle sorgenti mantenendo la coerenza di fase necessaria per
metriche come PLV e Coherence [[1]](#ref-farahibozorg2018).

### 5. Limitazione: nessuna MRI individuale

Il presente studio usa fsaverage come template MRI per tutti i soggetti (vincolo tecnico:
assenza di scansioni T1 individuali nel dataset matchingpennies). Questa scelta introduce
un errore di localizzazione stimato di 1--2 cm per soggetto, che si aggiunge al leakage
di sorgente. L'impatto sulla FC è atteso come sistematico (non random) e non altera
la comparazione relativa tra configurazioni di atlas/metrica/algoritmo del benchmark.

---

## Riferimenti

<a id="ref-farahibozorg2018"></a>
[1] Farahibozorg SR, Henson RN, Hauk O (2018). Adaptive cortical parcellations for source
reconstructed EEG/MEG connectomes. *NeuroImage* 169:103--115.
DOI: [10.1016/j.neuroimage.2017.09.015](https://doi.org/10.1016/j.neuroimage.2017.09.015)

<a id="ref-desikan2006"></a>
[2] Desikan RS et al. (2006). An automated labeling system for subdividing the human cerebral
cortex on MRI scans into gyral based regions of interest. *NeuroImage* 31(3):968--980.
DOI: [10.1016/j.neuroimage.2006.01.021](https://doi.org/10.1016/j.neuroimage.2006.01.021)

<a id="ref-schaefer2018"></a>
[3] Schaefer A et al. (2018). Local-Global Parcellation of the Human Cerebral Cortex from
Intrinsic Functional Connectivity MRI. *Cerebral Cortex* 28(9):3095--3114.
DOI: [10.1093/cercor/bhx179](https://doi.org/10.1093/cercor/bhx179)

<a id="ref-destrieux2010"></a>
[4] Destrieux C, Fischl B, Dale A, Halgren E (2010). Automatic parcellation of human cortical
gyri and sulci using standard anatomical nomenclature. *NeuroImage* 53(1):1--15.
DOI: [10.1016/j.neuroimage.2010.06.010](https://doi.org/10.1016/j.neuroimage.2010.06.010)

<a id="ref-glasser2016"></a>
[5] Glasser MF et al. (2016). A multi-modal parcellation of human cerebral cortex.
*Nature* 536:171--178. DOI: [10.1038/nature18933](https://doi.org/10.1038/nature18933)

<a id="ref-coito2015"></a>
[6] Coito A et al. (2015). Dynamic directed interictal connectivity in left and right temporal
lobe epilepsy. *Epilepsia* 56(2):207--217. DOI: [10.1111/epi.12904](https://doi.org/10.1111/epi.12904)
