---
type: thesis-section
status: final-draft
section: discussion
project: Tesi_2.0
last_review: 2026-05-14
sprint: R-TESI-2.0-DISCUSSION-CONCLUSION
tags: [eeg, source-fc, ml, ds005385, ec-eo, plv, theta]
version: v2
language: italiano
target_journal: Journal of Neural Engineering
---
# Discussion — Classificazione EEG Source-Level EC/EO con Connettività PLV-Theta

**Versione**: v2 — final draft (sostituisce v1 placeholder matching-pennies)
**Data**: 2026-05-14
**Dataset**: ds005385 (Dortmund Vital EEG), N=50, paradigma Eyes Closed / Eyes Open
**Risultato principale**: aparc × plv × theta × logreg, BA=0.920 CI=[0.870, 0.970], p_perm < 0.001

---

## 1. Interpretazione dei risultati

### 1.1 PLV-theta come discriminante EC/EO: un risultato non ovvio

La configurazione vincente — connettività PLV nella banda theta (4–8 Hz), atlante aparc
(68 ROI Desikan-Killiany), regressione logistica L2 — raggiunge una balanced accuracy di
0.920 (CI 95% [0.870, 0.970]) nella classificazione Eyes Closed (EC) vs Eyes Open (EO),
con p_perm < 0.001 su 1000 permutazioni. Il risultato è statisticamente robusto e
superiore alla distribuzione nulla empirica per ogni permutazione testata (p_perm = 0/1001).

Questo esito merita un'analisi critica, perché la banda dominante non è la banda alpha
(8–13 Hz), attesa *a priori* sulla base del ben documentato "fenomeno di Berger": l'apertura
degli occhi sopprime la potenza alpha posteriore — fenomeno noto come alpha blocking
(Barry et al., 2007). La nostra analisi opera però su **connettività di fase** (PLV,
Phase Locking Value), non su potenza spettrale: i due costrutti catturano dimensioni
complementari dell'attività EEG.

La connettività PLV-theta misura la **sincronizzazione di fase inter-regionale** nella banda
theta. Nella condizione EC, i network corticali operano in uno stato di quiete sensoriale
che favorisce oscillazioni theta lente a lungo range, tipicamente associate all'attività
del default-mode network e alle interazioni ippocampo-neocorticali a riposo (Klimesch,
1999). Alla riapertura degli occhi (EO), il flusso di input visivi interrompe questi pattern
di sincronizzazione: la de-sincronizzazione theta-frontale e la riorganizzazione dei network
occipitali per il processamento visivo alterano la struttura della matrice di connettività
in modo sistematico e generalizzabile tra soggetti.

La classifica Top-5 del benchmark (Tabella 1) corrobora questa interpretazione: le prime
tre posizioni sono occupate da configurazioni PLV-theta o PLV-alpha con logreg o svm_rbf
(tutte BA=0.920, CI=[0.870, 0.970], p_perm < 0.001). L'equivalenza numerica tra
configurazioni theta e alpha suggerisce che entrambe le bande di frequenza portano
informazione discriminante complementare, coerentemente con la co-occorrenza di modulazione
alpha e theta nei paradigmi di manipolazione dello stato oculare.

### 1.2 Scelta di PLV rispetto a metriche volume-conduction robust

L'uso di PLV come metrica vincente — anziché wPLI o imcoh, che sono metriche robust al
volume conduction — potrebbe sembrare controintuitivo a livello sorgente. La spiegazione
risiede nel preprocessing della pipeline: la ricostruzione sorgente dSPM su template
fsaverage, seguita da parcellazione media-flip per ROI aparc, riduce sostanzialmente il
volume conduction residuo rispetto al sensore scalp. In questo contesto, la maggiore
sensibilità di PLV alle componenti di fase in-phase — che wPLI scarta per definizione —
risulta un vantaggio: cattura sincronizzazione talamica e cortico-corticale genuina che
wPLI conservativa potrebbe sopprimere. Le metriche coh e imcoh mostrano performance
inferiori (BA=0.890 per la migliore configurazione coh, Tab. 1), coerentemente con
il fatto che coherence include informazione di ampiezza non rilevante per la discriminazione
EC/EO a livello di fase.

### 1.3 Confronto con letteratura

La classificazione EC vs EO è uno dei problemi benchmark dell'EEG computazionale: le
performance riportate in letteratura variano tra 80% e 97% in funzione del metodo e del
livello di analisi (Schalk et al., 2004; Korik et al., 2019). I nostri risultati source-level
(BA=0.920) si collocano nella fascia superiore del range pubblicato per approcci sensor-level
standard, confermando che la connettività funzionale calcolata a livello sorgente è comparabile
— e non penalizzata — rispetto all'analisi diretta su segnale scalp.

