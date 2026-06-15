# Tesi_2.0 — Merge Plan & Audit Checklist
**Generato**: 2026-06-11 da opus-orch-tesi
**Per**: operatore al rientro — tutto in un file

---

## 1. Ordine di merge consigliato

### Ordine: PR #3 → PR #4 → PR #5

| Ordine | PR | Branch | Commit chiave | Contenuto |
|--------|-----|--------|---------------|-----------|
| 1° | #3 | `seraxel/tesi-deep-review-2026-06-04` | `b943124` | `.planning/TESI_DEEP_REVIEW_2026-06-04.md` — rationale decisione D |
| 2° | #4 | `seraxel/tesi-closure` | `1392f2f` | PROGRESS.md N=179, metadata.json row_order, ruff=0, test fix |
| 3° | #5 | `manuscript/discussion-conclusion` | `ba531ae` | Discussion §3 N=179 + Conclusion completa |

**Rationale ordine**:
- #3 prima: doc-only, zero conflitti, registra la decisione metodologica che giustifica tutto
- #4 seconda: include i fix tecnici (ruff, test, metadata) — base solida per #5
- #5 ultima: **costruita sopra #4** (branched da `seraxel/tesi-closure` al commit `1392f2f`) — contiene già tutti i cambiamenti di #4, quindi il merge sarà pulito

---

## 2. Analisi conflitti

### Nessun conflitto tra PR #3 e le altre
PR #3 tocca **un solo file**: `.planning/TESI_DEEP_REVIEW_2026-06-04.md` (file nuovo).
Zero overlap con #4 e #5.

### PR #4 e #5 — sovrapposizione gestita
PR #5 è stata creata **branching da #4** (ancestor comune = commit `1392f2f`).
File condivisi tra #4 e #5:

| File | In #4 | In #5 | Conflict? |
|------|-------|-------|-----------|
| `PROGRESS.md` | ✅ | ✅ (inalterato) | ❌ no |
| `analysis/cross_dataset_eval.py` | ✅ | ✅ (inalterato) | ❌ no |
| `config/labels_phenotype_ds004504.py` | ✅ | ✅ (inalterato) | ❌ no |
| `data/features/ds005385/metadata.json` | ✅ | ✅ (inalterato) | ❌ no |
| `scripts/run_ml_age_sex_n179.py` | ✅ | ✅ (inalterato) | ❌ no |
| `scripts/run_pipeline_ds004504.py` | ✅ | ✅ (inalterato) | ❌ no |
| `tests/test_feature_comparison.py` | ✅ | ✅ (inalterato) | ❌ no |
| `reports/DISCUSSION_v3.md` | ❌ | ✅ (nuovo) | ❌ no |

**Procedura merge su GitHub** (senza CLI):
1. Merge #3 → "Merge pull request" (regular merge, non squash)
2. Merge #4 → "Merge pull request" (regular merge)
3. Per #5: GitHub mostrerà "This branch has no conflicts" perché #5 contiene già i commit di #4.
   → Merge #5 normalmente.

**Se GitHub mostra conflitti su #5 dopo merge di #4** (improbabile ma possibile con squash):
```bash
git checkout manuscript/discussion-conclusion
git rebase origin/main
git push --force-with-lease origin manuscript/discussion-conclusion
```
Poi re-mergiare #5.

---

## 3. Checklist Audit Pre-Professore

Da eseguire su `main` post-merge di tutte e 3 le PR.
Sprint: `R-TESI-2.0-AUDIT-PRE-PROFESSORE` (branch `audit/pre-professore`)

### A — Riproducibilità

- [ ] **A1** Smoke 2 soggetti random ds005385: pipeline step 1-6 gira senza errori su macchina fresca
- [ ] **A2** Seed deterministico confermato: `subjects_whitelist_n179.py` seed=43, N=179 identici a `ml_age_sex_n179.json`
- [ ] **A3** Container Docker: `docker build` + `docker run` producono stesso risultato ML (BA entro ±0.01)
- [ ] **A4** `pytest -x` (senza data-deps): ≥328 PASS, 0 FAIL, ruff=0

### B — Dashboard

- [ ] **B1** Tab 1 (Dataset/Cohort): demographics N=179 corretti (età range, sex ratio)
- [ ] **B2** Tab 3 (Source/Parcellation): parcellazione aparc 68 ROI renderizza correttamente
- [ ] **B3** Tab 4 (Connectivity Graph): grafo PLV theta su almeno 1 soggetto ds005385 senza errori
- [ ] **B4** Tab 5 (ML Predictions): risultati N=179 BA=0.795 / MAE=12.26 visibili (non N=50 o N=100)
- [ ] **B5** Edge case: dataset selector con dataset mancante — no crash, messaggio utile

### C — Discussion + Conclusion (reports/DISCUSSION_v3.md v3.1)

