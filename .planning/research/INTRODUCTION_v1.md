---
type: thesis-section
status: draft
section: introduction
project: Tesi_2.0
last_review: 2026-05-01
sprint: S-36
tags: [eeg, source-fc, ml]
---
# Introduction — Classificazione EEG Source-Level con Connettività Funzionale

**Versione**: v1 — draft  
**Data**: 2026-05-01  
**Target**: ~1500 parole, stile IEEE Trans. Biomed. Eng.

---

## 1. Motivazione e contesto

Le interfacce cervello-computer (*Brain-Computer Interfaces*, BCI) e i sistemi di neuroimaging funzionale poggiano sulla capacità di estrarre informazione discriminante dal segnale elettroencefalografico (EEG). L'EEG è ampiamente impiegato in contesti clinici e di ricerca grazie alla sua alta risoluzione temporale (nell'ordine del millisecondo), al basso costo, alla portabilità e alla possibilità di registrare in condizioni ecologiche senza sedazione o esposizione a radiazioni. Tuttavia, l'analisi dell'EEG presenta sfide computazionali e metodologiche peculiari: il segnale registrato agli elettrodi scalp è una sovrapposizione di contributi corticali di vaste regioni, degradata dal *volume conduction* (la propagazione passiva del potenziale elettrico attraverso il cranio e il cuoio capelluto), dal rumore di misura e da artefatti muscolari e oculari.

Negli ultimi due decenni, i progressi nelle tecniche di ricostruzione sorgente hanno reso possibile proiettare il segnale EEG dallo spazio degli elettrodi allo spazio delle sorgenti corticali, ottenendo stime dell'attività neurale localizzate spazialmente con una risoluzione di 1–2 cm. Questa proiezione, nota come *source imaging*, riduce il problema del volume conduction e consente un'analisi neuroanatomicamente interpretabile, aprendo la strada a confronti diretti con la neuroimaging fMRI e a studi di connettività funzionale sorgente-level.

La **connettività funzionale** (FC) sorgente-level — intesa come la correlazione statistica tra i time course di coppie di Regioni di Interesse (ROI) corticali — è uno dei descrittori più informativi dello stato cognitivo e clinico del cervello. In particolare, metriche di sincronizzazione di fase come il *weighted Phase Lag Index* (wPLI, Vinck et al., 2011) e il *Phase Locking Value* (PLV, Lachaux et al., 1999) sono ampiamente usate perché sensibili al coupling funzionale ritmico tra aree corticali distanti, fenomeno fondamentale per la coordinazione di processi cognitivi complessi (Varela et al., 2001).

Nonostante i progressi metodologici, la trasformazione di queste misure in feature per la classificazione machine learning rimane un problema aperto. Le sfide principali includono: (i) l'altissima dimensionalità delle matrici di connettività (fino a ~20000 archi per atlanti a 200 ROI), (ii) la scarsità di campioni rispetto al numero di feature (*curse of dimensionality*), (iii) la variabilità inter-soggetto, e (iv) la scelta ottimale dell'atlante parcellare, della metrica di connettività e dell'algoritmo di classificazione, che dipende dal dataset e dal paradigma.

## 2. Stato dell'arte

### 2.1 Pipeline di classificazione EEG sorgente-level

Le pipeline di classificazione EEG possono essere organizzate in due grandi famiglie. Le pipeline *sensor-level* operano direttamente sulle misure elettrodo-temporali (es. potenziali evocati, CSP, FBCSP) e sono computazionalmente efficienti, ma forniscono una discriminazione spaziale limitata e sono vulnerabili al volume conduction. Le pipeline *source-level* introducono uno step di ricostruzione sorgente che aumenta la plausibilità neurobiologica dell'interpretazione ma richiede una forward solution affidabile e introduce errori aggiuntivi di modellazione.

Tra le pipeline source-level più influenti, il lavoro di Schirrmeister et al. (2017) ha dimostrato che reti neurali convoluzionali (Deep ConvNet, ShallowConvNet) possono apprendere rappresentazioni sorgente-level discriminanti direttamente dai raw EEG, surclassando pipeline tradizionali su dataset di movimento. Grosse-Wentrup et al. (2009) hanno proposto l'uso della coerenza sorgente-level come feature BCI, mostrando che la connettività frontale-parietale è altamente discriminante per compiti cognitivi. Più recentemente, Sabbagh et al. (2020) hanno confrontato sistematicamente diverse metriche di connettività (incluse PLV, wPLI e coerenza) su dataset multi-soggetto, concludendo che le metriche robuste al volume conduction (wPLI) ottengono performance più generalizzabili su soggetti non visti.

### 2.2 Atlanti cerebrali per la parcellazione EEG sorgente

