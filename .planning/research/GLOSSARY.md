---
type: manuscript
status: draft
section: appendix
project: Tesi_2.0
last_review: 2026-05-01
sprint: S-35
tags: [eeg, source-fc, ml]
version: v1
language: italiano + inglese (termini canonici)
date: 2026-05-01
entries_count: 72
---
# Glossario

Termini tecnici utilizzati nel presente lavoro, ordinati alfabeticamente.
Definizioni in italiano; acronimi e nomi propri nella forma canonica inglese.

---

**aparc** — Atlante corticale Desikan-Killiany di FreeSurfer (~68 ROI). Mappa le
principali aree corticali del lobo frontale, parietale, temporale e occipitale.
Parametro: `atlas="aparc"` in `extract_label_tc.py`.

**apply_inverse** — Funzione MNE-Python (`mne.minimum_norm.apply_inverse`) che
applica l'operatore inverso a un segnale evocato producendo un SourceEstimate (STC).

**atlas** — Mappa di parcellazione del cervello che suddivide la corteccia in regioni
di interesse (ROI) con confini anatomo-funzionali definiti. In questo lavoro si usano
atlanti FreeSurfer (aparc, destrieux) e atlanti funzionali (Schaefer-100/200).

**BA** — Balanced Accuracy: (sensitivita' + specificita') / 2. Metrica robusta a classi
sbilanciate, usata come metrica primaria nel benchmark.

**band** — Banda di frequenza EEG: delta (1-4 Hz), theta (4-8), alpha (8-13),
beta (13-30), gamma (30-45 Hz). La connettivita' funzionale e' calcolata separatamente
per ogni banda.

**BEM** — Boundary Element Method. Metodo numerico per la soluzione del problema
forward EEG: calcola come le sorgenti corticali si propagano attraverso i tessuti
(corteccia, liquor, cranio, scalp) fino agli elettrodi.

**BIDS** — Brain Imaging Data Structure. Standard per l'organizzazione e la descrizione
di dati di neuroimaging e neurofisiologia, che garantisce interoperabilita' tra
pipeline di analisi. Specifica: https://bids.neuroimaging.io/

**BrainVision** — Formato file proprietario (.vhdr/.eeg/.vmrk) usato dal dataset
*matching pennies* e supportato nativamente da MNE-BIDS.

**CI** — Continuous Integration. Pratica di automazione del testing (pytest) e linting
(ruff) a ogni commit. Implementata in `.github/workflows/{lint,test,eeg-smoke}.yml`.

**ciPLV** — Corrected Imaginary Phase Locking Value. Variante del PLV robusta al volume
conduction, ottenuta trattenendo solo la parte immaginaria della Cross-Spectral Density.

**COH** — Coherence (Coerenza). Misura di FC spettrale che quantifica la correlazione
lineare tra due segnali nel dominio della frequenza. Sensibile al volume conduction.

**conftest.py** — File di configurazione pytest con fixture condivise. In questo progetto
punta ai dati reali di sub-05 per i test di integrazione.

**cross-validation** — Procedura di validazione che suddivide il dataset in piu' fold
per ottenere stime di generalizzazione meno influenzate dalla partizione train/test.
Vedi anche: GroupKFold, LOSO, StratifiedKFold.

**CSP** — Common Spatial Pattern. Metodo di filtro spaziale per BCI basato sulla
massimizzazione della varianza tra classi. Non usato in questo lavoro (si opera
a livello source-level).

**data leakage** — Contaminazione dei dati di test con informazioni del training set,
che produce stime di accuracy artificialmente gonfiate. Principali fonti: subject leakage,
temporal leakage, normalizzazione globale pre-split.

**decim** — Decimazione: riduzione della frequenza di campionamento dividendo per un
fattore intero. Usata per portare gli epoch a `sfreq_target = 500 Hz` prima della
stima FC.

**destrieux** — Atlante corticale Destrieux a2009s (~148 ROI), parcellazione anatomica
piu' fine di aparc. Parametro: `atlas="destrieux"`.

**dSPM** — Dynamic Statistical Parametric Mapping. Metodo di ricostruzione sorgente
derivato da MNE: normalizza la stima di minima norma per la covarianza del rumore,
producendo mappe in unita' di z-score che correggono il bias verso sorgenti superficiali.

