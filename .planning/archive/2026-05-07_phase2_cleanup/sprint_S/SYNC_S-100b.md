# SYNC S-100b — sonnet2-ts

**Sprint**: [WAVE-SCIENTIFIC-001b] STEP 1 SUBSET POLICY definizione N=10-20 max
**Owner**: sonnet2-ts
**Branch**: scientific/step1-subset-policy
**Pre-condizione**: S-100 done (BIDS analysis + EO/EC mapping).

## OPERATOR HARD CONSTRAINT

> "limit subjects + cleaning mirato. NO 200-sub full run. Tenere solo dati ESSENZIALI per pipeline. Max N=10-20 sub."

## Cosa fare

1. **Leggi `reports/DS005385_STRUCTURE.md` + `config/labels_ds005385.py`** (output S-100).

2. **Definisci subset policy**:
   - Criterio scelta: 3 opzioni da proporre, default=A.
     - **(A) Random seed=42**: random.choice 15 sub da participants.tsv (riproducibile).
     - **(B) Quality-filtered**: esclude sub con quality flag (se README ha sub_excluded list).
     - **(C) Stratified by age/sex**: 15 sub bilanciati age + sex.
   - Default: (A) random seed=42 N=15 (target middle range 10-20, lascia margine).

3. **Output**:
   - `config/subjects_whitelist.py`:
     ```python
     """Subjects whitelist ds005385 — operator HARD constraint N max=20."""
     SUBSET_POLICY = "random_seed_42_N15"
     N_SUBJECTS = 15
     SUBJECT_WHITELIST = ["sub-001", "sub-005", ...]  # 15 entries
     ```
   - `reports/SUBSET_POLICY.md`:
     - Header: operator constraint, criterio scelto, razionale.
     - Lista sub finale (15 entries con metadata: age, sex, n_runs).
     - Note quality flags applicate.
     - Cross-ref: `config/labels_ds005385.py`, `reports/DS005385_STRUCTURE.md`.

## Vincoli

- N MAX = 20 (HARD).
- N MIN suggerito = 10 (statistica minimale).
- DEFAULT N = 15 (middle).
- random_state = 42 ovunque.
- 2 file output.

## Gate

- 2 file deliverable.
- HB sonnet2-ts done verdict=PASS task=S-100b.
- Queue S-100b status=done.
- **POST-GATE OBBLIGATORIO**: scrivi `.planning/MSG_TO_FATHER_<ts>_S100b_DONE.md` con: subset list + N + criterio + STEP 2 PILOT 5-sub plan (lista 5 prima sub da subset).
- Auto-claim post: NON fare. STEP 2 (S-101) gated OPERATOR_APPROVE_5SUB.
