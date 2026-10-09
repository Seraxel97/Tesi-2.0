# Makefile Completeness Audit

**Generated**: 2026-05-01T07:15:00+02:00

---

## Target Inventory

### Vesta Makefile

| Target | Type | Scope |
|--------|------|-------|
| clean | maintenance | Remove build artifacts |
| coverage | testing | Generate coverage report |
| help | documentation | Show available targets |
| lint | quality | Run linting checks |
| test | testing | Run full test suite |
| test-fast | testing | Run fast subset |
| test-integration | testing | Run integration tests |

**Total**: 7 targets

### CLMForecast Makefile

| Target | Type | Scope |
|--------|------|-------|
| coverage-core | testing | Core module coverage |
| format | quality | Auto-format code |
| lint | quality | Run linting checks |
| rotate-log | maintenance | Rotate log files |
| smoke-test | testing | Quick smoke test |

**Total**: 5 targets

### Tesi_2.0 Makefile (Current)

| Target | Type | Scope |
|--------|------|-------|
| bench | pipeline | Run benchmark matrix (700 runs) |
| clean | maintenance | Remove cache/test artifacts |
| format | quality | Auto-format with ruff |
| help | documentation | Show available targets |
| lint | quality | Run ruff check + format check |
| run-step1 | pipeline | Run STEP 1 preprocessing |
| run-step2 | pipeline | Run STEP 2 source reconstruction |
| test | testing | Run full pytest suite |

**Total**: 8 targets

---

## Comparative Analysis

### Present in All Three Repos

- `help` (Vesta, Tesi)
- `lint` (all three)
- `clean` (Vesta, Tesi)
- `format` (CLMForecast, Tesi)
- `test` (Vesta, Tesi)

### Recommended Additions to Tesi_2.0

| Target | From | Rationale | Implementation |
|--------|------|-----------|-----------------|
| `coverage` | Vesta | Test coverage tracking (pytest-cov available) | Run pytest with --cov-report=html |
| `audit` | (proposed) | Repo sanity check (scripts/repo_sanity.sh exists) | bash scripts/repo_sanity.sh |
| `clean-cache` | (proposed) | Remove joblib/nilearn caches | rm -rf data/derivatives/_cache .joblib_cache |
| `test-fast` | Vesta | Quick smoke test (tests/test_smoke.py) | pytest tests/test_e2e_smoke_minimal.py |

---

## Recommendations

**Priority 1 (Add immediately)**:
- ✓ `audit`: Already have script, integrates repo sanity check
- ✓ `clean-cache`: Useful for cleanup before benchmarks

**Priority 2 (Consider)**:
- `coverage`: pytest-cov installed, good for CI integration
- `test-fast`: Quick validation, already possible via pytest subset

---

## Implementation Status

- ✓ `audit` target added to Makefile
- ✓ `clean-cache` target added to Makefile
- Considered but deferred: `coverage`, `test-fast`

---

**Verdict**: Tesi_2.0 Makefile now in line with vault patterns for maintenance/testing. 8 → 10 targets.
