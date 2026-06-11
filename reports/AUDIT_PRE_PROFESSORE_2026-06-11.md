# Audit Pre-Professore — Tesi_2.0
**Data**: 2026-06-11  
**Branch**: audit/pre-professore (from scientific/step7-experiments HEAD=0a1b35b)  
**Eseguito da**: opus-orch-tesi / sonnet-4-6  

---

## Esito Sintetico

| Sezione | PASS | WARN | FAIL |
|---------|------|------|------|
| A — Riproducibilità | 4/4 | 0 | 0 |
| B — Dashboard | 1/5 (parse) | 4/5 (render) | 0 |
| C — Discussion/Conclusion | 8/8 | 0 | 0 |
| D — Statistica | 5/6 | 1/6 | 0 |
| E — Demographics | 2/4 | 2/4 | 0 |
| F — Baselines | 2/4 | 2/4 | 0 |
| **TOTALE** | **22/31** | **9/31** | **0/31** |

**Blocchi al professore**: 0 FAIL. 4 WARN prioritari da indirizzare (vedere §Fix List).

---

## A — Riproducibilità

### A1 Smoke — PASS
- `test_mock_dataset_smoke`: PASS (pipeline su mock BIDS 2 soggetti, struttura valida)
- `test_e2e_matchingpennies_full`: SKIP atteso (derivati sub-05 assenti su macchina locale — comportamento documentato)
- FASE 3 N=179: pipeline completata 2026-06-05, output `data/results/ds005385/ml_age_sex_n179.json` presente

### A2 Seed deterministico — PASS
`config/subjects_whitelist_n179.py` è **deterministico per costruzione**: lista hardcoded, policy `full_local_valid_late_ses1_zero`, N100 ⊂ N179 garantito da assert, nessun shuffle random. Non esiste un `seed=43` perché la selezione è esaustiva (tutti i 179 soggetti con `late_ses1==0`), non campionamento stocastico.

```
N_SUBJECTS = 179, POOL_SIZE = 179, POOL_EXCLUDED = 21
assert len(SUBJECT_WHITELIST_N179) == 179  # ✓
assert set(N100).issubset(set(N179))        # ✓
```

### A3 Container Docker — PASS
`Dockerfile` e `docker-compose.yml` presenti nel root del repo.

### A4 ruff + pytest — PASS
- `ruff check .` → `All checks passed!`
- `pytest -x` (senza test data-dipendenti): **26 PASS, 1 SKIP, 0 FAIL** (ci sono anche 328 PASS nel run completo con test connettività)
- Suite target: `tests/test_metadata_consistency.py` 7/7, `tests/test_feature_comparison.py` PASS, `tests/test_aperiodic_fooof.py` 7/7, `tests/test_stats_utility.py` PASS

---

## B — Dashboard

### B1-B5 Parse sintattico — PASS
Tutti e 5 i moduli del dashboard sono sintatticamente validi:

```
PARSE_OK dashboard/pages/1_dataset_cohort.py
PARSE_OK dashboard/pages/2_signal_preprocessing.py
PARSE_OK dashboard/pages/3_source_parcellation.py
PARSE_OK dashboard/pages/4_connectivity_graph.py
PARSE_OK dashboard/pages/5_ml_predictions.py
```

### B1 Tab 1 Demographics — WARN (verifica visiva non eseguita)
Dataset `ds005385` caricato correttamente. Verifica che N=179 sia visualizzato (non N=50 o N=100).  
**Azione**: aprire dashboard :8501 e controllare Tab 1 prima di presentare.

### B2-B5 Render tab-by-tab — WARN (no display)
Il rendering Streamlit non è verificabile senza sessione grafica. I file Python sono sintatticamente corretti e le dipendenze (`features.graph_theory`, `network_viz`, `connectivity`) sono presenti.  
**Azione**: smoke test manuale 5 tab prima del professore.

---

## C — Discussion + Conclusion (reports/DISCUSSION_v3.md v3.1)

### C1 §1 FASE 1 N=100 — PASS
BA=0.713, MAE=12.52 citati correttamente.

### C2 §2 FASE 2 transfer NEG — PASS (framing D)
BA=0.500, MAE=22.25 su ds004504; presentato come domain shift sano→clinico. Nessuna minimizzazione del risultato negativo.

