# Risultati e limiti — claim consolidati e batteria di robustezza

> Scopo: una sola pagina che il relatore può leggere per capire **cosa regge e cosa no**,
> con i numeri veri. Filosofia: il contributo è la **macchina di validazione**, non un
> biomarcatore forte e generalizzabile.

## Risultato primario (ds005385, N=179)

Il **sesso** è classificabile dalla connettività EEG (banda theta, atlante aparc, metrica
PLV):
- Cross-validation (GroupKFold per-soggetto): **BA = 0.795** [CI95 0.744–0.843], p_perm = 0.001
- Transferability held-out (train N=100 → 79 soggetti nuovi entro-dataset): **BA = 0.776**
  [0.70–0.84], p = 0.001 → nessun double-dipping, il segnale regge sui soggetti mai visti.

L'**età** (regressione) è invece un risultato quasi-nullo onesto: R² con CI95 che include lo
zero → riportare **MAE-vs-Dummy** come metrica primaria, non R²-pooled. Non è un claim forte.

## Batteria di robustezza sul segnale-sesso (3 controlli che un revisore chiede sempre)

### 1. Confound età↔sesso — NEUTRALIZZATO, il segnale sopravvive
Nel campione l'età differisce per sesso (M mediana 50 vs F 42.5, Mann-Whitney p = 0.0061):
il classificatore poteva sfruttare pattern età-correlati. Age-matching ottimale 1:1 M↔F
(Hungarian su |Δetà|) → subset di 134 soggetti dove l'età **non differisce più** (p = 0.874,
Δetà media entro-coppia 0.58 anni). Ri-stima con lo stesso classificatore:
**BA = 0.719** [0.657–0.784], p_perm = 0.001. → Il segnale del sesso **non è un artefatto
dell'età**. (`scripts/confound_age_sex_rematch.py`)

### 2. Volume conduction — il PLV è GONFIATO, effect-size onesto ≈ 0.57
Il PLV è sensibile al volume conduction (connettività spuria a lag-zero). Ri-stima con
metriche **robuste** (ignorano il lag-zero), stessa banda/atlante:

| Metrica | Volume-conduction | BA sesso | CI95 | p_perm |
|---|---|---|---|---|
| PLV (winner) | sensibile | 0.795 | 0.744–0.843 | 0.001 |
| wPLI | robusta | 0.570 | 0.515–0.627 | 0.024 |
| imcoh | robusta | 0.574 | 0.515–0.627 | 0.024 |

Il sesso resta decodificabile **sopra il caso** anche con metriche robuste (p < 0.05), ma solo
il **~24%** dell'effetto sopra-il-caso sopravvive (PLV 0.295 → robuste 0.072). → **Il BA
headline 0.795 è sostanzialmente inflazionato dal volume conduction**; l'effect-size difendibile
è modesto (~0.57). Limitazione da dichiarare in **evidenza**, non in nota.
(`scripts/sensitivity_conn_metric.py`)

### 3. Generalizzazione cross-dataset — TESTATA su coorte SANA: NON generalizza
Test PULITO e reale: LEMON EEG scaricato davvero (FTP GWDG, adulti **sani** resting-state,
47 sogg/94 sample), processato con la **stessa pipeline** (feature aparc/theta 2278-dim
compatibili). Transfer ds005385(N=179) → LEMON, no-leakage (scaler su train), inference-only:

| Metrica | Volume-conduction | BA transfer → LEMON |
|---|---|---|
| PLV (winner) | sensibile | **0.583** |
| wPLI | robusta | 0.508 |
| imcoh | robusta | 0.506 |

vs 0.795 in-dataset. Nessun label-flip (BA ≥ 0.5). → **Il sesso NON generalizza a una coorte
sana indipendente**: PLV appena sopra il caso, metriche robuste al caso. **Risultato
dataset-specifico.** (`scripts/cross_dataset_lemon.py`, `reports/CROSS_DATASET_LEMON_SEX_ALTO2.md`)

> ⚠️ Il vecchio transfer su ds004504 (BA=0.500) era confuso (coorte Alzheimer/età-diversa); e
> l'ADR-004 che vantava LEMON BA=0.833 è un FANTASMA (nessun dato/file a supporto, mai eseguito
> — vedi vault `020_DECISIONS/ADR-004`, ora SUPERSEDED). Questo è il primo numero LEMON REALE.

## Claim difendibile (da mettere in Discussione/Conclusione)

> Su ds005385 (N=179) il sesso è decodificabile dalla connettività EEG theta con validazione
> interna rigorosa (held-out entro-dataset BA≈0.78, p=0.001). Il segnale **non è un artefatto
> dell'età** (regge l'age-matching, BA=0.719) ed è **parzialmente reale** ma **modesto** una
> volta rimosso il volume conduction (wPLI/imcoh BA≈0.57): il valore 0.795 del PLV è
> sostanzialmente inflazionato da conduzione spuria. La **generalizzazione a un dataset
> indipendente NON regge**: su una coorte sana (LEMON), il transfer del sesso è ~0.58 col PLV e
> al caso con le metriche robuste → il risultato è **specifico di ds005385**. L'**età** è un
> risultato quasi-nullo (MAE vicino al Dummy).

## Il vero contributo (posizionamento onesto)

Non "abbiamo trovato un biomarcatore-sesso forte e generalizzabile", ma: **una pipeline di
validazione rigorosa** — audit anti-leakage verificato nel codice, permutation design-aware
(between vs within soggetto), held-out entro-dataset, e questa **batteria di robustezza**
(confound d'età, volume conduction, transfer cross-dataset) — che distingue un effetto reale-ma-
modesto da un numero-vetrina fragile. È questo il prodotto vendibile.

---
*Numeri: `data/results/ds005385/{confound_age_sex,confound_age_sex_rematch,sensitivity_conn_metric}.json`,
`reports/{CONFOUND_AGE_SEX_REMATCH_F3,SENSITIVITY_CONN_METRIC_F3,CROSS_DATASET_TRANSFER}.md`.*