**EC/EO** — Eyes-Closed / Eyes-Open. Paradigma resting-state in cui il soggetto
mantiene gli occhi chiusi (EC) o aperti (EO) per periodi di 1-2 minuti. Usato in
dataset come LEMON e ds005385 per studiare la connettivita' funzionale a riposo.

**EEG** — Electroencephalography. Tecnica di registrazione dell'attivita' elettrica
cerebrale tramite elettrodi posti sul cuoio capelluto. Risoluzione temporale nell'ordine
del millisecondo; risoluzione spaziale limitata dal volume conduction.

**epoch** — Segmento di segnale EEG estratto attorno a un evento (stimolo o risposta).
In questo lavoro: finestra [-0.2, +0.5] s attorno all'evento motorio.

**evoked** — Media degli epoch allineati allo stesso evento: riduce il rumore casuale
per cancellazione. Input di `apply_inverse` per la stima source-level dell'ERP.

**FC** — Functional Connectivity (Connettivita' Funzionale). Correlazione statistica
tra i time course di coppie di regioni cerebrali, usata come misura indiretta del
coupling funzionale.

**FDR** — False Discovery Rate. Tasso atteso di falsi positivi tra i test rifiutati.
La correzione Benjamini-Hochberg (1995) controlla FDR a livello alpha=0.05 per i
700 test del benchmark.

**features** — Vettore di variabili estratte dal segnale per alimentare il classificatore.
In questo lavoro: feature univariate per ROI (mne-features) + upper triangle FC per banda.

**field spread** — Propagazione del campo elettrico di una sorgente corticale verso
elettrodi e sorgenti adiacenti, producendo correlazioni artificiali (volume conduction).

**forward solution** — Soluzione del problema forward EEG: dato il modello geometrico
del tessuto cerebrale (BEM) e lo spazio sorgente, calcola come ogni sorgente influenza
i sensori. File: `*-fwd.fif`.

**fsaverage** — Anatomia template di FreeSurfer mediata su decine di soggetti sani.
Usata come spazio sorgente condiviso quando non e' disponibile la MRI individuale.
Introdotta da MNE: `mne.datasets.fetch_fsaverage()`.

**GroupKFold** — Strategia di cross-validation sklearn in cui i fold sono assegnati
per group (subject ID). Garantisce l'assenza di subject leakage: nessun trial di un
soggetto del test set e' visibile durante il training. Vedi: LOSO.

**ICA** — Independent Component Analysis. Tecnica di decomposizione cieca del segnale
EEG in componenti statisticamente indipendenti, usata per rimuovere artefatti oculari
e muscolari.

**imcoh** — Imaginary Coherence. Parte immaginaria della coerenza complessa; robusta
al volume conduction perche' gli artefatti di campo condiviso sono in fase (parte reale).

**inverse operator** — Operatore che mappa i segnali dei sensori EEG allo spazio
sorgente, risolvendo il problema inverso mal posto. Calcolato da `make_inverse_operator`
e salvato come `*-inv.fif`.

**JSONL** — JSON Lines. Formato file in cui ogni riga e' un oggetto JSON valido.
Usato per `DISPATCH_QUEUE_tesi.jsonl` e `broadcast_log.jsonl`.

**label_tc** — Label time courses: array `(n_epochs, n_labels, n_times)` ottenuto
applicando `extract_label_time_course` al STC su un atlante. Input di `compute_fc`.

**lambda2** — Parametro di regolarizzazione dell'operatore inverso: `lambda2 = 1/SNR^2`.
Valore tipico per dSPM: 1/9 ≈ 0.111 (SNR = 3).

**LEMON** — Leipzig Study for Mind-Body-Emotion Interactions. Dataset resting-state
EEG multi-soggetto (228 sub, 62 canali + MRI strutturale). Candidato dataset scientifico.

**loose** — Parametro dell'operatore inverso che controlla l'orientamento dei dipoli:
0 = orientamento fisso normale alla superficie; 1 = orientamento completamente libero.
Valore adottato: 0.2 (semi-libero).

**LOSO** — Leave-One-Subject-Out. Schema di cross-validation in cui ogni soggetto
costituisce un fold di test indipendente. Equivalente a GroupKFold con k = N_soggetti.

**matching pennies** — Dataset EEG (`ds003029`, OpenNeuro) con paradigma di intenzione
motoria: il soggetto sceglie quale mano alzare senza eseguire il movimento fisico.
Usato come smoke test di sviluppo in questo lavoro.

**mean_flip** — Mode di aggregazione di `extract_label_time_course` che allinea il
segno dei dipoli prima di mediare, prevenendo la cancellazione di segnale per anti-fase.
Raccomandato per FC source-level.

**MEG** — Magnetoencephalography. Tecnica di registrazione dei campi magnetici prodotti
dall'attivita' neurale. Maggiore risoluzione spaziale rispetto a EEG; sensori superconduttori
(SQUID) richiedono camera schermata.

**MNE** — Minimum Norm Estimate. Soluzione del problema inverso EEG che minimizza
la norma L2 delle sorgenti, biased verso sorgenti superficiali. Anche: nome della
libreria Python MNE-Python (mne 1.11.0).

**mne-bids-pipeline** — Framework Python per il preprocessing standardizzato di dati
EEG/MEG in formato BIDS. Versione 1.10.1 usata in questo lavoro.

**mne-connectivity** — Libreria Python per il calcolo della connettivita' funzionale
su dati EEG/MEG. Funzione principale: `spectral_connectivity_epochs`. Versione 0.8.

**mne-features** — Libreria Python per l'estrazione di feature da segnali neurofisiologici.
Usata per feature univariate (varianza, kurtosi, Hjorth, potenza per banda).

**montage** — Configurazione degli elettrodi EEG nello spazio 3D. In questo lavoro
si usa il montage template `standard_1020` perche' il dataset non include posizioni
3D degli elettrodi.

**neuromaps** — Libreria Python per il fetch e la parcellazione di mappe neuroscientifiche
pre-calcolate (gradienti funzionali, mielinizzazione T1w/T2w, espansione evolutiva).
Versione 0.0.5. Usata in sprint S-10.

**noise_cov** — Covarianza del rumore, necessaria per il calcolo dell'operatore inverso.
In questo lavoro: `ad-hoc` (stima analitica da MNE, basata sul montaggio EEG) perche'
il dataset non ha baseline pre-stimolo pulito.

**oct6** — Sottocampionamento della superficie corticale: 6 suddivisioni ottaedriche,
produce ~4098 sorgenti per emisfero. Parametro `spacing="oct6"` in mne-bids-pipeline.

**p-value** — Probabilita' di osservare un effetto almeno altrettanto estremo sotto
l'ipotesi nulla. In questo lavoro: stimato empiricamente con permutation testing
(1000 permutazioni, risoluzione 0.001).

**parcellation** — Suddivisione della corteccia cerebrale in regioni discrete secondo
un atlante. In EEG source-level FC: permette di ridurre la dimensionalita' dallo
spazio vertici (~8000) a un numero gestibile di ROI (68-200).

**permutation testing** — Test di significativita' non parametrico: permuta le
etichette `y` 1000 volte mantenendo invariata la struttura dei dati, genera la
distribuzione null della metrica di classificazione, calcola p-value empirico.

**PLI** — Phase Lag Index. Misura di FC basata sulla distribuzione delle differenze
di fase istantanee tra due segnali: robusto al volume conduction perche' considera
solo la parte non-zero del lag di fase.

**PLV** — Phase Locking Value. Misura di sincronia di fase tra due segnali: modulo
della media del vettore di fase relativo. Non robusta al volume conduction.

**pyproject.toml** — File di configurazione del progetto Python. In questo repo:
configura `[tool.ruff]` (linting), `[tool.pytest.ini_options]` (test discovery),
`[build-system]` (setuptools).

**random_state** — Seed del generatore di numeri pseudocasuali. Fissato a 42 in tutti
i componenti stocastici della pipeline (classificatori sklearn, permutation test, bench).

**reject** — Soglia di rigetto delle epoch per ampiezza: `{"eeg": 150e-6}` (150 uV
peak-to-peak). Epoch che superano la soglia su almeno un canale vengono scartate.

**ROI** — Region of Interest. Nel contesto source-level: regione corticale definita
dall'atlante, i cui vertici vengono aggregati tramite `mean_flip` per produrre
un unico time course.

**ruff** — Linter e formatter Python ultraveloce (Rust). Usato in questo progetto
al posto di flake8+black. Configurato in `pyproject.toml [tool.ruff]`.

**SBOM** — Software Bill of Materials. Inventario formale delle dipendenze software
con versioni, licenze e metadati di provenienza.

**schaefer100 / schaefer200** — Atlanti corticali funzionali Schaefer 2018 a 100 o 200
parcelle, organizzate in 7 reti di ordine superiore (Default Mode, Control, Salience,
Dorsal Attention, Ventral Attention, Limbic, Somatomotor). Parametri: `atlas="schaefer100"`
o `atlas="schaefer200"`.

**seed** — Valore iniziale del generatore di numeri pseudocasuali. Un seed fisso
garantisce la riproducibilita' bit-for-bit. Valore adottato: 42.

**sfreq** — Frequenza di campionamento in Hz. Il dataset *matching pennies* ha
sfreq = 1000 Hz, decimato a 500 Hz prima della stima FC.

**SNR** — Signal-to-Noise Ratio. Rapporto segnale/rumore; determina il parametro di
regolarizzazione `lambda2 = 1/SNR^2`. Valore tipico EEG: SNR = 3, lambda2 = 1/9.

**source space** — Griglia di punti dipolo che modella le sorgenti corticali. In MNE:
definita da `mne.setup_source_space` sulla superficie FreeSurfer. Con spacing oct6:
~4098 sorgenti per emisfero.

**spectral_connectivity_epochs** — Funzione di `mne-connectivity` che calcola le
matrici di connettivita' funzionale spettrale (COH, PLV, wPLI, ecc.) su un array
di epoch. Input: `(n_epochs, n_channels, n_times)`.

**SSP** — Signal Space Projection. Metodo alternativo a ICA per la rimozione di
artefatti EEG, basato su proiezioni ortogonali nei dati. Non usato in questo lavoro.

**StandardScaler** — Trasformazione sklearn che normalizza le feature a media 0 e
varianza unitaria. Fittato solo sul training fold (per prevenire data leakage).

**STC** — SourceEstimate (Source Time Courses). Oggetto MNE che rappresenta l'attivita'
sorgente stimata: array `(n_sources, n_times)` con vertici per emisfero. File: `*-lh.stc`,
`*-rh.stc`.

**StratifiedKFold** — Strategia di cross-validation sklearn che mantiene la proporzione
delle classi bilanciata in ogni fold. Usata in modalita' mono-soggetto (smoke test)
dove GroupKFold non e' applicabile.

**subject leakage** — Forma di data leakage in cui trial dello stesso soggetto
appaiono sia nel training che nel test set, permettendo al modello di apprendere
pattern idiosincratici dell'individuo.

**SUBJECTS_DIR** — Directory radice di FreeSurfer che contiene le anatomie individuali
e il template fsaverage. Configurabile via env var `TESI_SUBJECTS_DIR`.

**temporal leakage** — Forma di data leakage in cui trial temporalmente adiacenti
(con correlazione residua dovuta al filtro o alle fluttuazioni lente) appaiono
in fold opposti della cross-validation.

**volume conduction** — Propagazione passiva del campo elettrico di una sorgente
attraverso i tessuti (cranio, scalp) fino agli elettrodi lontani dalla sorgente.
Principale artefatto nelle misure di FC sensor-level.

**wPLI** — weighted Phase Lag Index (Vinck et al. 2011). Metrica di FC che pesa
ogni campione per il modulo della parte immaginaria della Cross-Spectral Density,
riducendo l'influenza del volume conduction residuo.

**wpli2_debiased** — Debiased squared wPLI. Stimatore non distorto di wPLI^2,
appropriato per campioni di piccole dimensioni (singoli trial EEG). Implementato
in mne-connectivity come `method="wpli2_debiased"`.

**ZapLine** — Metodo di filtraggio per la rimozione del rumore di rete elettrica
(50/60 Hz e armoniche), sviluppato da de Cheveigne' & Arzounian (2018). Opera nel
dominio spettrale; meno distorsivo rispetto al notch filter tradizionale.
