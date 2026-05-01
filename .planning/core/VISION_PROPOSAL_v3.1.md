# Tesi_2.0 — Vision Proposal v3.1 (DRAFT) — 6 punti chiave Δ1-Δ6

**Stato**: 📝 PROPOSTA — non sostituisce ancora la VISION precedente
**Sorgente predecessore**: `~/Scrivania/Tesi/.planning/core/VISION.md` v3.0 (riallineamento prof, 2026-04-15)
**Generata**: 2026-05-01 (sessione `tesi-orch` / `opus-orch-ts`)
**Obiettivo**: allineare la vision al **restart minimale** rappresentato dal repo `Tesi_2.0/` e ai vincoli operativi 2026-04-28.
**Approvazione richiesta**: operatore (CEO) — discussione PRIMA di partire con workers.

---

## Sintesi: 6 punti chiave da aggiornare

> *Diff strutturale rispetto a VISION v3.0. Ognuno = 1 decisione operatore.*

### Δ1 — Pipeline base: da custom a `mne-bids-pipeline` (consolida D7→inverso)

**Stato v3.0**: D7 imponeva *"preprocessing custom (non mne-bids-pipeline) per controllo completo su fixed-length epoching resting-state"*. La pipeline custom (`neuro_ml_starter`, 634 LOC) era il motore.

**Restart Tesi_2.0**: `mne-bids-pipeline 1.10.1` è il **motore obbligatorio**, niente più pipeline custom (vincolo 1 + 2). Step custom solo a valle dei derivatives.

**Impatto**:
- ✅ Allineamento pieno con la richiesta del professore (era già S-11 in v3.0).
- ✅ Riduzione drastica codice da scrivere/manutenere.
- ⚠️ Per resting-state EC/EO l'epoching artificiale 2s sliding va costruito SOPRA gli output della pipeline (vedi STEP2_PROPOSAL §2.5).
- ⚠️ Decoding sensor-level built-in della pipeline (`decode=True`) **non sostituisce** il nostro ML; lo affianca come baseline.

**Decisione richiesta**: confermo che D7 è invertito? → tutto il preprocessing passa attraverso `mne-bids-pipeline`, codice custom solo per source-on-epochs e step 3-6.

---

### Δ2 — Scope-cut: rimuovere Riemannian + experiment tracking custom + AutoResearchClaw

**Stato v3.0**:
- D5: experiment tracking JSON custom → run-id, config-hash.
- D8: coffeine come prima scelta Riemannian baseline; PyRiemann fallback.
- D6: AutoResearchClaw rimosso ma literature review via Claude Code WebSearch.

**Restart Tesi_2.0** (vincoli 2 + 3):
- ❌ Niente coffeine, niente PyRiemann (libreria non in lista ammessa).
- ❌ Niente experiment tracking custom (è scope creep): output BIDS-derivatives + cache joblib + log Excel sono già forniti dalla pipeline. Per ML aggiungeremo solo un `results/` JSON snapshot per run.
- ❌ Niente literature review automatica gestita dall'orchestratore: gestita dall'operatore manualmente o via `research` skill ad-hoc, NON dentro la pipeline.

**Impatto**:
- ✅ Scope MVP più stretto, deliverable più rapido.
- ⚠️ Perdiamo benchmark Riemannian come comparator scientifico → da motivare in tesi (cap. VII Discussion).
- ⚠️ La VISION v3.0 elencava il confronto Riemannian come contributo #4 attesi — va RIMOSSO o RIDIMENSIONATO.

**Decisione richiesta**: confermo rimozione Riemannian dalla tesi? Oppure resta in Future Work (cap. VIII)?

---

### Δ3 — Dataset scientifico: scelta finale ANCORA pendente

**Stato v3.0**:
- v2.1 raccomandava ds005385 (Dortmund Vital, 608 sub) come primario; ds004362 (PhysioNet MI) come secondario.
- D14: 4 condizioni nel dataset (EC-pre, EO-pre, EC-post, EO-post), ordine fisso EC→EO per blocco.
- v3.0 D17: tenere ds005385.
- Lavoro vecchio repo: LEMON download in corso (PID 528009, 220 sub GWDG).

**Restart Tesi_2.0**:
- `PROGRESS.md` segna entrambi (`ds005385`, `LEMON`) come **NON scaricati**, blocco esplicito su attesa conferma operatore.
- STEP1_LOG §2.1 ribadisce: matchingpennies = solo TEST TECNICO.

