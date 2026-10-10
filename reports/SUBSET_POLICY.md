# Subset Policy — ds005385 Pilot

**Sprint**: S-100b  
**Data**: 2026-05-01  
**Worker**: sonnet2-ts  
**Cross-ref**: `config/labels_ds005385.py`, `reports/DS005385_STRUCTURE.md`, `config/subjects_whitelist.py`

---

## Vincolo operatore (HARD)

> "limit subjects + cleaning mirato. NO 200-sub full run. Tenere solo dati ESSENZIALI per pipeline. Max N=10-20 sub."

**N scelto**: 15 (middle range 10-20, lascia margine per drop-out preprocessing).

---

## Criteri valutati

| Opzione | Descrizione | N | Pro | Contro |
|---------|-------------|---|-----|--------|
| **(A) Random seed=42** | `random.sample(pool_179, 15, seed=42)` | 15 | Riproducibile, unbiased | Non ottimizzato per qualita' |
| (B) Quality-filtered | Esclude sub con quality flag aggiuntivi | ~15-20 | Dati piu' puliti | Richiede preprocessing preliminare |
| (C) Stratified age/sex | Campione bilanciato per eta' e sesso | 15 | Rappresentativita' demografica | Over-engineering per pilot |

**Default applicato: (A) random seed=42, N=15.**

Rationale: il pilot S-101 serve a validare la pipeline tecnica, non a produrre risultati statistici finali.
La riproducibilita' (seed fisso) e la semplicita' sono prioritarie in questa fase.

---

## Pool di selezione

| Parametro | Valore |
|-----------|--------|
| Soggetti totali nel dataset (scaricati) | 200 |
| Esclusi per `late_ses1 > 0` | 21 |
| Pool valido (`ses-1`, no late trigger) | **179** |
| Selezionati | **15** |

**Esclusi** (21 sub con late_ses1 > 0): sub-008, sub-009, sub-013, sub-027, sub-037, sub-049, sub-052, sub-055, sub-075, sub-085, sub-093, sub-097, sub-106, sub-108, sub-114, sub-115, sub-138, sub-170, sub-176, sub-179, sub-183.

---

## Subset finale (N=15)

| Subject | Age | Sex | Hand | ses-2 | EO EDF | EC EDF |
|---------|-----|-----|------|-------|--------|--------|
| sub-007 | 24 | F | right | no | OK | OK |
| sub-010 | 23 | F | right | no | OK | OK |
| sub-011 | 50 | F | right | no | OK | OK |
| sub-026 | 59 | F | right | no | OK | OK |
| sub-031 | 26 | F | right | no | OK | OK |
| sub-033 | 32 | M | right | yes | OK | OK |
| sub-041 | 53 | M | right | yes | OK | OK |
| sub-066 | 33 | F | right | no | OK | OK |
| sub-071 | 64 | F | right | no | OK | OK |
| sub-080 | 64 | F | left | yes | OK | OK |
| sub-125 | 70 | M | right | no | OK | OK |
| sub-157 | 57 | F | right | no | OK | OK |
| sub-169 | 63 | F | right | no | OK | OK |
| sub-185 | 31 | M | right | no | OK | OK |
| sub-195 | 60 | F | right | yes | OK | OK |

### Demografiche subset

| Parametro | Valore |
|-----------|--------|
| N | 15 |
| Eta' range | 23-70 anni |
| Eta' media | 47.3 anni |
| Sesso | F=11, M=4 |
| Mancini | 1 (sub-080) |
| Con ses-2 | 4 (sub-033, sub-041, sub-080, sub-195) |

**File EDF verificati**: 15/15 OK — `ses-1/eeg/{sub}_ses-1_task-EyesOpen_acq-pre_eeg.edf` + `_task-EyesClosed_acq-pre_eeg.edf` presenti per tutti.

---

## Quality flags applicate

1. **Esclusione late_ses1 > 0** (21 sub): trigger ritardati indicano acquisizione non continua — esclusi preventivamente.
2. **Sessione**: `ses-1` only (massima copertura; ses-2 solo per 4 sub nel subset).
3. **Acquisizione**: `acq-pre` only (baseline resting-state; acq-post esclude ~1/4 dei sub).

Nessun quality flag aggiuntivo applicato (non richiesto per criterio A).

---

## Riproducibilita'

```python
import random, csv
from pathlib import Path

EXCLUDE_LATE = {
    "sub-008","sub-009","sub-013","sub-027","sub-037",
    "sub-049","sub-052","sub-055","sub-075","sub-085",
    "sub-093","sub-097","sub-106","sub-108","sub-114",
    "sub-115","sub-138","sub-170","sub-176","sub-179","sub-183",
}
tsv = Path("data/raw/ds005385/participants.tsv")
present = {d.name for d in Path("data/raw/ds005385").iterdir() if d.name.startswith("sub-")}
with open(tsv) as f:
    rows = list(csv.DictReader(f, delimiter="\t"))
pool = sorted(
    [r["participant_id"] for r in rows
     if r["participant_id"] in present
     and r["participant_id"] not in EXCLUDE_LATE
     and r.get("session1") == "yes"],
)
random.seed(42)
subset = sorted(random.sample(pool, 15))
# → ['sub-007', 'sub-010', 'sub-011', 'sub-026', 'sub-031', 'sub-033',
#    'sub-041', 'sub-066', 'sub-071', 'sub-080', 'sub-125', 'sub-157',
#    'sub-169', 'sub-185', 'sub-195']
```

---

## Pilot 5-sub plan (per STEP 2 S-101)

I primi 5 soggetti del subset (ordinati) per il pilot iniziale:

1. **sub-007** — F, 24y, right-handed
2. **sub-010** — F, 23y, right-handed
3. **sub-011** — F, 50y, right-handed
4. **sub-026** — F, 59y, right-handed
5. **sub-031** — F, 26y, right-handed

> STEP 2 (S-101) gated OPERATOR_APPROVE_5SUB — non auto-claimato.
