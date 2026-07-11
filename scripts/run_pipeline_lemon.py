"""Pipeline LEMON adapter — validazione esterna SANA per classificazione sesso.

Adattamento di run_pipeline_ds004504.py per LEMON (MPI-Leipzig Mind-Brain-Body).
Differenze rispetto a ds004504:
  - Input:  data/raw/lemon/EEG_Preprocessed/{sub}_{EC,EO}.set  (EEGLAB .set/.fdt)
  - 2 condizioni per soggetto (EC=eyes-closed, EO=eyes-open) → 2 sample/soggetto
    (coerente con ds005385 che ha 2 sample/soggetto).
  - Montaggio: ~59 canali standard 10-20 (già presenti nel .set) → set_montage 1005.
  - Fenotipo: config/labels_phenotype_lemon (gender F/M + età midpoint bin-5-anni).
  - sfreq già 250 Hz (resample = no-op).

Feature prodotte: identiche a ds005385 (aparc 68 ROI → 2278 archi triu, banda theta,
metriche plv/wpli/coh/imcoh) in data/features/lemon/.

Usage:
    python scripts/run_pipeline_lemon.py --dry-run-1   # solo sub-010002 EC, verifica forma
    python scripts/run_pipeline_lemon.py               # tutti i soggetti scaricati
    python scripts/run_pipeline_lemon.py --skip-to-fc  # solo FC+features (label_ts già pronti)
"""

from __future__ import annotations

import argparse
import json
import re
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

RAW_DIR = Path("data/raw/lemon/EEG_Preprocessed")
DERIV = Path("data/derivatives/mne-bids-pipeline-lemon")
LABEL_TS_DIR = Path("data/label_ts/lemon")
CONN_DIR = Path("data/connectivity/lemon")
FEAT_DIR = Path("data/features/lemon")
SUBJECTS_DIR = Path.home() / "mne_data" / "MNE-fsaverage-data"

CONDITIONS = ["EC", "EO"]  # 2 sample/soggetto

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

ALL_METRICS = ["wpli", "coh", "plv", "imcoh"]
ALL_BANDS: dict[str, tuple[float, float]] = {
    "theta": (4.0, 8.0),
    "alpha": (8.0, 13.0),
    "beta": (13.0, 30.0),
    "gamma": (30.0, 45.0),
}

for d in [LABEL_TS_DIR, CONN_DIR, FEAT_DIR]:
    d.mkdir(parents=True, exist_ok=True)


# ── Discovery soggetti ─────────────────────────────────────────────────────────

def discover_subjects() -> list[str]:
    """Soggetti con ENTRAMBE le condizioni EC+EO scaricate (.set + .fdt)."""
    subs = set()
    for p in RAW_DIR.glob("sub-*_EC.set"):
        m = re.match(r"(sub-\d+)_EC\.set", p.name)
        if not m:
            continue
        sub = m.group(1)
        ok = all(
            (RAW_DIR / f"{sub}_{c}.set").exists() and (RAW_DIR / f"{sub}_{c}.fdt").exists()
            for c in CONDITIONS
        )
        if ok:
            subs.add(sub)
    return sorted(subs)


def _set_path(sub: str, cond: str) -> Path:
    return RAW_DIR / f"{sub}_{cond}.set"


def _out_dir(sub: str) -> Path:
    d = DERIV / sub / "eeg"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _load_raw(set_path: Path) -> mne.io.Raw:
    raw = mne.io.read_raw_eeglab(str(set_path), preload=True, verbose=False)
    raw.pick("eeg", verbose=False)
    # LEMON: montaggio standard 10-20 già presente; riapplichiamo standard_1005
    # (superset di 1020) coerente con fsaverage-trans, ignorando canali non-standard.
    raw.set_montage("standard_1005", match_case=False, on_missing="ignore", verbose=False)
    raw.filter(FILTER_LO, FILTER_HI, method="fir", verbose=False)
    if abs(raw.info["sfreq"] - SFREQ_TARGET) > 1e-6:
        raw.resample(SFREQ_TARGET, verbose=False)
    raw.set_eeg_reference("average", projection=True, verbose=False)
    return raw


# ── STEP 2 — Forward + inverse (condiviso EC/EO) ───────────────────────────────

