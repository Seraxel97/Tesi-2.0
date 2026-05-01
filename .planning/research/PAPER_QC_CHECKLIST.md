---
type: manuscript
status: active
section: qc_checklist
project: Tesi_2.0
last_review: 2026-05-01
sprint: S-50
tags: [eeg, source-fc, ml]
version: v1
date: 2026-05-01
last_update: 2026-05-01
---
# Paper QC Checklist — Tesi_2.0 Manuscript

Checklist per submission readiness. Marcare [x] quando il punto e' soddisfatto.
Cross-ref a sprint e file specifici di Tesi_2.0.

**Legenda**: [x] DONE | [ ] pending | [~] parziale/draft

---

## 1. Manuscript content

| Item | Stato | File / Sprint |
|------|-------|---------------|
| Abstract 250 ± 30 words | [x] | `ABSTRACT_v1.md` (278w) — S-32 |
| Introduction (~3000 words) | [~] | `INTRODUCTION_v1.md` — S-15 (draft) |
| Background & Related Work (~6000 words, ≥30 refs) | [~] | `RELATED_WORK_v1.md` — S-15 (draft, refs da completare) |
| Methods (~5000 words, riproducibili) | [x] | `METHODS_v1.md` — S-13; `APPENDIX_A_CONFIG.md` — S-36 |
| Results (~4000 words, figure presenti) | [ ] | benchmark pending esecuzione; `BENCH_MATRIX_RESULTS.json` — S-08 schema done |
| Discussion (~3000 words) | [~] | `DISCUSSION_v1.md` — S-15 (placeholder sezione risultati) |
| Conclusion + Future Work (~1500 words) | [x] | `CONCLUSION_v1.md` (369w) + `FUTURE_WORK_v1.md` (219w) — S-35 |
| References ≥50 BibTeX entries | [ ] | DR-VAULT-bibtex-import pending; refs parziali in `REFS_LOSO_CV.md`, `REFS_FC_LEAKAGE.md`, `REFS_PERMUTATION.md`, `REFS_PARCELLATION.md` |

---

## 2. Statistical reporting

| Item | Stato | File / Sprint |
|------|-------|---------------|
| Permutation testing 1000x implementato | [x] | `ml_training/permutation.py` — DR-RESEARCH-permutation-significance |
| FDR correction (Benjamini-Hochberg) applicata | [x] | `analysis/fdr_helper.py` — S-16 |
| CI bootstrap riportati | [x] | `analysis/stats_utility.py` — S-41 |
| Effect size Cohen's d riportato | [ ] | non ancora implementato — da aggiungere a stats_utility.py |
| p-value threshold 0.05 (pre-FDR) documentato | [x] | `CV_STRATEGY.md` sezione §5 |
| N soggetti e potenza statistica dichiarati | [~] | caveat N=1 smoke in `ABSTRACT_v1.md`; analisi potenza da fare su dataset finale |

---

## 3. Reproducibility

| Item | Stato | File / Sprint |
|------|-------|---------------|
| Manifest builder | [x] | `common/reproducibility.py` — S-42 |
| Seeds fixed random_state=42 ovunque | [x] | `ml_training/ml_dispatcher.py`, `permutation.py`, `bench/matrix.py` — `APPENDIX_A_CONFIG.md` §A.4 |
| Config files documentati | [x] | `APPENDIX_A_CONFIG.md` — S-36 |
| requirements.txt + environment.yml versionati | [x] | `requirements.txt` — S-20 |
| git_sha tracciato per ogni run | [x] | `pipeline_mne_bids/bench/matrix.py` (`_git_sha()`) |
| Dataset DOI e accession number citati | [~] | matching pennies: ds003029 in `METHODS_v1.md`; dataset scientifico finale pending Q1 |
| Schema migrations JSONL state | [x] | `common/state_lib.py`, `.planning/migrations/` — DR-VAULT-schema-migration |

---

## 4. Code quality