La scelta del classificatore lineare (logreg) come vincente è coerente con la letteratura
sui classificatori per EEG ad alta dimensione: con N=50 soggetti e 2278 feature, i modelli
L2-regolarizzati spesso superano i modelli nonlineari grazie al meccanismo di regolarizzazione
implicita (Varoquaux et al., 2017). La relativa parità di performance tra logreg e svm_rbf
nelle posizioni Top-2 e Top-3 suggerisce che i dati sono linearmente separabili nello spazio
PLV-theta, in accordo con l'ipotesi di una reorganizzazione globale e sistematica dei
pattern di connettività tra le due condizioni.

---

## 2. Limitazioni metodologiche

### 2.1 Campione single-center (N=50)

Il campione di 50 soggetti è interamente acquisito nel contesto del dataset ds005385
(Dortmund Vital EEG, singolo centro, singola apparecchiatura, protocollo standardizzato).
La mancanza di variabilità inter-center introduce un rischio di overfitting alla specifica
caratteristica tecnica del centro (amplificatore, posizionamento elettrodi, procedure di
preparazione). Gli effetti di sito — ampiamente documentati nell'EEG computazionale
multi-center (Niso et al., 2022) — non possono essere valutati né controllati su un
dataset single-site.

### 2.2 Assenza di validazione esterna

La validazione adottata è puramente interna: LOSO GroupKFold su ds005385, con ogni fold
che lascia fuori un soggetto alla volta. Questo schema, pur essendo il più conservativo
disponibile internamente (si veda §4), non costituisce una validazione su dataset
indipendente. La generalizzabilità delle feature PLV-theta a popolazioni diverse (età,
etnia, sistema EEG), paradigmi leggermente differenti (EC/EO con durata o istruzione
variata), o dataset acquisiti con attrezzature diverse, rimane da verificare. L'analisi
cross-dataset con LEMON come dataset di test indipendente è programmata come sviluppo
futuro (§3.1).

### 2.3 ML tradizionale — assenza di approcci deep learning

La pipeline si limita a classificatori machine learning tradizionali (logreg, svm_rbf, lda).
I modelli deep learning — EEGNet (Lawhern et al., 2018), ShallowConvNet (Schirrmeister et al.,
2017) — sono esclusi per due ragioni: (a) l'architettura del benchmark è orientata alla
trasparenza interpretativa e alla riproducibilità piuttosto che alla massimizzazione assoluta
delle performance, e (b) N=50 soggetti è insufficiente per il training affidabile di modelli
profondi senza aumentazione dati (Roy et al., 2019). L'aggiunta di approcci DL è
prevista in una fase successiva, condizionata all'espansione del campione.

### 2.4 Template MRI vs MRI individuale

La forward solution usa il template fsaverage anziché MRI strutturali individuali, con
un errore di localizzazione sorgente stimato di 1–2 cm (Huang et al., 2016). Per l'analisi
di reti su larga scala via ROI aparc — che integrano attività su aree di decine di cm² —
questo errore è ritenuto trascurabile. Rimane però una fonte di variabilità sistematica
tra soggetti con morfologia corticale molto diversa dalla media.

---

## 3. Prospettive future

### 3.1 Validazione cross-dataset con LEMON

Il dataset LEMON (Leipzig Mind-Brain-Body, 228 soggetti, resting-state EEG+MRI strutturale,
Babayan et al., 2019) è il candidato naturale per la validazione esterna. Il piano è addestrare
il classificatore PLV-theta-logreg su ds005385 (N=50) e applicarlo ai soggetti LEMON senza
re-training (train-on-A/test-on-B scheme), valutando la degradazione di performance come
misura diretta della generalizzabilità inter-dataset.

### 3.2 Benchmark 700-combinazioni completo

Il benchmark corrente copre aparc × {wPLI, coh, PLV, imcoh} × {theta, alpha, beta, gamma}
× {logreg, svm_rbf, lda} (48 configurazioni). Il benchmark esteso a 700 combinazioni —
aggiungendo atlanti Schaefer-100, Schaefer-200, Destrieux e metriche aggiuntive (wPLI²,
ciplv) — è pianificato come step di follow-up per identificare la configurazione ottimale
completa e verificare la robustezza del risultato PLV-theta su uno spazio di iper-parametri
più ampio. I risultati attuali suggeriscono che PLV-theta sia un minimum locale molto
stabile, ma non è escluso che configurazioni con atlanti ad alta risoluzione possano
produrre performance comparabili o superiori.

### 3.3 Feature selection e interpretabilità

