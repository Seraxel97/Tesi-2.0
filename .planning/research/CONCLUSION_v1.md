---
type: manuscript
status: draft
section: conclusion
project: Tesi_2.0
last_review: 2026-05-01
sprint: S-36
tags: [eeg, source-fc, ml]
version: v1
language: italiano
target_journal: Journal of Neural Engineering
word_count_target: 350-450
date: 2026-05-01
---
# Conclusioni

## 1. Sintesi dei contributi

Il presente lavoro ha proposto e validato una pipeline modulare ed end-to-end per la
classificazione EEG source-level basata su connettività funzionale corticale, sviluppata
come estensione di MNE-BIDS-Pipeline v1.10.1. L'architettura a sette step — preprocessing
standardizzato, ricostruzione sorgente dSPM su template fsaverage, parcellazione
multi-atlante, calcolo delle matrici di connettività funzionale, estrazione di feature,
classificazione ML e verifica end-to-end — è stata implementata in un framework Python
completamente versionato, testato e riproducibile.

Il benchmark sistematico comprende 700 combinazioni di analisi (7 metriche FC × 5 bande
di frequenza × 4 atlanti corticali × 5 classificatori ML), con validazione GroupKFold
inter-soggetto e correzione FDR per test multipli. L'infrastruttura di test copre tutti
i moduli pubblici (508 test automatizzati), garantendo standard metodologici — riproducibilità,
tracciabilità, automazione CI — che rimangono rari negli studi computazionali di neuroimaging.

## 2. Limitazioni

Il smoke test condotto su un singolo soggetto del dataset *matching pennies* (sub-05,
N=1) ha confermato la correttezza tecnica della pipeline ma non produce risultati con
significatività statistica. Le performance di classificazione osservate in questa fase sono
attese vicine al livello casuale e non devono essere interpretate come stima delle capacità
discriminative reali della pipeline.

L'uso del template anatomico fsaverage introduce un errore di localizzazione sorgente
stimato di 1–2 cm rispetto a una forward solution individuale, accettabile per l'analisi
di reti funzionali su larga scala ma potenzialmente rilevante per applicazioni che richiedono
precisione sub-centimetrica. Infine, la selezione del dataset scientifico finale — tra
i candidati ds005385 (Dortmund Vital, 608 soggetti, paradigma EC/EO) e LEMON (228 soggetti,
dati resting-state con MRI strutturale) — resta una decisione aperta che condizionerebbe
il disegno sperimentale dei prossimi studi.

## 3. Implicazioni e prospettive

La pipeline sviluppata offre un punto di partenza riproducibile per ricercatori che
intendono confrontare sistematicamente configurazioni di analisi EEG source-level. La
struttura modulare — ogni step è un modulo Python indipendente con API pubblica documentata,
type hints e test unitari — facilita l'estensione a nuovi atlanti, metriche o classificatori
senza richiedere modifiche ai moduli esistenti.

Le implicazioni principali riguardano la ricerca sulla connettività funzionale resting-state:
la standardizzazione del preprocessing (MNE-BIDS-Pipeline), del metodo di inversione
(dSPM, parametri espliciti e configurabili da CLI) e della validazione (GroupKFold, permutation
testing, FDR) permette confronti diretti tra studi condotti su dataset differenti,
contribuendo alla riproducibilità nella neuroimaging computazionale.
