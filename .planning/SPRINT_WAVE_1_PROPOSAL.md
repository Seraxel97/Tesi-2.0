# Sprint Wave 1 — PROPOSTA workers Tesi_2.0

**Data**: 2026-05-01
**Stato**: 📝 PROPOSAL — non eseguito, condizionato a:
1. Approvazione VISION v3.1 (`.planning/core/VISION_PROPOSAL_v3.1.md`).
2. Riallineamento vincolo 7 PROGRESS.md (Q3 di STATE.md, Δ4 di VISION).
3. Risposte alle 8 decisioni di STEP2_PROPOSAL §5.

**Scope geografico**: tutti i workers operano SOLO in `/home/seraxel/Scrivania/Tesi_2.0/`. NESSUN worker tocca `/home/seraxel/Scrivania/Tesi/` o altri repo.

---

## Architettura Wave 1

3 sprint atomici, **sequenziali con dipendenze esplicite**. Niente parallelismo selvaggio: ogni sprint chiude con artefatti verificabili e gate manuale prima del successivo. La pipeline è già in piedi, quindi non serve uno swarm aggressivo.

```
W1.1 (sonnet1) ──> W1.2 (sonnet1) ──> W1.3 (sonnet2)
   STEP 2             dataset           verifica E2E
   exec               selection         smoke
   smoke              helper            (Tesi_2.0)
```

Tempo stimato totale: 60-90 min wall-clock (con conferma operatore tra sprint).

---

## W1.1 — Esecuzione STEP 2 source reconstruction (sonnet1)

**Owner candidato**: `sonnet1` (modello: claude-sonnet-4-6)
**Pre-condizione**: VISION approvata + STEP2_PROPOSAL §5 risposte (D1-D8).
**Tempo stimato**: 20-30 min (incluso fetch fsaverage se mancante + run BEM/forward/inverse/STC).

