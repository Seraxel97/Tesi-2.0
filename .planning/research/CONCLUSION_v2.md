---
type: manuscript
status: final-draft
section: conclusion
project: Tesi_2.0
last_review: 2026-05-14
sprint: R-TESI-2.0-DISCUSSION-CONCLUSION
tags: [eeg, source-fc, ml, ds005385, ec-eo, plv, theta]
version: v2
language: italiano
target_journal: Journal of Neural Engineering
word_count_target: 350-450
---
# Conclusioni

## 1. Sintesi dei contributi

Il presente lavoro ha proposto e validato una pipeline modulare, reproducibile e
statisticamente rigorosa per la classificazione EEG source-level basata su connettività
funzionale corticale, applicata al dataset ds005385 (Dortmund Vital EEG, N=50 soggetti,
paradigma Eyes Closed / Eyes Open).

La configurazione ottimale identificata — connettività PLV nella banda theta (4–8 Hz),
atlante Desikan-Killiany (aparc, 68 ROI), regressione logistica L2 — raggiunge una
balanced accuracy di **0.920** (CI 95% BCa [0.870, 0.970]) con validazione
Leave-One-Subject-Out (LOSO, 50 fold) e significatività statistica p_perm < 0.001
(1000 permutazioni). La pipeline è implementata in Python, completamente versionata e
testata, e il codice è disponibile pubblicamente.

Il risultato evidenzia che la sincronizzazione di fase theta inter-regionale — catturata
a livello sorgente dSPM dopo parcellazione multi-ROI — è la firma neurofisiologica più
discriminante tra stato di riposo ad occhi chiusi e ad occhi aperti, in accordo con la
letteratura sulla de-sincronizzazione theta indotta da input sensoriali visivi e sulla
modulazione del default-mode network.

## 2. Limitazioni

La validazione si limita a un campione single-center (N=50), senza confronto cross-dataset
su popolazione indipendente. I classificatori adottati appartengono al paradigma ML
tradizionale; approcci deep learning sono esclusi per vincoli di dimensione del campione.
La LOSO CV è il gold standard di validazione **interna** disponibile, ma non sostituisce
una validazione esterna su dataset eterogeneo.

## 3. Impatto e prospettive

La pipeline sviluppata fornisce una base riproducibile per la ricerca sulla connettività
funzionale EEG resting-state. La struttura modulare — ogni step è un modulo Python
indipendente con API pubblica, type hints e test unitari — facilita estensioni a nuovi
atlanti, metriche e classificatori. I due sviluppi immediati pianificati sono:

1. **Validazione cross-dataset** con LEMON (228 soggetti, train-on-ds005385/test-on-LEMON)
   per quantificare la generalizzabilità inter-dataset dei pattern PLV-theta.
2. **Benchmark esteso** alle 700 combinazioni (aggiunta atlanti Schaefer-100/200/Destrieux
   e metriche wPLI/wPLI²/ciplv) per mappare sistematicamente il paesaggio di performance
   e verificare la robustezza del risultato PLV-theta su uno spazio iper-parametrico completo.

Questi sviluppi condizionano la trasformazione del presente studio da prova di concetto
rigorosa a contributo di ricerca pienamente generalizzabile.
