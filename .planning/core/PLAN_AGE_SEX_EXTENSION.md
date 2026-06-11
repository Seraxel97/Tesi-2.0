# PLAN — Estensione Età + Sesso (riformulazione scientifica Tesi_2.0)

> **Stato**: ATTIVO — avviato 2026-05-28. Owner: SL_father → orch-tesi.
> **Regola operativa**: ogni STEP si chiude solo con il suo **test gate** verde (pytest + ruff=0 + asserzione scientifica). Aggiornare la colonna Status di questo file a ogni STEP done. Documento durevole: NON cancellare, archiviare in `.planning/archive/` a milestone completata.

---

## 0. Razionale scientifico (perché cambiamo)

La pipeline attuale classifica **EO vs EC** (occhi aperti/chiusi). Problema: è l'effetto Berger — neurofisiologia nota dal 1929 → BA=0.92 è *atteso*, non una scoperta. Inoltre soffre di **p≫n** (2278 feature, 100 sample).

**Riformulazione**: EO/EC diventa **positive-control** (valida che la pipeline funzioni end-to-end), e si aggiungono due target scientificamente rilevanti, **già disponibili** in `participants.tsv`:

- **Età** → regressione (brain-age) + opz. young-vs-old.
- **Sesso** → classificazione binaria.

### Evidenza di apprendibilità (coorte N=50, verificata 2026-05-28)
- Età: min=20, max=70, mean=43.1, std=15.5. Bin: 20-35→21, 35-50→6, 50-65→22, 65+→1 (bimodale → young/old pulito).
- Sesso: F=32 / M=18 (64/36) → sbilanciato, gestire con `class_weight='balanced'` + balanced accuracy.
- Pool full (200 sub): età 20-70, sesso ~62/38 F/M.

---

## 1. Falle note da risolvere (da analisi 2026-05-28)

| ID | Falla | Gravità | Fix |
|----|-------|---------|-----|
| F-A | Target EO/EC banale (Berger) | 🔴 | rietichetta come positive-control + nuovi target |
| F-B | p≫n (2278 feat / 100 sample) | 🔴 | graph-theory features (2278→~8 scalari) + regolarizzazione |
| F-C | LOSO fold=2 sample → bootstrap su valori quantizzati {0,0.5,1} | 🟠 | bootstrap a livello predizione/soggetto, non sui fold-BA |
| F-D | `metadata.json` dice N=15, array N=50 | 🟠 | rigenera metadata coerente + test di consistenza |
| F-E | Subset N=50 su 200 non giustificato | 🟡 | documenta + scala incrementale 50→100→full |
| F-F | Sorgenti su fsaverage (no MRI indiv.) | 🟡 | dichiara limite in metodi |
| F-G | `p_perm=0.0` (va `p<1/n_perm`); `n_boot` incoerente (2000 vs 10000) | 🟡 | reporting fix |

---

## 2. Rigore matematico (definizioni di riferimento)

**Graph theory** su matrice di connettività `W` (grafo pesato G=(V,E)):
- Clustering coeff `C`, characteristic path length `L = mean(d_ij)`
- Global efficiency `E_glob = 1/(n(n-1)) · Σ_{i≠j} 1/d_ij`, local efficiency
- Modularità `Q` (Louvain), small-worldness `σ = (C/C_rand)/(L/L_rand)`
- Thresholding proporzionale (es. top-20% archi) per definire E. Output: ~8 scalari per (atlas,metric,band) → **riduce p≫n**.

**FOOOF** (proxy E/I, onesto): `PSD(f) = aperiodic(b − χ·log f) + Σ Gaussian_peaks`. Feature: esponente aperiodico `χ` (proxy E/I), offset `b`, picchi. **NB**: connettività ≠ eccitazione/inibizione → l'E/I è *inferenza*, dichiararlo.

**ML sesso**: balanced accuracy `=(sens+spec)/2`, AUC; logreg-L2 / RF / SVM; `class_weight='balanced'`.
**ML età**: MAE, R², bootstrap CI; ElasticNet / SVR / RF; confronto vs dummy (mean predictor); brain-age gap.

