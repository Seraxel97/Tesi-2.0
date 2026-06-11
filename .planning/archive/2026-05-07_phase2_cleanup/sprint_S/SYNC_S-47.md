# SYNC S-47 — sonnet2-ts

**Sprint**: Migration plan post-Q1 risolto: dispatcher dataset finale ds005385
**Owner**: sonnet2-ts
**Branch**: migration/post-q1
**Pre-condizione**: S-29 done, S-40 done, Q1 RISOLTO (ds005385 confirmed).

## Deliverable

`reports/MIGRATION_POST_Q1_PLAN.md`:

1. **Header**: Q1 risolto T13:34, dataset ds005385 confermato.
2. **Decision tree**: 
   - Symlink applicato (T18:30) ✅.
   - Subset policy N=15 (S-100b output) ✅.
   - PILOT 5 sub (S-101 in flight) ✅.
   - Step 3-7 sequenziali gated (S-103..S-107).
3. **Migration steps**:
   - S-100/S-100b/S-100c done.
   - S-101 PILOT 5 sub in flight (sonnet1-ts).
   - Post S-101 done: gate operatore → S-103 parcellation.
   - Post S-103 done: S-104 connectivity wPLI banda alpha.
   - Post S-104 done: S-105 features.
   - Post S-105 done: S-106 ML primo run reale.
   - Post S-106 done: S-107 esperimenti minimi.
4. **Rischi**:
   - Disk critical 22 GB liberi → S-101 5 sub ok, full scale (200) impossibile.
   - Operator hard constraint N max=20 → S-102 deprecated.
   - Source recon fail rendering 3D (xvfb) → bypass `finalize_inverse.py` already in place.
5. **Cross-ref**:
   - `config/subjects_whitelist.py` (S-100b)
   - `config/labels_ds005385.py` (S-100)
   - `reports/STEP2_DS005385_PILOT.md` (S-101 output futuro)

## Vincoli
- 1 file output, 800-1500 parole.
- Cross-ref ai file esistenti.

## Gate
- File esiste.
- HB sonnet2-ts done verdict=PASS task=S-47.
- Auto-claim post: idle (waiting S-101 done per next sprint scientifici).
