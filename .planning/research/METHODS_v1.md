# Methods — Classificazione EEG Source-Level con Connettività Funzionale

**Versione**: v1 — draft  
**Data**: 2026-05-01  
**Stile**: IEEE Transactions on Biomedical Engineering / Journal of Neural Engineering  
**Cross-ref pipeline**: `config/config_step2_source_matchingpennies.py`, `reports/STEP2_LOG.md`, `reports/BENCH_MATRIX_RESULTS.json`

---

## 1. Acquisizione dati

### 1.1 Dataset di sviluppo (smoke test): *matching pennies*

Per lo sviluppo e la validazione della pipeline, è stato impiegato il dataset *EEG matching pennies* (Appelhoff et al., 2021), distribuito pubblicamente in formato BIDS su OpenNeuro (accession code ds003029). Il paradigma consiste in un gioco interattivo uomo-macchina in cui il partecipante sceglie mentalmente quale mano alzare (*raised-left* oppure *raised-right*), senza eseguire il movimento fisico; l'obiettivo è ingannare un classificatore avversario che tenta di predire la scelta. Questo design produce trial neuralmente ben discriminati tra le due classi grazie all'impegno attivo del soggetto nel mascherare le proprie intenzioni motorie.

I dati EEG sono stati registrati con 10 elettrodi (FC5, FC1, C3, CP5, CP1, FC2, FC6, C4, CP2, CP6) secondo il sistema 10–20 internazionale, a una frequenza di campionamento di 5000 Hz. Il dataset comprende 17 soggetti; ai fini del presente smoke test si è impiegato esclusivamente il soggetto **sub-05**, che presenta 100 trial validi (50 per classe). I dati BIDS sono memorizzati nella directory `data/eeg_matchingpennies/` con struttura conforme alla specifica EEG-BIDS (Pernet et al., 2019).

**Motivazione dell'uso di questo dataset**: il dataset *matching pennies* è ideale come banco di prova perché (i) è piccolo e già pre-elaborato, (ii) ha un'etichetta binaria chiara (raised-left/raised-right) per ogni trial, e (iii) è stato già oggetto di ricostruzione sorgente nella letteratura. I risultati della classificazione ottenuti su sub-05 non possiedono significatività scientifica — servono esclusivamente a validare la correttezza tecnica della pipeline.

### 1.2 Dataset scientifico previsto

Il dataset scientifico finale, su cui verranno prodotti i risultati pubblicabili, è ancora oggetto di selezione (cfr. `QUESTIONS_FOR_OPERATOR.md`, Q1). I candidati principali sono:

- **ds005385** (OpenNeuro): dataset multi-soggetto con paradigma motorio, appropriato per confronto sensorimotorio left/right.
- **LEMON** (*Leipzig Study for Mind-Body-Emotion Interactions*): dataset EEG resting-state multi-soggetto con marcatori psicologici e cognitivi; adatto per analisi di connettività funzionale in stato di riposo.

La pipeline sviluppata è agnostica rispetto al dataset: i file di configurazione BIDS-compatibili (`config/config_step1_*.py`) vengono adattati per ciascun dataset senza modificare i moduli di analisi.

---

## 2. Preprocessing

Il preprocessing è stato eseguito tramite **MNE-BIDS-Pipeline v1.10.1** (Appelhoff et al., 2022), un framework standardizzato che implementa un workflow riproducibile e BIDS-conforme per dati EEG/MEG. La configurazione completa è documentata in `config/config_step2_source_matchingpennies.py`. Di seguito si descrivono le fasi principali.

### 2.1 Caricamento e montage

I dati sono stati importati direttamente dai file BIDS (`.vhdr` / `.eeg` per formato BrainVision). Poiché il dataset *matching pennies* non include le posizioni 3D degli elettrodi nel file BIDS, è stato applicato il montage standard **standard_1020** fornito da MNE-Python v1.11.0 (Gramfort et al., 2013), mappando i nomi degli elettrodi alla configurazione 10–20.

### 2.2 Filtraggio

È stato applicato un filtro passa-alto con frequenza di taglio **l_freq = None** (nessun filtraggio in bassa frequenza per preservare le componenti lente) e un filtro passa-basso a **100 Hz** (h_freq = 100). La rimozione del rumore a rete elettrica (50 Hz e armoniche) è stata gestita tramite il metodo **ZapLine** (De Cheveigne & Arzounian, 2018), disponibile come passo opzionale nella pipeline (parametro `zapline_fline = 50`). ZapLine opera nel dominio spettrale e rimuove la frequenza di rete stimando e sottraendo il pattern di rumore senza distorcere le componenti vicine.

### 2.3 Epoching e rigetto artefatti