**Anti-leakage / anti-HARKing** (non negoziabili):
- Split SEMPRE a livello soggetto (`GroupKFold` su subject id).
- Scaler `fit` solo su train-fold; **nested CV** per iperparametri.
- Permutation test (shuffle label → deve crollare a chance).
- Correzione multipla **FDR-BH** su famiglie feature × modelli.
- Target dichiarato **a priori** (età+sesso) — documentato qui.

---

## 3. STEP-BY-STEP (ogni step = 1 commit atomico + test gate)

### FASE 0 — Consolidamento (base pulita)
| Step | Azione | Test gate | Status |
|------|--------|-----------|--------|
| 0.1 | Fix F-D: rigenera `metadata.json` coerente (N=50) | assert `meta.n_subjects == groups.unique` | ✅ |
| 0.2 | Fix F-G: reporting `p<1/n_perm`, `n_boot` unico (10000), helper | unit test su formatter p-value | ✅ |
| 0.3 | Rietichetta EO/EC come "positive-control" in doc+dashboard | smoke dashboard (no crash) | ✅ |

### FASE 1 — Target età+sesso su ds005385 (N=50, poi 100)
| Step | Azione | Test gate | Status |
|------|--------|-----------|--------|
| 1.1 | Modulo `labels_phenotype.py`: estrai `y_age` (float), `y_sex` (0/1) da participants.tsv, allineati a groups | no NaN, len==n_subjects, range sani | ✅ 602ba60 |
| 1.2 | Modulo `features/graph_theory.py`: C,L,E_glob,E_loc,Q,σ,degree,strength per (atlas,metric,band) | valori in range validi, no NaN, dim ridotta | ✅ 626e203 |
| 1.3 | Modulo `features/aperiodic_fooof.py`: χ, offset, band-power, entropia spettrale | fit success rate >90%, no NaN | ✅ 899a937 |
| 1.4 | ML sesso: nested GroupKFold, logreg-L2/RF/SVM, balanced-acc+AUC, permutation | shuffle-label → BA≈0.5 (leakage check) | ✅ 68de4f1 |
| 1.5 | ML età: nested GroupKFold, ElasticNet/SVR/RF, MAE/R²+bootstrap CI, permutation, vs dummy | batte dummy; shuffle → R²≈0 | ✅ 9a43f3e |
| 1.6 | Scala ds005385 50→100: reprocess 50 sub (STEP 1-5) | feature shape ok, 0 sub falliti, ri-run ML | ✅ 6fbdd58 / 96b1d60 |
| 1.7 | Dashboard: selettore target (EO/EC | sesso | età) + viste risultati | pilot.click su nuovi controlli | ✅ f64aa66 |
| 1.8 | Report validità: risultati onesti + effect size + confronto letteratura | doc + tutti i test PASS | ✅ e2f2fdb |

### FASE 2 — Replica cross-dataset (sub-LEMON o alternativa piccola)

> **Decisione 2026-05-29 (operatore Samuele)**: LEMON full 200GB multimodale = NO.
> Strategia: scaricare SOLO porzione **EEG-BIDS** di LEMON, sotto-campione di ~50-100 sub
> (paragone diretto a N=100 ds005385 già completato). Obiettivo della FASE 2:
> *generalizzazione cross-dataset*, non scala. N piccolo è sufficiente per il test.
> Alternativa di fallback se LEMON resta inaccessibile: dataset EEG-BIDS pubblico
> più leggero (es. `ds004504`, `ds003490`, EEGBCI MNE) con sex+age in `participants.tsv`.

