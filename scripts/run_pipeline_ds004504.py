"""
Pipeline ds004504 adapter — step 2.1 smoke test su sub-001.

Adattamento di run_pipeline_n30.py per ds004504 (.set EEGLAB, no ses-*, no EyesOpen).

Usage:
    python scripts/run_pipeline_ds004504.py
"""

from __future__ import annotations

import json
import sys
import warnings
from datetime import UTC, datetime
from pathlib import Path

import mne
import mne.minimum_norm
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))
warnings.filterwarnings("ignore")

# ── Costanti ──────────────────────────────────────────────────────────────────

BIDS_ROOT = Path("data/raw/ds004504")
DERIV = Path("data/derivatives/mne-bids-pipeline-ds004504")
LABEL_TS_DIR = Path("data/label_ts/ds004504")
CONN_DIR = Path("data/connectivity/ds004504")
FEAT_DIR = Path("data/features/ds004504")
RESULTS_DIR = Path("data/results/ds004504")
HEARTBEAT_PATH = Path(".planning/heartbeats_tesi/haiku-tesi-lemon-2.json")
SUBJECTS_DIR = Path("/home/seraxel/mne_data/MNE-fsaverage-data")

SESSION = None
CONDITIONS = {"EC": "eyesclosed"}

SFREQ_TARGET = 250.0
FILTER_LO = 1.0
FILTER_HI = 40.0
EPOCH_DURATION = 2.0
EPOCH_OVERLAP = 0.5
LAMBDA2 = 1.0 / 9.0
METHOD = "dSPM"
LOOSE = 0.2
DEPTH = 0.8
MINDIST = 5.0

ATLASES = ["aparc"]
ALL_METRICS = ["wpli", "coh", "plv", "imcoh"]
ALL_BANDS: dict[str, tuple[float, float]] = {
    "theta": (4.0, 8.0),
    "alpha": (8.0, 13.0),
    "beta": (13.0, 30.0),
    "gamma": (30.0, 45.0),
}

SUBJECTS_DS004504 = [f"sub-{i:03d}" for i in range(1, 51)]

for d in [LABEL_TS_DIR, CONN_DIR, FEAT_DIR, RESULTS_DIR]:
    d.mkdir(parents=True, exist_ok=True)


# ── Heartbeat ─────────────────────────────────────────────────────────────────

def write_hb(step: str, progress: str, extra: dict | None = None) -> None:
    data: dict = {
        "worker": "haiku-tesi-lemon-2",
        "ts": datetime.now(UTC).isoformat(timespec="seconds"),
        "status": "in_progress",
        "current_sprint": "STEP_2.1_preprocessing_adapter",
        "current_step": step,
        "progress": progress,
    }
    if extra:
        data.update(extra)
    HEARTBEAT_PATH.write_text(json.dumps(data, indent=2))


# ── STEP 2 — Forward + inverse ────────────────────────────────────────────────

def _set_path(sub: str, cond_task: str) -> Path:
    return BIDS_ROOT / sub / "eeg" / f"{sub}_task-{cond_task}_eeg.set"


def _out_dir(sub: str) -> Path:
    d = DERIV / sub / "eeg"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _load_raw(set_path: Path) -> mne.io.Raw:
    raw = mne.io.read_raw_eeglab(str(set_path), preload=True, verbose=False)
    raw.pick("eeg", verbose=False)
    raw.set_montage("standard_1020", match_case=False, verbose=False)
    raw.filter(FILTER_LO, FILTER_HI, method="fir", verbose=False)
    raw.resample(SFREQ_TARGET, verbose=False)
    raw.set_eeg_reference("average", projection=True, verbose=False)
    return raw


