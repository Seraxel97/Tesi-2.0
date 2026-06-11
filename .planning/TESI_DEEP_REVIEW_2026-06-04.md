# Tesi_2.0 Deep-Review — Decisione Metodologica FASE 2/3

**Data**: 2026-06-04
**Autore**: orch-tesi (Opus, sessione tmux dedicata)
**Operatore**: Samuele
**Scope**: analisi scientifica + raccomandazione metodologica (NO auto-fix codice scientifico)
**Branch**: `seraxel/tesi-deep-review-2026-06-04`
**Pattern NM-confermato**: deep-review Tesi = decisione operatore, non auto-execution

---

## Executive summary research

Lo stato del progetto è più solido di quanto la narrativa "stallata" lasci intendere. FASE 1 è chiusa con un risultato onesto e metodologicamente difendibile (sesso BA=0.713 in linea con Kollia 2022, età modesta ma significativa); FASE 2 LEMON NON è stallata — è **completata** 2026-06-04 con un esito NEGATIVO scientificamente legittimo (BA_sex=0.500, MAE_age=22.25 in transfer ds005385→ds004504), già integrato in dashboard tab 6; FASE 3 N=179 ha solo lo step di setup committato (3.1) e la pipeline lunga è da lanciare. Il transfer negativo NON è un fallimento architetturale: è la diretta conseguenza di un domain shift catastrofico (sani 20-70 vs Alzheimer+ctrl 49-79, single-center, lab effect). **La raccomandazione è D (pivot framing) accoppiata a un lancio operativo di FASE 3 N=179 in-dataset** — la combinazione massimizza il segnale scientifico recuperabile entro l'orizzonte tesi, evita over-engineering metodologico (B) e dataset-grinding (C), e trasforma il transfer negativo da "buco" in un finding pubblicabile.

---

## Stato FASE 1 — honest interpretation

| Target | Modello | N=100 | p-value | CI95 | Confronto letteratura | Verdetto |
|---|---|---|---|---|---|---|
| Sesso | LogReg-L2 (2278-dim PLV-theta-aparc) | BA=**0.713** | 0.020 | (implicito da perm) | Kollia 2022 EEG-RS: 0.70-0.75 | ✅ in linea, generalizzabile in popolazione comparabile |
| Sesso | LogReg-L2 (8-dim graph-theory) | BA=**0.706** | 0.026 (FDR-BH) | — | n/a | ✅ firma topologica globale interpretabile |
| Età | RandomForest (2278-dim PLV-theta-aparc) | MAE=**12.52** R²=**0.097** | 0.020 | MAE [11.29, 13.81] | Franck 2019: 8-12 MAE con N>200 | ⚠️ modesto: vantaggio su dummy = 1.13 anni |
| Età | RandomForest (8-dim GT) | R²=**-0.222** | 0.863 (FDR-BH) | — | n/a | ❌ ns: età non catturabile da scalari globali GT |

**Rigore statistico (verificato `reports/AGE_SEX_VALIDITY.md`)**:
- Outer GroupKFold K=5 subject-level (no inter-subject leakage)
- Inner nested CV GridSearch C ∈ [0.01..100] (commit `25cad1c` Statistical Hardening)
- Permutation **subject-level** n_perm=50 (broadcast via groups) — fix `5bdb6bb`
- Bootstrap CI **cluster subject-level** n_boot=1000 — fix `93a9dfc`
- GT threshold `abs(W)` + clustering unweighted per coerenza σ — fix `7f896cd`
- StandardScaler fit solo su train fold (`ml_dispatcher`)
- FDR-BH su 4 confronti GT-vs-baseline
- Target età+sesso dichiarati a-priori in `.planning/core/PLAN_AGE_SEX_EXTENSION.md` (anti-HARKing)

**Limitazioni dichiarate (`AGE_SEX_VALIDITY.md` §4.2)**:
- N=100 single-center → potere statistico moderato
- p≫n (2278 feature / 100 sample) → regolarizzazione obbligatoria (RF > ElasticNet su età)
- Sorgenti su `fsaverage` (no MRI individuale) → distorsione stimata per soggetto
- E/I ratio da aperiodic exponent = inferenza proxy, non misura diretta
- PLV residuamente sensibile a volume conduction (mitigato da parcellazione)
- `schaefer100` X incompleto per N=100 (80/100 soggetti) → usato solo `aparc`

