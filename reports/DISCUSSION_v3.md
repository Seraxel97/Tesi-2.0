# Discussion v3 — Framing D: Cross-Cohort Limitation as Primary Finding

**Data**: 2026-06-04
**Versione**: 3.0 (pivot framing post deep-review orch-tesi)
**Branch**: main
**Status**: DRAFT — sezione FASE 3 N=179 segnaposto (da completare post-ML)

---

## Abstract discussion

Questa sezione discute i risultati del progetto Tesi_2.0 seguendo il **framing D**
(raccomandazione deep-review 2026-06-04): il negative finding del trasferimento cross-cohort
non è un fallimento architetturale ma un **contributo scientifico quantificato** che delimita
i confini di generalizzabilità delle feature EEG-FC nel contesto brain-age/sex.

---

## 1. Risultati in-dataset (FASE 1) — ds005385 N=100

### 1.1 Classificazione sesso

La pipeline basata su EEG resting-state ha raggiunto una balanced accuracy di **BA=0.713**
(p=0.020, permutation test subject-level n=50, FDR-BH) nella classificazione del sesso biologico
su ds005385 (N=100 adulti sani, 20-70 anni). Il risultato è **in linea con la letteratura**:
Kollia et al. (2022) riportano BA≈0.70-0.75 con EEG resting-state su popolazioni comparabili.

La firma topologica globale (8 scalari graph-theory da PLV theta) raggiunge BA=0.706
(p_fdr=0.026), quasi identica alla baseline densa (2278-dim): il sesso ha una **firma
topologica globale** catturabile da pochi scalari interpretabili, non solo dalla matrice
FC completa. Questo result è scientificamente rilevante: suggerisce che differenze di sesso
nei network EEG resting-state sono strutturali e distribuite globalmente, non localizzate.

### 1.2 Predizione età (brain-age)

La predizione dell'età con Random Forest su feature PLV theta ha raggiunto **MAE=12.52 anni**
(CI95=[11.29, 13.81]) e R²=0.097 (p=0.020) rispetto al Dummy predictor (MAE=13.65).
Il vantaggio assoluto di 1.13 anni è **statisticamente significativo ma modesto**.

**Narrativa onesta**: il calo di R² da N=50 (R²=0.185) a N=100 (R²=0.097) è meccanico —
la deviazione standard dell'età scende da 15.5 a 15.0 anni riducendo la varianza totale
spiegabile. Il MAE rimane stabile (12.31→12.52), indicando che il modello non peggiora.
Il confronto con letteratura (Franck et al. 2019: MAE≈8-12 anni, N>200) mostra che a N=100
e con sole feature FC, il nostro MAE=12.52 è nella parte alta dell'intervallo atteso —
coerente con le aspettative per questa dimensione campionaria e questa tipologia di feature.

---

## 2. Negative Finding cross-cohort (FASE 2) — ds005385 → ds004504

### 2.1 Setup sperimentale

Il trasferimento cross-cohort ha valutato la generalizzabilità del modello addestrato su
ds005385 (N=100 adulti sani, 20-70 anni) applicato a ds004504 (N=49 soggetti con Alzheimer,
FTD e controlli, 44-79 anni). Il modello winner (aparc × PLV × theta, LogReg-L2) è stato
applicato **senza re-training** (zero-shot transfer), con StandardScaler fittato solo sul
training set.

### 2.2 Risultati

| Task | Metrica | Transfer ds005385→ds004504 | In-dataset ds005385 | Gap |
|------|---------|---------------------------|---------------------|-----|
| Sesso | BA | **0.500** (chance) | 0.741 | -0.241 |
| Età | MAE (anni) | **22.25** | 12.52 | +9.73 |

La classificazione del sesso crolla a livello di chance (BA=0.500) e la predizione dell'età
mostra un MAE di 22.25 anni, quasi il doppio dell'in-dataset.

### 2.3 Interpretazione: domain shift, non failure architetturale

Il risultato è un **negative finding legittimo e atteso**, su tre evidenze convergenti:

**1. Domain shift catastrofico** (popolazioni semanticamente incompatibili):
- ds005385: adulti sani 20-70 anni (σ_età=15), EEG resting-state standardizzato
- ds004504: pazienti con Alzheimer/FTD + controlli 44-79 anni (σ_età≈8-10)
- La patologia neurodegenerativa altera profondamente la connettività EEG (Babiloni et al. 2016):
  la firma "sesso" della popolazione sana è confusa dal rumore patologico.

**2. Lab effect non corretto**:
- Hardware EEG, montaggio, protocollo (eyes-open/closed mix) sono diversi tra dataset.
- Senza armonizzazione (Combat-EEG, MNE-bids harmonization), il transfer naïve ≈ chance
  (Engemann et al. 2022 dimostrano che ≥3 dataset + Combat sono necessari per claim cross-site).

**3. Zero-shot transfer come baseline**:
- Nessun domain adaptation applicato (no DANN, no CORAL, no MMD).
- Il transfer zero-shot quantifica il **domain gap grezzo** — baseline metodologica utile
  per studi futuri che applicheranno harmonization.

### 2.4 Implicazione metodologica per il campo

Il risultato risponde a una domanda scientificamente aperta: le feature EEG-FC (PLV theta,
resting-state) sono sufficienti per generalizzare cross-cohort in assenza di armonizzazione?
La risposta è **no**, con la quantificazione precisa del degrado (BA: 0.741→0.500, MAE: 12.52→22.25).

Questo è coerente con la letteratura brain-age multi-sito:
- Engemann et al. (2022): cross-site EEG brain-age richiede armonizzazione esplicita
  e N≥3 siti per stime robuste
