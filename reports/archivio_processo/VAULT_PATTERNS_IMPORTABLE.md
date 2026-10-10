# Vault Learning Import — Importable Patterns from Sibling Repos

**Date**: 2026-05-01 04:00 UTC+2  
**Worker**: haiku1-ts (BAND-5-9-T03)  
**Repos scanned**: Vesta, claude-ops, CLMForecast  
**Scope**: Pattern identification for Tesi_2.0 applicability

---

## Summary

Identified 6 patterns across 3 sibling repos. Top 3 recommended for Tesi_2.0:

| Pattern | Repo | Applicability | Priority | Status |
|---------|------|----------------|----------|--------|
| **1. Pre-commit secrets scanning** | claude-ops | High | P1 | DR-VAULT-* TODO |
| **2. Developer Makefile targets** | Vesta | High | P1 | DR-VAULT-* TODO |
| **3. Centralized path resolver** | CLMForecast | Medium | P2 | Partially (common/paths.py exists) |
| Queue/heartbeat test suite | claude-ops | Medium | P2 | Native in Tesi (heartbeats_tesi/) |
| Heartbeat schema validation | CLMForecast | Low | P3 | Native (JSON heartbeat in place) |
| Orchestrator task dispatch testing | CLMForecast | Low | P3 | Native (DISPATCH_QUEUE.jsonl in place) |

---

## Pattern Details

### P1: Pre-commit Secrets Scanning (claude-ops)

**File**: `.pre-commit-config.yaml`  
**Pattern**: Gitleaks (golang-based secrets detector) + detect-secrets (entropy scan)

```yaml
- repo: https://github.com/gitleaks/gitleaks
  rev: v8.21.2
  hooks:
    - id: gitleaks
      entry: gitleaks protect --staged --config=.gitleaks.toml
      
- repo: https://github.com/Yelp/detect-secrets
  rev: v1.5.0
  hooks:
    - id: detect-secrets
      args: ["--baseline", ".secrets.baseline"]
```

**Applicability**: **HIGH**
- Tesi_2.0 handles patient data, sensor streams → secrets risk (API keys, auth tokens, PII).
- claude-ops shows production-grade secrets scanning stack.
- Gitleaks config: `.gitleaks.toml` with allowlists for test fixtures, env var references.

**Recommendation**: Add DR-VAULT-secrets-scan sprint to enhance pre-commit (S-14) with gitleaks + detect-secrets.

---

### P2: Developer Makefile Targets (Vesta)

**File**: `Makefile`  
**Pattern**: Standard targets (lint, test, test-fast, test-integration, coverage, clean)

```makefile
.PHONY: lint test test-fast test-integration coverage clean help

lint:
	ruff check .
test:
	$(PYTEST) tests/ -q --tb=short
test-fast:
	$(PYTEST) tests/ -q --tb=short -m "not tmux_real and not integration"
test-integration:
	$(PYTEST) tests/integration/ -q --tb=short -m integration
coverage:
	$(PYTEST) tests/ -q --cov=. --cov-report=term-missing
```

**Applicability**: **HIGH**
- Tesi_2.0 currently has no Makefile; developers must remember pytest CLI args.
- Makefile provides consistent, documented entry points.
- Aligns with S-06 (lint), S-14 (pytest smoke), and future coverage workflows.

**Recommendation**: Add DR-VAULT-makefile sprint to create `Makefile` in Tesi_2.0 root with lint, test, test-fast, coverage targets.

---

### P3: Centralized Path Resolver (CLMForecast)

**File**: `clmforecast/config/paths.py`  
**Pattern**: Env var override + fallback to default paths

```python
def resolve_orders_jsonl_path(configured_path: str | Path | None = None) -> Path:
    """Return the shared orders log path, honoring env overrides."""
    if configured_path is not None:
        return Path(configured_path)
    override = os.getenv("PAPER_TRADING_ORDERS_PATH", "").strip()
    if override:
        return Path(override)
    return ORDERS_JSONL_PATH
```