**Interpretazione onesta**:
- **Sesso**: risultato **robusto e generalizzabile in popolazione equivalente** (sani, range età 20-70). La firma topologica globale (8-dim GT) raggiunge prestazioni equivalenti alla baseline FC dense — informazione **scientificamente interpretabile** e adatta a Discussion.
- **Età**: il calo R² da N=50 (0.185) a N=100 (0.097) è **meccanico, non un fallimento**: std età 15.5→15.0 riduce la varianza totale; MAE rimane stabile. Il vantaggio assoluto su Dummy scende 2.41→1.13 anni. **Non usare R²=0.185 come headline**; usare N=100 R²=0.097. Brain-age da sola connettività FC è notoriamente debole — feature aperiodic (FOOOF) o graph-theory per banda servono per rilanciare.

**Honest assessment**: FASE 1 è chiusa correttamente. Nessuna over-claim, fix matematici tutti applicati e committati, target a-priori, replicazione su N=50 e N=100 coerente. Pronta per Discussion/Conclusion.

---

## Stato FASE 2 — root cause "stallo" + restartability

**Premessa**: il SYNC indicava "FASE 2 sub-LEMON stallata 29/05". Verifica empirica contraddice questa narrativa:

| Evento | Data | Commit | Status |
|---|---|---|---|
| Decisione operatore: LEMON full 200GB → no, usare sub-LEMON o ds004504 | 2026-05-29 | (memo) | OK |
| Step 2.0 BLOCCO download EEG-BIDS (OpenNeuro no LEMON-EEG, EEGBCI no age/sex) | 2026-06-04 | `bc40d26` | risolto pivot |
| Pivot a ds004504 (49 sub Alzheimer+ctrl, age+sex disponibili) | 2026-06-04 | `c1cda5f` | OK |
| Step 2.1 adapter pipeline ds004504 + phenotype loader | 2026-06-04 | `22119df` | DONE |
| Step 2.2 source recon + parcellation ds004504 N=49 | 2026-06-04 | `5850a50` | DONE |
| Step 2.3 FC features ds004504 N=49 (aparc × 4 metric × 4 band) | 2026-06-04 | `75656e7` | DONE |
| Step 2.4 cross-dataset transfer ML | 2026-06-04 | `285dd93` | DONE — risultato NEG |
| Dashboard tab 6 cross-dataset integrato | 2026-06-04 | `c424a60` | DONE |
| Night-closure queue sync post FASE 2 | 2026-06-04 | `f08f889` | DONE |

**HB worker LEMON squad (verificato `heartbeats_tesi/`)**:
- `sonnet-orch-tesi-lemon`: status `FULLY_CLOSED` 06:00, "dashboard tab 6 cross-dataset integrato — FASE 2 + dashboard COMPLETE"
- `haiku-tesi-lemon-1`: status `idle_waiting_operator`, "FASE 2 LEMON complete — all steps 2.0..2.4 done"
- `sonnet-tesi-dashboard`: status `complete`, "DONE — 6 tab complete, LEMON integrato"

**Root cause "stallo"**: confusione narrativa nel SYNC. NON è uno stallo metodologico, è una **chiusura squad legittima in attesa di decisione operatore sul prossimo target**. Nessun tmux morto, nessun bug, nessun blocker tecnico. La squad LEMON è in **HOLD volontario** post-completamento step 2.0-2.4, in attesa di GO operatore per step 2.5+ (che non esiste ancora finché non si decide A/B/C/D).

**Restartability**: 100%. Squad re-spawnable in minuti; nessun lavoro perso; dashboard e report già committati e push'ati. Il "problema" è metodologico (cosa fare con il transfer NEG), non operativo.

---

## Cross-dataset transfer — findings vs failure

**Dati `reports/CROSS_DATASET_TRANSFER.md`**:

| Task | Metrica | Transfer ds005385→ds004504 | In-dataset ds005385 (5-fold CV) | Gap |
|---|---|---|---|---|
| Sesso | BA | **0.500** (chance) | 0.741 | -0.241 |
| Età | MAE (anni) | **22.25** | 12.52 | +9.73 |