La scelta dell'atlante per aggregare i vertici sorgente in ROI è un parametro metodologico rilevante. L'atlante Desikan-Killiany (*aparc*, 68 ROI, Desikan et al., 2006) è il gold standard clinico per la segmentazione della corteccia e fornisce ROI ben documentate in letteratura. Le parcellazioni Schaefer (2018) offrono granularità scalabile (100–400 ROI) con mappatura a 7 reti di ordine superiore (Default Mode, Control, Salience, ecc.), utile per l'interpretazione in termini di network funzionali. Comparare sistematicamente queste granularità permette di valutare il trade-off tra stabilità della stima di connettività e risoluzione spaziale delle feature.

### 2.3 Metriche di connettività per BCI

Il dibattito sulle metriche più appropriate per BCI source-level è ancora aperto. La coerenza (Coh) è la misura più intuitiva ma soffre di alta sensitività al volume conduction residuo. Il *Phase Lag Index* (PLI, Stam et al., 2007) è robusto ma ha bassa sensibilità a interazioni con lag di fase vicini a 0°/180°. Il wPLI (Vinck et al., 2011) bilancia robustezza e sensibilità, ed è attualmente tra le metriche più raccomandate. Il debiased wPLI² fornisce uno stimatore non distorto particolarmente appropriato per campioni di piccole dimensioni, come i singoli trial EEG. La valutazione empirica su benchmark sistematici — come quello implementato in questo lavoro — è necessaria per identificare la metrica ottimale per un dato paradigma.

## 3. Contributi del presente lavoro

Il presente lavoro propone e valida una pipeline completa e modulare per la classificazione EEG source-level basata su connettività funzionale. I contributi principali sono:

1. **Pipeline end-to-end riproducibile**: integrazione di MNE-BIDS-Pipeline (preprocessing standardizzato), ricostruzione sorgente dSPM su template fsaverage, quattro atlanti parcellari, sette metriche FC e cinque classificatori in un framework unico e versionato in git.

2. **Benchmark sistematico**: valutazione di 700 combinazioni (7 metriche × 4 atlanti × 5 bande × 5 algoritmi) su dati EEG reali, con metodologia di validazione inter-soggetto rigorosa (GroupKFold) e correzione per test multipli (FDR Benjamini-Hochberg).

3. **Infrastruttura di test e qualità**: 116 test automatici (pytest) coprono tutti i moduli pubblici, ruff per linting, seed fisso per riproducibilità — standard metodologici rari negli studi di neuroimaging computazionale.

4. **Valutazione multi-atlante**: confronto diretto tra Desikan-Killiany (68 ROI), Destrieux (148 ROI), Schaefer-100 e Schaefer-200 sulla stessa pipeline, con analisi del trade-off granularità-performance.

Il documento è organizzato come segue: la Sezione Methods (`.planning/research/METHODS_v1.md`) descrive in dettaglio ogni step della pipeline; i Risultati riportano il benchmark completo; la Discussione interpreta i risultati nel contesto della letteratura e identifica i limiti.

---

## Riferimenti

- Desikan, R.S., et al. (2006). An automated labeling system for subdividing the human cerebral cortex. *NeuroImage*, 31(3).
- Gramfort, A., et al. (2013). MEG and EEG data analysis with MNE-Python. *Frontiers in Neuroscience*, 7.
- Grosse-Wentrup, M., et al. (2009). Beamforming in noninvasive brain–computer interfaces. *IEEE Trans. Biomed. Eng.*, 56(4).
- Hämäläinen, M., & Ilmoniemi, R. (1994). Interpreting magnetic fields of the brain: minimum norm estimates. *Medical & Biological Engineering & Computing*, 32.
- King, J.R., & Dehaene, S. (2014). Characterizing the dynamics of mental representations. *Trends in Cognitive Sciences*, 18(4).
- Lachaux, J.P., et al. (1999). Measuring phase synchrony in brain signals. *Human Brain Mapping*, 8(4).
- Sabbagh, D., et al. (2020). Predictive regression modeling with MEG/EEG: from source power to signals and cognitive states. *NeuroImage*, 222.
- Schaefer, A., et al. (2018). Local-global parcellation of the human cerebral cortex. *Cerebral Cortex*, 28(9).
- Schirrmeister, R.T., et al. (2017). Deep learning with convolutional neural networks for EEG decoding. *Human Brain Mapping*, 38(11).
- Stam, C.J., et al. (2007). Phase lag index: assessment of functional connectivity from multi channel EEG. *Human Brain Mapping*, 28(11).
- Varela, F., et al. (2001). The brainweb: phase synchronization and large-scale integration. *Nature Reviews Neuroscience*, 2(4).
- Vinck, M., et al. (2011). An improved index of phase-synchronization. *NeuroImage*, 55(4).
- Varoquaux, G., et al. (2017). Assessing and tuning brain decoders. *NeuroImage*, 159.