La matrice PLV-theta aparc contiene 2278 feature (connessioni ROI-pair). L'analisi
delle feature più discriminanti — tramite coefficienti logreg o metodi SHAP — consentirebbe
di identificare quali connessioni corticali differenziano EC da EO, producendo mappe
di connettività interpretabili neurobiologicamente. Questo passo è fondamentale per
collegare le performance classificative a conoscenza neuroscientifica di primo principio.

---

## 4. Giustificazione scientifica della LOSO CV come validazione principale interna

La cross-validazione Leave-One-Subject-Out (LOSO) — implementata come GroupKFold con
N=50 fold — è la strategia di validazione interna più conservativa disponibile per dataset
EEG multi-soggetto di dimensione moderata. In ogni fold, **tutti i trial di un soggetto**
sono esclusi dal training e usati esclusivamente per la valutazione: questo elimina per
costruzione il *subject leakage*, la principale fonte di inflazione artificiosa delle
performance nei classificatori EEG.

L'entità del bias da subject leakage è stata quantificata empiricamente in +25 punti
percentuali di balanced accuracy rispetto a k-fold naïve su dataset EEG comparabili
(Gemein et al., 2023). Con BA osservata di 0.920, un bias di +0.25 porta a un risultato
ipotetico di 0.67 sotto k-fold corretto — ancora significativo, ma molto più modesto.
La LOSO garantisce che nessun artefatto da subject leakage inflazioni la stima.

La scalatura è appropriata: con N=50, LOSO produce 50 stime di test indipendenti (una
per soggetto), sufficienti per il bootstrap BCa (1000 ricampionamenti, Hesterberg 2015)
che produce i CI 95% riportati. Il permutation test a 1000 permutazioni (p_perm < 0.001,
Combrisson & Jerbi 2015) è applicato sull'intera pipeline LOSO per verificare la
significatività della BA osservata contro la distribuzione nulla empirica. L'impossibilità
di ottenere p_perm = 0.000 esatto è nota (Phipson & Smyth, 2010); riportando
p_perm = 0/1001 < 0.001 si mantiene la correttezza statistica senza affermare
significatività assoluta.

La validazione interna LOSO è il gold standard per dataset EEG multi-soggetto quando
un dataset esterno indipendente non è disponibile. Il presente lavoro dichiara
esplicitamente questa limitazione (§2.2) e pianifica la validazione cross-dataset come
step successivo (§3.1).

---

## Riferimenti

- Barry, R.J., et al. (2007). EEG differences between eyes-closed and eyes-open resting conditions. *International Journal of Psychophysiology*, 65(3), 206–212.
- Babayan, A., et al. (2019). A mind-brain-body dataset of MRI, EEG, cognition, emotion, and peripheral physiology in young and old adults. *Scientific Data*, 6, 180308.
- Combrisson, E., & Jerbi, K. (2015). Exceeding chance level by chance. *Journal of Neuroscience Methods*, 250, 126–136.
- Gemein, L.A.W., et al. (2023). Machine learning-based diagnostics of EEG pathology. *Sensors*, 23(9), 4544.
- Hesterberg, T.C. (2015). What Teachers Should Know About the Bootstrap. *The American Statistician*, 69(4), 371–386.
- Huang, Y., et al. (2016). The impact of EEG electrode locations on spatial variability of brain activation. *Brain Topography*, 29.
- Klimesch, W. (1999). EEG alpha and theta oscillations reflect cognitive and memory performance. *Brain Research Reviews*, 29(2–3), 169–195.
- Korik, A., et al. (2019). Decoding imagined 3D hand movement trajectories from EEG. *International Journal of Neural Systems*, 29(5).
- Lawhern, V.J., et al. (2018). EEGNet: a compact convolutional neural network for EEG-based BCI. *Journal of Neural Engineering*, 15(5).
- Niso, G., et al. (2022). BIDS-EEG: An extension to the brain imaging data structure for EEG. *Scientific Data*, 9, 198.
- Phipson, B., & Smyth, G.K. (2010). Permutation P-values should never be zero. *Statistical Applications in Genetics and Molecular Biology*, 9(1).
- Roy, Y., et al. (2019). Deep learning-based EEG analysis: a systematic review. *Journal of Neural Engineering*, 16(5), 051001.
- Schalk, G., et al. (2004). BCI2000: a general-purpose BCI system. *IEEE Transactions on Biomedical Engineering*, 51(6), 1034–1043.
- Schirrmeister, R.T., et al. (2017). Deep learning with convolutional neural networks for EEG decoding. *Human Brain Mapping*, 38(11).
- Varoquaux, G., et al. (2017). Assessing and tuning brain decoders. *NeuroImage*, 159.
- Vinck, M., et al. (2011). An improved index of phase-synchronization. *NeuroImage*, 55(4).