**Setup train/test (verificato)**:
- Train: ds005385 N=200 osservazioni (N=100 soggetti, sani 20-70aa)
- Test: ds004504 N=49 osservazioni (N=49 soggetti, Alzheimer+controlli 49-79aa)
- Feature: `X_aparc_plv_theta` (winner FASE 1)
- Scaler fit solo su train → no data leakage
- Stesso pipeline (no re-train su ds004504)

**È un FINDING legittimo o un FAILURE architetturale?**

→ **FINDING LEGITTIMO**, su tre evidenze convergenti:

1. **Domain shift catastrofico e prevedibile**: popolazioni semanticamente diverse.
   - ds005385: sani 20-70, range età 50 anni, σ=15
   - ds004504: Alzheimer + ctrl 49-79, range età 30 anni shifted-up, σ=8-10
   - Patologia (Alzheimer) altera profondamente la connettività EEG (Babiloni et al. 2016, Dauwels 2010): la firma "sesso" del cervello sano è confusa dal rumore patologico.
2. **Lab effect non corretto**: hardware EEG, montaggio, protocollo (eyes-open/closed mix) sono diversi tra dataset. Senza harmonization (Combat-EEG, MNE-bids resampling) il transfer naïve atteso ≈ chance.
3. **No domain adaptation tentata**: scaler fit-only-on-train è il MINIMO; nessun DANN/CORAL/MMD applicato. È un transfer **zero-shot puro**, baseline metodologica per quantificare il gap, non un tentativo serio di generalizzazione.

**Failure architetturale** richiederebbe: pipeline non riproducibile cross-dataset (smentito da step 2.2-2.4 che girano `aparc × plv × theta` identico), bug nel feature extractor (smentito da feature_comparison_n100 robusta), o classifier brittle (smentito da CI in-dataset). Nessuno di questi è il caso.

**Conclusione metodologica**: il transfer negativo è **dataset-specificity dichiarato e quantificato** — esito scientificamente prezioso per la Discussion (limitazione di brain-age FC-only su cohort eterogenee) ma NON un proof-of-failure della pipeline.

---

## Stato FASE 3 — readiness N=179

**Commits identificati**:
- `da60e70` 2026-05-29: FASE 3 step 3.1 — whitelist N=179 + pipeline `--n-subjects 179`

**Setup verificato (dal memo `project_tesi2_age_sex_reframing.md`)**:
- `config/subjects_whitelist_n179.py`: deterministico seed=43, hard-rule N=100 ⊂ N=179, `late_ses1==0`, sub scaricati, `len=179`, `new_79=79`
- `scripts/run_pipeline_n30.py --n-subjects 179`: smoke import OK
- Comando pronto: `cd ~/Scrivania/Tesi_2.0 && conda activate base && python3 scripts/run_pipeline_n30.py --n-subjects 179`

**Step rimanenti**:
- 3.2: lancio pipeline N=179 sui 79 sub nuovi (fwd+inv+stcs+cleanup+FC su aparc × 4 metric × 4 band)
- 3.3: aggregate features X matrices N=179
- 3.4: ML LOSO-179 con n_perm≥500
- 3.5: report `EXPERIMENTS_N179.md` + amend `AGE_SEX_VALIDITY.md`

**Bottleneck**: il lancio 3.2 è long-running. Stima estrapolata da H-SCALE-N50 (451 min su N=50 aparc, 32 combo, 3 clf, n_perm=500):
- N=179 ha ~3.6× il numero di soggetti → costo source-recon+FC scala lineare in N
- ML LOSO scala come N² (più fold + più sample per fold), ma feature dim resta 2278 (aparc) → LogReg veloce
- **Stima realistica**: ~12-15h CPU per pipeline completa, dominata da source recon+FC dei 79 nuovi sub.
- Mitigabile con tmux dedicato + HB monitoring; nessun blocker tecnico, solo wallclock.

**Beneficio scientifico atteso N=179 vs N=100**:
- Riduzione CI sesso da ~[0.62, 0.81] a ~[0.66, 0.78] (stima √(N1/N2)·width)
- Aumento potenza per età (R² più stabile, possibile R²>0.15)
- Validazione robustezza GT 8-dim su N maggiore
- Compliance con range letteratura Kollia 2022 (N=100) e Engemann 2022 (N>200 per brain-age)

---

## Decisione next: A/B/C/D valutate scientificamente con score