**Impatto**:
- ⚠️ La decisione `ds005385` vs `LEMON` (vs altro EC/EO BIDS) è **bloccante** per Step 3-6.
- ⚠️ Ci sono trade-off concreti:
  - `ds005385`: 608 sub, 64 ch, BIDS nativo, EC+EO post-task confound (D2 era una mitigation in v3.0).
  - `LEMON`: 228 sub, 62 ch, MRI individuali (rilevante se torniamo a forward modelling individuale e non template `fsaverage`).

**Decisione richiesta**: scelta finale **prima** che Wave 1 worker tocchi anything beyond matchingpennies. Proposta operativa: tenere ds005385 (allineato a v3.0 D17) + LEMON come validation secondaria solo se tempo lo consente.

---

### Δ4 — Orchestrazione: vincolo 7 va riallineato per la routine notturna

**Stato v3.0**: vecchio repo `Tesi/` aveva orchestrazione (`opus-father` + sonnet workers + cron + tmux file-bus + heartbeats) attiva nello sprint S13c.

**`PROGRESS.md` vincolo 7 (2026-04-28)**: *"NO orchestrazioni cross-session"*. Decisione presa per fase di restart manuale.

**Sessione corrente (2026-05-01)**: prompt orchestratore `tesi-orch` chiede esplicitamente DISPATCH_QUEUE_tesi.jsonl + heartbeats_tesi/ + workers sonnet → contraddice il vincolo.

**Lettura proposta**: il vincolo 7 valeva per la fase di "controllo manuale" iniziale (STEP 1 → STEP 2 PROPOSAL); ora che STEP 1 è chiuso e la struttura è chiara, l'operatore può RILASSARE quel vincolo SOLO per:
- Workers che operano in `Tesi_2.0/` (mai cross-repo).
- Sprint atomici, ognuno con conferma operatore o auto-exec whitelist documentata.
- Heartbeat ogni 10 min, escalation a `father` → operatore se blocked.

**Decisione richiesta**: vincolo 7 viene riformulato come *"NO orchestrazioni cross-repo dal worker; SÌ orchestrazione interna a Tesi_2.0/ con queue + heartbeats"*? O resto strict (=no workers)?

---

### Δ5 — Roadmap: 7 step lineari sostituiscono "Foundation/Source Pipeline/ML Benchmark/Deep Experiments/..."

**Stato v3.0**: timeline narrativa (Apr 1-15 Foundation, ..., Set-Ott 2026 submission) e sprint S01-S18.

**Restart Tesi_2.0** (`PROGRESS.md` §Stato step):

| Step | Titolo | Output atteso |
|------|--------|----------------|
| 1 | Setup pipeline | ✅ DONE — preprocessing su matchingpennies validato |
| 2 | Source reconstruction smoke test | `*-fwd.fif`, `*-inv.fif`, `*-stc-*` su matchingpennies, fsaverage template |
| 3 | Parcellazione | `extract_label_time_course` su aparc + Schaefer-100 + neuromaps |
| 4 | Connettività | matrix wPLI/PLI/COH/PLV per epoch su parcels |
| 5 | Feature extraction | `mne-features` univariate + connectivity edges flatten |
| 6 | ML custom | sklearn LR/SVM/RF/GB con GroupKFold (LOSO) + permutation testing |
| 7 | Verifica end-to-end | run completo dataset scientifico finale (post Δ3) |

**Impatto**:
- ✅ Roadmap lineare, ogni step verificabile, gate di conferma esplicito.
- ⚠️ Lo Step 7 dipende da Δ3. Tutto il blocco "Discussion / Writing / Submission" della v3.0 §11 manca da questa numerazione → va aggiunto come Step 8 (Manuscript) parallelizzabile a step 5-6.

**Decisione richiesta**: confermo i 7 step + aggiungo Step 8 "Manuscript draft + cap. methods/results"?

---

## Cosa NON cambia rispetto a v3.0

Mantenuto invariato (e proposto ancora come binding):

- **RQ principale + RQ secondarie 1-4** (RQ-5 Riemannian decade per Δ2).
- **Leave-Subjects-Out CV obbligatorio** (D2/D11 v2.1 + Sensors 2023 risk).
- **Permutation testing** ≥1000 permutazioni per ogni confronto (criterio §10).
- **wPLI come metrica leakage-corrected primaria** (RQ-1 + Nagy et al. 2024).
- **3 livelli parcellazione**: ~35 (aparc), ~70 (Schaefer-100), ~150 (Destrieux/Schaefer-200).
- **Source vs Sensor confronto** (RQ-4) come contributo principale.
- **Pipeline riproducibile end-to-end** come contributo #1.
- **8 capitoli tesi** (~27,500 parole) come blueprint.
- **Criteri di successo §10** salvo eliminazione "Riemannian baseline".
- **D14 condizioni dataset**: rimane se ds005385 confermato.

