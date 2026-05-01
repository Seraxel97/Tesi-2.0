# Handover — {WORKER} → next session

**Generato**: {TIMESTAMP}  
**Worker**: {WORKER} ({SESSION_NAME})  
**Branch attivo**: {BRANCH}

---

## Sprint completati questa sessione

| ID | Scope | Verdict | Commit |
|----|-------|---------|--------|
| {S-XX} | {scope} | PASS/FAIL | {sha7} |

## Sprint in corso (se sessione interrotta)

| ID | Scope | Stato | Blockers |
|----|-------|-------|----------|
| — | — | — | — |

## Branch creati / push status

```
{branch_name}  →  pushed: YES/NO  →  PR: YES/NO
```

## Queue status (al momento del handover)

```
queued:   N
claimed:  N
done:     N
blocked:  N
```

Sprint claimabili al successivo boot:
- {ID} | {scope} | deps=[...]

## Blockers attivi

- [ ] {descrizione blocker, referenza ticket/file}

## Decisioni prese (non ovvie dal codice)

- {decisione + motivazione}

## Next actions per il worker successivo

1. `cat .planning/DISPATCH_QUEUE_tesi.jsonl | python3 -c "..."` → claim primo sprint disponibile
2. Verificare heartbeat stale (>15 min senza aggiornamento)
3. Leggere MSG_TO_ORCH pending se ci sono

## Artefatti prodotti

```
{path/to/file}  ({size}, {descrizione})
```

## Note finali

{osservazioni libere — contesto che non emerge dalla codebase}