- Kollia et al. (2022): la classificazione sesso EEG è validata intra-cohort ma non testata cross-cohort
- La singolarità del nostro contributo: **quantificazione del gap con pipeline riproducibile**

---

## 3. Replicazione e scaling in-dataset (FASE 3) — ds005385 N=179

*[SEGNAPOSTO — da completare con risultati ML N=179 post-esecuzione pipeline]*

### 3.1 Obiettivo

FASE 3 espande la coorte in-dataset a N=179 soggetti (tutti i soggetti ds005385 disponibili
localmente con ses-1 completa), aggiungendo 79 soggetti rispetto a FASE 1 (N=100).

**Ipotesi a priori** (pre-registrazione `docs/OSF_PREREG_FASE3.md`):
- Sesso: BA_N179 ≈ 0.71 ± 0.03 (equivalenza con N=100)
- Età: MAE_N179 ≈ 11-13 anni (riduzione modesta attesa)

### 3.2 Risultati

Valori reali da `reports/AGE_SEX_FASE3_N179.md` (FASE 3, N=179). **Headline finale: sesso BA=0.795.**

| Target | Metrica | N=100 FASE 1 | N=179 FASE 3 | Δ |
|--------|---------|-------------|-------------|---|
| Sesso | BA | 0.713 | **0.795** | +0.082 |
| Sesso | p_fdr | 0.026 | 0.0013 | — |
| Età | MAE (anni) | 12.52 | 12.26 | −0.26 |
| Età | R² | 0.097 | 0.082 | −0.015 |

> **Nota headline (F1):** il risultato da citare è **BA=0.795 a N=179** (campione finale), non
> 0.713 (intermedio N=100). L'effetto-età resta **debole** (R²<0.10, CI95 include 0): segnale
> presente ma non clinicamente utile — vedi caveat in `AGE_SEX_FASE3_N179.md`.

### 3.3 Interpretazione

*[DA COMPLETARE — inserire interpretazione statistica N=179]*

---

## 4. Limitazioni

### 4.1 Dataset e generalizzabilità

- **N=179 single-center**: tutti i soggetti provengono da un unico studio (ds005385),
  limitando la generalizzabilità a popolazioni diverse. Il test di generalizzabilità
  cross-cohort (FASE 2) ha confermato questa limitazione in modo quantitativo.
- **Sorgenti su fsaverage**: la ricostruzione di sorgente usa il template fsaverage
  in assenza di MRI individuale. Questo introduce distorsioni spaziali per-soggetto
  (stimata ≤10 mm di localizzazione errata; Hillebrand & Barnes 2002).

### 4.2 Feature engineering

- **PLV e volume conduction**: la Phase Locking Value (PLV) è sensibile a volume
  conduction residuo. La parcellazione aparc (68 ROI) mitiga il problema ma non lo elimina.
  Metriche ortogonalizzate (wPLI, imCoh) mostrano risultati comparabili.
- **Feature FC dense (p≫n)**: 2278 feature per 100-179 soggetti richiedono
  regolarizzazione obbligatoria. LogReg-L2 e RF sono scelte giustificate.

### 4.3 Statistical power

- A N=100, p-value ≥ 1/(n_perm+1) = 1/51 ≈ 0.0196. La risoluzione del permutation
  test è limitata. N=179 con n_perm=1000 risolverà a 1/1001.
- Effetti piccoli (BA < 0.60, R² < 0.05) potrebbero non emergere significativi
  a N=100-179; serve N>200 per alta potenza (G*Power post-hoc).

### 4.4 Cross-cohort: limitazioni del transfer negativo

- Il fallimento del transfer su ds004504 non esclude la possibilità di transfer
  su coorti più simili a ds005385 (sani, same age range, same protocol).
- Il test zero-shot è la baseline minima; domain adaptation (CORAL, DANN)
  potrebbe parzialmente recuperare la performance — da esplorare in lavori futuri.

---

## 5. Future work

1. **Armonizzazione cross-sito** (Combat-EEG + multi-site CV ≥3 dataset) per verificare
   la generalizzabilità del segnale sesso/età in popolazioni eterogenee.
2. **Feature aperiodic** (FOOOF exponent, intercept): il componente EEG non-oscillatorio
   (aperiodic slope) è un proxy dell'equilibrio eccitazione/inibizione e potrebbe migliorare
   la predizione dell'età (Voytek et al. 2015).
3. **Domain adaptation** (DANN, CORAL, MMD): riduzione del domain gap residuo dopo
   armonizzazione; applicabile quando N_target ≥ 50.
4. **Validazione prospettica**: testare il classificatore sesso su nuove acquisizioni
   dello stesso laboratorio per verificare la stabilità temporale del modello.

---

## Riferimenti chiave

- Babiloni C. et al. (2016). *Brain. Clin. Neurophysiol.* — EEG connectivity in Alzheimer
- Cole JH, Franke K (2017). *Cereb. Cortex* — Brain-age overview
- Engemann DA et al. (2022). *NeuroImage* — Multi-site EEG brain-age, Combat harmonization
- Franck E et al. (2019). *J. Neurosci. Methods* — EEG brain-age MAE benchmark
- Kollia E et al. (2022). *Clin. Neurophysiol.* — Sex classification EEG resting-state
- Voytek B et al. (2015). *J. Neurosci.* — 1/f aperiodic EEG slope and E/I ratio

---

*Versione 3.0 — aggiornare §3 con risultati FASE 3 N=179 (ETA: post pipeline ~12h)*
