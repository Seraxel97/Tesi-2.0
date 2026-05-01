"""
STEP 4 — Dispatcher metriche di connettività funzionale.

Wrapper su `mne_connectivity.spectral_connectivity_epochs` che espone la sola
scelta della metrica come parametro `metric`. Allinea direttamente al brief
del professore: "possibilità di cambiare metriche (wpli, plv, coherence, imgcoher)".

Metriche supportate (tutte native in mne-connectivity 0.8):
  - "coh"             : Coherence
  - "imcoh"           : Imaginary Coherence
  - "plv"             : Phase Locking Value
  - "ciplv"           : corrected imaginary PLV
  - "pli"             : Phase Lag Index
  - "wpli"            : weighted PLI
  - "wpli2_debiased"  : debiased squared wPLI

Bande standard EEG (override-abile):
  - delta : 1-4 Hz
  - theta : 4-8 Hz
  - alpha : 8-13 Hz
  - beta  : 13-30 Hz
  - gamma : 30-45 Hz
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

import numpy as np
from mne_connectivity import spectral_connectivity_epochs


Metric = Literal["coh", "imcoh", "plv", "ciplv", "pli", "wpli", "wpli2_debiased"]

DEFAULT_BANDS: dict[str, tuple[float, float]] = {
    "delta": (1.0, 4.0),
    "theta": (4.0, 8.0),
    "alpha": (8.0, 13.0),
    "beta": (13.0, 30.0),
    "gamma": (30.0, 45.0),
}


def compute_fc(
    label_tc: np.ndarray,
    sfreq: float,
    metric: Metric,
    *,
    bands: dict[str, tuple[float, float]] | None = None,
    mode: str = "multitaper",
    n_jobs: int = 1,
) -> dict[str, np.ndarray]:
    """Calcola matrici FC per ogni banda.

    Args:
        label_tc: shape (n_epochs, n_labels, n_times) — output di
            `mne.extract_label_time_course` su epochs.
        sfreq: sampling frequency in Hz.
        metric: una delle Metric supportate.
        bands: override delle bande di frequenza. Se None usa DEFAULT_BANDS.
        mode: spectral estimation mode (multitaper / fourier / cwt_morlet).
        n_jobs: parallelism.

    Returns:
        dict {band_name: matrix_NxN} simmetrica per ogni banda.
    """
    if label_tc.ndim != 3:
        raise ValueError(
            f"label_tc must be (n_epochs, n_labels, n_times), got shape {label_tc.shape}"
        )
    bands = bands or DEFAULT_BANDS
    n_labels = label_tc.shape[1]

    out: dict[str, np.ndarray] = {}
    for band_name, (fmin, fmax) in bands.items():
        con = spectral_connectivity_epochs(
            label_tc,
            method=metric,
            mode=mode,
            sfreq=sfreq,
            fmin=fmin,
            fmax=fmax,
            faverage=True,
            n_jobs=n_jobs,
            verbose=False,
        )
        # con.get_data(output="dense") shape (n_labels, n_labels, n_freqs=1)
        mat = con.get_data(output="dense").squeeze(-1)
        # symmetrize: lower triangle only viene popolata; rifletto
        mat = mat + mat.T - np.diag(np.diag(mat))
        out[band_name] = mat
    return out


def save_fc(fc: dict[str, np.ndarray], names: list[str], out_path: str | Path) -> None:
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        out_path,
        names=np.array(names),
        **{f"fc_{b}": m for b, m in fc.items()},
    )


if __name__ == "__main__":
    # Smoke test sintetico: 10 epochs × 20 labels × 1000 timepoints, sfreq 250
    rng = np.random.default_rng(42)
    n_ep, n_lab, n_t, sfreq = 10, 20, 1000, 250.0
    label_tc = rng.standard_normal((n_ep, n_lab, n_t))
    for metric in ("wpli", "plv", "coh", "imcoh", "pli", "ciplv", "wpli2_debiased"):
        fc = compute_fc(label_tc, sfreq, metric)
        bands_str = ", ".join(f"{b}={fc[b].shape}" for b in fc)
        print(f"metric={metric:18s}  shapes: {bands_str}")
