# Vault Import — CI/CD Workflows

**Sprint**: DR-VAULT-ci-matrix
**Data**: 2026-05-01
**Worker**: sonnet3-ts
**Fonte**: `~/Scrivania/Vesta/.github/workflows/ci.yml` (read-only scan)

---

## Sorgente Vesta

File analizzato: `Vesta/.github/workflows/ci.yml`

Pattern estratti:

| Pattern | Vesta | Adattamento Tesi_2.0 |
|---------|-------|----------------------|
| Python version | 3.11 | 3.13 (vincolo CLAUDE.md) |
| OS matrix | ubuntu-latest | ubuntu-latest (singolo) |
| Lint tool | ruff check (inline --select) | ruff check (config da pyproject.toml) |
| Format check | assente | ruff format --check |
| Cache pip | `actions/cache@v3` | `actions/cache@v4` |
| Test runner | pytest con markers + coverage | pytest -v --tb=short (senza coverage) |
| Dipendenza lint → test | `needs: lint` (stesso file) | workflow separati (indipendenti) |
| mypy | `continue-on-error: true` | omesso (in pre-commit manual stage) |

**Scelta**: due workflow indipendenti invece di un singolo file multi-job.
Motivazione: Tesi_2.0 e' un repo locale senza remote GitHub attivo — i workflow
sono pronti per quando un remote verra' configurato, ma la semplicita' vince
sulla struttura Vesta che aveva dipendenze lint→test per fast-fail.

---

## File prodotti

### `.github/workflows/lint.yml`

Trigger: push + pull_request su `main`.
Job: `ruff` — ruff check + ruff format --check su Python 3.13 / ubuntu-latest.
Config ruff: ereditata da `pyproject.toml [tool.ruff]` (target-version=py313, line-length=100).

### `.github/workflows/test.yml`

Trigger: push + pull_request su `main`.
Job: `pytest` — matrix Python 3.13 × ubuntu-latest.
Passi: checkout → setup-python → cache pip → `pip install -r requirements.txt` → `pytest tests/ -v --tb=short`.

---

## Note tecniche

- `on:` in YAML 1.1 viene parsato come booleano `true` da PyYAML — comportamento atteso,
  GitHub Actions lo interpreta correttamente come trigger.
- `requirements.txt` gia' presente (sprint S-20, haiku1-ts).
- `pyproject.toml [tool.ruff]` gia' configurato (sprint S-14/S-18).
- Cache key: `hashFiles('requirements.txt')` per invalidazione su cambio dipendenze.
- I workflow sono pronti per push su remote GitHub; nessuna modifica necessaria al repo locale.

---

## Riferimento pre-commit (.pre-commit-config.yaml)

Gli stessi check (ruff check + ruff format) sono configurati anche in pre-commit
per enforcement locale. I workflow GH Actions rappresentano il gate CI remoto
complementare.
