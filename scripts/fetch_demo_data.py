#!/usr/bin/env python
"""Scarica/predispone i dati demo della pipeline Tesi_2.0.

Prepara due risorse (idempotente: se gia' presenti non scarica nulla):

1. Dataset BIDS ``eeg_matchingpennies`` in ``data/eeg_matchingpennies``
   (path atteso da ``config/config_step1_matchingpennies.py``).
   Fonte: progetto OSF https://osf.io/cj2dr/ (la stessa usata da
   mne-bids-pipeline nei suoi test, ``DATASET_OPTIONS["eeg_matchingpennies"]``).
   Per default si scarica solo il soggetto sub-05 piu' i file BIDS top-level
   (circa 0.7 GB); con ``--all-subjects`` l'intero dataset.
2. ``fsaverage`` (FreeSurfer, ~0.5 GB) tramite ``mne.datasets.fetch_fsaverage``
   in ``MNE_DATA`` (default ``~/mne_data``).

Uso::

    python scripts/fetch_demo_data.py            # tutto
    python scripts/fetch_demo_data.py --skip-fsaverage
    python scripts/fetch_demo_data.py --subjects 05 06
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEFAULT_DEST = REPO / "data" / "eeg_matchingpennies"
OSF_NODE = "cj2dr"
OSF_API = f"https://api.osf.io/v2/nodes/{OSF_NODE}/files/osfstorage/"


def _get_json(url: str) -> dict:
    with urllib.request.urlopen(url, timeout=60) as r:  # noqa: S310 (URL fisso OSF)
        return json.load(r)


def _walk_osf(url: str, prefix: str = ""):
    """Genera (percorso_relativo, url_download, dimensione) ricorsivamente."""
    while url:
        page = _get_json(url)
        for item in page["data"]:
            a = item["attributes"]
            rel = f"{prefix}{a['name']}"
            if a["kind"] == "folder":
                sub = item["relationships"]["files"]["links"]["related"]["href"]
                yield from _walk_osf(sub, rel + "/")
            else:
                yield rel, item["links"]["download"], a.get("size") or 0
        url = page["links"].get("next")


def _wanted(rel: str, subjects: list[str] | None) -> bool:
    top = rel.split("/")[0]
    if subjects is None or not top.startswith("sub-"):
        return True
    return top in {f"sub-{s}" for s in subjects}


def fetch_bids(dest: Path, subjects: list[str] | None, dry_run: bool) -> None:
    """Scarica il dataset BIDS da OSF saltando i file gia' presenti."""
    print(f"[bids] destinazione: {dest}")
    todo = []
    for rel, url, size in _walk_osf(OSF_API):
        if not _wanted(rel, subjects):
            continue
        out = dest / rel
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
    for i, (rel, url, _, out) in enumerate(todo, 1):
        out.parent.mkdir(parents=True, exist_ok=True)
        tmp = out.with_suffix(out.suffix + ".part")
        print(f"[bids] ({i}/{len(todo)}) {rel}")
        urllib.request.urlretrieve(url, tmp)  # noqa: S310
        tmp.rename(out)
    print("[bids] completato.")


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
    p.add_argument("--all-subjects", action="store_true", help="scarica tutti i soggetti")
    p.add_argument("--skip-bids", action="store_true", help="salta il dataset BIDS")
    p.add_argument("--skip-fsaverage", action="store_true", help="salta fsaverage")
    p.add_argument("--dry-run", action="store_true", help="elenca cosa verrebbe scaricato")
    args = p.parse_args(argv)
    try:
        if not args.skip_bids:
            fetch_bids(args.dest, None if args.all_subjects else args.subjects, args.dry_run)
        if not args.skip_fsaverage:
            fetch_fsaverage(args.dry_run)
    except OSError as e:
        print(f"ERRORE di rete/disco: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
