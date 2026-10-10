# Mock BIDS Validation Report

**Sprint**: S-52  
**Data**: 2026-05-01  
**Worker**: sonnet2-ts  
**Status**: OK

---

## Test 1 — Smoke test generazione (5 soggetti)

| Check | Risultato |
|-------|-----------|
| generate (generate_mock_bids.py) | PASS |
| dataset_description.json esiste | PASS |
| participants.tsv esiste | PASS |
| BIDSVersion presente | PASS (1.9.0) |
| DatasetType | PASS (raw) |
| Struttura 5 soggetti | PASS (5/5) |
| mne_bids import | PASS |

**Errori**: nessuno  
**Cleanup**: directory temporanea rimossa ✓

---

## Test 2 — Validazione dataset esistente (data/mock_eceo, 50 soggetti)

| Check | Risultato |
|-------|-----------|
| Soggetti presenti | 50/50 |
| Struttura eeg/ per ogni sub | PASS (0 errori) |
| File per run-1 e run-2 (.vhdr/.vmrk/.eeg/.json) | PASS (0 mancanti) |

**Errori strutturali**: 0

---

## Conclusione

Dataset mock `data/mock_eceo` (S-29) supera tutti i smoke test.  
Script di validazione: `scripts/validate_mock_bids.py`