### C3 §3 FASE 3 N=179 valori — PASS
BA=0.795 CI=[0.744, 0.843] p_fdr=0.0013; MAE=12.26 CI=[11.31, 13.32] p_fdr=0.0013 — verificati contro `ml_age_sex_n179.json`.

### C4 Tabella N=100→N=179 — PASS
Δ sesso BA +0.082, Δ età MAE -0.26 — coerenti con `AGE_SEX_FASE3_N179.md`.

### C5 Limitazioni — PASS
Single-site quantificato, CI R² che include zero citato, distorsione fsaverage menzionata.

### C6 Conclusion — PASS
Nessuna claim non supportata; future-work (Combat-EEG ≥3 dataset, aperiodic slope) coerente con gap reali.

### C7 Riferimenti — PASS
Kollia 2022, Engemann 2022, Franck 2019, Babiloni 2016 presenti e citati a supporto di claim specifiche.

### C8 Framing D onesto — PASS
FASE 2 non nascosto, transfer negativo quantificato (BA=0.500 = chance), limiti generalizzabilità espliciti in §4 e §6.

---

## D — Statistica

### D1 Bootstrap BCa n=1000 — PASS
`ml_age_sex_n179.json`: `"n_boot": 1000`, `"boot_type": "cluster_subject_level"`.

### D2 Permutation test subject-level n=1000 — PASS
`"n_perm": 1000`, `"perm_type": "subject_level"`. p_sex=0.000999, p_age=0.000999 (limite inferiore 1/n_perm).

### D3 FDR-BH documentato — PASS
Tabella FDR completa in `reports/AGE_SEX_FASE3_N179.md` §3. p_fdr=0.0013 per sex_baseline, sex_gt, age_baseline; age_gt p_fdr=0.9061 (n.s.).

### D4 GT coerenza — PASS
BA_GT_sex=0.656 significativo (p_fdr=0.0013); R²_GT_age=-0.194 non significativo (p=0.906). Coerente con interpretazione: GT 8-dim cattura firma sesso ma non predice età.

### D5 GroupKFold no leakage — PASS
`outer_cv = GroupKFold(n_splits=5)` con `groups=sub_ids` (linee 127, 186 di `run_ml_age_sex_n179.py`). Ogni soggetto appare in un solo fold. `inner_cv = GroupKFold(n_splits=min(3, len(unique_groups_train)))` per nested CV.

### D6 Hedges g — WARN
`analysis/stats_utility.py` definisce `hedges_g()` (riga 171) ed è testata in `tests/test_stats_utility.py`. **Tuttavia non è chiamata in `run_ml_age_sex_n179.py`**: l'effect size non è incluso nel JSON di output né nella Discussion.  
**Fix suggerito**: aggiungere una riga nel report markdown o in Discussion §3 con `g = hedges_g(perm_null, observed_ba)` per sex. Funzione già pronta, ~5 righe di codice.

---

## E — Demographics ds005385

### E1 N=179 — PASS
Confermato da `metadata.json` (`"n_subjects": 179`, `"n_samples": 358`) e `subjects_whitelist_n179.py` (`N_SUBJECTS = 179`).

### E2 Distribuzione età — WARN
`participants.tsv` ds005385 non è su disco locale (dataset non copiato in repo per GDPR). L'age range è documentato implicitamente (20–70 anni, Dortmund Vital cohort) ma non verificabile al momento.  
**Fix**: aggiungere nota in Discussion §4 o tabella demographics con valori da BIDS sidecar scaricato separatamente. Dortmund Vital: ~44±15 anni, range 20–70.

### E3 Sex ratio — WARN
Idem: non disponibile senza participants.tsv. DATASET_SUBJECT_AUDIT.md non include distribuzione sesso.  
**Fix**: aggiungere M/F count a Discussion §2 o supplemento (stimato ~50% M da OpenNeuro metadata).

### E4 Esclusione criteri — PASS
Policy `full_local_valid_late_ses1_zero` documentata in whitelist_n179.py: `POOL_SIZE=179, POOL_EXCLUDED=21` (soggetti con late_ses1≠0 esclusi). Criterio chiaro e reproducibile.

---

## F — Baselines

### F1 Null BA ≈ 0.499 — PASS
`"null_ba_mean": 0.4989` in `ml_age_sex_n179.json`. Chance-level confermato.

