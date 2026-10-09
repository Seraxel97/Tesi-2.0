"""
STEP 2 — Finalizzazione inverse + STC.

mne-bids-pipeline calcola la forward solution ma fallisce sul rendering 3D del
report HTML in ambienti headless (manca xvfb). Questo script bypassa solo il
rendering: legge il forward già prodotto, costruisce noise covariance ad-hoc,
calcola l'inverse operator e applica inverse alle evoked → STC.

Allineato al vincolo "usare mne-bids-pipeline come base": tutto l'upstream
(preprocessing, sensor, forward) viene dalla pipeline; questo step usa solo
API MNE pure.

Usage:
    python source_reconstruction/finalize_inverse.py --subject 05 --task matchingpennies \
        --method dSPM --loose 0.2 --depth 0.8 --lambda2 0.1111
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import mne

# Repo-relativo + env-override (riproducibilità F0). Prima era assoluto hardcoded.
_DERIV_ENV = os.environ.get("TESI_DERIV", "").strip()
DERIV = (
    Path(_DERIV_ENV).expanduser()
    if _DERIV_ENV
    else Path(__file__).resolve().parents[1] / "data" / "derivatives" / "mne-bids-pipeline"
)


def finalize(
    subject: str,
    task: str,
    *,
    method: str = "dSPM",
    loose: float = 0.2,
    depth: float = 0.8,
    lambda2: float = 1.0 / 9.0,
) -> None:
    """Costruisce e salva l'operatore inverso di un soggetto con covarianza ad-hoc.

    Legge forward solution ed evoked, crea l'inversa minimum-norm e la scrive
    in `sub-<subject>_inv.fif`.

    Args:
        subject: Identificativo soggetto (senza prefisso "sub-").
        task: Nome del task BIDS.
        method: Metodo inverso (default "dSPM").
        loose: Vincolo sull'orientazione dei dipoli (0 = fissa, 1 = libera).
        depth: Esponente di depth weighting.
        lambda2: Regolarizzazione (1 / SNR^2, default SNR=3).

    Raises:
        SystemExit: Se mancano forward solution o evoked.
    """
    sub_dir = DERIV / f"sub-{subject}" / "eeg"
    fwd_path = sub_dir / f"sub-{subject}_fwd.fif"
    ave_path = sub_dir / f"sub-{subject}_task-{task}_ave.fif"

    if not fwd_path.exists():
        sys.exit(
            f"Forward solution missing: {fwd_path}. Run mne_bids_pipeline --steps source first."
        )
    if not ave_path.exists():
        sys.exit(f"Evoked missing: {ave_path}. Run --steps sensor first.")

    fwd = mne.read_forward_solution(str(fwd_path))
    evokeds = mne.read_evokeds(str(ave_path))

    info = evokeds[0].info
    noise_cov = mne.make_ad_hoc_cov(info)
    inv_op = mne.minimum_norm.make_inverse_operator(info, fwd, noise_cov, loose=loose, depth=depth)

    inv_path = sub_dir / f"sub-{subject}_inv.fif"
    mne.minimum_norm.write_inverse_operator(str(inv_path), inv_op, overwrite=True)

    for evoked in evokeds:
        cond_safe = evoked.comment.replace("/", "_").replace(" ", "_")
        stc = mne.minimum_norm.apply_inverse(evoked, inv_op, lambda2=lambda2, method=method)
        stc_stem = sub_dir / f"sub-{subject}_task-{task}_cond-{cond_safe}_inv-{method}"
        stc.save(str(stc_stem), overwrite=True)
        print(
            f"  saved STC '{evoked.comment}' → {stc_stem}-lh.stc / -rh.stc "
            f"shape data={stc.data.shape} tstep={stc.tstep:.4f}s "
            f"vertices=({len(stc.vertices[0])},{len(stc.vertices[1])})"
        )

    print(f"Inverse operator saved → {inv_path}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--subject", required=True)
    ap.add_argument("--task", required=True)
    ap.add_argument("--method", default="dSPM", choices=["MNE", "dSPM", "sLORETA", "eLORETA"])
    ap.add_argument("--loose", type=float, default=0.2)
    ap.add_argument("--depth", type=float, default=0.8)
    ap.add_argument("--lambda2", type=float, default=1.0 / 9.0)
    args = ap.parse_args()
    finalize(
        args.subject,
        args.task,
        method=args.method,
        loose=args.loose,
        depth=args.depth,
        lambda2=args.lambda2,
    )
