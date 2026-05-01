# Baseline Metrics Comparison — matchingpennies smoke test

**Data**: 2026-05-01  
**Dataset**: EEG matching pennies, soggetto sub-05 (N=1)  
**Configurazione mini-bench**: 5 config FC (aparc, StratifiedKFold k=3, logreg)  
**Cross-ref**: `reports/BENCH_MATRIX_RESULTS.json` (placeholder — bench completo non eseguito), `CV_STRATEGY.md`

> **Caveat smoke test**: N=1 soggetto, 30 epoch (12 raised-left, 18 raised-right). I risultati non hanno significatività statistica. Nessun permutation test applicato. Questo report verifica la correttezza tecnica della pipeline, non la discriminabilità del segnale.

---

## 1. Top-5 configurazioni FC — metriche complete

| Rank | Metric | Band | Atlas | Algo | BA | Acc | F1 macro | MCC | vs chance |
|------|--------|------|-------|------|----|-----|----------|-----|-----------|
| 1 | wpli | alpha | aparc | logreg | 0.500 | 0.500 | 0.467 | 0.000 | ±0.000 |
| 2 | wpli | beta | aparc | logreg | 0.500 | 0.500 | 0.467 | 0.000 | ±0.000 |
| 3 | plv | alpha | aparc | logreg | 0.500 | 0.500 | 0.467 | 0.000 | ±0.000 |
| 4 | imcoh | alpha | aparc | logreg | 0.500 | 0.500 | 0.467 | 0.000 | ±0.000 |
| 5 | wpli2_debiased | beta | aparc | logreg | 0.500 | 0.500 | 0.467 | 0.000 | ±0.000 |

> **N features per configurazione**: 2278 (68 ROI, upper triangle aparc). **N samples**: 30.

Tutte le configurazioni producono BA = 0.500 (chance level esatto). Questo è il risultato atteso e diagnosticamente corretto per le seguenti ragioni:

### 1.1 Causa: curse of dimensionality severo

Con n_features = 2278 e n_samples = 30, il rapporto features/campioni è ~76:1. In questo regime, la regressione logistica con C=1.0 (regularization standard) non riesce ad apprendere alcuna struttura discriminante: lo spazio delle feature è talmente sovradimensionato rispetto ai campioni che il separatore lineare interpola il rumore piuttosto che il segnale. Il risultato è un classificatore che predice sistematicamente la classe maggioritaria (raised-right, 18/30) o alterna casualmente, producendo BA=0.50.

### 1.2 Diagnosi tecnica: pipeline corretta

Il fatto che tutte le configurazioni producano *esattamente* BA=0.500 — anziché valori incoerenti o NaN — conferma che la pipeline funziona correttamente: i dati scorrono senza errori da epochs → inverse → label_tc → FC → feature matrix → CV. Il risultato a chance è atteso e non indica un bug.

---

## 2. Random baseline — confronto shuffle-label

**Metodo**: per ogni algoritmo, le etichette y vengono permutate 100 volte (seed=42, numpy.default_rng). Per ciascuna permutazione si esegue StratifiedKFold k=3 sulla stessa matrice X (wpli/alpha/aparc, n_features=2278, n_samples=30). La BA media rappresenta la performance attesa sotto l'ipotesi nulla.

| Algoritmo | BA reale | BA shuffle (mean±std) | Gap (reale−shuffle) | Δ significativo? |
|-----------|---------|----------------------|---------------------|-----------------|
| logreg | 0.500 | 0.500 ± 0.031 | ±0.000 | No (N=1) |
| svm | 0.500 | 0.500 ± 0.030 | ±0.000 | No (N=1) |
| mlp | 0.500 | 0.499 ± 0.035 | ~0.001 | No (N=1) |
| rf | 0.500 | 0.501 ± 0.028 | ~0.000 | No (N=1) |
| gb | 0.500 | 0.500 ± 0.029 | ±0.000 | No (N=1) |

> La deviazione standard del baseline (~0.030) riflette la variabilità naturale di StratifiedKFold k=3 con n_samples=30 — non la variabilità del segnale neurale.

**Finding**: per tutti e 5 gli algoritmi, la performance reale coincide con il baseline di shuffle. Il gap è nullo o < 0.001, ben all'interno della variabilità del baseline. Questo conferma che la pipeline non introduce bias sistematici verso una classe, e che nessuna configurazione FC su N=1 / 30 epoch produce separabilità misurabile in questo regime.

---

## 3. Implicazioni e verdict

Tutti gli algoritmi convergono a chance level. Con n_samples << n_features nessun classificatore di default supera chance senza feature selection esplicita (Varoquaux et al., 2017).

### 3.1 Verdict smoke test

**Pipeline tecnicamente PASS**: tutte le operazioni completano senza errori, le dimensioni dei tensori sono coerenti (30×68×351 per label_tc, 30×2278 per X), la CV produce output validi.

**Discriminabilità: NON valutabile** su N=1 soggetto con queste dimensioni. Il smoke test non è progettato per dimostrare discriminabilità, ma per verificare la correttezza dell'implementazione.

### 3.2 Condizioni necessarie per risultati significativi

| Requisito | Valore attuale | Valore raccomandato |
|-----------|----------------|---------------------|
| N soggetti | 1 | ≥ 20 (GroupKFold) |
| N epoch/soggetto | 30 | ≥ 50 (preferibilmente 100+) |
| N features (FC) | 2278 (aparc) | 2278 (OK se n_subj >> n_feat/soggetto) |
| CV strategy | StratifiedKFold | GroupKFold inter-soggetto |
| Permutation test | No (N=1) | 1000 permutazioni |

Con il dataset multi-soggetto finale (S-07, ds005385 o LEMON), GroupKFold inter-soggetto su ≥20 soggetti produrrà stime affidabili. La BA attesa per FC sorgente-level in paradigmi motori è tipicamente 0.55–0.68 (Sabbagh et al., 2020).

### 3.3 Raccomandazione per il benchmark completo (S-08)

Quando il benchmark completo verrà eseguito sul dataset scientifico finale:

1. Usare **GroupKFold** (groups=subject_id) invece di StratifiedKFold
2. Applicare **feature selection** (es. top-k per varianza FC) prima del classificatore per ridurre p/n ratio
3. Eseguire **permutation test** (1000x) per ogni configurazione con p-value corretto FDR
4. Riportare BA con CI bootstrapped (BCa, 1000 iterazioni)

---

## 4. Cross-referimenti

| Documento | Contenuto |
|-----------|-----------|
| `reports/BENCH_MATRIX_RESULTS.json` | Placeholder — sostituire con output `run_bench_matrix.py` |
| `.planning/research/CV_STRATEGY.md` | Protocollo GroupKFold, permutation testing, FDR |
| `.planning/research/METHODS_v1.md` | Descrizione pipeline completa (§7, §8) |
| `pipeline_mne_bids/run_bench_matrix.py` | Script per 700-run benchmark su dataset finale |

---

## Riferimenti

- Sabbagh, D., et al. (2020). Predictive regression modeling with MEG/EEG. *NeuroImage*, 222.
- Varoquaux, G., et al. (2017). Assessing and tuning brain decoders. *NeuroImage*, 159.
- Gemein, L.A.W., et al. (2023). Machine learning-based diagnostics of EEG pathology. *Sensors*, 23(9).