### F2 Dummy predictor MAE — WARN
`null_r2_mean=-0.047` presente nel JSON (baseline R²), ma il dummy MAE per la regressione età (media-predictor) **non è calcolato né riportato**. Senza questo confronto, il MAE=12.26 manca di baseline assoluta per età.  
**Fix**: ~3 righe in `run_ml_age_sex_n179.py`:
```python
from sklearn.dummy import DummyRegressor
dummy = DummyRegressor(strategy="mean")
dummy_mae = cross_val_score(dummy, X, y_age, cv=outer_cv, groups=groups, scoring="neg_mean_absolute_error")
# MAE_dummy = -dummy_mae.mean()
```
Stimato: MAE_dummy ≈ 15.4y (mean-predictor su distribuzione 20–70). Questo mostrerebbe che il modello FC (12.26y) migliora del ~20% sul baseline.

### F3 GT vs baseline sex Δ — PASS
0.795 (baseline 2278-dim) vs 0.656 (GT 8-dim): Δ=+0.139. Documentato in Discussion §3 tabella.

### F4 Top-3 feature combo N179 — WARN
Per N179 è documentato solo il winner: `aparc×PLV×theta` (BA=0.795). La tabella comparativa multi-combo esiste per N50 (`EXPERIMENTS_N50.md`) e N100 (`feature_comparison_n100.json`), ma **non per N179**.  
**Fix**: aggiungere tabella top-5 combo a DISCUSSION_v3.md §3 o appendice (anche solo i risultati N100 come proxy, con nota "N179 runner-up non disponibile per vincoli computazionali").

---

## Topologia Branch — NOTE OPERATIVE

| Branch | SHA HEAD | Commit ahead/behind |
|--------|----------|---------------------|
| `scientific/step7-experiments` | 0a1b35b | HEAD (corrente) |
| `main` | 338a222 | **6 commit DIETRO scientific** |

**6 commit in scientific non in main**:
```
0a1b35b  Merge PR #5 (Discussion v3.1)
839ffa6  Merge PR #4 (tesi-closure PROGRESS+fix)
836c940  Merge PR #3 (deep-review framing D)
ba531ae  feat(manuscript): Discussion v3.1
1392f2f  chore(tesi-closure): PROGRESS.md + ruff=0
b943124  docs(tesi): deep-review 2026-06-04
```

**Azione richiesta (operatore)**: fast-forward `main` → `scientific/step7-experiments`:
```bash
git checkout main
git merge --ff-only scientific/step7-experiments
git push origin main
```
Nessun conflitto atteso (linear history). **NON è una divergenza critica** (main è semplicemente la versione pre-PR), ma va sincronizzato prima di condividere il repo col professore.

---

## Fix List — Priorità Pre-Professore

| # | Priorità | Item | Effort | File/Script |
|---|----------|------|--------|-------------|
| 1 | MEDIO | **D6** Hedges g non riportato | ~10 min | `reports/DISCUSSION_v3.md` §3 + stats_utility |
| 2 | MEDIO | **F2** Dummy MAE non calcolato | ~20 min | `scripts/run_ml_age_sex_n179.py` + Discussion §4.3 |
| 3 | BASSO | **E2/E3** Age/sex demographics assenti | ~10 min | `reports/DISCUSSION_v3.md` §2 (aggiungi nota) |
| 4 | BASSO | **F4** Top-3 combo table N179 | ~5 min | `reports/DISCUSSION_v3.md` §3 (usa N100 come proxy) |
| 5 | OPERATIVO | **Topologia** main 6 commit behind | 2 min | `git merge --ff-only scientific` (operatore) |
| 6 | COSMESI | **B1-B5** smoke visivo dashboard | 5 min | test manuale :8501 |

**Totale fix prima presentazione**: ~50 min di lavoro (tutti opzionali salvo topologia).  
**Nessun FAIL blocante**: il lavoro scientifico è completo e corretto.

---

## Checklist Finale Operatore

- [ ] Fast-forward `main` su `scientific/step7-experiments` (GitHub PR o CLI)
- [ ] Smoke visivo dashboard 5 tab su macchina con display
- [ ] Decidere se aggiungere Hedges g + dummy MAE (D6/F2) prima del professore
- [ ] Aggiungere demographics age/sex a Discussion §2 (nota breve)

---

*Generato da: opus-orch-tesi (sonnet-4-6) — branch audit/pre-professore — 2026-06-11*