### Obiettivo
Eseguire `--steps source` di mne-bids-pipeline su `eeg_matchingpennies sub-05` con i parametri proposti in STEP2_PROPOSAL §2.2 (eventualmente modificati dall'operatore).

### Input
- `config/config_step1_matchingpennies.py` (NON modificare).
- `data/derivatives/mne-bids-pipeline/sub-05/eeg/*_clean_epo.fif` (output STEP 1).
- Decisioni operatore D1-D8 di STEP2_PROPOSAL.

### Deliverable
1. Nuovo file `config/config_step2_source_matchingpennies.py` (eredita STEP 1, aggiunge i 9 parametri source).
2. Verifica/scarica `fsaverage` template (path da decidere via D5).
3. Run pipeline con `--steps source`, log full output.
4. Verifica file prodotti: `*-fwd.fif`, `*-inv.fif`, `*-stc-*` per condizione.
5. Smoke test interpretazione (carica STC, stampa shape/tstep/vertices).
6. Scrivere `reports/STEP2_LOG.md` con stessa struttura di STEP1_LOG.md.
7. Aggiornare `PROGRESS.md` step 2 → DONE.

### Gate uscita
- Tutti i criteri di accettazione di STEP2_PROPOSAL §6 soddisfatti.
- Heartbeat finale `.planning/heartbeats_tesi/sonnet1_W1.1.json` con `status=done`.

### Rischi
R1-R9 di STEP2_PROPOSAL §4. Mitigation come da proposta.

### Auto-exec whitelist
- `mne_bids_pipeline --config ...`
- `python -c "import mne; mne.datasets.fetch_fsaverage()"` (solo se path mancante)
- `git status`, `git diff` (read-only)

### NON-auto-exec
- Modifica `PROGRESS.md` o `config/config_step1_*.py` → richiede gate operatore.
- `git commit` → richiede gate.

---

## W1.2 — Dataset selection helper (sonnet1, dipende da W1.1)

**Owner candidato**: `sonnet1` (continuazione)
**Pre-condizione**: W1.1 ✅ DONE, vision approvata, Q1 dataset finale ANCORA non risolto.
**Tempo stimato**: 15-20 min.

### Obiettivo
Generare un confronto strutturato tra `ds005385` e `LEMON` (e opz. 1-2 alternativi BIDS EC/EO) per consentire all'operatore di scegliere il dataset scientifico finale, **senza scaricare niente**.

### Input
- VISION v3.1 §Δ3.
- Tesi/.planning/core/VISION.md §6.2 (tabella dataset v3.0) come riferimento.
- Web search via `research` skill o WebFetch su OpenNeuro per metadata aggiornato.

### Deliverable
1. `.planning/core/DATASET_CANDIDATES.md` con tabella:
   - N soggetti, N canali, durata EC, durata EO, BIDS native?, MRI?, License, Size, OpenNeuro ID.
   - Pro/contro tecnici per ogni dataset.
   - Raccomandazione operativa motivata.
2. Script Python `pipeline_mne_bids/dataset_inspect.py` (modulo, NON eseguito) che:
   - Accetta `bids_root` come arg.
   - Stampa: subject count, ch_types, sampling rate, durata media run.
   - Riusa solo API `mne_bids` (no scraping).
3. NESSUN download di dataset.

### Gate uscita
- Documento DATASET_CANDIDATES.md leggibile e completo.
- Heartbeat finale `.planning/heartbeats_tesi/sonnet1_W1.2.json` con `status=done`.

### Auto-exec whitelist
- WebFetch su `openneuro.org`, `osf.io`, `gwdg.de` (read-only, no auth).
- `pip show mne-bids` (read-only).

### NON-auto-exec
- `pip install` di package non in lista vincolo 2.
- Download dataset (>50 MB).

---

## W1.3 — Verifica end-to-end smoke (sonnet2, dipende da W1.1)

**Owner candidato**: `sonnet2` (parallelo a W1.2)
**Pre-condizione**: W1.1 ✅ DONE.
**Tempo stimato**: 25-35 min.

### Obiettivo
Costruire uno smoke test minimale **end-to-end su matchingpennies** che esercita STEP 1+2+ stub di STEP 3-4, senza scrivere ancora la logica scientifica reale degli step 3-6. Serve a:
- Validare che l'output STC è leggibile e ha shape attesa.
- Validare che `extract_label_time_course` su `aparc` funziona sul dato reale.
- Validare che `mne-connectivity` `spectral_connectivity_epochs` accetta i parcel time courses.
- Identificare gotcha tecnici ANTE step 3-6 reali.

### Input
- Output W1.1.
- API: `mne.read_source_estimate`, `mne.extract_label_time_course`, `mne.read_labels_from_annot`, `mne_connectivity.spectral_connectivity_epochs`.

### Deliverable
1. `tests/test_e2e_matchingpennies.py` (pytest) con:
   - `test_step2_outputs_present` (file `.fif` esistono).
   - `test_stc_loadable` (`mne.read_source_estimate` non raises).
   - `test_aparc_extract_smoke` (`extract_label_time_course` produce array (n_labels, n_times) coerente).
   - `test_connectivity_smoke` (wPLI con n_epochs=10 fittizi, output matrix shape == (n_labels, n_labels, n_freqs)).
2. Report `reports/E2E_SMOKE.md` con: run pytest output, problemi trovati, raccomandazioni per STEP 3 reale.
3. NESSUNA modifica ai moduli `parcellation/`, `connectivity/` (resta vuoto, lo smoke test vive sotto `tests/`).

### Gate uscita
- `pytest tests/test_e2e_matchingpennies.py -v` ritorna 0.
- Heartbeat finale `.planning/heartbeats_tesi/sonnet2_W1.3.json` con `status=done`.

### Auto-exec whitelist
- `pytest tests/test_e2e_matchingpennies.py` (read-only file system, scrive solo report).
- `python -c "import mne; ..."` (validation).

### NON-auto-exec
- Tocco di `parcellation/` o `connectivity/` (sono Step 3-4 veri).
- Download dataset.

---

## Format DISPATCH_QUEUE_tesi.jsonl (proposta schema)

Una riga JSONL per sprint:

```json
{"sprint_id":"W1.1","owner":"sonnet1","status":"queued","priority":1,"deps":[],"created":"2026-05-01T00:00:00Z","estimate_min":30,"deliverable":"config/config_step2_source_matchingpennies.py + reports/STEP2_LOG.md","auto_exec_whitelist":["mne_bids_pipeline","fetch_fsaverage"],"sync_file":".planning/SYNC_W1.1.md"}
```

Stati: `queued` → `claimed` → `in_progress` → `blocked` | `done` | `failed`.

`sync_file` punta a un MD per sprint con istruzioni dettagliate (formato `tmux-dispatch` skill).

## Format heartbeats_tesi/*.json

Una riga JSON per worker per sprint:

```json
{"worker":"sonnet1","sprint_id":"W1.1","status":"in_progress","last_heartbeat":"2026-05-01T01:14:00Z","action_current":"running mne_bids_pipeline --steps source","tokens_used":12000,"blocker":null}
```

Heartbeat ogni 10 min via tmux send-keys o file write.

## Comunicazione orchestratore ↔ workers

- **Dispatch**: `tmux-dispatch` skill — `tmux send-keys -t sonnet1 -l "<cmd>" && tmux send-keys -t sonnet1 C-m` (mai \\n, mai Enter, sempre 2 step).
- **Monitor**: `monitor-lite` skill ogni 7-8 min.
- **Escalation**: blocker → orchestratore aggiorna `.planning/QUESTIONS_FOR_OPERATOR.md` → father controlla con cron 15min e escala via TG se urgente.

---

## Cosa Wave 1 NON fa

- ❌ NON esegue Step 3 reale (parcellazione su EC/EO scientifico).
- ❌ NON esegue Step 4-5-6 reali (connettività/feature/ML su dato reale).
- ❌ NON scarica `ds005385` o `LEMON`.
- ❌ NON tocca repo Tesi/ (vecchio).
- ❌ NON modifica `config/config_step1_matchingpennies.py`.
- ❌ NON crea sprint paralleli senza dipendenze esplicite.

## Wave successive (anteprima, NON in questa proposta)

| Wave | Trigger | Scope |
|------|---------|-------|
| W2 | Q1 risolta + W1 done | Download dataset scientifico finale + STEP1 preprocessing su esso |
| W3 | W2 done | STEP 2 source su dataset scientifico (con epoching sliding 2s per RS) |
| W4 | W3 done | STEP 3 parcellation reale (aparc + Schaefer-100 + neuromaps) |
| W5 | W4 done | STEP 4 connectivity wPLI/PLI/COH/PLV |
| W6 | W5 done | STEP 5-6 features + ML (LR/SVM/RF/GB con LOSO + permutation) |
| W7 | W6 done | STEP 7 verifica E2E + manuscript drafting |

---

*Proposta condizionata. Awaiting operator approval su VISION v3.1 prima di committare i 3 sprint a DISPATCH_QUEUE_tesi.jsonl.*
