# Validity Report — Età e Sesso (FASE 1)

**Data**: 2026-05-28
**Branch**: main
**Coorte**: ds005385 N=50 (sub-whitelist: `config/subjects_whitelist_n50.py`)
**Positive-control**: EO vs EC BA=0.920 (effetto Berger, atteso)

---

## 1. Razionale Scientifico

### 1.1 Perché EO/EC non è una scoperta
EO vs EC classifica l'**effetto Berger** (1929): la soppressione dell'attività alpha all'apertura
degli occhi è neurofisiologia nota. BA=0.920 conferma che la pipeline funziona (positive-control),
non che abbia trovato un biomarcatore nuovo.

### 1.2 Target scientificamente rilevanti
- **Sesso biologico** (classificazione binaria): biomarcatore EEG riconosciuto in letteratura
  (Kollia et al. 2022: BA≈0.70-0.75 con resting-state EEG). Target a priori dichiarato.
- **Età** (regressione brain-age): modelli brain-age (Franck et al. 2019, Cole & Franke 2017)
  predicono l'età da EEG con MAE≈5-10 anni. Deviazione età-predetta/età-reale = brain-age gap.
  Target a priori dichiarato.

### 1.3 Anti-HARKing
I target età e sesso sono stati dichiarati a priori nel file
`.planning/core/PLAN_AGE_SEX_EXTENSION.md` (creato 2026-05-28, prima di qualsiasi run).

---

## 2. Metodi ML

### 2.1 Features
- FC flattened: atlas=aparc, metric=plv, banda=theta — (100 sample, 2278 feature)
- Riduzione dimensionale futura: graph-theory scalari (step 1.2) + aperiodic features (step 1.3)

### 2.2 Classificazione Sesso
- Algoritmi: LogisticRegression-L2 (class_weight='balanced'), RF, SVM-RBF
- CV: outer GroupKFold K=5, inner GridSearchCV GroupKFold K=3
- StandardScaler fit ONLY su train fold
- Metriche: balanced_accuracy (=(sens+spec)/2), AUC-ROC
- Permutation test: n_perm=200, shuffle y_sex → distribuzione null
- p-value = (#{null ≥ obs} + 1) / (n_perm + 1)

### 2.3 Regressione Età
- Algoritmi: ElasticNet (nested α,l1_ratio), SVR-RBF, RandomForestRegressor, Dummy(mean)
- CV: outer GroupKFold K=5, inner GridSearchCV GroupKFold K=3
- Metriche: MAE, R², bootstrap CI (n_boot=1000), brain-age gap
- Confronto vs dummy (mean predictor): deve battere dummy per R²>0
- Permutation test: n_perm=200, shuffle y_age → R²≈0

---

## 3. Risultati

### 3.1 Distribuzione fenotipica N=50
- **Età**: min=20, max=70, mean=43.1, std=15.5 (da participants.tsv)
- **Sesso**: F=32 (64%), M=18 (36%) — sbilanciato, gestito con class_weight='balanced'

### 3.2 Classificazione Sesso — Risultati
*N=50, X_aparc_plv_theta (2278 feature), permutation subject-level n_perm=50*

| Modello | BA (mean±std) | AUC | p-value (subj-perm) | Interpretazione |
|---------|---------------|-----|---------------------|-----------------|
| logreg  | 0.694 ± — | 0.814 | 0.0196 | ✅ significativo |

*Atteso da letteratura: BA≈0.65-0.75 (Kollia et al. 2022, N piccolo)*
*Shuffle null BA≈0.51 → no leakage confermato*

### 3.3 Regressione Età — Risultati
*N=50, X_aparc_plv_theta (2278 feature), bootstrap cluster subject-level n_boot=1000, permutation subject-level n_perm=50*

| Modello | MAE (anni) | MAE CI95 | R² | p-value (subj-perm) | Batte dummy? |
|---------|------------|----------|----|---------------------|--------------|
| RF      | 12.31 | [10.73, 13.94] | 0.185 | 0.0196 | ✅ sì |
| ElasticNet | 15.04 | — | -0.135 | 0.686 | ❌ no (non converge) |
| dummy   | 14.72 | — | ≈-0.05 | N/A | — |

*Atteso da letteratura: MAE≈8-12 anni con N>200 (Franck et al. 2019). N=50 → MAE più alto atteso.*
*y_age mean=43.1, std=15.5 → dummy MAE≈14.7 (mean predictor); RF batte di 16%*

### 3.4 Confronto Feature: Baseline (2278-dim) vs Graph-Theory (8-dim)
*FDR-BH su 4 test: sex × {baseline,GT} + age × {baseline,GT}*

| Confronto | Score | p_raw | p_fdr | Significativo? |
|-----------|-------|-------|-------|----------------|
| sex_baseline (2278-dim FC) | BA=0.694 | 0.0196 | 0.026 | ✅ |
| sex_GT (8 scalari GT) | BA=0.678 | 0.0196 | 0.026 | ✅ |
| age_baseline (2278-dim FC, RF) | R²=0.185 | 0.0196 | 0.026 | ✅ |
| age_GT (8 scalari GT) | R²=-0.072 | 0.118 | 0.118 | ❌ |

**Interpretazione**: le metriche graph-theory (8 scalari) catturano il segnale sesso (BA=0.678 ≈ baseline 0.694) ma non l'età (R²<0). Il sesso ha firma topologica globale; l'età richiede informazioni distribuite nella matrice FC completa.

---

## 4. Validità Scientifica

### 4.1 Anti-leakage checklist
- [x] GroupKFold a livello soggetto (stesso soggetto mai split tra train/test)
- [x] StandardScaler fit solo su train fold
- [x] Nested CV per selezione iperparametri
- [x] Shuffle test: BA(sesso shuffle)≈0.5, R²(età shuffle)≈0
- [x] Target dichiarati a priori (anti-HARKing)

### 4.2 Limitazioni dichiarate
- N=50: potere statistico basso; effetti piccoli non rilevabili con p<0.05
- p≫n: 2278 feature, 50 soggetti → regularizzazione obbligatoria
- Sorgenti su fsaverage (no MRI individuale) → distorsione stimata per soggetti individuali
- E/I ratio da aperiodic exponent (step 1.3) è *inferenza proxy*, non misura diretta
- Feature FC: PLV sensibile a volume conduction residuo (mitigato da aparc parcellazione)

### 4.3 Confronto letteratura
- **Brain-age EEG**: Franck et al. 2019 (MAE≈8-12 anni, N>200); Engemann et al. 2022
- **Sex classification EEG**: Kollia et al. 2022 (BA≈0.70-0.75, resting-state, N=100)
- **N=50 constraints**: power analysis: per BA=0.65 con α=0.05, 1-β=0.8 richiede N≈80 soggetti

---

## 5. Definition of Done FASE 1
- [ ] Tutti i test PASS
- [ ] ml_sex_results.json generato (inserire risultati nella tabella 3.2)
- [ ] ml_age_results.json generato (inserire risultati nella tabella 3.3)
- [ ] Step 1.6 (scala 50→100): in attesa di GO padre
- [ ] FASE 2 LEMON: bloccato su download operatore
