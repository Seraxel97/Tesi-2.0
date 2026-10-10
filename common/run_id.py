"""Standard run-id generator: timestamp + git_sha + config_hash.

Posizione nella pipeline: infrastruttura trasversale agli STEP 1-7 (non appartiene a un singolo step).
"""

from __future__ import annotations

import hashlib
import subprocess
from datetime import UTC, datetime
from pathlib import Path

_REPO_ROOT = Path(__file__).parent.parent


def _git_sha_short(length: int = 8) -> str:
    """SHA git corto del commit corrente.

    Args:
        length: Numero massimo di caratteri.

    Returns:
        SHA troncato, oppure "nogit" se git non e' disponibile o va in timeout.
    """
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            cwd=str(_REPO_ROOT),
            timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()[:length]
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return "nogit"


def _config_hash_short(config_path: Path, length: int = 8) -> str:
    """Hash SHA-256 troncato del contenuto di un file di configurazione.

    Args:
        config_path: File di config.
        length: Numero di caratteri esadecimali restituiti.

    Raises:
        FileNotFoundError: Se il file non esiste.
    """
    sha = hashlib.sha256(config_path.read_bytes()).hexdigest()
    return sha[:length]


def generate(
    config_path: str | Path | None = None,
    *,
    prefix: str = "run",
    ts: datetime | None = None,
    sha_len: int = 8,
    hash_len: int = 8,
) -> str:
    """Genera un run-id standard: {prefix}_{ts}_{git_sha}[_{config_hash}].

    Parameters
    ----------
    config_path:
        Path al file config (opzionale). Se fornito, appende il config_hash.
    prefix:
        Prefisso dell'id (default 'run').
    ts:
        Timestamp da usare (default: now UTC).
    sha_len:
        Lunghezza del git sha short (default 8).
    hash_len:
        Lunghezza del config hash short (default 8).

    Returns
    -------
    str
        Run-id nel formato ``{prefix}_{YYYYMMDDTHHMMSS}_{git_sha}[_{config_hash}]``.
    """
    if ts is None:
        ts = datetime.now(UTC)
    ts_str = ts.strftime("%Y%m%dT%H%M%S")
    sha = _git_sha_short(sha_len)
    parts = [prefix, ts_str, sha]
    if config_path is not None:
        p = Path(config_path)
        if p.exists():
            parts.append(_config_hash_short(p, hash_len))
    return "_".join(parts)