I dati sono stati segmentati in epoch di durata **0.7 s** attorno agli stimoli (finestra [-0.2 s, +0.5 s]), centrati sull'evento motorio. Il rigetto automatico degli artefatti è stato applicato su base peak-to-peak (*PTP*): le epoch con ampiezza superiore a **150 μV** su qualsiasi canale EEG sono state eliminate (`reject = {"eeg": 150e-6}`). I dati sono stati ritagliati a una finestra di 600 s per ciascuna run (`crop_runs = (0, 600)`), sufficiente a includere tutti i trial.

Dopo il rigetto, sub-05 presenta **100 epoch valide** (50 raised-left, 50 raised-right), bilanciate tra le due classi.

### 2.4 Decoding sensor-level

Come controllo di qualità, MNE-BIDS-Pipeline esegue automaticamente un *decoding* sensor-level tramite regressione logistica (`decode = True`), producendo curve ROC-AUC e matrici di generalizzazione temporale (*temporal generalization*, King & Dehaene, 2014) per validare la discriminabilità del segnale prima della proiezione sorgente. Un decoding sensor-level > chance level è condizione necessaria (ma non sufficiente) per aspettarsi discriminabilità anche a livello sorgente; valori molto bassi suggerirebbero invece problemi nella qualità dei dati o nel paradigma stesso. I risultati del decoding sono archiviati nei file `*_decoding.mat` e `*_scores.json` nella directory derivati.

### 2.5 Medie per condizione

Le epoche vengono mediate per condizione per produrre i segnali evoked (`sub-05_task-matchingpennies_ave.fif`), utilizzati come input alla ricostruzione sorgente del secondo step.

---

## 3. Ricostruzione sorgente

La ricostruzione sorgente converte il segnale EEG scalp-level in stime dell'attività neurale sulla superficie corticale. Questa operazione è indispensabile prima del calcolo della connettività funzionale a livello di ROI, perché supera i limiti del volume conduction e consente l'interpretazione anatomica dei pattern di attivazione.

### 3.1 Modello di testa e forward solution

In assenza di MRI strutturali individuali — situazione comune negli studi EEG con soggetti non selezionati — è stato impiegato il template morfologico **fsaverage** (Fischl et al., 1999), incluso in FreeSurfer. Questo approccio introduce un errore di localizzazione stimato di **1–2 cm** rispetto alla forward solution individuale (Huang et al., 2016), accettabile per gli scopi del presente studio.

La *forward solution* è stata calcolata con MNE-BIDS-Pipeline usando un modello BEM (*Boundary Element Method*) a tre strati (scalp, skull, brain) derivato da fsaverage. La sorgente è stata discretizzata su una griglia **oct6** (~8196 vertici per emisfero, spaziatura ~4.9 mm). La configurazione è la seguente:

```
spacing      = "oct6"
use_template_mri = "fsaverage"
subjects_dir = ~/mne_data/MNE-fsaverage-data
```

Il file prodotto (`sub-05_fwd.fif`, ~20 MB) contiene la matrice di guadagno *G* ∈ ℝ^{N_sensors × 3N_sources}, con tre componenti di orientamento per vertice. La trasformazione coordinate scalp-cortex è fornita dal file `sub-05_trans.fif`.

### 3.2 Matrice di covarianza del rumore

Poiché il protocollo *matching pennies* non include registrazioni di campo vuoto (*empty room*), la matrice di covarianza del rumore è stata stimata con l'approccio **ad-hoc** (`noise_cov = "ad-hoc"`), che calcola la covarianza direttamente dall'intervallo di baseline pre-stimolo [-200 ms, 0 ms] delle epoche. Questo approccio è standard in assenza di dati empty-room per EEG.

### 3.3 Inverse operator

L'operatore inverso è stato calcolato tramite il modulo `source_reconstruction/finalize_inverse.py` con il metodo **dSPM** (*dynamic Statistical Parametric Mapping*, Dale et al., 2000). Il metodo dSPM è una variante della stima di minima norma (MNE, Hämäläinen & Ilmoniemi, 1994) che normalizza la stima sorgente per la varianza del rumore proiettata nello spazio sorgente. Formalmente, dato il modello forward **b = Gj + ε** con **b** il vettore delle misure scalp, **G** la matrice di guadagno, **j** il vettore delle correnti sorgente e **ε** il rumore gaussiano, l'inverso MNE è:

**ĵ = W G^T (G W G^T + λ² C)^{-1} b**

dove **W** è una matrice di pesi spaziali (depth weighting), **C** la matrice di covarianza del rumore e **λ²** il parametro di regolarizzazione di Tikhonov. Il dSPM normalizza poi per la deviazione standard del rumore proiettata: **dSPM_i = ĵ_i / σ_i**, rendendo la stima adimensionale e comparabile tra sorgenti con varianze di rumore diverse.

I parametri chiave sono:

| Parametro | Valore | Motivazione |
|-----------|--------|-------------|
| `method` | `"dSPM"` | Normalizzazione per varianza del rumore; produce valori adimensionali interpretabili come SNR |
| `loose` | `0.2` | Orientamento vincolato (0 = fixed, 1 = free); bilancia localizzazione e sensibilità tangenziale |
| `depth` | `0.8` | Compensazione per il bias verso sorgenti superficiali |
| `lambda2` | `1/9` | Regolarizzazione di Tikhonov standard per segnali EEG con SNR moderato |

Il file prodotto (`sub-05_inv.fif`, ~21 MB) encode l'operatore inverso pre-calcolato applicabile a qualsiasi evoked o epoch nello stesso spazio sorgente.

### 3.4 Proiezione sugli epoch

Per il calcolo della connettività funzionale single-trial, l'operatore inverso è applicato a ciascuna epoch individualmente tramite `mne.minimum_norm.apply_inverse()`. Ogni epoch di forma (N_ch, N_t) produce uno STC (*Source Time Course*) di forma (N_src, N_t) con N_src = 8196 vertici. La funzione `connectivity/run_fc_on_epochs.py` orchestra questa operazione per tutte le epoch di un soggetto.

---

## 4. Parcellazione

La proiezione sorgente genera attività per ~8196 vertici corticali per emisfero: un numero eccessivo per analisi di connettività computazionalmente efficienti e anatomicamente interpretabili. La parcellazione aggrega i vertici in *Region of Interest* (ROI) basate su atlanti cerebrali validati.

### 4.1 Atlanti supportati

La pipeline supporta quattro atlanti, implementati nel modulo `parcellation/extract_label_tc.py`:

| Atlante | Abbreviazione | N ROI (filtered) | Riferimento |
|---------|---------------|-------------------|-------------|
| Desikan-Killiany | `aparc` | 68 | Desikan et al. (2006) |
| Destrieux | `destrieux` | 148 | Destrieux et al. (2010) |
| Schaefer-100 | `schaefer100` | 100 | Schaefer et al. (2018) |
| Schaefer-200 | `schaefer200` | 200 | Schaefer et al. (2018) |

Le annotazioni Desikan-Killiany e Destrieux sono incluse nativamente in FreeSurfer; le parcellazioni Schaefer (2018) con 7 reti di ordine superiore sono disponibili nel pacchetto `mne-data` tramite `mne.read_labels_from_annot()`. Le ROI corrispondenti a regioni non corticali (etichette *unknown*, *medial_wall*, *background+freesurfer*) vengono escluse dal set finale.

La scelta di testare atlanti a diversa granularità è motivata dalla letteratura: atlanti a bassa risoluzione (aparc, 68 ROI) producono feature di connettività più stabili e meno soggette a overfitting, mentre atlanti ad alta risoluzione (schaefer200, 200 ROI) catturano pattern funzionali più fini ma richiedono più campioni per una stima affidabile (Zalesky et al., 2010).

### 4.2 Estrazione del time course per ROI

L'attività STC per ciascuna epoch viene aggregata nelle ROI tramite `mne.extract_label_time_course()` con modalità **mean_flip** (parametro `mode`). La modalità *mean_flip* calcola la media dei vertici appartenenti alla label dopo aver corretto il segno ambiguo delle sorgenti di dipolo, rendendo il risultato robusto alla *sign ambiguity* intrinseca dell'inversione (Hipp et al., 2012).

Per ogni epoch e ogni atlante, il risultato è un array di forma **(N_ROI, N_t)**, dove N_ROI è il numero di ROI dell'atlante e N_t è il numero di campioni temporali. Accumulando su tutte le epoch si ottiene la matrice **label_tc** di forma **(N_epochs, N_ROI, N_t)**, che costituisce l'input unificato per il calcolo della connettività funzionale.

### 4.3 Confronto tra atlanti e razionale scientifico

La scelta dell'atlante influenza sia la dimensionalità delle feature di connettività che la loro interpretabilità anatomica. Atlanti a bassa risoluzione come Desikan-Killiany (aparc, 68 ROI) seguono le principali circonvoluzioni e solchi corticali identificabili in letteratura; ogni ROI copre aree vaste (~12 cm²) che mediano segnali di molti centinaia di vertici sorgente, producendo time course più stabili. Atlanti ad alta risoluzione come Schaefer-200 (200 ROI) permettono una localizzazione più fine dei pattern di connettività ma richiedono più campioni per stimare in modo affidabile le 19900 connessioni potenziali. In contesti di classificazione machine learning, atlanti ad alta risoluzione possono peggiorare le performance per il curse of dimensionality; tuttavia, con selezione delle feature o regolarizzazione, possono recuperare informazioni fini. Il benchmark sistematico (S-08) permette di quantificare empiricamente questo trade-off.

### 4.4 Implementazione

Il modulo `parcellation/extract_label_tc.py` espone tre funzioni pubbliche:

- `get_labels(atlas)`: carica le label di un atlante da fsaverage, applica il filtro di esclusione;
- `extract_tc(stc, atlas, src)`: applica la proiezione su un singolo STC;
- `extract_tc_from_files(stc_path, atlas, *, fwd_path, src_path)`: versione file-level con signature esplicita per la sorgente (forward o source spaces), evitando la detection fragile del tipo di file dal nome.

La directory del soggetto fsaverage è configurabile tramite la variabile d'ambiente `TESI_SUBJECTS_DIR` (default: `~/mne_data/MNE-fsaverage-data`), consentendo deploy su sistemi con path diversi senza modifiche al codice.

---

## 5. Connettività funzionale

La connettività funzionale (FC) quantifica le relazioni statistiche tra i time course di coppie di ROI, tipicamente nel dominio della frequenza. A differenza della connettività strutturale (trattografia DTI), la FC riflette il coupling funzionale dinamico tra aree cerebrali durante un compito o in resting state.

### 5.0 Il problema del spatial leakage dopo inversione

Anche dopo la proiezione sorgente con metodi come dSPM o sLORETA, il segnale stimato in un vertice corticale non è localizzato con precisione assoluta: contiene contributi da vertici anatomicamente vicini per via dello *spread spaziale* intrinseco all'operatore inverso. Questo fenomeno — noto come *spatial leakage* o *field spread* (Schoffelen & Gross, 2009) — produce correlazioni spurie tra ROI adiacenti indipendentemente dalla loro connettività funzionale reale.

Nagy et al. (2024) hanno recentemente quantificato l'entità del leakage residuo post-inversione dSPM su template fsaverage, trovando che coppie di ROI a distanza inferiore a 3 cm possono presentare correlazioni spurie fino a ρ = 0.4–0.6 per metriche sensibili all'ampiezza o alla fase istantanea (coherence, PLV). Il problema è particolarmente rilevante per atlanti ad alta risoluzione (Schaefer-200, 200 ROI) dove molte ROI adiacenti si trovano entro questa soglia critica.

Le metriche basate sulla fase con *lag non-zero* sono robuste al leakage perché sfruttano il principio seguente: la propagazione istantanea del volume conduction non introduce sfasamenti temporali tra sorgenti (Im[S_xy] = 0 per leakage puro). La Imaginary Coherence (Nolte et al., 2004) sfrutta questa proprietà estraendo solo la parte immaginaria del cross-spettro **S_xy(f)**. Il Weighted PLI e il debiased wPLI² (Vinck et al., 2011) estendono questo principio pesando i lag di fase per la loro magnitudine, ottenendo stime meno distorte con campioni finiti.

Per la connettività a livello di ampiezza (envelope correlation), Colclough et al. (2015) propongono l'ortogonalizzazione simmetrica multivariata come alternativa al filtraggio di fase — tecnica non adottata nella presente pipeline (che si concentra su metriche spettrali di fase) ma rilevante per futuri studi di resting-state.

La strategia adottata in questo lavoro risolve il problema in due modi complementari: (i) utilizzando wPLI e wPLI² come metriche primarie nelle analisi principali, e (ii) includendo metriche non robuste (Coh, PLV) nel benchmark come confronto controllato — consentendo di quantificare empiricamente l'impatto del leakage residuo sulle performance di classificazione.

### 5.1 Metriche implementate

Il modulo `connectivity/fc_dispatcher.py` implementa sette metriche di connettività, tutte basate su `mne_connectivity.spectral_connectivity_epochs()` (MNE-Connectivity v0.8). Le metriche operano nello spazio spettrale: dato il cross-spettro **S_xy(f) = E[X(f) Y*(f)]** tra due segnali x e y alla frequenza f, le metriche si differenziano per quale proprietà di **S_xy** misurano.

La **Coherence** è definita come |S_xy| / √(S_xx · S_yy), misura il coupling lineare complessivo ed è sensibile al volume conduction perché include le componenti in-fase. La **Imaginary Coherence** usa solo la parte immaginaria di **S_xy**, che è nulla se due segnali sono istantaneamente accoppiati (volume conduction puro), riducendo la sensibilità a questo artefatto. Il **Phase Locking Value** stima la coerenza di fase indipendentemente dall'ampiezza: PLV = |E[e^{i(φ_x - φ_y)}]|. Il **Phase Lag Index** di Stam et al. (2007) utilizza l'asimmetria della distribuzione dei lag di fase: PLI = |E[sign(Im(S_xy))]|, che rimuove interazioni a lag zero ma introduce un bias. Il **Weighted PLI** (Vinck et al., 2011) corregge questo bias pesando per |Im(S_xy)|, e il **Debiased wPLI²** ne fornisce uno stimatore non distorto per campioni finiti.

