#!/usr/bin/env python3
"""Verifica requirements.txt contro le versioni dei pacchetti installati.

Scopo:
    Controllo di riproducibilita': ogni pacchetto fissato con ``==`` in
    requirements.txt deve avere esattamente la stessa versione installata.

Input:
    ``requirements.txt`` nella radice del repo (righe ``pacchetto==versione``;
    commenti e righe vuote ignorati) e metadati ``importlib.metadata``.

Output:
    Tabella Required/Installed/Match su stdout. Nessun file scritto.
    Exit code 0 se tutte le versioni coincidono, 1 altrimenti.

Esempio:
    python scripts/verify_requirements.py
"""

from __future__ import annotations

import importlib.metadata
import re
import sys
from pathlib import Path

REQUIREMENTS_PATH = Path(__file__).parent.parent / "requirements.txt"


# ===== 1. Lettura requirements e versioni installate =====
def parse_requirements(path: Path) -> list[tuple[str, str]]:
    """Legge requirements.txt ignorando commenti e righe vuote.

    Args:
        path: percorso del file requirements.txt.

    Returns:
        Lista di tuple ``(nome_pacchetto, versione_fissata)``; le righe senza
        ``==`` vengono scartate. Nessun side effect.
    """
    packages = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            # Parse "package==version"
            match = re.match(r"^([a-zA-Z0-9\-_.]+)==(.+)$", line)
            if match:
                pkg, ver = match.groups()
                packages.append((pkg, ver))
    return packages


def get_installed_version(package_name: str) -> str | None:
    """Restituisce la versione installata di un pacchetto.

    Args:
        package_name: nome della distribuzione (come in requirements.txt).

    Returns:
        Stringa versione, oppure None se il pacchetto non e' installato.
    """
    try:
        return importlib.metadata.version(package_name)
    except importlib.metadata.PackageNotFoundError:
        return None


# ===== 2. Confronto e report =====
def main() -> int:
    """Confronta versioni richieste e installate e stampa la tabella.

    Returns:
        0 se tutte le versioni coincidono, 1 se ci sono differenze, pacchetti
        mancanti o requirements.txt assente/vuoto. Solo output su stdout/stderr.
    """
    if not REQUIREMENTS_PATH.exists():
        print(f"Error: {REQUIREMENTS_PATH} not found", file=sys.stderr)
        return 1

    packages = parse_requirements(REQUIREMENTS_PATH)
    if not packages:
        print("No packages found in requirements.txt", file=sys.stderr)
        return 1

    print(f"Verifying {len(packages)} packages...\n")
    print(f"{'Package':<30} {'Required':<15} {'Installed':<15} {'Match':<6}")
    print("-" * 70)

    mismatches = []
    for pkg_name, req_ver in packages:
        inst_ver = get_installed_version(pkg_name)
        if inst_ver is None:
            match = "✗ (not installed)"
            mismatches.append((pkg_name, req_ver, "NOT_INSTALLED"))
        elif inst_ver == req_ver:
            match = "✓"
        else:
            match = "✗"
            mismatches.append((pkg_name, req_ver, inst_ver))

        inst_display = inst_ver or "—"
        print(f"{pkg_name:<30} {req_ver:<15} {inst_display:<15} {match:<6}")

    print("-" * 70)
    print(
        f"Total: {len(packages)} packages. Matches: {len(packages) - len(mismatches)}/{len(packages)}"
    )

    if mismatches:
        print(f"\n⚠ {len(mismatches)} MISMATCH(ES):")
        for pkg, req, inst in mismatches:
            inst_str = inst if inst != "NOT_INSTALLED" else "not installed"
            print(f"  {pkg}: required={req}, installed={inst_str}")
        return 1

    print("\n✓ All packages match!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