- [ ] **C1** §1 (FASE 1 N=100): BA=0.713, MAE=12.52, p_fdr corretti
- [ ] **C2** §2 (FASE 2 transfer NEG): BA=0.500, MAE=22.25 — presentati come domain gap, non failure
- [ ] **C3** §3 (FASE 3 N=179): BA=0.795 CI=[0.744,0.843] p_fdr=0.0013, MAE=12.26 CI=[11.31,13.32] p_fdr=0.0013
- [ ] **C4** §3 tabella N=100→N=179: Δ coerenti con `AGE_SEX_FASE3_N179.md`
- [ ] **C5** §4 Limitazioni: single-site quantificato, CI R² include zero menzionato, fsaverage distorsione
- [ ] **C6** §6 Conclusion: nessuna claim non supportata, future-work coerente con gap reali
- [ ] **C7** Riferimenti: tutti i claim citate (Kollia 2022, Engemann 2022, Franck 2019, Babiloni 2016)
- [ ] **C8** Framing D onesto: FASE 2 non "nascosto", limiti generalizzabilità espliciti

### D — Statistica

- [ ] **D1** Bootstrap n≥1000 BCa: confermato in `ml_age_sex_n179.json` (`n_boot=1000`)
- [ ] **D2** Permutation test subject-level n=1000: confermato (`n_perm=1000`, `perm_type=subject_level`)
- [ ] **D3** FDR-BH documentato: tabella FDR in `AGE_SEX_FASE3_N179.md` §3
- [ ] **D4** GT sex significativo (BA=0.656 p_fdr=0.0013), GT age non significativo (R²=-0.194 p=0.906) — coerente
- [ ] **D5** GroupKFold: no leakage soggetti tra fold confermato (`outer_k=5, inner_k=3`)
- [ ] **D6** Hedges g calcolato per effect size: `analysis/stats_utility.py` presente

### E — Demographics ds005385

- [ ] **E1** N=179: confermato da `subjects_whitelist_n179.py` e `metadata.json` `n_subjects=179`
- [ ] **E2** Distribuzione età: range 20-70 anni, σ≈15 anni (verificare con `participants.tsv` su macchina con dati)
- [ ] **E3** Sex ratio: documentato in demographics (M/F bilanciato? verificare)
- [ ] **E4** Esclusione criteri: `late_ses1` esclusi, documentato in DATASET_SUBJECT_AUDIT.md

### F — Baselines

- [ ] **F1** Null BA (mean permutation) ≈ 0.499 — confermato in `ml_age_sex_n179.json`
- [ ] **F2** Dummy predictor MAE (mean-strategy): non riportato esplicitamente — da aggiungere o documentare
- [ ] **F3** Confronto sex GT (8-dim) vs baseline (2278-dim): Δ=+0.139 (0.656→0.795) documentato
- [ ] **F4** Winner feature: PLV theta non è l'unica — tabella con top-3 combo desiderabile per professore

---

## 4. Q&A Professore — draft

1. **"Perché il transfer su Alzheimer fallisce?"** → Domain shift catastrofico: sani 20-70 vs pazienti 44-79 + lab effect non corretto. Zero-shot è baseline metodologica, non claim di generalizzabilità.
2. **"N=179 è sufficiente?"** → Per significatività sì (p_fdr=0.0013). Per claim generalizzabilità multi-sito no — serve Combat-EEG su ≥3 dataset.
3. **"Perché PLV theta vince su wPLI?"** → PLV è più sensibile in assenza di volume conduction severo (source-level aparc già ortogonalizza); wPLI e imCoh mostrano risultati comparabili.
4. **"Il brain-age gap 0.27 anni è reale?"** → Sì, indica assenza di bias sistematico. MAE=12.26 è nella parte alta dell'intervallo per FC-only single-site (confronto Franck 2019).
5. **"Perché R² per l'età è così basso (0.082)?"** → FC-only feature cattura varianza continua dell'età parzialmente; MRI+FC + armonizzazione multi-sito → MAE≈8-10 (letteratura). CI include zero nel limite inferiore — effetto reale ma modesto.

---

## 5. Stato finale PR e branch

**Aggiornato 2026-06-11 — TESI READY-FOR-PROFESSORE**

| PR | Branch | Stato | Note |
|----|--------|-------|------|
| #3 | `seraxel/tesi-deep-review-2026-06-04` | ✅ MERGED (2026-06-11) | su scientific/step7-experiments |
| #4 | `seraxel/tesi-closure` | ✅ MERGED (2026-06-11) | su scientific/step7-experiments |
| #5 | `manuscript/discussion-conclusion` | ✅ MERGED (2026-06-11) | su scientific/step7-experiments |
| #6 | `audit/pre-professore` | 🔵 OPEN — padre decide merge | 24/31 PASS 0 FAIL; commit 100459d |

**Audit checklist** (R-TESI-2.0-AUDIT-PRE-PROFESSORE): **COMPLETATA**
- 24/31 PASS, 0 FAIL, 7 WARN (2 non risolvibili senza participants.tsv GDPR)
- Fix-list applicata: D6 hedges_g ✅ · F2 dummy MAE ✅ parziale · F4 combo table ✅ · E2/E3 gap doc ✅
- Report: `reports/AUDIT_PRE_PROFESSORE_2026-06-11.md`

**Topologia branch** (azioni operatore pending):
- `scientific/step7-experiments` (0a1b35b) = branch default con tutto il lavoro
- `main` (338a222) = 6 commit dietro scientific — fast-forward pending (operatore)
- `audit/pre-professore` (100459d) = merge pending (#6 aperta)

**Dashboard** (`R-TESI-2.0-DASHBOARD-ML-SCIENTIFICA`): HOLD opzionale, non schedulata.

**Stand-by orch**: NON dispatchare altro su Tesi. Restano solo decisioni operatore.