def step2_fwd_inv(sub: str) -> tuple[mne.Forward, mne.minimum_norm.InverseOperator]:
    out = _out_dir(sub)
    fwd_p = out / f"{sub}_fwd.fif"
    inv_p = out / f"{sub}_inv.fif"

    if fwd_p.exists() and inv_p.exists():
        fwd = mne.read_forward_solution(str(fwd_p), verbose=False)
        inv = mne.minimum_norm.read_inverse_operator(str(inv_p), verbose=False)
        print(f"  [step2] {sub}: fwd+inv cached")
        return fwd, inv

    first_set = _set_path(sub, "EC")
    if not first_set.exists():
        raise FileNotFoundError(f"File .set non trovato: {first_set}")
    raw = _load_raw(first_set)
    info = raw.info
    del raw

    src = mne.read_source_spaces(
        str(SUBJECTS_DIR / "fsaverage" / "bem" / "fsaverage-oct6-src.fif"), verbose=False)
    bem = mne.read_bem_solution(
        str(SUBJECTS_DIR / "fsaverage" / "bem" / "fsaverage-5120-5120-5120-bem-sol.fif"),
        verbose=False)
    trans = str(SUBJECTS_DIR / "fsaverage" / "bem" / "fsaverage-trans.fif")
    fwd = mne.make_forward_solution(
        info, trans=trans, src=src, bem=bem,
        eeg=True, meg=False, mindist=MINDIST, verbose=False)
    mne.write_forward_solution(str(fwd_p), fwd, overwrite=True, verbose=False)

    noise_cov = mne.make_ad_hoc_cov(info, verbose=False)
    inv = mne.minimum_norm.make_inverse_operator(
        info, fwd, noise_cov, loose=LOOSE, depth=DEPTH, verbose=False)
    mne.minimum_norm.write_inverse_operator(str(inv_p), inv, overwrite=True, verbose=False)
    print(f"  [step2] {sub}: fwd+inv computed ({len(info['ch_names'])} ch)")
    return fwd, inv


# ── STEP 2b — Per-epoch STCs ──────────────────────────────────────────────────

def _stcs_npz(sub: str, cond: str) -> Path:
    return DERIV / sub / "eeg" / f"{sub}_cond-{cond}_inv-{METHOD}-stcs.npz"


def step2b_stcs(sub: str, cond: str, inv_op: mne.minimum_norm.InverseOperator) -> dict:
    npz = _stcs_npz(sub, cond)
    if npz.exists():
        d = np.load(npz, allow_pickle=True)
        return {"n_epochs": int(d["n_epochs"]), "file_mb": npz.stat().st_size / 1e6}

    set_p = _set_path(sub, cond)
    if not set_p.exists():
        return {"n_epochs": 0, "file_mb": 0, "status": "missing_set"}

    raw = _load_raw(set_p)
    events = mne.make_fixed_length_events(raw, duration=EPOCH_DURATION, overlap=EPOCH_OVERLAP)
    epochs = mne.Epochs(raw, events, tmin=0.0, tmax=EPOCH_DURATION,
                        baseline=None, preload=True, verbose=False)
    del raw

    stcs = mne.minimum_norm.apply_inverse_epochs(
        epochs, inv_op, lambda2=LAMBDA2, method=METHOD,
        return_generator=False, verbose=False)
    del epochs

    data = np.stack([s.data for s in stcs]).astype(np.float32)
    vl, vr = stcs[0].vertices[0], stcs[0].vertices[1]
    np.savez_compressed(npz, data=data, vertices_lh=vl, vertices_rh=vr,
                        tmin=stcs[0].tmin, tstep=stcs[0].tstep,
                        n_epochs=len(stcs), sfreq=SFREQ_TARGET)
    n_ep = len(stcs)
    del stcs, data
    mb = npz.stat().st_size / 1e6
    print(f"  [step2b] {sub} {cond}: {n_ep} ep, {mb:.0f} MB")
    return {"n_epochs": n_ep, "file_mb": mb}


# ── STEP 3b — Parcellazione aparc ─────────────────────────────────────────────

def _label_ts_npz(sub: str, cond: str) -> Path:
    return LABEL_TS_DIR / f"{sub}_cond-{cond}_aparc_label_ts.npz"


