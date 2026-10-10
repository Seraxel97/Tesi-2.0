# Vault Import CI Patterns — BAND-5-9-T05

**Sprint**: BAND-5-9-T05  
**Data**: 2026-05-01  
**Owner**: sonnet2-ts  

---

## Sorgenti scansionate (read-only)

| Repo | File | Pattern utili trovati |
|------|------|----------------------|
| `~/Scrivania/Vesta` | `.github/workflows/ci.yml` | `actions/cache@v3`, struttura lint+test |
| `~/Scrivania/CLMForecast` | `.github/workflows/ci.yml` | `actions/cache@v4`, `timeout-minutes`, `concurrency`, `paths-ignore` implicito, diff-coverage |

---

## Pattern importati → Tesi_2.0

| Pattern | Sorgente | Applicato | Motivazione |
|---------|----------|-----------|-------------|
| `paths-ignore: ['**.md', 'reports/**', '.planning/**']` | CLMForecast (adattato) | ✓ `.github/workflows/test.yml` | Skip CI su push doc-only: MD, report, heartbeat |
| `concurrency.group + cancel-in-progress: true` | CLMForecast | ✓ `.github/workflows/test.yml` | Cancella run duplicati su stessa branch/PR |
| `timeout-minutes: 30` | CLMForecast | ✓ job `pytest` | Limite esplicito — parcellation test reale richiede ~20 min |
| `cache key include pyproject.toml` | CLMForecast | ✓ cache step | Invalida cache quando cambiano dipendenze in pyproject.toml |
| `actions/cache@v4` | CLMForecast | già presente | Già aggiornato in DR-VAULT-ci-matrix |

### Pattern CLMForecast scartati (out of scope per Tesi)

| Pattern | Motivo scarto |
|---------|---------------|
| `diff-cover 60% threshold` | Nessun requirements.txt CI-specific; test suite ha 400+ test già |
| `bandit security scan` | Security review già in DR-SEC-* sprint |
| `docker-build` | Nessun Dockerfile in Tesi_2.0 |
| `chaos-tests` | Non applicabile a pipeline EEG |

---

## Diff before/after `.github/workflows/test.yml`

### Before (DR-VAULT-ci-matrix baseline)

```yaml
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  pytest:
    name: Test suite ...
    strategy: ...
    runs-on: ${{ matrix.os }}
    steps:
      ...
      - uses: actions/cache@v4
        with:
          key: ${{ runner.os }}-py${{ matrix.python }}-pip-${{ hashFiles('requirements.txt') }}
```

### After (BAND-5-9-T05)

```yaml
on:
  push:
    branches: [main]
    paths-ignore:           # NEW: skip CI su doc/report/planning changes
      - "**.md"
      - "reports/**"
      - ".planning/**"
  pull_request:
    branches: [main]
    paths-ignore:           # NEW: idem per PR
      - "**.md"
      - "reports/**"
      - ".planning/**"

concurrency:                # NEW: cancella run duplicati
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  pytest:
    name: Test suite ...
    timeout-minutes: 30     # NEW: limite esplicito (parcellation = ~20 min reale)
    strategy: ...
    runs-on: ${{ matrix.os }}
    steps:
      ...
      - uses: actions/cache@v4
        with:
          key: ${{ runner.os }}-py${{ matrix.python }}-pip-${{ hashFiles('pyproject.toml', 'requirements.txt') }}
          #                                                  ^^^^^^^^^^^^^^^^^^ NEW: include pyproject.toml
```

---

## Impatto atteso

- **paths-ignore**: CI non parte su push di heartbeat, report MD, note di planning (~30% dei push in sessione worker sono file .planning/)
- **concurrency**: elimina code duplication quando sonnet1/sonnet2 fanno push in rapida successione sullo stesso branch
- **timeout-minutes: 30**: garantisce che un test bloccato (es. MNE I/O su file corrotto) non consumi risorse CI indefinitamente
- **cache key**: `pyproject.toml` contiene `[tool.pytest.ini_options]` e `[tool.ruff]` — la cache va invalidata quando cambiano