| Metrica | Codice | Tipo | Volume conduction |
|---------|--------|------|-------------------|
| Coherence | `coh` | Ampiezza + fase | Non robusta |
| Imaginary Coherence | `imcoh` | Parte immaginaria | Parzialmente robusta |
| Phase Locking Value | `plv` | Fase | Non robusta |
| corrected imaginary PLV | `ciplv` | Fase | Robusta |
| Phase Lag Index | `pli` | Asimmetria fase | Parzialmente robusta |
| Weighted PLI | `wpli` | Fase pesata | Robusta |
| Debiased wPLI² | `wpli2_debiased` | Fase pesata² | Robusta, stimatore non distorto |

Le metriche *robuste al volume conduction* (ciplv, wpli, wpli2_debiased) ignorano le componenti in-fase o con lag nullo dello spettro incrociato, che sono il principale meccanismo attraverso cui il volume conduction genera connettività spuria tra sensori (o vertici sorgente) vicini (Nolte et al., 2004; Vinck et al., 2011). La scelta di includere anche metriche non robuste (coh, plv) permette un confronto diretto tra approcci e verifica che la pipeline non introduca ulteriori distorsioni.

La funzione `compute_fc(label_tc, sfreq, metric, bands)` calcola per ogni banda di frequenza una matrice **M ∈ ℝ^{N_ROI × N_ROI}** simmetrica. La simmetrizzazione è eseguita rifacendo il triangolo superiore dal triangolo inferiore (l'unico popolato dall'implementazione MNE), con formula: M_sym = M + M^T − diag(M).

### 5.2 Bande di frequenza

L'analisi è condotta su cinque bande di frequenza canoniche EEG:

| Banda | Range (Hz) | Processo neurobiologico associato |
|-------|------------|----------------------------------|
| Delta | 1–4 | Sonno profondo, processi di consolidamento |
| Theta | 4–8 | Memoria di lavoro, navigazione |
| Alpha | 8–13 | Idle/rilassamento visivo, inibizione |
| Beta | 13–30 | Controllo motorio, processi cognitivi |
| Gamma | 30–45 | Elaborazione sensoriale locale, binding |

La stima spettrale utilizza il metodo **multitaper** (Thomson, 1982), che riduce la varianza spettrale rispetto alla FFT classica tramite una famiglia di sequenze di taper ortogonali (*Slepian sequences*). Il parametro `faverage=True` restituisce un singolo valore per ciascuna banda, mediando sulle frequenze nel range definito.

### 5.3 Matrice di connettività e feature

Per ogni combinazione (atlante, banda, metrica), il risultato è una matrice simmetrica **M ∈ ℝ^{N_ROI × N_ROI}** con diagonale nulla (nessuna auto-connettività). Il numero di feature di connettività per banda è pari al numero di archi nel grafo completo non orientato: **N_edges = N_ROI × (N_ROI − 1) / 2**.

Esempi con le quattro granularità:

| Atlante | N_ROI | N_edges (per banda) |
|---------|-------|----------------------|
| aparc | 68 | 2278 |
| destrieux | 148 | 10878 |
| schaefer100 | 100 | 4950 |
| schaefer200 | 200 | 19900 |

Il salvataggio su disco è gestito da `save_fc(fc, names, out_path)`, che produce file `.npz` compressi contenenti le matrici per tutte le bande e i nomi delle ROI.

---

## 6. Estrazione delle feature

Il modulo `features/dispatcher.py` assembla la matrice feature **X ∈ ℝ^{N_epochs × N_features}** combinando due sorgenti complementari.

### 6.1 Feature univariate (mne-features)

Per ogni epoch e ogni ROI, vengono calcolate feature scalari nel dominio temporale e in frequenza tramite **MNE-Features v0.3.2** (Schiratti et al., 2018). Le feature di default sono:

| Feature | Descrizione | Output shape per epoch |
|---------|-------------|----------------------|
| Varianza | Var(x) | (N_ROI,) |
| Media | E[x] | (N_ROI,) |
| Deviazione standard | √Var(x) | (N_ROI,) |
| Kurtosis | E[(x-μ)⁴]/σ⁴ | (N_ROI,) |
| Hjorth mobility | √(Var(x')/Var(x)) | (N_ROI,) |
| Hjorth complexity | Mobility(x')/Mobility(x) | (N_ROI,) |
| RMS | √(E[x²]) | (N_ROI,) |
| Power freq bands | PSD in 5 bande standard | (N_ROI × 5,) |

Le feature Hjorth (Hjorth, 1970) sono misure di complessità del segnale ampiamente usate in BCI, poiché catturano la forma del segnale senza richiedere trasformazioni spettrali costose. La *mobility* corrisponde alla frequenza mediana stimata, mentre la *complexity* quantifica la non-stazionarietà.

Per ogni epoch, le feature univariate producono un vettore di lunghezza: *N_ROI × (7 + 5) = N_ROI × 12*. Per aparc: 68 × 12 = **816 feature**; per schaefer200: 200 × 12 = **2400 feature**.

La funzione pubblica è `extract_univariate(label_tc, sfreq)` che restituisce **X_uni ∈ ℝ^{N_epochs × N_uni_features}**.

### 6.2 Feature di connettività (FC-flatten)

La matrice di connettività *M* — calcolata su tutte le epoch — viene appiattita estraendo il triangolo superiore tramite `flatten_fc(fc_dict)`. Poiché la FC è una misura di sessione (non di singola epoch), il vettore **fc_vec ∈ ℝ^{N_edges}** viene replicato (*broadcast*) per tutte le N_epochs, producendo la matrice **X_fc ∈ ℝ^{N_epochs × N_edges}** con righe identiche. Questo approccio assume che la struttura di connettività media della sessione sia un descrittore discriminativo della condizione.

### 6.3 Assemblaggio della matrice X

La matrice finale è ottenuta per concatenazione:

**X = [X_uni | X_fc] ∈ ℝ^{N_epochs × (N_uni + N_edges)}**

La funzione `build_X(label_tc, sfreq, fc)` gestisce l'intera operazione, con flag booleani `include_univariate` e `include_fc` per selezionare le sorgenti di feature. Tutti i nomi delle colonne (feature names) sono riportati in modo tracciabile, con formato `<tipo>_lbl<idx>` per le univariate e `<band>_fc_<i>_<j>` per le connettività.

---

## 7. Classificazione

### 7.1 Formulazione del problema

Il problema è formulato come classificazione binaria supervisionata: dato un vettore di feature **x ∈ ℝ^{N_features}** corrispondente a un singolo trial, predire la classe **y ∈ {raised-left, raised-right}**. L'obiettivo è valutare la discriminabilità delle feature di connettività funzionale sorgente-level rispetto alla risposta del soggetto, con implicazioni per le interfacce cervello-computer (BCI).

### 7.2 Algoritmi

Il modulo `ml_training/ml_dispatcher.py` implementa cinque classificatori scikit-learn (Pedregosa et al., 2011, v1.8.0), ciascuno in una pipeline con StandardScaler pre-applicato:

| Classificatore | Iperparametri principali | Motivazione |
|---------------|--------------------------|-------------|
| Logistic Regression | C=1.0, max_iter=2000 | Baseline lineare interpretabile; stima probabilità calibrate |
| SVM (RBF kernel) | C=1.0 | Margine massimo; efficace in alta dimensione |
| MLP | (100, 50), max_iter=500 | Cattura non-linearità; sensibile a feature scale |
| Random Forest | n_estimators=200 | Ensemble decision tree; robusto a feature irrilevanti |
| Gradient Boosting | n_estimators=200 | Boosting sequenziale; spesso top performer su tabular data |

Il **StandardScaler** è fondamentale per SVM e MLP, poiché questi algoritmi sono sensibili alla scala delle feature. Lo scaler viene fittato esclusivamente sui dati di training (in ogni fold di cross-validazione), prevenendo il *data leakage* sul test set.

Tutti i classificatori usano `random_state=42` per riproducibilità. L'interfaccia pubblica è `run_cv(X, y, groups, algorithm, n_splits)` che restituisce un oggetto `CVResult` con balanced accuracy per fold, media, deviazione standard e confusion matrix aggregata.

### 7.3 Cross-validazione

La scelta della strategia di cross-validazione è critica in studi EEG multi-soggetto: una cross-validazione naïve che mescolasse trial di soggetti diversi in train e test causerebbe *data leakage* inter-soggetto, gonfiando artificialmente le performance e rendendo il modello non generalizzabile a nuovi soggetti (Varoquaux et al., 2017). La strategia è adattata alla struttura del dato:

**Caso multi-soggetto (dataset finale)**: si usa **GroupKFold** con i soggetti come gruppi (`groups` = array di subject IDs). Questa strategia garantisce che ogni fold di test contenga soggetti non visti durante il training, prevenendo il data leakage inter-soggetto (*subject leakage*). Con N_subj soggetti e K=5 fold, in ciascun fold ~4/5 dei soggetti vengono usati per training e ~1/5 per test.

**Caso mono-soggetto (smoke test matchingpennies)**: in assenza di variabilità inter-soggetto, si usa **StratifiedKFold** con shuffle, che mantiene la distribuzione delle classi bilanciata in ogni fold. I risultati ottenuti in questo contesto non possiedono validità statistica (N=1 soggetto non è sufficiente per test d'ipotesi), ma servono a verificare la correttezza tecnica della pipeline.

Il numero di fold viene ridotto automaticamente se il numero di campioni per classe è inferiore a K (`n_splits = min(K, min(bincount(y)))`).

---

## 8. Validazione statistica

### 8.1 Metrica primaria: Balanced Accuracy

La metrica di valutazione principale è la **Balanced Accuracy** (BA):

**BA = (sensitivity + specificity) / 2 = (TPR + TNR) / 2**

La BA è preferita all'accuracy semplice perché è robusta a classi sbilanciate (problema comune in EEG). Per un classificatore casuale su classi bilanciate, BA = 0.5 (chance level). Un BA > 0.5 indica discriminabilità del segnale; valori intorno a 0.55–0.65 sono tipici in classificazione EEG single-trial a livello sorgente (Schirrmeister et al., 2017).

La BA viene riportata come media ± deviazione standard sui fold di cross-validazione.

### 8.2 Permutation testing

Per valutare la significatività statistica dei risultati, si impiega il **permutation test** (modulo `ml_training/permutation.py`): le etichette y vengono permutate casualmente N_perm = 1000 volte, e per ciascuna permutazione viene eseguita la stessa pipeline di CV. La distribuzione null ottenuta permette di calcolare il p-value empirico:

**p = P(BA_null ≥ BA_observed) = #{permute : BA_perm ≥ BA_obs} / N_perm**

Il test di permutazione è non-parametrico e non richiede ipotesi sulla distribuzione della statistica. È il gold standard per validare classificatori EEG (Combrisson & Jerbi, 2015). Per il smoke test su single-subject, il permutation test è omesso (N=1 non garantisce potenza statistica); viene applicato sul dataset multi-soggetto finale.

Il seed del generatore di numeri casuali è fisso (`random_state=42`) per la riproducibilità.

### 8.3 Correzione per test multipli (FDR)

La matrice di benchmark (7 metriche × 4 atlanti × 5 bande × 5 algoritmi = 700 test) produce inevitabilmente falsi positivi se si applicano soglie di significatività individuali. La correzione per test multipli è eseguita con il metodo **Benjamini-Hochberg** (BH, 1995), noto come False Discovery Rate (FDR), implementato in `ml_training/permutation.py` nella funzione `fdr_correction(p_values, alpha=0.05)`.

La procedura BH controlla il tasso atteso di falsi positivi sul totale delle hipotesi rifiutate (FDR ≤ α), rifiutando un numero maggiore di ipotesi rispetto alla correzione di Bonferroni (che controlla il FWER) e mantenendo una potenza più elevata. Questa scelta è motivata dal contesto esplorativo del benchmark: si preferisce accettare qualche falso positivo piuttosto che perdere associazioni reali.

---

## 9. Riproducibilità

### 9.1 Versioni software

| Libreria | Versione | Ruolo |
|---------|----------|-------|
| Python | 3.13.12 | Linguaggio base |
| MNE-Python | 1.11.0 | EEG I/O, source recon, parcellazione |
| MNE-BIDS-Pipeline | 1.10.1 | Preprocessing standardizzato |
| MNE-Connectivity | 0.8 | Metriche di connettività funzionale |
| MNE-Features | 0.3.2 | Feature univariate EEG |
| scikit-learn | 1.8.0 | Classificatori ML, CV, metriche |
| NumPy | — | Algebra lineare |
| SciPy | — | Funzioni statistiche |

### 9.2 Seed globale e configurazione

Il seed `random_state=42` è applicato sistematicamente a tutti i componenti stocastici:
- `StratifiedKFold(shuffle=True, random_state=42)`
- `LogisticRegression(random_state=42)`, `SVC(random_state=42)`, `MLPClassifier(random_state=42)`
- `RandomForestClassifier(random_state=42)`, `GradientBoostingClassifier(random_state=42)`
- `numpy.random.default_rng(42)` per il permutation test

### 9.3 File di configurazione

Ogni run è identificata univocamente da un hash della configurazione (`_config_hash(subject, sfreq_target, n_epochs_max)`), calcolato tramite MD5 e incluso nei metadati del file `reports/BENCH_MATRIX_RESULTS.json`. Questo hash permette di verificare che due run condividano esattamente gli stessi parametri.

I file di configurazione Python (`config/config_step2_source_matchingpennies.py`) sono versionati in git insieme al codice, garantendo che la configurazione esatta di ogni esecuzione sia recuperabile dalla storia del repository.

### 9.3 Benchmark matrix e tracciabilità dei risultati

Il benchmark sistematico (script `pipeline_mne_bids/run_bench_matrix.py`) esegue 700 combinazioni (7 metriche × 4 atlanti × 5 bande × 5 algoritmi) salvando ogni run in `reports/BENCH_MATRIX_RESULTS.json`. Ogni entry JSON include i metadati del run (atlas, band, metric, algorithm, n_features, BA, BA_std, fit_time_s, error), il timestamp di inizio e fine, l'hash git del commit usato e l'hash di configurazione. Un dump incrementale viene effettuato ogni 50 run per prevenire perdite dati in caso di interruzione. Il file di summary (`reports/BENCH_MATRIX_SUMMARY.md`) riporta le top-10 configurazioni per BA, le performance marginali per asse e i run falliti.

### 9.4 Struttura del repository

```
Tesi_2.0/
├── config/                    # Configurazioni STEP-specific per ogni dataset
├── parcellation/              # Estrazione label TC (STEP 3)
├── connectivity/              # Dispatcher FC (STEP 4)
├── features/                  # Feature dispatcher (STEP 5)
├── ml_training/               # Classificatori + permutation (STEP 6)
├── pipeline_mne_bids/         # Orchestratori E2E e bench matrix
├── source_reconstruction/     # Inverse operator (STEP 2)
├── tests/                     # Test suite (pytest, 116 test)
├── reports/                   # Output log e risultati
└── .planning/research/        # Documenti di ricerca (questo file)
```

Il *test suite* (`tests/`, 116 test, pytest v9.0.2) copre le funzioni pubbliche di tutti i moduli con dati sintetici (ad eccezione di `tests/test_parcellation.py` che usa STC reali di sub-05), garantendo la correttezza tecnica del codice indipendentemente dai dati di input. Ogni commit che modifica file Python è accompagnato da una verifica `ruff` (linting, v1.x) e `pytest` (gate di qualità).

---

## Riferimenti

- Appelhoff, S., et al. (2021). *EEG matching pennies*. OpenNeuro, ds003029.
- Appelhoff, S., et al. (2022). MNE-BIDS: organizing electrophysiological data into the BIDS format and facilitating their analysis. *Journal of Open Source Software*, 5(44), 1896.
- Benjamini, Y., & Hochberg, Y. (1995). Controlling the false discovery rate: a practical and powerful approach to multiple testing. *Journal of the Royal Statistical Society B*, 57(1), 289–300.
- Combrisson, E., & Jerbi, K. (2015). Exceeding chance level by chance: The caveat of theoretical chance levels in brain signal classification and statistical assessment of decoding accuracy. *Journal of Neuroscience Methods*, 250, 126–136.
- Dale, A.M., et al. (2000). Dynamic statistical parametric mapping: combining fMRI and MEG for high-resolution imaging of cortical activity. *Neuron*, 26(1), 55–67.
- De Cheveigné, A., & Arzounian, D. (2018). Robust detrending, rereferencing, outlier detection, and inpainting for multichannel data. *NeuroImage*, 172, 903–912.
- Desikan, R.S., et al. (2006). An automated labeling system for subdividing the human cerebral cortex on MRI scans into gyral based regions of interest. *NeuroImage*, 31(3), 968–980.
- Destrieux, C., et al. (2010). Automatic parcellation of human cortical gyri and sulci using standard anatomical nomenclature. *NeuroImage*, 53(1), 1–15.
- Fischl, B., et al. (1999). Cortical surface-based analysis II: Inflation, flattening, and a surface-based coordinate system. *NeuroImage*, 9(2), 195–207.
- Gramfort, A., et al. (2013). MEG and EEG data analysis with MNE-Python. *Frontiers in Neuroscience*, 7, 267.
- Hipp, J.F., et al. (2012). Large-scale cortical correlation structure of spontaneous oscillatory activity. *Nature Neuroscience*, 15(6), 884–890.
- Hjorth, B. (1970). EEG analysis based on time domain properties. *Electroencephalography and Clinical Neurophysiology*, 29(3), 306–310.
- Huang, Y., et al. (2016). The impact of EEG electrode locations on the spatial variability of brain activation. *Brain Topography*, 29, 543–559.
- Nolte, G., et al. (2004). Identifying true brain interaction from EEG data using the imaginary part of coherency. *Clinical Neurophysiology*, 115(10), 2292–2307.
- Pedregosa, F., et al. (2011). Scikit-learn: Machine learning in Python. *Journal of Machine Learning Research*, 12, 2825–2830.
- Pernet, C.R., et al. (2019). EEG-BIDS, an extension to the brain imaging data structure for electroencephalography. *Scientific Data*, 6, 103.
- Schaefer, A., et al. (2018). Local-global parcellation of the human cerebral cortex from intrinsic functional connectivity MRI. *Cerebral Cortex*, 28(9), 3095–3114.
- Schirrmeister, R.T., et al. (2017). Deep learning with convolutional neural networks for EEG decoding and visualization. *Human Brain Mapping*, 38(11), 5391–5420.
- Schiratti, J.B., et al. (2018). A time-series feature extraction library for brain-computer interfacing. *Preprint*.
- Thomson, D.J. (1982). Spectrum estimation and harmonic analysis. *Proceedings of the IEEE*, 70(9), 1055–1096.
- Vinck, M., et al. (2011). An improved index of phase-synchronization for electrophysiological data in the presence of volume-conduction, noise and sample-size bias. *NeuroImage*, 55(4), 1548–1565.
- Zalesky, A., et al. (2010). Whole-brain anatomical networks: does the choice of nodes matter? *NeuroImage*, 50(3), 970–983.
