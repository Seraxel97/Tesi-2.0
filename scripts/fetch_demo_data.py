#!/usr/bin/env python
"""Scarica/predispone i dati demo della pipeline Tesi_2.0.

Prepara due risorse (idempotente: se gia' presenti non scarica nulla):

1. Dataset BIDS ``eeg_matchingpennies`` in ``data/eeg_matchingpennies``
   (path atteso da ``config/config_step1_matchingpennies.py``).
   Fonte: repository GIN https://gin.g-node.org/sappelhoff/eeg_matchingpennies
   (DOI 10.17605/OSF.IO/CJ2DR; il progetto OSF contiene solo il README).
   Per default si scarica solo il soggetto sub-05 piu' i file BIDS top-level
   (circa 0.4 GB); con ``--all-subjects`` i soggetti sub-05..sub-11 (~2.5 GB).
2. ``fsaverage`` (FreeSurfer, ~0.5 GB) tramite ``mne.datasets.fetch_fsaverage``
   in ``MNE_DATA`` (default ``~/mne_data``).

Uso::

    python scripts/fetch_demo_data.py            # tutto (sub-05 + fsaverage)
    python scripts/fetch_demo_data.py --skip-fsaverage
    python scripts/fetch_demo_data.py --subjects 05 06
    python scripts/fetch_demo_data.py --dry-run
"""

from __future__ import annotations

import argparse
import sys
import urllib.request
from pathlib import Path

# ===== 1. Configurazione =====

REPO = Path(__file__).resolve().parents[1]
DEFAULT_DEST = REPO / "data" / "eeg_matchingpennies"
GIN_RAW = "https://gin.g-node.org/sappelhoff/eeg_matchingpennies/raw/master/"

ALL_SUBJECTS = ["05", "06", "07", "08", "09", "10", "11"]
# File BIDS a livello radice del dataset
ROOT_FILES = [
    "dataset_description.json",
    "participants.tsv",
    "participants.json",
    "README.md",
    "task-matchingpennies_eeg.json",
    "task-matchingpennies_events.json",
    "CHANGES",
    "LICENSE",
]
# File per soggetto (cartella eeg/)
SUBJECT_SUFFIXES = ["channels.tsv", "eeg.eeg", "eeg.vhdr", "eeg.vmrk", "events.tsv"]


# ===== 2. Download del dataset BIDS =====


def _manifest(subjects: list[str]) -> list[str]:
    """Elenco dei percorsi relativi da scaricare per i soggetti richiesti."""
    files = list(ROOT_FILES)
    for sub in subjects:
        for suf in SUBJECT_SUFFIXES:
            files.append(f"sub-{sub}/eeg/sub-{sub}_task-matchingpennies_{suf}")
    return files


def _remote_size(url: str) -> int:
    """Dimensione in byte del file remoto (HEAD); 0 se non disponibile."""
    req = urllib.request.Request(url, method="HEAD")
    with urllib.request.urlopen(req, timeout=60) as r:  # noqa: S310 (URL fisso GIN)
        return int(r.headers.get("Content-Length") or 0)


def fetch_bids(dest: Path, subjects: list[str], dry_run: bool) -> None:
    """Scarica il dataset BIDS da GIN saltando i file gia' presenti e completi."""
    print(f"[bids] destinazione: {dest}")
    todo = []
    for rel in _manifest(subjects):
        url = GIN_RAW + rel
        out = dest / rel
        size = _remote_size(url)
        if out.exists() and (size == 0 or out.stat().st_size == size):
            continue
        todo.append((rel, url, size, out))
    if not todo:
        print("[bids] gia' completo, nulla da scaricare.")
        return
    tot = sum(t[2] for t in todo) / 1e9
    print(f"[bids] {len(todo)} file da scaricare (~{tot:.2f} GB)")
    if dry_run:
        return
    for i, (rel, url, size, out) in enumerate(todo, 1):
        out.parent.mkdir(parents=True, exist_ok=True)
        tmp = out.with_suffix(out.suffix + ".part")
        print(f"[bids] ({i}/{len(todo)}) {rel}")
        urllib.request.urlretrieve(url, tmp)  # noqa: S310
        if size and tmp.stat().st_size != size:
            tmp.unlink()
            raise OSError(f"download incompleto: {rel}")
        tmp.rename(out)
    print("[bids] completato.")


# ===== 3. fsaverage =====


def fetch_fsaverage(dry_run: bool) -> None:
    """Scarica fsaverage (se assente) via MNE."""
    import mne

    data_path = Path(mne.get_config("MNE_DATA") or Path.home() / "mne_data")
    present = (data_path / "MNE-fsaverage-data" / "fsaverage").exists()
    if present:
        print(f"[fsaverage] gia' presente in {data_path}")
        return
    print(f"[fsaverage] download in {data_path} (~0.5 GB)")
    if dry_run:
        return
    data_path.mkdir(parents=True, exist_ok=True)
    mne.datasets.fetch_fsaverage(subjects_dir=None, verbose=True)
    print("[fsaverage] completato.")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Scarica i dati demo (matchingpennies + fsaverage).")
    p.add_argument("--dest", type=Path, default=DEFAULT_DEST, help="cartella BIDS di destinazione")
    p.add_argument("--subjects", nargs="+", default=["05"], help="soggetti (default: 05)")
    p.add_argument("--all-subjects", action="store_true", help="scarica tutti i soggetti (05-11)")
    p.add_argument("--skip-bids", action="store_true", help="salta il dataset BIDS")
    p.add_argument("--skip-fsaverage", action="store_true", help="salta fsaverage")
    p.add_argument("--dry-run", action="store_true", help="elenca cosa verrebbe scaricato")
    args = p.parse_args(argv)
    try:
        if not args.skip_bids:
            fetch_bids(
                args.dest, ALL_SUBJECTS if args.all_subjects else args.subjects, args.dry_run
            )
        if not args.skip_fsaverage:
            fetch_fsaverage(args.dry_run)
    except OSError as e:
        print(f"ERRORE di rete/disco: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
