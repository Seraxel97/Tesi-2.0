# Cross-Validation Strategy — EEG ML Classification

**Versione**: v1  
**Data**: 2026-05-01  
**Cross-ref**: `ml_training/ml_dispatcher.py`, `ml_training/permutation.py`  
**Target**: ~800 parole, stile IEEE Trans. Biomed. Eng.

---

## 1. Background: perché GroupKFold per EEG multi-soggetto

La scelta della strategia di cross-validazione è una delle decisioni metodologiche più critiche negli studi di classificazione EEG multi-soggetto. Una cross-validazione naïve — in cui i trial di soggetti diversi vengono mescolati prima della suddivisione — produce stime gonfiate perché lo stesso soggetto può comparire sia nel training che nel test set. Questo fenomeno, noto come *subject leakage*, permette al classificatore di apprendere pattern idiosincratici dell'individuo piuttosto che segnali neurali genuini associati al task.

L'entità del bias è stata quantificata empiricamente: Gemein et al. (2023, *Sensors*) hanno riscontrato un'inflazione media della balanced accuracy di **+25 punti percentuali** con k-fold naïve rispetto a LOSO inter-soggetto su dataset EEG comparabili. Questo valore supera le differenze tipiche tra algoritmi, rendendo la strategia di CV il fattore più determinante per la validità dei risultati. GroupKFold assegna gli interi soggetti a fold distinti, eliminando il subject leakage e prevenendo anche il *temporal leakage* tra trial adiacenti dello stesso soggetto.

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

## Riferimenti

- Gemein, L.A.W., et al. (2023). Machine learning-based diagnostics of EEG pathology. *Sensors*, 23(9).
- Varoquaux, G., et al. (2017). Assessing and tuning brain decoders. *NeuroImage*, 159.
- Salzberg, S.L. (1997). On comparing classifiers. *Machine Learning*, 26, 251–256.
- Benjamini, Y., & Hochberg, Y. (1995). Controlling the false discovery rate. *Journal of the Royal Statistical Society B*, 57(1).
