---
type: manuscript
status: draft
section: discussion
project: Tesi_2.0
last_review: 2026-05-01
sprint: S-36
tags: [eeg, source-fc, ml]
version: v1
language: italiano
target_journal: Journal of Neural Engineering
word_count_target: 180-220
date: 2026-05-01
---
# Lavori Futuri

## 1. Estensione della pipeline

La pipeline nella sua forma attuale esclude esplicitamente il deep learning per rispettare
i vincoli di minimalità dello studio. Una direzione naturale di espansione prevede
l'integrazione di baseline EEGNet o ShallowConvNet come termine di confronto per le
architetture tradizionali di feature engineering. L'applicazione a segnali MEG source-level
è immediata senza modifiche architetturali, poiché MNE-Python e MNE-Connectivity supportano
entrambe le modalità. Un ulteriore sviluppo riguarda l'adattamento a scenari BCI real-time,
in cui la stima della connettività funzionale deve operare su finestre temporali brevi
con latenza compatibile con il controllo online.

## 2. Validazione cross-dataset

I risultati del benchmark su *matching pennies* (paradigma di intenzione motoria, task-based)
andranno integrati con esperimenti su dataset resting-state multi-soggetto. I candidati
principali sono ds005385 (Dortmund Vital, 608 soggetti EEG EC/EO) e LEMON (228 soggetti,
EEG resting-state con MRI strutturale disponibile). La disponibilità di MRI nel dataset LEMON permetterebbe di confrontare la forward solution
individuale con quella su template fsaverage, quantificando l'impatto dell'errore di
localizzazione sulle performance classificative.

## 3. Affinamenti metodologici

Sul piano della connettività funzionale, due direzioni meritano priorità: l'ortogonalizzazione
dei segnali source-level (Hipp et al., 2012) come alternativa alle metriche robuste al
volume conduction, e la correzione simmetrica del field spread (symmetric leakage
correction, Colclough et al., 2016) che rimuove in modo più sistematico le correlazioni
artificiali indotte dalla forward solution. Entrambe sono integrate in MNE-Python e compatibili con l'architettura dispatcher.