def step2_fwd_inv(sub: str) -> tuple[mne.Forward, mne.minimum_norm.InverseOperator]:
    out = _out_dir(sub)
    fwd_p = out / f"{sub}_fwd.fif"
    inv_p = out / f"{sub}_inv.fif"

    if fwd_p.exists() and inv_p.exists():
        fwd = mne.read_forward_solution(str(fwd_p), verbose=False)
        inv = mne.minimum_norm.read_inverse_operator(str(inv_p), verbose=False)
        print(f"  [step2] {sub}: fwd+inv cached")
        return fwd, inv

    first_set = _set_path(sub, "eyesclosed")
    if not first_set.exists():
        raise FileNotFoundError(f"File .set non trovato: {first_set}")
    raw = _load_raw(first_set)
    info = raw.info
    del raw

    if not fwd_p.exists():
        print(f"  [step2] {sub}: computing forward…")
        src = mne.read_source_spaces(
            str(SUBJECTS_DIR / "fsaverage" / "bem" / "fsaverage-oct6-src.fif"), verbose=False)
        bem = mne.read_bem_solution(
            str(SUBJECTS_DIR / "fsaverage" / "bem" / "fsaverage-5120-5120-5120-bem-sol.fif"), verbose=False)
        trans = str(SUBJECTS_DIR / "fsaverage" / "bem" / "fsaverage-trans.fif")
        fwd = mne.make_forward_solution(
            info, trans=trans, src=src, bem=bem,
            eeg=True, meg=False, mindist=MINDIST, verbose=False)
        mne.write_forward_solution(str(fwd_p), fwd, overwrite=True, verbose=False)
        print(f"    → {fwd_p.name}")
    else:
        fwd = mne.read_forward_solution(str(fwd_p), verbose=False)

    if not inv_p.exists():
        noise_cov = mne.make_ad_hoc_cov(info, verbose=False)
        inv = mne.minimum_norm.make_inverse_operator(
            info, fwd, noise_cov, loose=LOOSE, depth=DEPTH, verbose=False)
        mne.minimum_norm.write_inverse_operator(str(inv_p), inv, overwrite=True, verbose=False)
        print(f"    → {inv_p.name}")
    else:
        inv = mne.minimum_norm.read_inverse_operator(str(inv_p), verbose=False)

    return fwd, inv


# ── Main — smoke test sub-001 ─────────────────────────────────────────────────

def main() -> None:
    print("SMOKE TEST ds004504 adapter — sub-001")
    write_hb("smoke_start", "Testing sub-001 preprocessing", {"last_action": "smoke_test_start"})

    try:
        # Test 1: forward + inverse
        print("\n[1] Testing step2_fwd_inv(sub-001)...")
        fwd, inv_op = step2_fwd_inv("sub-001")
        print(f"  ✓ Forward solution: {len(fwd['src'])} sources")
        print(f"  ✓ Inverse operator computed")

        # Test 2: raw load and epoch
        print("\n[2] Testing raw load + epoch generation...")
        set_p = _set_path("sub-001", "eyesclosed")
        assert set_p.exists(), f"FAIL: {set_p}"
        raw = _load_raw(set_p)
        print(f"  ✓ Raw loaded: {len(raw.ch_names)} ch, {raw.times[-1]:.1f}s, sfreq={raw.info['sfreq']} Hz")
        assert raw.info['sfreq'] == SFREQ_TARGET, f"FAIL sfreq: {raw.info['sfreq']}"

        events = mne.make_fixed_length_events(raw, duration=EPOCH_DURATION, overlap=EPOCH_OVERLAP)
        epochs = mne.Epochs(raw, events, tmin=0.0, tmax=EPOCH_DURATION,
                            baseline=None, preload=True, verbose=False)
        print(f"  ✓ Epochs created: {len(epochs)} epochs")
        assert len(epochs) > 0, "FAIL: no epochs"

        # Test 3: phenotype loader
        print("\n[3] Testing phenotype loader...")
        from config.labels_phenotype_ds004504 import load_phenotype_ds004504
        y_age, y_sex = load_phenotype_ds004504(['sub-001', 'sub-002'])
        print(f"  ✓ Phenotype loaded: age={y_age}, sex={y_sex}")
        assert y_age.shape == (2,), f"FAIL y_age shape: {y_age.shape}"
        assert set(y_sex).issubset({0, 1}), f"FAIL y_sex values: {y_sex}"

        print("\n✅ SMOKE TEST PASSED — ds004504 adapter ready for full pipeline")
        write_hb("smoke_done", "sub-001 preprocessing OK",
                 {"last_action": "smoke_test_passed", "n_epochs": len(epochs)})

    except Exception as e:
        print(f"\n❌ SMOKE TEST FAILED: {e}")
        write_hb("smoke_failed", f"Error: {e}",
                 {"last_action": "smoke_test_failed", "error": str(e)})
        sys.exit(1)


if __name__ == "__main__":
    main()