Scoring 1-5 su 5 assi:
- **SR** (Scientific Rigor): solidità metodologica del finding generato
- **F** (Feasibility): fattibilità entro orizzonte tesi (mesi residui)
- **TI** (Thesis Impact): impatto sulla narrativa Discussion/Conclusion
- **R** (Risk): rischio (basso=5, alto=1) di null result o blocker tecnici
- **C** (Cost): costo opposto effort (basso=5, alto=1)

| Opzione | SR | F | TI | R | C | **Total** |
|---|---|---|---|---|---|---|
| **A** Subgroup ds004504 controls-only | 2 | 4 | 2 | 2 | 4 | **14/25** |
| **B** Domain adaptation (DANN/CORAL/MMD) | 3 | 2 | 3 | 1 | 1 | **10/25** |
| **C** 3rd dataset aggiuntivo | 4 | 1 | 4 | 2 | 1 | **12/25** |
| **D** Pivot thesis to cross-dataset limitation | 5 | 5 | 4 | 5 | 5 | **24/25** |

### A — Subgroup ds004504 controls-only

**Razionale**: ds004504 contiene controlli sani (non-Alzheimer) e Alzheimer. Isolare i controlli omogenizza la popolazione (rimuove confound patologia) e permette transfer sani→sani.

**Pro**:
- Riduce un confound (patologia)
- Pipeline già pronta (step 2.2-2.4 girano identico su subset)
- Effort minimo (~2-4h: filter participants.tsv su dx="control", re-run ML)

**Contro CRITICI**:
- ds004504 controlli stimati ~17-22 sub (a verifica `participants.tsv`); LOSO-17 produce CI larghissimi e potenza ~0.4
- Resta il **range età shift** (49-79 ctrl vs 20-70 train) — il problema non è solo patologia
- Resta il **lab effect** (hardware/protocollo diversi)
- Risultato atteso: BA_sex 0.55-0.65, MAE_age 18-20 — meglio di chance ma **non sufficiente per claim di generalizzazione**
- N piccolo viola implicitamente la regola "complessità ∝ N" → ulteriore p≫n

**Quando ha senso**: come *exploratory secondary analysis* in appendice, non come primary FASE 2.

### B — Domain adaptation (DANN / CORAL / MMD)

**Razionale**: state-of-art transfer learning per allineare distribuzioni source/target nel feature space.

**Pro**:
- SOTA metodologico, citabile (Ganin 2016, Sun 2016, Long 2015)
- Quantifica il "domain gap" residuo dopo correzione

**Contro CRITICI**:
- **N target piccolo**: DANN richiede tipicamente N_target ≥ 100; ds004504 ha 49 → over-fitting domain critic quasi certo
- **DL component**: DANN è una rete neurale; viola vincolo operatore "NO deep learning" (PROGRESS.md §"Vincoli operatore #3")
- CORAL/MMD su 2278-dim require centering matrices instabili con N=49
- **Altri confounders non gestiti**: età-shift + patologia + lab → DA risolve uno (covariate shift) ma non gli altri (concept shift)
- Effort: 2-4 settimane di implementazione + tuning + ablation
- Risk: null result probabile (gap troppo profondo)

**Quando ha senso**: future work in articolo separato post-tesi.

### C — 3rd dataset aggiuntivo

**Razionale**: aggiungere un dataset più simile a ds005385 (sani, range età comparabile) per testare replicabilità.

**Candidati possibili**: PEERS (Healthy Brain Network), TUH EEG corpus subset sani, BCI Competition IV, MPI-LEMON (subset EEG-only se downloadable).

**Pro**:
- Genera evidence cross-dataset legittima (se transfer funziona)
- Robusta per claim di generalizzazione

**Contro CRITICI**:
- **Tempo**: download + BIDS conversion + harmonization + pipeline run = 3-6 settimane minimo
- **Harmonization complessa**: sampling rate, riferimento, montaggio, protocollo eyes-open/closed → richiede pre-processing custom per ciascuno
- ETA tesi: probabilmente non compatibile con discussione
- **Rischio gate**: come è successo con LEMON download (step 2.0 bloccato), un nuovo dataset può rivelarsi inaccessibile o non-BIDS
- Diverge da focus: la tesi è già scritta su ds005385

**Quando ha senso**: estensione post-tesi per pubblicazione, NON nel timeline corrente.

### D — Pivot thesis to "cross-dataset limitation as primary finding"

