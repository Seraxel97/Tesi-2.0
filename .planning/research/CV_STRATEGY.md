---
type: thesis-section
status: draft
section: methods
project: Tesi_2.0
last_review: 2026-05-01
sprint: S-50
tags: [eeg, source-fc, ml]
---
# Cross-Validation Strategy — EEG ML Classification

**Versione**: v1  
**Data**: 2026-05-01  
**Cross-ref**: `ml_training/ml_dispatcher.py`, `ml_training/permutation.py`  
**Target**: ~800 parole, stile IEEE Trans. Biomed. Eng.

---

## 1. Background: perché GroupKFold per EEG multi-soggetto

La scelta della strategia di cross-validazione è una delle decisioni metodologiche più critiche negli studi di classificazione EEG multi-soggetto. Una cross-validazione naïve — in cui i trial di soggetti diversi vengono mescolati prima della suddivisione — produce stime gonfiate perché lo stesso soggetto può comparire sia nel training che nel test set. Questo fenomeno, noto come *subject leakage*, permette al classificatore di apprendere pattern idiosincratici dell'individuo piuttosto che segnali neurali genuini associati al task.

L'entità del bias è stata quantificata empiricamente: Gemein et al. (2023, *Sensors*) hanno riscontrato un'inflazione media della balanced accuracy di **+25 punti percentuali** con k-fold naïve rispetto a LOSO inter-soggetto su dataset EEG comparabili. Questo valore supera le differenze tipiche tra algoritmi, rendendo la strategia di CV il fattore più determinante per la validità dei risultati. GroupKFold assegna gli interi soggetti a fold distinti, eliminando il subject leakage e prevenendo anche il *temporal leakage* tra trial adiacenti dello stesso soggetto.

### 1.1 Why not standard k-fold for EEG?

Standard k-fold is inappropriate for multi-subject EEG for three compounding reasons.

**Subject leakage (+25 pp inflation, Gemein et al. 2023)**: When trials from the same
subject appear in both training and test folds, the classifier learns subject-specific
scalp topography rather than generalizable neural signatures. Saeb et al. (2017) further
show that global normalization applied before splitting introduces an additional leakage
channel: test-set statistics contaminate the scaler fitted on training data.

**Temporal leakage**: In continuous EEG recordings, adjacent trials share filter state
and slow cortical drifts. Standard k-fold may place temporally neighboring trials on
opposite sides of the train/test boundary. Jas et al. (2018) demonstrate this in the
context of artifact rejection thresholds and recommend leave-one-subject-out schemes
even during preprocessing.

**Selection bias from model search (Bishop & Bishop 2024, §9)**: When CV is used to
both select hyperparameters and estimate generalization, the test error is optimistically
biased. This bias compounds across the 700 configurations of the benchmark matrix. FDR
correction (Benjamini-Hochberg 1995) controls the expected proportion of false positives,
but only if the null distribution is correctly estimated — requiring a leakage-free CV
procedure as the base.

Roy et al. (2019, *Journal of Neural Engineering*) surveyed 154 EEG deep-learning studies
and found that 60% used naive k-fold despite known leakage risks. The present pipeline
explicitly adopts GroupKFold and documents the choice with quantitative justification.

---

## 2. Protocollo adottato in Tesi_2.0

La pipeline implementa due modalità di cross-validazione selezionate in base alla disponibilità del dataset:

**Caso multi-soggetto — GroupKFold(n_splits=5)**. Questa è la modalità attiva per il dataset scientifico finale. I soggetti vengono assegnati a 5 fold disgiunti tramite il parametro `groups` (array di subject ID corrispondente a ciascun trial). In ogni iterazione, 4 fold (circa l'80% dei soggetti) costituiscono il training set e 1 fold (circa 20% dei soggetti) il test set. Nessun trial appartenente a un soggetto nel test set è visibile durante il training. Con dataset di 20–50 soggetti, questo schema garantisce stime di generalizzazione affidabili e statisticamente interpretabili.

**Caso mono-soggetto — StratifiedKFold(n_splits=5, shuffle=True)**. Utilizzato esclusivamente per il dataset di sviluppo *matching pennies* (N=1 soggetto, sub-05). In questo contesto, GroupKFold non è applicabile e lo schema stratificato mantiene la proporzione delle classi bilanciata in ogni fold. Come esplicitato nella documentazione del benchmark, i risultati su singolo soggetto non hanno validità statistica per inferenze sulla popolazione e servono unicamente a verificare la correttezza tecnica della pipeline.

Il numero di fold viene ridotto automaticamente se il numero di campioni per classe è inferiore a `n_splits` (`n_splits = min(K, min(bincount(y)))`), prevenendo fold con zero campioni di una classe.

In entrambe le modalità, un **StandardScaler** viene fittato esclusivamente sui dati di training di ciascun fold e applicato al test set senza re-stima dei parametri di normalizzazione — eliminando una seconda possibile fonte di data leakage (la normalizzazione globale).

| Setting | CV strategy | Groups | Leakage-free |
|---------|-------------|--------|-------------|
| Multi-subject (dataset finale) | GroupKFold(k=5) | subject_id | ✓ |
| Single-subject (smoke test) | StratifiedKFold(k=5) | — | N/A |

---

## 3. Implementazione

La logica di cross-validazione è centralizzata in `ml_training/ml_dispatcher.py`. La funzione `run_cv(X, y, groups, algorithm, n_splits)` restituisce un oggetto `CVResult` con balanced accuracy per fold, media, deviazione standard e confusion matrix aggregata. Ogni classificatore è eseguito all'interno di una `Pipeline` scikit-learn che concatena `StandardScaler` e il modello — garantendo che la normalizzazione sia sempre interna al fold. La funzione `run_all_algorithms(X, y, groups)` esegue la CV per tutti e cinque i classificatori disponibili (logreg, svm, mlp, rf, gb) e restituisce un dizionario `{algorithm: CVResult}`.

---

## 4. Permutation testing

La significatività statistica dei risultati di classificazione viene valutata tramite permutation test non parametrico, implementato in `ml_training/permutation.py`. Il test esegue 1000 permutazioni delle etichette `y` — randomizzando l'assegnazione trial-classe mantenendo invariata la struttura di gruppi e feature — e per ciascuna permutazione calcola la balanced accuracy tramite la stessa pipeline CV. La distribuzione null ottenuta riflette il tasso di accuracy atteso sotto l'ipotesi nulla di assenza di segnale discriminante.

Il p-value empirico è definito come la proporzione di permutazioni in cui la BA null è maggiore o uguale alla BA osservata:

**p = #{BA_null ≥ BA_obs} / N_perm**

Con 1000 permutazioni, la risoluzione del p-value è 0.001. Il seed del generatore di numeri casuali è fissato a 42 per la riproducibilità.

Il permutation test è applicato al dataset multi-soggetto finale. Sul dataset di sviluppo singolo-soggetto viene omesso per mancanza di potenza statistica.

### 4.1 Rationale: perché il permutation test è necessario

**Il livello di chance teorico non è sufficiente.** La soglia del 50% per classificazione binaria è valida solo asintoticamente. Combrisson & Jerbi (2015) dimostrano che con campioni finiti tipici dell'EEG (N = 50–200 trial per soggetto), un classificatore casuale supera il 50% con probabilità non trascurabile: con N = 50 trial, il 5° percentile superiore della distribuzione casuale è ~62%. Usare 50% come soglia di significatività porta quindi a tassi di falsi positivi reali molto superiori al 5% nominale. Questo problema è particolarmente acuto nel presente benchmark, dove si confrontano 700 configurazioni con dataset mono-soggetto (N piccolo per classe).

**La distribuzione null empirica è la soluzione.** Il permutation test costruisce la distribuzione null dell'accuracy permutando le etichette — preservando la struttura di feature, gruppi e splits — e calcola quante permutazioni producono accuracy ≥ al risultato osservato. Questa procedura è non-parametrica (non assume gaussianità della distribuzione della statistica), valida sotto la sola condizione di scambiabilità delle osservazioni sotto H0 (Nichols & Holmes, 2002; Good, 2005), e applicabile a qualsiasi metrica di classificazione.

**Numero minimo di permutazioni e calcolo corretto del p-value.** Phipson & Smyth (2010) mostrano che il p-value empirico #{perm ≥ obs} / N_perm può apparentemente essere zero per N_perm piccoli, il che è statisticamente impossibile (un p-value esatto non può essere 0 con permutazioni finite). La formula corretta, che evita questo artefatto, è:

**p = (#{perm ≥ obs} + 1) / (N_perm + 1)**

Con N_perm = 1000, la risoluzione minima è p = 1/1001 ≈ 0.001, sufficiente per testare a α = 0.05 con potenza adeguata. Phipson & Smyth raccomandano N_perm ≥ 999 come minimo per p-values ≤ 0.001 affidabili.

**FDR correction obbligatoria per test multipli.** Con 700 test nel benchmark, la probabilità di almeno un falso positivo usando soglia α = 0.05 individuale senza correzione è 1 − (0.95)^700 ≈ 1.0 (certezza pratica di falsi positivi). La correzione FDR Benjamini-Hochberg (§5) è obbligatoria per mantenere un tasso di falsi positivi controllato sull'insieme del benchmark. La scelta FDR rispetto a Bonferroni è motivata dalla natura esplorativa del confronto: si accetta un numero limitato di falsi positivi (FDR ≤ 5%) per non perdere associazioni reali (Maris & Oostenveld, 2007).

---

## 5. Reporting

Le metriche riportate per ciascuna configurazione del benchmark (atlas × metrica FC × banda × algoritmo) sono:

| Metrica | Significato | Valore atteso (EEG single-trial) |
|---------|-------------|----------------------------------|
| Balanced Accuracy (BA) | (sensitivity + specificity) / 2 | 0.55–0.70 |
| BA std | Variabilità tra fold | < 0.10 |
| p_perm | P-value permutation test | < 0.05 (soglia pre-FDR) |
| p_fdr | P-value corretto BH-FDR | < 0.05 (soglia post-FDR) |
| Confusion matrix | Matrice aggregata su tutti i fold | — |

La balanced accuracy è preferita all'accuracy classica perché è robusta a classi sbilanciate (cfr. Salzberg, 1997). La correzione FDR Benjamini-Hochberg viene applicata sull'insieme completo dei 700 test del benchmark, controllando il tasso di falsi positivi attesi a livello α=0.05.

---

## 5. Bootstrap Confidence Intervals su Balanced Accuracy

La balanced accuracy (BA) è riportata con intervallo di confidenza al 95% calcolato
via **bootstrap BCa** (bias-corrected accelerated, 1000 ricampionamenti) sui valori
per-fold. Il bootstrap BCa è preferito al CI normale per due ragioni:

1. Con N fold piccoli (tipicamente 5–20), la distribuzione campionaria della BA è
   asimmetrica e potenzialmente non-normale (Hesterberg 2015).
2. Il livello del caso teorico (50% per classificazione binaria bilanciata) può essere
   fuorviante con dataset piccoli; il CI bootstrap fornisce una stima empirica della
   variabilità (Combrisson & Jerbi 2015).

**Implementazione** (`analysis/stats_utility.py`, S-41):

```python
from analysis.stats_utility import ci_bootstrap
ci_low, ci_high = ci_bootstrap(ba_per_fold, n_bootstrap=1000, ci=0.95, method="bca")
```

**Reporting standard**:

> "Balanced accuracy (BA) è riportata come media ± CI 95% BCa bootstrap su fold LOSO
> (1000 ricampionamenti). La significatività statistica è valutata tramite permutation
> test (1000 permutazioni) con correzione FDR-BH [Efron 1979, Hesterberg 2015,
> Combrisson & Jerbi 2015]."

---

## Riferimenti

- Gemein, L.A.W., et al. (2023). Machine learning-based diagnostics of EEG pathology. *Sensors*, 23(9), 4544.
- Saeb, S., et al. (2017). The need for fully automated analysis of EEG biomarkers. *npj Digital Medicine*, 1, 12.
- Jas, M., et al. (2018). Autoreject: Automated artifact rejection for MEG and EEG data. *NeuroImage*, 159, 417–429.
- Roy, Y., et al. (2019). Deep learning-based electroencephalography analysis: a systematic review. *Journal of Neural Engineering*, 16(5), 051001.
- Bishop, C.M., & Bishop, H. (2024). *Deep Learning: Foundations and Concepts*. Springer.
- Varoquaux, G., et al. (2017). Assessing and tuning brain decoders. *NeuroImage*, 159.
- Salzberg, S.L. (1997). On comparing classifiers. *Machine Learning*, 26, 251–256.
- Benjamini, Y., & Hochberg, Y. (1995). Controlling the false discovery rate. *Journal of the Royal Statistical Society B*, 57(1).
- Efron, B. (1979). Bootstrap Methods: Another Look at the Jackknife. *The Annals of Statistics*, 7(1), 1–26.
- Hesterberg, T.C. (2015). What Teachers Should Know About the Bootstrap. *The American Statistician*, 69(4), 371–386.
- Combrisson, E., & Jerbi, K. (2015). Exceeding chance level by chance. *Journal of Neuroscience Methods*, 250, 126–136.

> BibTeX entries completi in `.planning/research/REFS_BOOTSTRAP.md` e `bibliografia.bib`.

> BibTeX entries completi in `.planning/research/REFS_LOSO_CV.md`.
