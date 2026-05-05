---
type: thesis-section
status: draft
section: discussion
project: Tesi_2.0
last_review: 2026-05-01
sprint: S-35
tags: [eeg, source-fc, ml]
---
# Discussion — Classificazione EEG Source-Level con Connettività Funzionale

**Versione**: v1 — draft  
**Data**: 2026-05-01  
**Target**: ~1200 parole, stile IEEE Trans. Biomed. Eng.

---

## 1. Interpretazione dei risultati

*[Sezione da completare dopo l'esecuzione del benchmark S-08 su dataset completo. Segnaposto strutturale.]*

Il benchmark sistematico (700 combinazioni, `reports/BENCH_MATRIX_RESULTS.json`) permetterà di rispondere alle seguenti domande principali:

**Q1 — Quale metrica FC è più discriminante?**  
La letteratura suggerisce wPLI e wPLI² come metriche più robuste per source-level EEG (Vinck et al., 2011; Sabbagh et al., 2020). Se confermato empiricamente, questo supporta l'ipotesi che il volume conduction residuo — presente anche dopo ricostruzione sorgente con template MRI — sia una sorgente rilevante di rumore nella pipeline. In alternativa, se le metriche non robuste (Coh, PLV) ottengono performance comparabili, suggerirebbe che la proiezione sorgente ha già ridotto sufficientemente il volume conduction.

**Q2 — Quale atlante produce le feature più discriminanti?**  
Un atlante a bassa risoluzione (aparc, 68 ROI) produce feature stabili ma potenzialmente poco specifiche. Un atlante ad alta risoluzione (schaefer200, 200 ROI) cattura topologie funzionali più fini ma espone a curse of dimensionality. Le performance marginali per asse atlante nel benchmark forniranno una risposta empirica a questo trade-off per il paradigma motorio.

**Q3 — Quale classificatore generalizza meglio?**  
La regressione logistica, pur essendo il modello più semplice, è spesso competitiva in BCI grazie alla sua regolarizzazione naturale (C=1.0) e alla robustezza in alta dimensione con pochi campioni. I modelli ensemble (RF, GB) potrebbero beneficiare della struttura gerarchica delle feature di connettività. I risultati empirici guideranno la selezione del classificatore per gli esperimenti scientifici principali.

**Q4 — Quale banda di frequenza contribuisce maggiormente?**  
In letteratura, la banda alpha (8–13 Hz) è associata a processi di inibizione e selezione attentiva, mentre beta (13–30 Hz) è collegata al controllo motorio. Per un paradigma di intenzione motoria come *matching pennies*, è atteso un contributo prominente delle bande alpha e beta. Il benchmark verificherà questa ipotesi e identificherà eventuali contributi inaspettati dalle bande delta/theta/gamma.

---

## 2. Limiti metodologici

### 2.1 Template MRI vs. MRI individuale

L'uso del template fsaverage introduce un errore di localizzazione stimato di 1–2 cm rispetto a una forward solution individuale (Huang et al., 2016). Questo errore è maggiore per soggetti con morfologia corticale molto diversa dalla media. Per studi clinici o di neurofeedback che richiedono localizzazione precisa, l'acquisizione di una MRI strutturale individuale è raccomandata. Nel contesto del presente studio — classificazione di pattern di connettività su larga scala — l'errore di localizzazione è ritenuto accettabile, poiché le ROI parcellate integrano l'attività su aree di centinaia di cm², assorbendo errori di pochi centimetri.

### 2.2 Covarianza rumore ad-hoc

L'utilizzo della covarianza rumore *ad-hoc* (baseline pre-stimolo) è una soluzione pragmatica in assenza di registrazioni empty-room o dati di riposo sufficientemente lunghi. Questa stima è potenzialmente poco robusta se la baseline contiene attività neurale specifica della condizione (es. aspettativa motoria pre-stimolo). Una valutazione futura con dati resting-state come noise covariance (se il dataset lo consente) potrebbe migliorare la qualità dell'inversione.

### 2.3 Stima FC su singola sessione

La matrice di connettività funzionale è calcolata sull'insieme di tutti i trial di una sessione (100 epoch per sub-05) e poi replicata per tutti i trial come feature costante. Questo implica che la FC riflette la connettività *media* della sessione, non le fluttuazioni trial-to-trial. Approcci alternativi — come la FC calcolata per singolo trial tramite wavelet o metodi nel dominio del tempo — potrebbero catturare dinamiche più fini ma richiedono più dati e introdurre ulteriore varianza di stima.

### 2.4 Generalizzabilità inter-soggetto

Lo smoke test è condotto su un solo soggetto (sub-05), rendendo impossibile valutare la generalizzabilità. Il dataset scientifico finale (Q1 pendente) permetterà di applicare GroupKFold inter-soggetto e di testare se i pattern di connettività appresi sono generalizzabili a nuovi individui — requisito fondamentale per applicazioni BCI real-world.

### 2.5 Assenza di denoising artefatti avanzato

La pipeline attuale non include componenti ICA (*Independent Component Analysis*) per la rimozione di artefatti oculari e muscolari, né SSP (*Signal Space Projection*). MNE-BIDS-Pipeline supporta entrambi (parametri `ica_method`, `ssp_*`), e il loro impiego sul dataset finale potrebbe migliorare la qualità del segnale pre-inversione. La scelta di escluderli dallo smoke test è motivata dalla semplicità e dalla mancanza di un modello ICA validato per il dataset *matching pennies*.

---

## 3. Prospettive future

### 3.1 Estensione a resting-state

Il framework sviluppato è direttamente applicabile all'analisi resting-state (dataset LEMON o equivalente), dove la connettività funzionale in stato di riposo è correlata a tratti cognitivi, personalità e marcatori clinici (Buckner et al., 2008). In questo contesto, il paradigma di classificazione cambia: le etichette non sono legate a trial discreti ma a caratteristiche del soggetto (es. giovane/anziano, sano/clinico), richiedendo una segmentazione temporale sliding-window e una strategia di aggregazione su più finestre.

Il modulo `source_reconstruction/apply_inverse_epochs_rs.py` (S-09) è già predisposto per l'analisi resting-state con epoch sliding di 2 secondi.

### 3.2 Integrazione neuromaps

Il modulo `parcellation/neuromaps_helper.py` consente di arricchire le feature di connettività con annotazioni neuroscientifiche per ROI (es. gradient evolutivo di Margulies et al., 2016; mappa di mielinizzazione di Glasser et al., 2016). Questi descrittori neurobiologici potrebbero funzionare come *priors* per la selezione delle feature o come feature aggiuntive in modelli multi-source.

### 3.3 Feature selection e riduzione dimensionale

Con 700 run nel benchmark, emerge la necessità di metodologie sistematiche di selezione delle feature per ridurre la dimensionalità del problema di classificazione. Approcci come Elastic Net, Recursive Feature Elimination (RFE), o metodi basati su importanza feature (SHAP) potrebbero migliorare la performance su dataset multi-soggetto. Una sezione futura del paper potrebbe confrontare sistematicamente queste strategie.

### 3.4 Modelli profondi

Le reti neurali convoluzionali sul segnale raw (EEGNet, Lawhern et al., 2018; ShallowConvNet, Schirrmeister et al., 2017) sono alternative competitive alle pipeline tradizionali e potrebbero essere integrate come sesto classificatore nel benchmark. Tuttavia, i modelli profondi richiedono dataset più grandi (tipicamente >100 soggetti) per evitare overfitting, e la loro interpetabilità è più limitata rispetto ai classificatori lineari.

---

## 4. Conclusioni

*[Sezione da completare dopo analisi risultati benchmark.]*

Il presente lavoro ha sviluppato una pipeline modulare, riproducibile e sistematicamente validata per la classificazione EEG source-level basata su connettività funzionale. La pipeline integra step di preprocessing standardizzato (MNE-BIDS-Pipeline), ricostruzione sorgente con template morfologico (dSPM, fsaverage), parcellazione multi-atlante (aparc, destrieux, Schaefer 100/200), sette metriche di connettività funzionale e cinque classificatori machine learning in un'architettura completamente riproducibile. Il benchmark sistematico su 700 combinazioni su dati EEG reali fornisce la base empirica per identificare la configurazione ottimale per il dataset scientifico finale.

---

## Riferimenti

- Buckner, R.L., et al. (2008). The brain's default network. *Annals of the New York Academy of Sciences*, 1124(1).
- Glasser, M.F., et al. (2016). A multi-modal parcellation of human cerebral cortex. *Nature*, 536.
- Huang, Y., et al. (2016). The impact of EEG electrode locations on spatial variability of brain activation. *Brain Topography*, 29.
- Lawhern, V.J., et al. (2018). EEGNet: a compact convolutional neural network for EEG-based brain–computer interfaces. *Journal of Neural Engineering*, 15(5).
- Margulies, D.S., et al. (2016). Situating the default-mode network along a principal gradient of macroscale cortical organization. *PNAS*, 113(44).
- Sabbagh, D., et al. (2020). Predictive regression modeling with MEG/EEG: from source power to signals and cognitive states. *NeuroImage*, 222.
- Schirrmeister, R.T., et al. (2017). Deep learning with convolutional neural networks for EEG decoding. *Human Brain Mapping*, 38(11).
- Vinck, M., et al. (2011). An improved index of phase-synchronization. *NeuroImage*, 55(4).
- Varoquaux, G., et al. (2017). Assessing and tuning brain decoders. *NeuroImage*, 159.