## Cosa va archiviato (vecchio scope, non più applicabile a Tesi_2.0)

- D5 (experiment tracking custom JSON) → solo `results/run_*.json` minimal.
- D6 (AutoResearchClaw + literature review automatica) → manuale.
- D8 (coffeine/PyRiemann Riemannian baseline) → fuori scope.
- D12 (refactor incrementale `neuro_ml_starter`) → repo non esiste più, restart fresco.
- D13 (catena sprint sequenziale + ramo parallelo Riemannian) → sequenziale puro.
- Sezione 12 (repo open-source analizzati) → mantenere solo MNE / mne-bids-pipeline / mne-connectivity / DISCOVER-EEG come riferimenti.

---

### Δ6 — Architettura a 2 dispatcher per STEP 4 (FC) e STEP 6 (ML)

**Sorgente**: proposta da VS (Vesta orch) durante recon 2026-05-01, allineata al brief operatore *"pipeline per analisi segnali eeg con possibilità di cambiare metriche (wpli, plv, coherence, imgcoher), e algoritmi per ml (foresta, svm, mlp, logreg ecc)"*.

**Stato v3.0**: nessuna architettura dispatcher esplicita; il vecchio repo aveva moduli per metric/clf separati ma senza interfaccia unificata.

**Restart Tesi_2.0**:
- `connectivity/fc_dispatcher.py` con `metric: Literal["wpli","wpli2_debiased","plv","coh","imcoh","pli","ciplv"]` → wraps `mne_connectivity.spectral_connectivity_epochs(method=metric, ...)`. Tutte le metriche sono native in mne-connectivity 0.8 → niente librerie extra.
- `ml_training/ml_dispatcher.py` con `algorithm: Literal["rf","svm","mlp","logreg","gb"]` → sklearn (RandomForest, SVC, MLPClassifier shallow, LogReg, GradientBoosting) wrappato in GroupKFold subject-level per evitare leakage cross-subject.

**Impatto**:
- ✅ Cambio metrica/algoritmo = un solo parametro in CLI/config, **zero** scrittura di codice nuovo per ogni esperimento.
- ✅ Allineamento esplicito al brief prof ("possibilità di cambiare X").
- ✅ Riusabile sia su matchingpennies (per smoke) sia sul dataset scientifico finale.
- ⚠️ Strategia di esecuzione (dispatcher one-shot vs step-by-step vs ibrido) è la decisione **Q7** in `.planning/QUESTIONS_FOR_OPERATOR.md`.

**Decisione richiesta** (combinata con Q7): adotti l'architettura a 2 dispatcher come scelta canonica per Tesi_2.0?

---

## Materiale del professore (riferimento)

5 link ufficiali del professore (canonici, salvati in vault `[[070_THESIS/MNE_PROFESSOR_LINKS]]`):

1. **mne-bids-pipeline** → STEP 1 preprocessing — https://mne.tools/mne-bids-pipeline/stable/index.html
2. **neuromaps** → STEP 3 parcellation — https://netneurolab.github.io/neuromaps/usage.html
3. **mne-connectivity** → STEP 4 FC — https://mne.tools/mne-connectivity/stable/index.html
4. **mne-features** → STEP 5 features — https://mne.tools/mne-features/
5. **dataset examples** → riferimento STEP 1 — https://mne.tools/mne-bids-pipeline/stable/examples/examples.html

✅ Tutti installati in conda `base` (Python 3.13.12) verificato 2026-05-01.

> Regola fondamentale prof: *"non presentare come software standalone; presentare come estensione modulare compatibile con la pipeline MNE"*.

---

## Versioning

- VISION v2.1 → 2026-04-06 (CEO approved, 14 decisioni)
- VISION v3.0 → 2026-04-15 (riallineamento prof, +6 decisioni)
- **VISION v3.1 (DRAFT)** → 2026-05-01 (restart Tesi_2.0, 6 punti chiave Δ1-Δ6 — Δ6 aggiunto post recon VS, materiale prof linkato in vault)

Una volta approvata, questa diventa `VISION.md` (sostituendo riferimento al vecchio file in repo Tesi/).

---

*Pronto per discussione operatore. Workers Wave 1 NON parte finché Δ1-Δ5 confermati.*