| Item | Stato | File / Sprint |
|------|-------|---------------|
| pytest -v PASS tutto (≥60% coverage) | [x] | 554 test PASS; soglia 60% in `.coveragerc` — DR-VAULT-test-coverage-import |
| Soglia coverage ≥70% post-benchmark | [ ] | roadmap — `reports/COVERAGE_THRESHOLDS.md` |
| ruff check . exit 0 | [x] | `reports/LINT_SWEEP.md` (13 fix applicati) — S-06 |
| type hints PEP 604 | [x] | sweep `ml_training/`, `common/`, `connectivity/` — S-31 |
| docstrings numpy-style public functions | [x] | DR-REVIEW-docstrings DONE |
| `__all__` explicit in tutti i package | [x] | 9 package — DR-REVIEW-package-init-explicit |
| CI workflows attivi (lint + test + eeg-smoke) | [x] | `.github/workflows/` — DR-VAULT-ci-matrix, DR-VAULT-eeg-ci-import |
| Pre-commit hooks installati | [x] | `.pre-commit-config.yaml` — S-14 |
| Security audit dipendenze | [x] | `reports/CI_SECURITY_AUDIT.md`, `reports/SBOM_REPORT.md` |

---

## 5. Documentation

| Item | Stato | File / Sprint |
|------|-------|---------------|
| README.md badges + run examples | [x] | `README.md` (4 badge, 6 comandi) — S-19, S-27 |
| CONTRIBUTING.md developer setup | [x] | `CONTRIBUTING.md` — S-19 |
| docs/PIPELINE_OVERVIEW.md ASCII diagram | [x] | `docs/PIPELINE_OVERVIEW.md` — S-19 |
| docs/PIPELINE_OVERVIEW.md figure PNG | [ ] | S-55 pending |
| API docs auto-gen (sphinx) | [ ] | S-49 pending |
| GLOSSARY.md (72+ entries) | [x] | `GLOSSARY.md` (77 entries) — S-38 |
| Shared test fixture library | [x] | `tests/fixtures/synthetic.py` — S-46 |
| Appendix A config dump | [x] | `APPENDIX_A_CONFIG.md` — S-36 |

---

## 6. Vault sync (Obsidian)

| Item | Stato | File / Sprint |
|------|-------|---------------|
| `[[MNE_PROFESSOR_LINKS]]` aggiornato | [x] | `070_THESIS/MNE_PROFESSOR_LINKS.md` — baseline |
| `[[RESULTS_BASELINE]]` aggiornato con reports | [x] | `070_THESIS/RESULTS_BASELINE.md` (20 report cross-link) — S-12, S-37 |
| `[[050_METHODS/PIPELINE_OVERVIEW]]` sync con repo | [x] | implementation status tabella — S-37 |
| `[[THESIS_MAP]]` capitoli aggiornati | [x] | 11 sezioni + latest reports — S-37 |
| `[[CONNECTIVITY_METRICS]]` aggiornato | [x] | `050_METHODS/CONNECTIVITY_METRICS.md` |

---

## 7. Pre-submission

| Item | Stato | Note |
|------|-------|------|
| Cover letter draft | [ ] | target: Journal of Neural Engineering (JNE) |
| Supplementary materials archive | [ ] | codice sorgente + config + requirements |
| Pre-print upload (arXiv/bioRxiv) decisione | [ ] | decisione operatore necessaria |
| Journal target conferma | [~] | JNE ipotizzato (METHODS_v1.md frontmatter) — conferma operatore |
| Reviewer suggestions list (3-5 nomi) | [ ] | da preparare post-completamento Results |
| ORCID autore dichiarato | [ ] | da aggiungere al manoscritto |
| Data availability statement | [ ] | dataset matchingpennies: OpenNeuro ds003029 (pubblico) |
| Code availability statement | [ ] | repository URL da definire (GitHub public?) |
| Author contributions (CRediT) | [ ] | da compilare |
| Conflict of interest statement | [ ] | dichiarazione standard |

---

## Dipendenze critiche pendenti

Le seguenti decisioni/esecuzioni bloccano la finalizzazione del manoscritto:

1. **Q1 dataset scientifico** (ds005385 vs LEMON) — blocca Results reali e Discussion finale
2. **Esecuzione benchmark S-08** (`run_bench_matrix.py`) — blocca Results numerici
3. **DR-VAULT-bibtex-import** — blocca References ≥50 BibTeX
4. **S-55 architecture diagram** — blocca figure in docs
5. **S-49 sphinx API docs** — opzionale pre-submission, utile per review

---

*Aggiornamento: 2026-05-01 — sonnet3-ts S-50*