def step3b_parc(sub: str, cond: str, fwd: mne.Forward) -> dict:
    from parcellation.extract_label_tc import get_labels
    src = fwd["src"]

    out_p = _label_ts_npz(sub, cond)
    if out_p.exists():
        return {"status": "cached"}

    labels = get_labels("aparc", subject="fsaverage")
    label_names = [lbl.name for lbl in labels]

    stcs_p = _stcs_npz(sub, cond)
    if not stcs_p.exists():
        return {"status": "missing_stcs"}

    d = np.load(stcs_p, allow_pickle=True)
    data = d["data"]
    stcs_list = [
        mne.SourceEstimate(
            data=data[i].astype(np.float64),
            vertices=[d["vertices_lh"], d["vertices_rh"]],
            tmin=float(d["tmin"]), tstep=float(d["tstep"]),
            subject="fsaverage")
        for i in range(data.shape[0])]
    del data

    tcs = mne.extract_label_time_course(
        stcs_list, labels, src, mode="mean_flip",
        allow_empty=True, verbose=False)
    del stcs_list

    label_tc = np.stack(tcs).astype(np.float32)
    del tcs

    np.savez_compressed(out_p, label_tc=label_tc,
                        label_names=np.array(label_names),
                        subject=sub, condition=cond, atlas="aparc",
                        mode="mean_flip", sfreq=SFREQ_TARGET)
    print(f"  [step3b] {sub} {cond}: {label_tc.shape[1]} ROI OK")
    return {"status": "done", "n_roi": int(label_tc.shape[1])}


# ── STEP 4b — FC per-epoch ────────────────────────────────────────────────────

def _conn_npz(sub: str, cond: str, metric: str, band: str) -> Path:
    return CONN_DIR / f"{sub}_atlas-aparc_cond-{cond}_metric-{metric}_band-{band}_per-epoch.npz"


def step4b_fc(sub: str, cond: str) -> int:
    from connectivity.fc_dispatcher import compute_fc
    label_ts_p = _label_ts_npz(sub, cond)
    if not label_ts_p.exists():
        return 0

    d_lt = np.load(label_ts_p, allow_pickle=True)
    label_tc = d_lt["label_tc"].astype(np.float64)
    n_done = 0

    for metric in ALL_METRICS:
        need_bands = {
            b: hz for b, hz in ALL_BANDS.items()
            if not _conn_npz(sub, cond, metric, b).exists()
        }
        if not need_bands:
            n_done += len(ALL_BANDS)
            continue
        fc_dict = compute_fc(label_tc, SFREQ_TARGET, metric,
                             bands=need_bands, mode="multitaper")
        for b, mat in fc_dict.items():
            out_p = _conn_npz(sub, cond, metric, b)
            np.savez_compressed(out_p, fc_matrix=mat,
                                subject=sub, condition=cond, atlas="aparc",
                                metric=metric, band=b, sfreq=SFREQ_TARGET)
            n_done += 1
    del label_tc
    return n_done


# ── STEP 5 — Feature aggregation ──────────────────────────────────────────────

def step5_features(subjects: list[str], force: bool = False) -> list[dict]:
    """Aggrega FC → feature matrix per ogni metric×band.

    Ordine sample: per soggetto [EC, EO] → allineato a groups=repeat(sub_idx, 2).
    Salva anche y.npy (y_sex per-sample) e groups.npy.
    """
    from config.labels_phenotype_lemon import load_phenotype_lemon

    # Costruisci lista sample ordinata + labels
    sample_ids: list[str] = []
    groups: list[int] = []
    for i, sub in enumerate(subjects):
        for cond in CONDITIONS:
            sample_ids.append(f"{sub}_{cond}")
            groups.append(i)

    y_age_sub, y_sex_sub = load_phenotype_lemon(subjects)
    y_sex = np.repeat(y_sex_sub, len(CONDITIONS)).astype(np.int32)
    y_age = np.repeat(y_age_sub, len(CONDITIONS)).astype(np.float64)

    np.save(FEAT_DIR / "y.npy", y_sex)
    np.save(FEAT_DIR / "y_age.npy", y_age)
    np.save(FEAT_DIR / "groups.npy", np.array(groups, dtype=np.int32))

    results = []
    for metric in ALL_METRICS:
        for band in ALL_BANDS:
            out_p = FEAT_DIR / f"X_aparc_{metric}_{band}.npz"
            if not force and out_p.exists():
                d = np.load(out_p, allow_pickle=True)
                if d["X"].shape[0] == len(sample_ids):
                    results.append({"metric": metric, "band": band,
                                    "shape": list(d["X"].shape), "skipped": True})
                    continue

            rows = []
            ok = True
            for sub in subjects:
                for cond in CONDITIONS:
                    fc_p = _conn_npz(sub, cond, metric, band)
                    if not fc_p.exists():
                        print(f"  [step5] MISSING: {fc_p.name}")
                        ok = False
                        break
                    d = np.load(fc_p, allow_pickle=True)
                    mat = d["fc_matrix"].astype(np.float64)
                    n = mat.shape[0]
                    idx = np.triu_indices(n, k=1)
                    rows.append(mat[idx])
                if not ok:
                    break

            if not ok:
                results.append({"metric": metric, "band": band, "error": "missing_fc"})
                continue

            X = np.stack(rows)
            np.savez_compressed(out_p, X=X)
            print(f"  [step5] {metric} {band}: shape={X.shape}")
            results.append({"metric": metric, "band": band, "shape": list(X.shape)})

    meta = {
        "timestamp": datetime.now(UTC).isoformat(timespec="seconds"),
        "dataset": "lemon",
        "subjects": sample_ids,
        "subject_ids": subjects,
        "conditions": CONDITIONS,
        "atlases": ["aparc"],
        "metrics": ALL_METRICS,
        "bands": list(ALL_BANDS.keys()),
        "n_subjects": len(subjects),
        "n_samples": len(sample_ids),
    }
    (FEAT_DIR / "metadata.json").write_text(json.dumps(meta, indent=2))
    return results