| Step | Azione | Test gate | Status |
|------|--------|-----------|--------|
| 2.0 | **GATE**: operatore scarica sotto-set EEG-BIDS LEMON (~50-100 sub, no MRI/fMRI/PET) **oppure** sceglie dataset alternativo piccolo con `age`+`sex` in participants.tsv | path valido + N≥50 + verify `age`/`sex` columns | ⬜ BLOCKED-LITE |
| 2.1 | STEP 1-5 su dataset cross (50-100 sub) | feature shape ok | ⬜ |
| 2.2 | young-vs-old (se 2 coorti) + età/sesso | come 1.4/1.5 | ⬜ |
| 2.3 | **Replica cross-dataset**: train ds005385 → test cross (e viceversa) | generalizzazione documentata | ⬜ |

### FASE 3 — Scala ds005385 N=100 → N=179 full local
> ds005385 full (179 valid scaricati localmente); source-space connectivity +
> leakage-correction (ortogonalizzazione Colclough); eLORETA vs dSPM; task-decoding
> solo con dataset task.

| Step | Azione | Test gate | Status |
|------|--------|-----------|--------|
| 3.1 | Whitelist N=179 deterministica (hard-rule N=100 ⊂ N=179, `late_ses1==0`, sub scaricati) + estensione `run_pipeline_n30.py --n-subjects 179` | `len(SUBJECT_WHITELIST_N179)==179`, assert N100⊂N179, smoke import | ✅ 2026-05-29 |
| 3.2 | Lancio pipeline ds005385 N=179 (STEP 2→2b→3b→4b→5→6+7, 79 sub nuovi) | HB live, no abort disk, X shape (179,2,2278), 0 sub falliti | ⬜ |
| 3.3 | ML età+sesso su N=179 (GT 8-dim + baseline 2278-dim), permutation+bootstrap | confronta vs N=100: ΔBA, ΔMAE, FDR-BH stabile | ⬜ |
| 3.4 | Report AGE_SEX_VALIDITY_N179 + aggiornamento dashboard | doc + pilot smoke | ⬜ |
| 3.5 | (opzionale) Leakage-correction Colclough source-space + eLORETA vs dSPM | confronto metriche, decisione caso-per-caso | ⬜ |

---

## 4. Definition of Done (milestone)
- Tutti i test PASS, ruff=0, commit atomici, no `--no-verify`, no mock.
- Età: MAE < std baseline (batte dummy), R²>0 significativo (permutation p<0.05).
- Sesso: balanced-acc > 0.5 significativo (permutation p<0.05).
- EO/EC positive-control ancora verde.
- Report `reports/AGE_SEX_VALIDITY.md` + aggiornato `STATISTICAL_VALIDITY_NOTES.md`.

---

## 5. Log avanzamento
- 2026-05-28: piano creato (SL_father). Fenotipo N=50 verificato (età 20-70, sesso 64/36). Dispatch FASE 0 → orch-tesi.
- 2026-05-28 sera: orch-tesi avvia FASE 1. Step 1.1-1.4 completati (602ba60,626e203,899a937,68de4f1). Step 1.5 in corso (haiku1). STOP a 1.6 in attesa GO padre.
- 2026-05-29: FASE 1 chiusa. Step 1.5→1.8 completi (9a43f3e, 6fbdd58, f64aa66, e2f2fdb). Risultati N=100: sex_GT BA=0.713 p=0.020 sig; age_GT MAE=12.52 R²=0.097 modesto. Fix matematici subject-level (permutation 5bdb6bb, bootstrap 93a9dfc, GT abs(W) 7f896cd, RF age 606d5e7). Report `reports/AGE_SEX_VALIDITY.md` narrativa onesta (sesso forte, età modesta).
- 2026-05-29: decisione operatore — FASE 2 LEMON full 200GB NO. Strategia: sub-set EEG-BIDS ~50-100 sub o dataset alternativo piccolo per cross-replica.
- 2026-05-29: FASE 3 step 3.1 setup. Whitelist N=179 deterministica creata (`config/subjects_whitelist_n179.py`, hard-rule N100⊂N179, late_ses1==0, sub scaricati). Esteso `run_pipeline_n30.py --n-subjects 179`. Smoke import OK. Pronto per step 3.2 (lancio pipeline, 79 sub nuovi).