**Razionale**: il risultato transfer negativo non è un buco da riempire — è **un finding scientifico in sé**. Riformulare la narrativa Discussion attorno a:
1. EEG-FC features (PLV-theta) generalizzano **dentro** una popolazione omogenea (sex BA=0.713 su sani ds005385)
2. **Non generalizzano cross-cohort** quando il target dataset differisce per patologia, range età, lab → quantificato (BA crolla a chance)
3. Questo è **coerente con letteratura**: brain-age FC-only è instabile cross-site senza harmonization (Engemann 2022 raccomanda ≥3 dataset + Combat); sex EEG cross-cohort è ancora un open problem (Kollia 2022 lavora intra-cohort)
4. **Implicazione metodologica per il campo**: serve harmonization esplicita + multi-site CV + N≥200 per claim cross-dataset.

**Pro**:
- **Onestà scientifica massima**: riconosce il finding come legittimo invece di nasconderlo
- **Pubblicabile come limitation-driven contribution** (Nature Methods, NeuroImage)
- Zero effort metodologico nuovo: il finding c'è già, va solo scritto bene
- Lascia spazio per **FASE 3 N=179 in-dataset** come consolidamento del positivo
- Anticipate professore Q5 "I risultati sono generalizzabili?" → "No, e abbiamo quantificato il gap esattamente"
- Future-work onesto: domain adaptation + multi-site → articolo successivo

**Contro**:
- Cambia framing (Tesi 2.0 era nata "cross-dataset transfer"), ma il framing nuovo è più forte scientificamente
- Richiede riscrittura ~30% Discussion (1 settimana)
- Possibile resistenza operatore se aveva committed a "cross-dataset transfer success" come narrativa

**Quando ha senso**: **adesso**, dato lo stato dei fatti.

---

## Pipeline rigor checklist

| Item | Status | Note |
|---|---|---|
| BIDS conformance (ds005385) | ✅ | `reports/DS005385_STRUCTURE.md` + bids-validator on |
| BIDS conformance (ds004504) | ✅ | adapter `step 2.1` (commit `22119df`) |
| Source reconstruction (dSPM) | ✅ | fsaverage template, MNE; limitazione MRI individuale dichiarata §4.2 AGE_SEX |
| Parcellation (aparc 68 ROI) | ✅ | `parcellation/extract_label_tc.py` |
| Parcellation (schaefer100) | ⚠️ | 80/100 sub completati N=100; usato solo per N=30 (audit pre-prof) |
| FC (wpli/plv/coh/aec) | ✅ | `connectivity/fc_dispatcher.py`, 4 metric × 4 band confirmed |
| GroupKFold subject-level outer | ✅ | `ml_dispatcher`, fix `5bdb6bb` |
| Nested CV inner GroupKFold K=3 | ✅ | LogReg GridSearch C, commit `25cad1c` |
| StandardScaler train-only | ✅ | verificato in `ml_dispatcher` |
| Permutation subject-level | ✅ | fix `5bdb6bb`, n_perm=50 (FASE 1) / 500-1000 (N50/N30) |
| Bootstrap CI cluster subject-level | ✅ | fix `93a9dfc`, n_boot=1000 |
| FDR-BH multi-comparison | ✅ | `analysis/fdr_helper.py`, applicato a 4 confronti GT vs baseline |
| Target a-priori (anti-HARKing) | ✅ | `.planning/core/PLAN_AGE_SEX_EXTENSION.md` |
| Mock-free | ✅ | nessun mock fallback in pipeline scientifica |

**Gap minori**:
- `schaefer100` incompleto su N=100 → da non re-claim per FASE 3 senza completarlo o documentare esplicitamente come "subset N=30"
- n_perm=50 in FASE 1 è soglia minima ammissibile (Phipson & Smyth 2010 raccomanda ≥1000 per p<0.01); il N50/N30 ha n_perm=500-1000. **Raccomandazione**: per FASE 3 N=179 forzare n_perm≥1000 sul winner.

---

## Statistical methodology audit

