"""
STEP 3 — Estrazione time course per ROI da source estimates (STC).

Wraps `mne.extract_label_time_course` su STC prodotti da STEP 2.
Atlasi supportati (tutti già presenti in fsaverage/label/):
  - "aparc"        : Desikan-Killiany ~68 ROI corticali (aparc.annot)
  - "destrieux"    : Destrieux a2009s ~148 ROI (aparc.a2009s.annot)
  - "schaefer100"  : Schaefer2018 100 parcels x 7 networks
  - "schaefer200"  : Schaefer2018 200 parcels x 7 networks
  - "schaefer400"  : Schaefer2018 400 parcels x 7 networks

Mode di aggregazione: vedi `mne.extract_label_time_course` (default="mean_flip"
per source-level functional connectivity, robusto a sign-flip).
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

import mne
import numpy as np


SUBJECTS_DIR = Path("/home/seraxel/mne_data/MNE-fsaverage-data")

ATLAS_TO_PARC: dict[str, str] = {
    "aparc": "aparc",
    "destrieux": "aparc.a2009s",
    "schaefer100": "Schaefer2018_100Parcels_7Networks_order",
    "schaefer200": "Schaefer2018_200Parcels_7Networks_order",
    "schaefer400": "Schaefer2018_400Parcels_7Networks_order",
}

AtlasName = Literal["aparc", "destrieux", "schaefer100", "schaefer200", "schaefer400"]


_EXCLUDE_KEYWORDS = ("unknown", "medial_wall", "background+freesurfer")


def get_labels(atlas: AtlasName, *, subject: str = "fsaverage") -> list[mne.Label]:
    parc = ATLAS_TO_PARC[atlas]
    labels = mne.read_labels_from_annot(
        subject=subject, parc=parc, subjects_dir=str(SUBJECTS_DIR), verbose=False
    )
    return [
        lbl for lbl in labels
        if not any(kw in lbl.name.lower() for kw in _EXCLUDE_KEYWORDS)
    ]


def extract_tc(
    stc: mne.SourceEstimate,
    atlas: AtlasName,
    src: mne.SourceSpaces | str | Path,
    *,
    mode: str = "mean_flip",
    subject: str = "fsaverage",
) -> tuple[np.ndarray, list[str]]:
    """Estrae time course per ROI da uno STC.

    Returns:
        tc: array shape (n_labels, n_times)
        names: lista nomi label (ordinati come righe di tc)
    """
    if isinstance(src, (str, Path)):
        src = mne.read_source_spaces(str(src), verbose=False)
    labels = get_labels(atlas, subject=subject)
    tc = mne.extract_label_time_course(
        stc, labels, src, mode=mode, allow_empty=True, verbose=False
    )
    names = [lbl.name for lbl in labels]
    return np.asarray(tc), names


def extract_tc_from_files(
    stc_path: str | Path,
    fwd_or_src_path: str | Path,
    atlas: AtlasName,
    *,
    mode: str = "mean_flip",
    subject: str = "fsaverage",
) -> tuple[np.ndarray, list[str]]:
    stc = mne.read_source_estimate(str(stc_path))
    p = Path(fwd_or_src_path)
    if p.name.endswith("_fwd.fif") or "fwd" in p.stem:
        fwd = mne.read_forward_solution(str(p), verbose=False)
        src = fwd["src"]
    else:
        src = mne.read_source_spaces(str(p), verbose=False)
    return extract_tc(stc, atlas, src, mode=mode, subject=subject)


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--stc", required=True)
    ap.add_argument("--src", required=True, help="path .fif fwd o src")
    ap.add_argument("--atlas", required=True, choices=list(ATLAS_TO_PARC))
    ap.add_argument("--mode", default="mean_flip")
    args = ap.parse_args()

    tc, names = extract_tc_from_files(args.stc, args.src, args.atlas, mode=args.mode)
    print(f"atlas={args.atlas} mode={args.mode}")
    print(f"shape tc=({tc.shape[0]}, {tc.shape[1]})  ({len(names)} labels × n_times)")
    print(f"first 5 labels: {names[:5]}")
    print(f"last  5 labels: {names[-5:]}")
