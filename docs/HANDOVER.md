# HANDOVER — Tesi_2.0

**Generato**: 2026-05-01 (sprint DR-FINAL-handover-docs, sonnet1-ts)  
**Da leggere all'inizio di ogni nuova sessione** prima di procedere.

---

## 1. Stato attuale (snapshot 2026-05-01 T11:20)

| Aspetto | Stato |
|---------|-------|
| Pipeline step 1-6 | ✅ completi (smoke test matchingpennies) |
| Step 7 (dataset scientifico) | ❌ bloccato su Q1 |
| Test suite | 244 PASS, 1 errore pre-esistente (`test_dispatcher_base.py` fixture missing) |
| Ruff | 0 errori su tutti i moduli |
| Queue | 113 done, 2 blocked, 0 claimable |

## 2. Prima cosa da fare in ogni nuova sessione

```bash
cd /home/seraxel/Scrivania/Tesi_2.0

# 1. Heartbeat (rimpiazza <session-name> con il nome tmux)
python3 -c "
import json; from pathlib import Path; from datetime import datetime, timezone
p = Path('.planning/heartbeats_tesi/<session-name>.json')
p.write_text(json.dumps({'worker': '<session-name>', 'status': 'working',
  'timestamp': datetime.now(timezone.utc).isoformat(), 'sprint_id': None,
  'milestone': 'boot', 'last_capture': 'session start', 'next_action': 'check queue'}) + '\n')
"

# 2. Verifica queue
python3 -c "
import json
all_done = set()
all_items = []
with open('.planning/DISPATCH_QUEUE_tesi.jsonl') as f:
    for line in f:
        line = line.strip()
        if not line: continue
        try:
            obj = json.loads(line)
            all_items.append(obj)
            if obj.get('status') == 'done': all_done.add(obj.get('id'))
        except: pass
claimable = [o for o in all_items if o.get('status')=='queued' and not o.get('owner')
             and all(d in all_done for d in o.get('deps',[]))]
print(f'Claimable: {len(claimable)}')
for c in claimable: print(f'  {c[\"id\"]}: {c[\"sprint\"][:70]}')
"

# 3. Leggi SYNC se esiste, poi claim
```

## 3. File chiave

| File | Scopo |
|------|-------|
| `PROGRESS.md` | Stato step pipeline + asset + vincoli operatore |
| `.planning/SESSION_SUMMARY_2026-05-01.md` | Riepilogo completo sessione precedente |
| `.planning/QUESTIONS_FOR_OPERATOR.md` | **Q1 aperta** — scelta dataset scientifico |
| `.planning/DISPATCH_QUEUE_tesi.jsonl` | Queue master (113 done) |
| `.planning/heartbeats_tesi/` | Heartbeat per worker |
| `docs/PIPELINE_OVERVIEW.md` | Diagramma ASCII pipeline 7 step |
| `reports/PERF_BENCHMARK.md` | Bottleneck: inverse_parcellation 55% |

## 4. Decisione urgente (Q1)

**Scegliere il dataset scientifico finale** — rispondere a `.planning/QUESTIONS_FOR_OPERATOR.md`:

- **Opzione A**: `ds005385` — 200 soggetti, 21 GB, EC/EO, OpenNeuro, già su disco
- **Opzione B**: `LEMON` — 220 soggetti, 65 GB, EC/EO+, già su disco

La scelta sblocca S-07 (BIDS prep) e S-47 (migration plan post-Q1).

## 5. Come riprendere il lavoro tecnico

```bash
# Smoke test rapido (10s)
python3 -m pytest tests/test_integration_final.py -q

# Perf regression (5s)
python3 -m pytest tests/test_perf_regression.py -q

# Ruff clean check
python3 -m ruff check common/ connectivity/ features/ ml_training/ pipeline_mne_bids/ analysis/

# Validazione completa
bash scripts/final_validation.sh
```

## 6. Prossime ottimizzazioni raccomandate

1. **P0 — Performance**: refactor `inverse_parcellation` in `run_e2e_matchingpennies.py`
   con `mne.minimum_norm.apply_inverse_epochs()` (batch API). Riduzione stimata ~40%.
2. **P1 — ML**: aggiungere `n_jobs=-1` agli stimatori sklearn in `ml_dispatcher.py`.
3. **Post-Q1**: configurare `config/config_step1_<dataset>.py` e avviare STEP 1 su dataset scientifico.

## 7. Struttura repo

```
Tesi_2.0/
├── common/          # Utilities (run_id, logger, queue_lib, paths, …)
├── connectivity/    # FC dispatcher (wpli, plv, coh, …)
├── features/        # Feature extraction (mne-features + FC flatten)
├── ml_training/     # ML dispatcher + permutation test
├── parcellation/    # Source parcellation (extract_label_tc)
├── pipeline_mne_bids/  # E2E orchestratore (STEP 1-7)
├── source_reconstruction/  # Inverse operator (finalize_inverse.py)
├── analysis/        # Stats, bench, compare
├── scripts/         # Utility shell/python
├── tests/           # 244+ test PASS
├── config/          # Config step1 + step2 + schema
├── data/            # Dataset (eeg_matchingpennies + derivatives)
├── reports/         # Report + manifests
└── docs/            # Pipeline overview, architecture, handover
```

## 8. Cross-reference

- Architettura: `docs/PIPELINE_OVERVIEW.md`, `docs/figures/architecture.svg`
- Config: `~/.claude/CLAUDE.md` (regole globali), `PROGRESS.md` (vincoli operatore)
- Metodologia: `.planning/research/CV_STRATEGY.md`, `.planning/research/METHODS_v1.md`
- BibTeX: `.planning/research/bibliografia.bib` (27 entries), `citation_style.csl` (IEEE)
