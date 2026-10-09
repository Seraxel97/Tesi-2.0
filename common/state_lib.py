"""Schema migration framework per file JSONL di stato (queue, heartbeats).

Pattern da skill schema_migration. Le migrazioni sono registrate via
@register_migration e scope su file fisici tramite state file companion.

Uso:
    from common.state_lib import migrate_on_load, apply_migration, rollback_migration
    from pathlib import Path

    queue = Path(".planning/DISPATCH_QUEUE_tesi.jsonl")
    migrate_on_load(queue, target_version="002")

Posizione nella pipeline: infrastruttura trasversale agli STEP 1-7 (non appartiene a un singolo step).
"""

from __future__ import annotations

import importlib.util
import json
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

# ── Registry globale ──────────────────────────────────────────────────────────

# ===== Registro migrazioni =====


@dataclass
class _MigrationEntry:
    """Voce di registro: versione, descrizione e funzioni forward/backward di una migrazione."""

    version: str
    description: str
    forward_fn: Callable[[list[dict]], list[dict]]
    backward_fn: Callable[[list[dict]], list[dict]]


_REGISTRY: dict[str, _MigrationEntry] = {}
_LOADED_MIGRATION_FILES: set[Path] = set()

_MIGRATIONS_DIR = Path(__file__).parent.parent / ".planning" / "migrations"


def register_migration(version: str, description: str = "") -> Callable:
    """Decorator per registrare una migrazione nel registry globale.

    La classe decorata deve definire:
      - ``forward(records: list[dict]) -> list[dict]``
      - ``backward(records: list[dict]) -> list[dict]``
    """

    def decorator(cls):
        """Registra la classe come migrazione.

        Raises:
            ValueError: Se la versione e' gia' registrata.
            TypeError: Se la classe non definisce forward() e backward().
        """
        if version in _REGISTRY:
            raise ValueError(f"Migration version already registered: {version!r}")
        if not (hasattr(cls, "forward") and hasattr(cls, "backward")):
            raise TypeError(f"{cls.__name__} must define forward() and backward()")
        _REGISTRY[version] = _MigrationEntry(
            version=version,
            description=description,
            forward_fn=cls.forward,
            backward_fn=cls.backward,
        )
        return cls

    return decorator


# ── Caricamento dinamico migrazioni ───────────────────────────────────────────


def _load_migration_modules() -> None:
    """Importa tutti i file [0-9]*.py in .planning/migrations/ per trigger decorator.

    Idempotente: file gia' caricati vengono saltati.
    """
    for f in sorted(_MIGRATIONS_DIR.glob("[0-9]*.py")):
        resolved = f.resolve()
        if resolved in _LOADED_MIGRATION_FILES:
            continue
        spec = importlib.util.spec_from_file_location(f"_tesi_migration_{f.stem}", f)
        if spec and spec.loader:
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            _LOADED_MIGRATION_FILES.add(resolved)


# ── State file per file target ────────────────────────────────────────────────

# ===== Stato e I/O JSONL =====


def _state_path(target: Path) -> Path:
    """Percorso del file di stato (nascosto) delle migrazioni applicate a `target`."""
    return target.parent / f".{target.name}.migration_state.json"


def _load_state(target: Path) -> dict:
    """Legge lo stato delle migrazioni; se assente o corrotto restituisce {"applied": []}."""
    sp = _state_path(target)
    if not sp.exists():
        return {"applied": []}
    try:
        return json.loads(sp.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {"applied": []}


def _save_state(target: Path, state: dict) -> None:
    """Scrive lo stato delle migrazioni su disco (JSON indentato)."""
    _state_path(target).write_text(
        json.dumps(state, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _is_applied(target: Path, version: str) -> bool:
    """True se la migrazione `version` risulta gia' applicata a `target`."""
    return any(e["version"] == version for e in _load_state(target).get("applied", []))


# ── I/O JSONL ─────────────────────────────────────────────────────────────────


def _read_records(target: Path) -> list[dict]:
    """Legge un file JSONL come lista di dict, ignorando righe vuote o malformate."""
    if not target.exists():
        return []
    out = []
    for line in target.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return out


def _write_records(target: Path, records: list[dict]) -> None:
    """Riscrive per intero il file JSONL con i record forniti."""
    target.write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in records),
        encoding="utf-8",
    )


# ── API pubblica ──────────────────────────────────────────────────────────────

# ===== Applicazione e rollback =====


def apply_migration(version: str, target: Path) -> dict:
    """Applica la migrazione ``version`` su ``target``. Idempotente.

    Returns:
        dict con ``version``, ``status`` (applied|skipped), ``records_affected``.
    """
    _load_migration_modules()
    if version not in _REGISTRY:
        raise KeyError(f"Migration {version!r} not registered.")
    if _is_applied(target, version):
        return {"version": version, "status": "skipped", "records_affected": 0}

    entry = _REGISTRY[version]
    records = _read_records(target)
    transformed = entry.forward_fn(list(records))
    _write_records(target, transformed)

    state = _load_state(target)
    state.setdefault("applied", []).append(
        {
            "version": version,
            "direction": "forward",
            "ts": datetime.now(UTC).isoformat(),
            "records_before": len(records),
            "records_after": len(transformed),
        }
    )
    _save_state(target, state)
    return {"version": version, "status": "applied", "records_affected": len(transformed)}


def rollback_migration(version: str, target: Path) -> dict:
    """Esegue il rollback della migrazione ``version`` su ``target``. Idempotente.

    Returns:
        dict con ``version``, ``status`` (rolled_back|skipped), ``records_affected``.
    """
    _load_migration_modules()
    if version not in _REGISTRY:
        raise KeyError(f"Migration {version!r} not registered.")
    if not _is_applied(target, version):
        return {"version": version, "status": "skipped", "records_affected": 0}

    entry = _REGISTRY[version]
    records = _read_records(target)
    reverted = entry.backward_fn(list(records))
    _write_records(target, reverted)

    state = _load_state(target)
    state["applied"] = [e for e in state.get("applied", []) if e["version"] != version]
    _save_state(target, state)
    return {"version": version, "status": "rolled_back", "records_affected": len(reverted)}


def load_schema_version(target: Path) -> str | None:
    """Versione massima applicata per ``target``, o None se nessuna."""
    applied = _load_state(target).get("applied", [])
    return max((e["version"] for e in applied), default=None)


def migrate_on_load(jsonl_path: Path, target_version: str) -> list[dict]:
    """Applica tutte le migrazioni <= target_version non ancora applicate.

    Idempotente: chiamate successive sono no-op se gia' aggiornato.

    Returns:
        Lista di result dict (una per migrazione applicata o skippata).
    """
    _load_migration_modules()
    results = []
    for version in sorted(v for v in _REGISTRY if v <= target_version):
        result = apply_migration(version, jsonl_path)
        results.append(result)
    return results
