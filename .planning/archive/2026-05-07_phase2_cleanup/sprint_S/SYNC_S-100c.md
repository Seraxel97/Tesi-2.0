# SYNC S-100c — haiku1-ts

**Sprint**: [WAVE-SCIENTIFIC-001c] Data dir audit + cleanup
**Owner**: haiku1-ts
**Branch**: scientific/step1-data-audit
**Pre-condizione**: nessuna.

## OPERATOR CONSTRAINT

> "disk critical 22 GB liberi su 915 GB → cleanup essenziale prima di scientific exec".

## Cosa fare

1. `scripts/data_audit.sh`:
   ```bash
   #!/usr/bin/env bash
   ROOT="/home/seraxel/Scrivania/Tesi_2.0"
   echo "=== data/ inventory ==="
   du -sh "$ROOT/data"/* 2>/dev/null | sort -h
   echo
   echo "=== large files >100MB ==="
   find "$ROOT/data" -type f -size +100M -exec ls -lh {} + 2>/dev/null | head -20
   echo
   echo "=== orphan derivatives (no source sub) ==="
   if [ -d "$ROOT/data/derivatives" ]; then
       ls -la "$ROOT/data/derivatives/mne-bids-pipeline/" 2>/dev/null
   fi
   echo
   echo "=== mock_eceo size (S-29 generated) ==="
   du -sh "$ROOT/data/mock_eceo" 2>/dev/null
   echo
   echo "=== free disk ==="
   df -h "$ROOT"
   ```

2. Run + dump:
   ```bash
   bash scripts/data_audit.sh > reports/DATA_AUDIT.md 2>&1
   ```

3. `reports/DATA_AUDIT.md`:
   - Header timestamp.
   - Output script (inventory data/).
   - Sezione "Cleanup raccomandato": lista candidati (con stima size recoverable).
   - Sezione "Disk delta atteso post-cleanup".

4. **NIENTE delete automatico** — solo report + raccomandazioni. Father deciderà cleanup applicabile.

## Vincoli

- 2 file output.
- NIENTE delete su `data/raw/` (read-only symlink).
- NIENTE delete su `data/derivatives/mne-bids-pipeline/` (output STEP 1 valido).
- Solo audit + recommendations.

## Gate

- 2 file deliverable.
- HB haiku1-ts done verdict=PASS task=S-100c.
- Queue S-100c status=done.
- Auto-claim post: idle MSG_TO_ORCH (haiku free).