| Item | Implementato | Riferimento | Note |
|---|---|---|---|
| Bootstrap CI subject-level cluster | ✅ n_boot=1000 | `analysis/stats_utility.py::bootstrap_ci`, fix `93a9dfc` | Documentazione corretta a "percentile" non "BCa" (audit pre-prof D1) |
| Sign test / paired tests | ⚠️ assente | n/a | Non applicato per confronti modelli (Demšar 2006); ammissibile vista la dimensione ridotta del benchmark, ma raccomandato per N=179 |
| Permutation test subject-level | ✅ n_perm=50 (FASE 1) / 1000 (N50 winner) | fix `5bdb6bb` | OK ma forzare n_perm=1000 per claim definitivi |
| Effect size (Cohen d, Hedges g) | ✅ | `analysis/stats_utility.py` + Hedges g sprint `96f3edd` | OK |
| Power analysis | ✅ post-hoc | G*Power via cerebras MCP, audit D5 | Pre-hoc per FASE 3 N=179 raccomandato |
| Multi-comparison correction | ✅ FDR-BH | `analysis/fdr_helper.py` | Applicato dove richiesto |
| Nested CV (anti-HARKing su iperparam) | ✅ | LogReg GridSearch inner K=3 | OK |

**Statistical Hardening sprint (2026-05-27, commits `96f3edd`→`6a4937e`)**: già applicato FIX-01..FIX-07 → BCa formalizzato come percentile, nested CV, Hedges g, dashboard validator, FDR-BH, HARKing disclosure. Sprint chiuso 8dc8eb0+6a4937e. Codebase è in stato pre-tesi pulito.

---

## Reproducibility audit

| Item | Status | Path |
|---|---|---|
| Seed control | ✅ | `seed=42` (`run_cv`, `bootstrap_ci`, `permutation_test`); whitelist N=179 `seed=43` |
| Whitelist hash deterministico | ✅ | hash `1594bf5d4914a864` per N=30, hashes documentati |
| Env pinning (pyproject.toml + requirements.txt) | ✅ | `environment.yml`, `requirements.txt`, `pyproject.toml` |
| Container (Docker/Singularity) | ❌ assente | Da considerare per future submission ma non bloccante tesi |
| Run-id standard | ✅ | `common/run_id.py` (`S-53` deliverato) |
| Manifest riproducibilità | ✅ | `common/reproducibility.py` |
| Pre-commit hooks | ⚠️ | non installato in env (debito `H-HARD-PRECOMMIT`) |
| Test suite | ✅ | 276 PASS post-hardening (272 → 276 in FIX-04) |
| ruff=0 | ⚠️ | 25 errori pre-esistenti (debito `H-HARD-RUFF`); 20/25 auto-fixable |

**Gap minori, non bloccanti per tesi**: container e pre-commit installation sono nice-to-have. Ruff debt è tracciato.

---

## RACCOMANDAZIONE FINALE per operatore

**Opzione raccomandata: D — Pivot thesis to "cross-dataset limitation as primary finding"**
**Accoppiata a: lancio operativo FASE 3 N=179 in-dataset (consolidamento positivo)**

### Razionale sintetico

1. **Lo stato dei fatti supporta D meglio di A/B/C**: il transfer negativo è già misurato, quantificato e contestualizzato (dataset eterogenei + lab effect + Alzheimer); è un risultato **scientifico** non un buco. Re-inventare il framing della tesi è meno costoso che inseguire un transfer cross-dataset positivo con N=49 target.
2. **A è scientificamente debole (N=17-22 ctrl, no power); B è metodologicamente vietato (DL no, complexity > N); C è time-impossibile (3-6 settimane harmonization).**
3. **D è onesto, pubblicabile, e libera tempo per FASE 3 N=179** che è l'unico passo che migliora **realmente** la potenza statistica del risultato positivo della tesi (sex BA=0.713 → stima più stretta su N=179).
4. **Coerente con Q&A professore pre-preparate (audit D Q5)**: "I risultati sono generalizzabili a nuove popolazioni?" → "No — questa è la limitazione principale esplicitamente dichiarata"; ora è quantificata.

### Cost-benefit

| Voce | D + FASE 3 N=179 | A (subgroup) | B (DANN) | C (3rd dataset) |
|---|---|---|---|---|
| Effort (ore) | 4h riscrittura + 15h pipeline | 4h | 80h | 150h+ |
| Risk null result | basso (positivo già acquisito) | alto (N=17-22) | alto | alto |
| Pubblicabilità | alta (limitation-driven) | bassa (negative again) | bassa (no DL allowed) | media |
| Thesis impact | alto (narrative coerente) | basso | basso | alto se funziona |
| Coerenza vincoli | ✅ | ✅ | ❌ (DL vietato) | ⚠️ (time) |

