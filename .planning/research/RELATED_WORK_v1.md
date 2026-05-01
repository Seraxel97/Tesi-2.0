# Related Work — EEG Source-Level FC Pipelines

**Versione**: v1  
**Data**: 2026-05-01  
**Sprint**: DR-RESEARCH-eeg-fc-pipelines-soa  
**Cross-ref**: `EEG_PIPELINES_COMPARISON.md`, `INTRODUCTION_v1.md`, `METHODS_v1.md`  
**Target**: ~600 parole, stile IEEE Trans. Biomed. Eng.

---

## Related Work

Negli ultimi anni, la comunità di neuroimaging computazionale ha sviluppato diverse pipeline open-source per l'analisi EEG. Queste possono essere organizzate in tre categorie: pipeline di preprocessing standardizzato, framework di benchmark BCI, e pipeline di connettività funzionale. Il presente lavoro si posiziona all'intersezione delle ultime due categorie, colmando un gap specifico nella letteratura.

### Preprocessing standardizzato

**Discover-EEG** (Crisol-Martínez et al., 2023) e **mne-bids-pipeline** (Appelhoff et al., 2022) rappresentano lo stato dell'arte per il preprocessing standardizzato di dati EEG in formato BIDS. Discover-EEG si focalizza sul quality control automatizzato (ICA, rejection PTP, interpolazione bad channels) e sulla produzione di report diagnostici. mne-bids-pipeline estende questa visione integrando la ricostruzione sorgente e il decoding sensor-level, diventando il framework di riferimento per studi di gruppo secondo le raccomandazioni della comunità MNE. Entrambe le pipeline, tuttavia, si fermano prima della connettività funzionale source-level: mne-bids-pipeline produce source time courses (STC) evoked ma non include moduli per l'estrazione di FC tra ROI parcellate.

### Benchmark BCI sensor-level

**MOABB** (Jayaram & Barachant, 2018; Chevallier et al., 2024) è il gold standard per il benchmark riproducibile di algoritmi BCI sensor-level. MOABB implementa il protocollo Leave-One-Subject-Out (LOSO) con seed fisso e correzione statistica, e supporta nativamente decine di dataset e algoritmi scikit-learn. Il punto di forza di MOABB — la comparazione sistematica di centinaia di configurazioni con validità statistica — è direttamente mutuato nel presente lavoro (700-run benchmark matrix, GroupKFold, permutation test + FDR). Il limite di MOABB è il dominio sensor-level: opera su covarianze spaziali e pattern ERPsenza proiezione sorgente, rendendo i risultati meno interpretabili neurobiologicamente.

### Connettività funzionale source-level

**NeuroPycon/ephypype** (Meunier et al., 2020) è la pipeline open-source più vicina concettualmente al presente lavoro. Implementata su nipype, supporta la ricostruzione sorgente MNE e il calcolo di connettività tramite mne-connectivity (coerenza, PLV, coerenza immaginaria). Tuttavia, NeuroPycon presenta limitazioni rilevanti: le dipendenze nipype introducono overhead di configurazione significativo; il supporto per metriche robuste al volume conduction (wPLI, debiased wPLI²) è parziale; e non include un modulo di classificazione machine learning con validazione inter-soggetto. La documentazione è stata ridotta dopo il 2021.

Studi singoli — non organizzati in framework riutilizzabili — hanno dimostrato la fattibilità della classificazione EEG source-level FC. Sabbagh et al. (2020) comparano regressione su potenza sorgente e FC-MEG per la predizione di età cognitiva, trovando che la FC source-level supera le feature sensor-level. Grosse-Wentrup et al. (2009) applicano beamforming + coerenza sorgente a un paradigma BCI, mostrando che la connettività fronto-parietale discrimina l'intenzione motoria. Nessuno di questi lavori, tuttavia, fornisce un framework riutilizzabile con benchmark sistematico su metriche e atlanti multipli.

### Posizionamento di Tesi_2.0

Il presente lavoro colma il gap tra mne-bids-pipeline (upstream, preprocessing) e la letteratura di classificazione source-level FC (downstream, analisi singole). La pipeline Tesi_2.0 è progettata come **estensione modulare** di mne-bids-pipeline: non reimplementa il preprocessing ma parte dagli output prodotti (STC, epochs, forward .fif) e aggiunge quattro moduli downstream — parcellazione multi-atlante, sette metriche FC robuste al volume conduction, estrazione feature e ML dispatcher — in un pattern che permette il cambio di configurazione tramite parametro senza modifiche al codice.

Rispetto allo stato dell'arte, i contributi distintivi sono: (i) la scelta esplicita di metriche robuste al volume conduction (wPLI, wPLI², ciplv) come metriche primarie, motivata empiricamente dalla letteratura recente (Nagy et al., 2024; Vinck et al., 2011); (ii) l'implementazione di GroupKFold inter-soggetto con permutation testing batch su 700 configurazioni — una scala di validazione sistematica non raggiunta dai framework esistenti; (iii) il confronto multi-atlante (Desikan-Killiany, Destrieux, Schaefer-100/200) come analisi della sensitività alla granularità parcellare, rara nella letteratura EEG source-level.

---

## Riferimenti

- Appelhoff, S., et al. (2022). MNE-BIDS. *Journal of Open Source Software*, 5(44).
- Chevallier, S., et al. (2024). The largest EEG-based BCI reproducibility study. *NeuroImage*, 285.
- Crisol-Martínez, E., et al. (2023). Discover-EEG. *Scientific Data*, 10, 286.
- Grosse-Wentrup, M., et al. (2009). Beamforming in noninvasive brain–computer interfaces. *IEEE Trans. Biomed. Eng.*, 56(4).
- Jayaram, V., & Barachant, A. (2018). MOABB. *Journal of Neural Engineering*, 15(6).
- Meunier, D., et al. (2020). NeuroPycon. *NeuroImage*, 219.
- Nagy, Z., et al. (2024). Disentangling spurious from genuine source-level FC. *Human Brain Mapping*, 45(3).
- Sabbagh, D., et al. (2020). Predictive regression modeling with MEG/EEG. *NeuroImage*, 222.
- Vinck, M., et al. (2011). An improved index of phase-synchronization. *NeuroImage*, 55(4).