# ── Orchestrazione per-soggetto ───────────────────────────────────────────────

def process_subject(sub: str, conditions: list[str], cleanup: bool = True) -> None:
    fwd, inv = step2_fwd_inv(sub)
    for cond in conditions:
        step2b_stcs(sub, cond, inv)
        step3b_parc(sub, cond, fwd)
        step4b_fc(sub, cond)
        if cleanup:
            npz = _stcs_npz(sub, cond)
            if npz.exists():
                npz.unlink()  # disco preservato


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run-1", action="store_true",
                        help="Processa solo 1 soggetto/1 condizione (EC) e verifica forma feature")
    parser.add_argument("--skip-to-fc", action="store_true",
                        help="Salta a step4b+5 (label_ts già presenti)")
    parser.add_argument("--no-cleanup", action="store_true")
    args = parser.parse_args()

    subjects = discover_subjects()
    print(f"[lemon] soggetti disponibili (EC+EO): {len(subjects)}")
    if not subjects:
        print("[lemon] nessun soggetto scaricato ancora — riprovare più tardi")
        return

    if args.dry_run_1:
        sub = subjects[0]
        print(f"[DRY-RUN] processo {sub} condizione EC…")
        fwd, inv = step2_fwd_inv(sub)
        step2b_stcs(sub, "EC", inv)
        r_parc = step3b_parc(sub, "EC", fwd)
        n_fc = step4b_fc(sub, "EC")
        print(f"[DRY-RUN] parc={r_parc}, fc_files={n_fc}")
        # Verifica forma feature aparc/plv/theta
        fc_p = _conn_npz(sub, "EC", "plv", "theta")
        d = np.load(fc_p, allow_pickle=True)
        mat = d["fc_matrix"]
        n = mat.shape[0]
        vec = mat[np.triu_indices(n, k=1)]
        print(f"[DRY-RUN] FC matrix {mat.shape} → triu vec dim={vec.shape[0]} (atteso 2278)")
        assert n == 68, f"ROI attese 68, trovate {n}"
        assert vec.shape[0] == 2278, f"dim feature attesa 2278, trovata {vec.shape[0]}"
        print("[DRY-RUN OK] dimensione feature corretta (68 ROI → 2278 archi)")
        return

    if not args.skip_to_fc:
        for i, sub in enumerate(subjects):
            print(f"\n[{i+1}/{len(subjects)}] {sub}")
            try:
                process_subject(sub, CONDITIONS, cleanup=not args.no_cleanup)
            except Exception as e:  # noqa: BLE001
                print(f"  ERROR {sub}: {e}")
                continue

    # Solo soggetti con FC completo per entrambe le condizioni + tutte metric/band
    complete = [
        sub for sub in subjects
        if all(
            _conn_npz(sub, c, m, b).exists()
            for c in CONDITIONS for m in ALL_METRICS for b in ALL_BANDS
        )
    ]
    print(f"\n[lemon step5] {len(complete)} soggetti con FC completo")
    step5_features(complete)
    print("\n[LEMON_PIPELINE_DONE]")


if __name__ == "__main__":
    main()