### Piano operativo concreto (se operatore approva D)

**Sprint immediati (settimana 1)**:
1. Riformulare Discussion v3: §1 risultato in-dataset positivo (sex BA=0.713, GT 8-dim interpretabile); §2 risultato cross-dataset NEG come finding quantificato (BA 0.713→0.500); §3 limitazioni → "cross-cohort generalization requires Combat-EEG + N≥200 + multi-site CV"; §4 future-work → domain adaptation, multi-site, FOOOF aperiodic.
2. Aggiornare Conclusion in parallelo per coerenza.
3. Citazioni nuove richieste: Babiloni 2016 (Alzheimer EEG-FC), Engemann 2022 (brain-age multi-site), Combat-EEG (harmonization).

**Sprint FASE 3 (settimana 2-3)**:
4. Lancio `python3 scripts/run_pipeline_n30.py --n-subjects 179` in tmux dedicato `tesi-fase3-n179` con HB monitoring (sonnet1-tesi o haiku1-tesi worker).
5. Aggregate features + ML LOSO-179 con n_perm=1000 + nested CV.
6. Generare `reports/EXPERIMENTS_N179.md` + amendment ad `AGE_SEX_VALIDITY.md`.
7. Verificare che sex BA N=179 sia compatibile con N=100 (test di equivalenza statistica).
8. Update dashboard tab 0 con risultati N=179.

**Sprint finale (settimana 4)**:
9. Audit pre-professore v2 (estende `audit_pre_professore.md`) con sezione G "Cross-dataset transfer limitation" e sezione H "N=179 scaling validation".
10. Q&A professore aggiornate (Q5 ampliata, nuova Q11 su transfer NEG, Q12 su scaling N=179).

**Squad re-spawn richiesto**:
- `sonnet-orch-tesi-lemon` (re-purpose come `sonnet-orch-tesi-fase3`)
- `haiku-tesi-lemon-1` o `haiku-tesi-fase3` per atomici (aggregate, report scaffolding)
- 1 sonnet o opus per riscrittura Discussion v3

---

## Open questions per operatore

1. **Approvi D (pivot framing + FASE 3 N=179)?** Sì/No/Variant.
2. Se Sì, vuoi includere **A come exploratory secondary analysis** in appendice (subgroup ctrl ds004504), o lasciarla del tutto fuori dalla tesi?
3. Per FASE 3 N=179: confermi lancio in tmux dedicato con HB monitoring? Worker preferito (sonnet1-tesi / haiku1-tesi / nuovo `sonnet-tesi-fase3`)?
4. Discussion v3: lo scrivi tu o autorizzi un worker (sonnet1-tesi) per il primo draft con tuo review iterativo?
5. Dashboard tab 6: il transfer NEG come è ora va bene per la versione tesi o vuoi una v2 con riformulazione "Cross-Cohort Generalization Limitation" come titolo del tab invece di "Cross-Dataset Transfer"?
6. Container Docker per riproducibilità: nice-to-have o richiesto dal relatore?
7. Vuoi pre-registrare l'analisi N=179 (anti-HARKing v2) prima di lanciarla? Aggiunge robustezza ma costa 1h scrittura pre-reg.

---

## Note metodologiche finali

- **Vincoli scientifici rispettati**: no mock, no fallback nascosti, honest assessment, no auto-fix codice scientifico, decisione = operatore.
- **MCP-First**: questo deep-review è 100% ragionamento sintetico su artefatti già nel context (AGE_SEX_VALIDITY, CROSS_DATASET_TRANSFER, audit_pre_professore, memorie progetto, queue, HB). Nessuna delega MCP richiesta perché nessuna analisi statistica nuova è stata eseguita; tutti i numeri sono letti da report committati. `mcp_assisted: no`.
- **NO dispatch worker per fix**: nessun fix codice scientifico richiesto a worker. Eventuali sprint successivi (Discussion v3, FASE 3) verranno dispatched DOPO decisione operatore A/B/C/D, non da questo orch in questa sessione.
- **Branch + PR**: questo deliverable verrà committato su `seraxel/tesi-deep-review-2026-06-04` e aperto come PR per review operatore. Main resta intatto.