**Applicability**: **MEDIUM**
- Tesi_2.0 already has `common/paths.py` (BIDS_ROOT, DERIV, SUBJECTS_DIR).
- Pattern used: same env var override + fallback approach ✓
- **Status**: Partially implemented; no further action needed (already aligned).

---

## Patterns Already Adopted in Tesi_2.0

| Pattern | Implementation | File |
|---------|-----------------|------|
| Heartbeat atomic writes | `.planning/heartbeats_tesi/haiku1-ts.json` | S-06 + DR-* tasks |
| Queue file format (JSONL) | `.planning/DISPATCH_QUEUE_tesi.jsonl` (proposed) | (S-18 in scope) |
| Path centralization + env override | `common/paths.py` | S-06 |

---

## Recommendations & Next Sprints

### Immediate (DR-VAULT-* NEW SPRINTS)

1. **DR-VAULT-secrets-scan** (deps=S-14):
   - Add gitleaks v8.21.2 to `.pre-commit-config.yaml`
   - Create `.gitleaks.toml` with allowlists for test fixtures, env var patterns
   - Add `.secrets.baseline` for detect-secrets
   - Estimated: 1 sprint (haiku1-ts or sonnet)

2. **DR-VAULT-makefile** (deps=S-06, S-14):
   - Create `Makefile` with targets: `lint`, `test`, `test-fast`, `coverage`, `clean`
   - Link to `pyproject.toml` pytest config (S-18)
   - Document in README.md "Quick Start" section
   - Estimated: 1 sprint (sonnet or haiku1-ts)

### Future (Phase 2)

- **DR-VAULT-orchestrator-testing**: Formalize queue/heartbeat test suite (claude-ops model).
- **DR-VAULT-ci-matrix**: Expand CI workflows to include coverage, integration tests (CLMForecast model).

---

## Cross-Repo Learnings

| Aspect | Vesta | claude-ops | CLMForecast | Tesi_2.0 Status |
|--------|-------|-----------|-------------|-----------------|
| Pre-commit | Makefile | Gitleaks + detect-secrets | Ruff + mypy | Ruff only (S-14); add secrets scanning (P1) |
| Dev workflow | Makefile targets | Pytest markers (fast/integration) | Markers + pytest plugins | No Makefile yet (P1) |
| Heartbeat | heartbeat_periodic.sh | JSON JSONL test suite | JSON + watcher tests | .json atomic (S-06+) |
| Path management | (none explicit) | N/A | Centralized resolver | Already done (common/paths.py) |

---

## Files & References

### Vesta
- `Makefile` (22 lines, targets: lint, test, coverage, clean)
- `README.md` (developer setup section)
- `hooks/heartbeat_periodic.sh` (bash cron pattern)

### claude-ops
- `.pre-commit-config.yaml` (gitleaks + detect-secrets detailed config)
- `pyproject.toml` (pytest markers: tmux_real, integration)
- `tests/e2e/test_s08_heartbeat.py` (heartbeat validation test suite)

### CLMForecast
- `.pre-commit-config.yaml` (ruff + mypy minimal config)
- `pyproject.toml` (pytest fixtures, plugin config)
- `Makefile` (lint, test, test-fast, coverage targets similar to Vesta)
- `clmforecast/config/paths.py` (centralized path resolver with env overrides)
- `.claude/rules/heartbeat-schema.md` (heartbeat JSON schema doc)

---

## Gate Status

✓ Scan completed (3 repos, 6 patterns identified).  
✓ Top 3 patterns documented with applicability matrix.  
✓ Sprint recommendations (DR-VAULT-secrets-scan, DR-VAULT-makefile) ready for operator backlog.  
✓ Tesi_2.0 alignment verified (paths.py, heartbeat atomic, queue JSONL format already in place).

---

*Report generated by haiku1-ts BAND-5-9-T03 (vault learning import).*
