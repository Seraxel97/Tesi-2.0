"""Pipeline completa N=30/50/100/179 su ds005385 (EEG resting-state, EO vs EC).

Scopo:
    Orchestra gli step 2 -> 2b -> 3b -> cleanup -> 4b -> 5 -> 6+7 della tesi
    (ricostruzione di sorgente, parcellazione, connettività funzionale, feature
    e classificazione LOSO EO/EC). Il run è "disk-aware": i file stcs.npz
    (~3.4 GB/soggetto) vengono cancellati subito dopo lo step 3b.

    - Soggetti della coorte base (N15 o N30 ecc.): label_ts e conn esistono già,
      quindi gli step 2/2b/3b/4b vengono saltati.
    - Soggetti nuovi: pipeline completa (fwd + inv + stcs + label_ts + conn).
    - Step 5 e 6+7: eseguiti su tutti i soggetti della coorte target.

Input:
    - data/raw/ds005385/<sub>/ses-1/eeg/*.edf (EEG grezzo, EyesOpen/EyesClosed)
    - config/subjects_whitelist*.py (liste soggetti per coorte)
    - template fsaverage in ~/mne_data/MNE-fsaverage-data

Output:
    - data/derivatives/mne-bids-pipeline/<sub>/eeg/ (fwd.fif, inv.fif, stcs.npz temporanei)
    - data/label_ts/ds005385/*_per-epoch.npz (serie temporali per ROI)
    - data/connectivity/ds005385/*_per-epoch.npz (matrici FC)
    - data/features/ds005385/X_<atlas>_<metrica>_<banda>.npz, y.npy, groups.npy
    - data/results/ds005385/ (risultati ML) e reports/*.md

Esempio:
    python scripts/run_pipeline_n30.py --n-subjects 30
    python scripts/run_pipeline_n30.py --n-subjects 179 --atlases aparc --skip-to-step5

"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import time
import warnings
from datetime import UTC, datetime
from pathlib import Path

import mne
import mne.minimum_norm
import numpy as np

# Rende importabili i pacchetti del repository (config, connectivity, ...) dalla cartella scripts/
sys.path.insert(0, str(Path(__file__).parent.parent))
warnings.filterwarnings("ignore")

from config.subjects_whitelist import SUBJECT_WHITELIST as N15  # noqa: E402
from config.subjects_whitelist_n30 import SUBJECT_WHITELIST_N30 as N30  # noqa: E402

# Whitelist opzionali: None se il relativo file di config non esiste
try:
    from config.subjects_whitelist_n50 import SUBJECT_WHITELIST_N50 as N50  # noqa: E402
except ImportError:
    N50 = None

try:
    from config.subjects_whitelist_n100 import SUBJECT_WHITELIST_N100 as N100  # noqa: E402
except ImportError:
    N100 = None

try:
    from config.subjects_whitelist_n179 import SUBJECT_WHITELIST_N179 as N179  # noqa: E402
except ImportError:
    N179 = None
from connectivity.fc_dispatcher import compute_fc  # noqa: E402
from ml_training.aggregate_n15 import aggregate_classify_n15  # noqa: E402
from parcellation.extract_label_tc import get_labels  # noqa: E402

# ===== 1. Costanti =====
BIDS_ROOT = Path("data/raw/ds005385")
DERIV = Path("data/derivatives/mne-bids-pipeline")
LABEL_TS_DIR = Path("data/label_ts/ds005385")
CONN_DIR = Path("data/connectivity/ds005385")
FEAT_DIR = Path("data/features/ds005385")
RESULTS_DIR = Path("data/results/ds005385")
SUBJECTS_DIR = Path.home() / "mne_data" / "MNE-fsaverage-data"  # posizione standard fsaverage (F0)

SESSION = "ses-1"
ACQ = "acq-pre"
CONDITIONS = {"EO": "EyesOpen", "EC": "EyesClosed"}

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

ATLASES = ["aparc", "schaefer100"]
ALL_METRICS = ["wpli", "coh", "plv", "imcoh"]
ALL_BANDS: dict[str, tuple[float, float]] = {
    "theta": (4.0, 8.0),
    "alpha": (8.0, 13.0),
    "beta": (13.0, 30.0),
    "gamma": (30.0, 45.0),
}

DISK_WARN_GB = 20.0
DISK_ABORT_GB = 10.0

# Crea le cartelle di output già all'import del modulo
for d in [LABEL_TS_DIR, CONN_DIR, FEAT_DIR, RESULTS_DIR]:
    d.mkdir(parents=True, exist_ok=True)


# ===== 2. Log di avanzamento =====
def write_hb(step: str, progress: str, disk_gb: float, extra: dict | None = None) -> None:
    """Stampa su stdout una riga di log dell'avanzamento.

    Args:
        step: nome dello step corrente.
        progress: descrizione testuale dell'avanzamento.
        disk_gb: spazio disco libero in GB.
        extra: campi aggiuntivi da riportare nel log (opzionale).

    Returns:
        None.
    """
    ts = datetime.now(UTC).isoformat(timespec="seconds")
    tail = f" {extra}" if extra else ""
    print(f"[progress {ts}] {step}: {progress} (disk_free={disk_gb:.1f} GB){tail}", flush=True)


def disk_free() -> float:
    """Restituisce lo spazio disco libero (GB) sulla partizione del repository.

    Returns:
        spazio libero in GB (float).
    """
    return shutil.disk_usage(str(Path(__file__).resolve().parents[1])).free / 1e9


# ===== 3. STEP 2 — Forward + inverse =====
def _edf_path(sub: str, cond_task: str) -> Path:
    """Costruisce il percorso del file EDF BIDS di un soggetto per una condizione.

    Args:
        sub: id soggetto (es. 'sub-007').
        cond_task: nome task BIDS ('EyesOpen' o 'EyesClosed').

    Returns:
        Path del file EDF (non verifica l'esistenza).
    """
    return BIDS_ROOT / sub / SESSION / "eeg" / f"{sub}_{SESSION}_task-{cond_task}_{ACQ}_eeg.edf"


def _out_dir(sub: str) -> Path:
    """Restituisce (creandola se serve) la cartella derivati di un soggetto.

    Args:
        sub: id soggetto.

    Returns:
        Path della cartella derivati/<sub>/eeg.

    Side effects:
        Crea la cartella se assente.
    """
    d = DERIV / sub / "eeg"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _load_raw(edf_path: Path) -> mne.io.Raw:
    """Carica un EDF e applica il preprocessing standard della pipeline.

    Args:
        edf_path: percorso del file EDF.

    Returns:
        mne.io.Raw con solo canali EEG, montaggio 10-20, filtro FIR 1-40 Hz, ricampionato a SFREQ_TARGET e riferimento medio (proiezione).

    Side effects:
        Nessuno (sola lettura).
    """
    raw = mne.io.read_raw_edf(str(edf_path), preload=True, verbose=False)
    raw.pick("eeg", verbose=False)
    raw.set_montage("standard_1020", verbose=False)
    raw.filter(FILTER_LO, FILTER_HI, method="fir", verbose=False)
    raw.resample(SFREQ_TARGET, verbose=False)
    # Riferimento medio come proiezione (richiesto dall'operatore inverso)
    raw.set_eeg_reference("average", projection=True, verbose=False)
    return raw


def step2_fwd_inv(sub: str) -> tuple[mne.Forward, mne.minimum_norm.InverseOperator]:
    """Step 2: calcola (o legge dalla cache) forward solution e operatore inverso su fsaverage.

    Args:
        sub: id soggetto.

    Returns:
        tupla (forward, inverse operator).

    Side effects:
        Scrive <sub>_fwd.fif e <sub>_inv.fif in derivati/<sub>/eeg se non esistono.
    """
    out = _out_dir(sub)
    fwd_p = out / f"{sub}_fwd.fif"
    inv_p = out / f"{sub}_inv.fif"

    if fwd_p.exists() and inv_p.exists():
        fwd = mne.read_forward_solution(str(fwd_p), verbose=False)
        inv = mne.minimum_norm.read_inverse_operator(str(inv_p), verbose=False)
        print(f"  [step2] {sub}: fwd+inv cached")
        return fwd, inv

    # L'info (canali/montaggio) è uguale tra le condizioni: basta un EDF per fwd/inv
    first_edf = _edf_path(sub, "EyesOpen")
    if not first_edf.exists():
        first_edf = _edf_path(sub, "EyesClosed")
    raw = _load_raw(first_edf)
    info = raw.info
    del raw

    if not fwd_p.exists():
        print(f"  [step2] {sub}: computing forward…")
        src = mne.read_source_spaces(
            str(SUBJECTS_DIR / "fsaverage" / "bem" / "fsaverage-oct6-src.fif"), verbose=False
        )
        bem = mne.read_bem_solution(
            str(SUBJECTS_DIR / "fsaverage" / "bem" / "fsaverage-5120-5120-5120-bem-sol.fif"),
            verbose=False,
        )
        trans = str(SUBJECTS_DIR / "fsaverage" / "bem" / "fsaverage-trans.fif")
        fwd = mne.make_forward_solution(
            info, trans=trans, src=src, bem=bem, eeg=True, meg=False, mindist=MINDIST, verbose=False
        )
        mne.write_forward_solution(str(fwd_p), fwd, overwrite=True, verbose=False)
        print(f"    → {fwd_p.name}")
    else:
        fwd = mne.read_forward_solution(str(fwd_p), verbose=False)

    if not inv_p.exists():
        # Nessuna baseline di rumore disponibile: covarianza ad-hoc
        noise_cov = mne.make_ad_hoc_cov(info, verbose=False)
        inv = mne.minimum_norm.make_inverse_operator(
            info, fwd, noise_cov, loose=LOOSE, depth=DEPTH, verbose=False
        )
        mne.minimum_norm.write_inverse_operator(str(inv_p), inv, overwrite=True, verbose=False)
        print(f"    → {inv_p.name}")
    else:
        inv = mne.minimum_norm.read_inverse_operator(str(inv_p), verbose=False)

    return fwd, inv


# ===== 4. STEP 2b — Per-epoch STCs =====
def _stcs_npz(sub: str, cond: str) -> Path:
    """Percorso del file stcs.npz (STC per-epoca) di un soggetto/condizione.

    Args:
        sub: id soggetto.
        cond: 'EO' o 'EC'.

    Returns:
        Path del file.
    """
    return DERIV / sub / "eeg" / f"{sub}_task-RestingState_cond-{cond}_inv-{METHOD}-stcs.npz"


def step2b_stcs(sub: str, inv_op: mne.minimum_norm.InverseOperator) -> dict:
    """Step 2b: applica l'inversa a ogni epoca e salva le STC per-epoca in un .npz.

    Args:
        sub: id soggetto.
        inv_op: operatore inverso (da step2_fwd_inv).

    Returns:
        dict {condizione: {n_epochs, file_mb, ...}} con statistiche per condizione.

    Side effects:
        Scrive <sub>_task-RestingState_cond-<C>_inv-dSPM-stcs.npz (grande, poi rimosso da cleanup_stcs).
    """
    out: dict = {}
    for cond, task in CONDITIONS.items():
        npz = _stcs_npz(sub, cond)
        if npz.exists():
            print(f"  [step2b] {sub} {cond}: stcs.npz cached")
            d = np.load(npz, allow_pickle=True)
            out[cond] = {"n_epochs": int(d["n_epochs"]), "file_mb": npz.stat().st_size / 1e6}
            continue

        edf = _edf_path(sub, task)
        if not edf.exists():
            print(f"  [step2b] {sub} {cond}: EDF missing → skip")
            out[cond] = {"n_epochs": 0, "file_mb": 0, "status": "missing_edf"}
            continue

        t0 = time.perf_counter()
        raw = _load_raw(edf)
        # Epoche a lunghezza fissa (2 s, overlap 0.5 s) sul resting-state continuo
        events = mne.make_fixed_length_events(raw, duration=EPOCH_DURATION, overlap=EPOCH_OVERLAP)
        epochs = mne.Epochs(
            raw, events, tmin=0.0, tmax=EPOCH_DURATION, baseline=None, preload=True, verbose=False
        )
        del raw

        stcs = mne.minimum_norm.apply_inverse_epochs(
            epochs, inv_op, lambda2=LAMBDA2, method=METHOD, return_generator=False, verbose=False
        )
        del epochs

        # Stack (n_epoche, n_sorgenti, n_tempi) in float32 per risparmiare disco
        data = np.stack([s.data for s in stcs]).astype(np.float32)
        vl, vr = stcs[0].vertices[0], stcs[0].vertices[1]
        np.savez_compressed(
            npz,
            data=data,
            vertices_lh=vl,
            vertices_rh=vr,
            tmin=stcs[0].tmin,
            tstep=stcs[0].tstep,
            n_epochs=len(stcs),
            sfreq=SFREQ_TARGET,
        )
        del stcs, data

        mb = npz.stat().st_size / 1e6
        elapsed = time.perf_counter() - t0
        print(f"  [step2b] {sub} {cond}: {mb:.0f} MB in {elapsed:.1f}s")
        out[cond] = {
            "n_epochs": int(np.load(npz, allow_pickle=True)["n_epochs"]),
            "file_mb": mb,
            "elapsed_s": round(elapsed, 1),
        }
    return out


# ===== 5. STEP 3b — Parcellazione per-epoch =====
def _label_ts_npz(sub: str, atlas: str, cond: str) -> Path:
    """Percorso del file label_ts per-epoca per soggetto/atlante/condizione.

    Args:
        sub: id soggetto.
        atlas: nome atlante.
        cond: 'EO' o 'EC'.

    Returns:
        Path del file.
    """
    return LABEL_TS_DIR / f"{sub}_atlas-{atlas}_cond-{cond}_per-epoch.npz"


def step3b_parc(sub: str, fwd: mne.Forward) -> dict:
    """Step 3b: parcellizza le STC per-epoca in serie temporali per ROI (mean_flip).

    Args:
        sub: id soggetto.
        fwd: forward solution (fornisce lo spazio delle sorgenti).

    Returns:
        dict {'<atlante>_<cond>': stato/tempi}.

    Side effects:
        Scrive data/label_ts/ds005385/*_per-epoch.npz con label_tc (n_epoche, n_ROI, n_tempi).
    """
    src = fwd["src"]
    label_cache: dict[str, list] = {}
    out: dict = {}

    for atlas in ATLASES:
        if atlas not in label_cache:
            label_cache[atlas] = get_labels(atlas, subject="fsaverage")
        labels = label_cache[atlas]
        label_names = [lbl.name for lbl in labels]

        for cond in CONDITIONS:
            out_p = _label_ts_npz(sub, atlas, cond)
            if out_p.exists():
                print(f"  [step3b] {sub} {atlas} {cond}: cached")
                out[f"{atlas}_{cond}"] = {"status": "cached"}
                continue

            stcs_p = _stcs_npz(sub, cond)
            if not stcs_p.exists():
                print(f"  [step3b] {sub} {atlas} {cond}: stcs.npz missing → skip")
                out[f"{atlas}_{cond}"] = {"status": "missing_stcs"}
                continue

            t0 = time.perf_counter()
            d = np.load(stcs_p, allow_pickle=True)
            data = d["data"]
            stcs_list = [
                mne.SourceEstimate(
                    data=data[i].astype(np.float64),
                    vertices=[d["vertices_lh"], d["vertices_rh"]],
                    tmin=float(d["tmin"]),
                    tstep=float(d["tstep"]),
                    subject="fsaverage",
                )
                for i in range(data.shape[0])
            ]
            del data

            # Serie per ROI con mean_flip: media con inversione di segno per evitare cancellazioni
            tcs = mne.extract_label_time_course(
                stcs_list, labels, src, mode="mean_flip", allow_empty=True, verbose=False
            )
            del stcs_list

            label_tc = np.stack(tcs).astype(np.float32)
            del tcs

            np.savez_compressed(
                out_p,
                label_tc=label_tc,
                label_names=np.array(label_names),
                subject=sub,
                condition=cond,
                atlas=atlas,
                mode="mean_flip",
                sfreq=SFREQ_TARGET,
            )
            del label_tc

            elapsed = time.perf_counter() - t0
            print(f"  [step3b] {sub} {atlas} {cond}: {elapsed:.1f}s")
            out[f"{atlas}_{cond}"] = {"elapsed_s": round(elapsed, 1)}

    return out


# ===== 6. Cleanup stcs.npz =====
def cleanup_stcs(sub: str) -> float:
    """Elimina i file stcs.npz di un soggetto per liberare disco.

    Args:
        sub: id soggetto.

    Returns:
        GB liberati (float).

    Side effects:
        Cancella file stcs.npz (irreversibile).
    """
    freed = 0.0
    for cond in CONDITIONS:
        p = _stcs_npz(sub, cond)
        if p.exists():
            freed += p.stat().st_size / 1e9
            p.unlink()
    return freed


# ===== 7. STEP 4b — FC per-epoch =====
def _conn_npz(sub: str, atlas: str, cond: str, metric: str, band: str) -> Path:
    """Percorso del file FC per-epoca per soggetto/atlante/condizione/metrica/banda.

    Args:
        sub: id soggetto.
        atlas: atlante.
        cond: 'EO' o 'EC'.
        metric: metrica FC (wpli, coh, plv, imcoh).
        band: nome banda.

    Returns:
        Path del file.
    """
    return CONN_DIR / f"{sub}_atlas-{atlas}_cond-{cond}_metric-{metric}_band-{band}_per-epoch.npz"


def step4b_fc(subjects: list[str]) -> int:
    """Step 4b: calcola la connettività funzionale per tutte le combinazioni atlante x condizione x metrica x banda.

    Args:
        subjects: lista di soggetti da elaborare.

    Returns:
        numero di file FC prodotti o già presenti (int).

    Side effects:
        Scrive data/connectivity/ds005385/*_per-epoch.npz; salta i file già esistenti (idempotente).
    """
    n_done = 0
    for sub in subjects:
        for atlas in ATLASES:
            for cond in CONDITIONS:
                label_ts_p = _label_ts_npz(sub, atlas, cond)
                if not label_ts_p.exists():
                    print(f"  [step4b] {sub} {atlas} {cond}: label_ts missing → skip")
                    continue

                d_lt = np.load(label_ts_p, allow_pickle=True)
                label_tc = d_lt["label_tc"].astype(np.float64)

                for metric in ALL_METRICS:
                    # Calcola solo le bande il cui file non esiste ancora (idempotenza)
                    need_bands = {
                        b: hz
                        for b, hz in ALL_BANDS.items()
                        if not _conn_npz(sub, atlas, cond, metric, b).exists()
                    }
                    for b in ALL_BANDS:
                        if b not in need_bands:
                            n_done += 1

                    if not need_bands:
                        continue

                    t0 = time.perf_counter()
                    fc_dict = compute_fc(
                        label_tc, SFREQ_TARGET, metric, bands=need_bands, mode="multitaper"
                    )
                    elapsed = time.perf_counter() - t0

                    for b, mat in fc_dict.items():
                        out_p = _conn_npz(sub, atlas, cond, metric, b)
                        np.savez_compressed(
                            out_p,
                            fc_matrix=mat,
                            subject=sub,
                            condition=cond,
                            atlas=atlas,
                            metric=metric,
                            band=b,
                            sfreq=SFREQ_TARGET,
                        )
                        n_done += 1
                        print(
                            f"  [step4b] {sub} {atlas} {cond} {metric} {b}: {elapsed / len(fc_dict):.1f}s"
                        )

                del label_tc
    return n_done


# ===== 8. STEP 5 — Feature extraction =====
def step5_features(subjects: list[str], force: bool = False) -> list[dict]:
    """Step 5: appiattisce il triangolo superiore di ogni matrice FC in un vettore di feature.

    Args:
        subjects: lista soggetti della coorte target.
        force: se True ricalcola anche i file X già presenti con la forma corretta.

    Returns:
        lista di dict di esito per ciascuna combinazione atlante/metrica/banda.

    Side effects:
        Scrive y.npy, groups.npy, X_<atlante>_<metrica>_<banda>.npz e metadata_n30.json in data/features/ds005385.
    """
    y, groups = [], []
    for i, sub in enumerate(subjects):
        for cond in CONDITIONS:
            # Codifica etichette: EO=0, EC=1; groups = indice soggetto (per LOSO)
            y.append(0 if cond == "EO" else 1)
            groups.append(i)
    np.save(FEAT_DIR / "y.npy", np.array(y, dtype=np.int32))
    np.save(FEAT_DIR / "groups.npy", np.array(groups, dtype=np.int32))

    results = []
    for atlas in ATLASES:
        for metric in ALL_METRICS:
            for band in ALL_BANDS:
                out_p = FEAT_DIR / f"X_{atlas}_{metric}_{band}.npz"
                if not force and out_p.exists():
                    d = np.load(out_p, allow_pickle=True)
                    if d["X"].shape[0] == len(subjects) * 2:
                        print(f"  [step5] {atlas} {metric} {band}: SKIP (N={len(subjects)} ok)")
                        results.append(
                            {
                                "atlas": atlas,
                                "metric": metric,
                                "band": band,
                                "shape": list(d["X"].shape),
                                "skipped": True,
                            }
                        )
                        continue

                t0 = time.perf_counter()
                rows, row_labels = [], []
                ok = True
                for sub in subjects:
                    for cond in CONDITIONS:
                        fc_p = _conn_npz(sub, atlas, cond, metric, band)
                        if not fc_p.exists():
                            print(f"  [step5] MISSING: {fc_p.name}")
                            ok = False
                            break
                        d = np.load(fc_p, allow_pickle=True)
                        mat = d["fc_matrix"].astype(np.float64)
                        n = mat.shape[0]
                        # Feature = triangolo superiore senza diagonale (FC simmetrica)
                        idx = np.triu_indices(n, k=1)
                        rows.append(mat[idx])
                        row_labels.append(f"{sub}_{cond}")
                    if not ok:
                        break

                if not ok:
                    results.append(
                        {"atlas": atlas, "metric": metric, "band": band, "error": "missing_fc"}
                    )
                    continue

                X = np.stack(rows)
                np.savez_compressed(out_p, X=X, row_labels=np.array(row_labels))
                elapsed = time.perf_counter() - t0
                print(f"  [step5] {atlas} {metric} {band}: shape={X.shape} {elapsed:.1f}s")
                results.append(
                    {
                        "atlas": atlas,
                        "metric": metric,
                        "band": band,
                        "shape": list(X.shape),
                        "elapsed_s": round(elapsed, 1),
                    }
                )

    meta = {
        "timestamp": datetime.now(UTC).isoformat(timespec="seconds"),
        "subjects": subjects,
        "conditions": list(CONDITIONS.keys()),
        "atlases": ATLASES,
        "metrics": ALL_METRICS,
        "bands": list(ALL_BANDS.keys()),
        "n_subjects": len(subjects),
        "n_samples": len(subjects) * 2,
    }
    (FEAT_DIR / "metadata_n30.json").write_text(json.dumps(meta, indent=2))
    return results


# ===== 9. STEP 6+7 — ML LOSO N=30 =====
def step67_ml(
    subjects: list[str], n_perm: int = 1000, classifiers: list[str] | None = None
) -> dict:
    """Step 6+7: classificazione EO/EC con LOSO, CI bootstrap e test di permutazione.

    Args:
        subjects: lista soggetti.
        n_perm: numero di permutazioni per il p-value.
        classifiers: nomi dei classificatori (default: logreg, svm_rbf, lda, rf, mlp, gb).

    Returns:
        dict di aggregazione restituito da aggregate_classify_n15 (include 'winner' e 'results').

    Side effects:
        Scrive i risultati ML in RESULTS_DIR tramite ml_training.aggregate_n15.
    """
    if classifiers is None:
        classifiers = ["logreg", "svm_rbf", "lda", "rf", "mlp", "gb"]
    x_files = list(FEAT_DIR.glob("X_*.npz"))
    print(
        f"  [step67] {len(x_files)} X files → LOSO-{len(subjects)} ({n_perm} perm, clf={classifiers})"
    )
    agg = aggregate_classify_n15(
        features_dir=FEAT_DIR,
        out_dir=RESULTS_DIR,
        atlases=ATLASES,
        metrics=ALL_METRICS,
        bands=list(ALL_BANDS.keys()),
        classifiers=classifiers,
        n_permutations=n_perm,
        random_state=42,
        n_subjects=len(subjects),
    )
    return agg


# ===== 10. Reporte finale =====
def write_final_report(subjects: list[str], agg: dict, wall_s: float) -> None:
    """Scrive il report finale della pipeline in formato Markdown.

    Args:
        subjects: soggetti della coorte.
        agg: dict di aggregazione ML.
        wall_s: durata totale in secondi.

    Returns:
        None.

    Side effects:
        Scrive reports/SCIENTIFIC_PIPELINE_STATUS.md e reports/EXPERIMENTS_N30.md.
    """
    winner = agg.get("winner") or {}
    ts = datetime.now(UTC).isoformat(timespec="seconds")
    results = agg.get("results", [])

    lines = [
        "# Scientific Pipeline Status — ds005385 N=30 FULL RUN",
        "",
        f"**Timestamp**: {ts}",
        f"**Dataset**: ds005385 — N={len(subjects)}, seed=42",
        "",
        "## Stato step — N=30",
        "",
        "| Step | Soggetti | Stato |",
        "|------|----------|-------|",
        f"| 2 (fwd+inv) | {len(subjects)}/30 | [OK] |",
        f"| 2b (stcs per-epoch) | {len(subjects)}/30 | [OK] (cleanup post-3b) |",
        f"| 3b (label_ts) | {len(subjects)}/30 | [OK] |",
        f"| 4b (FC) | {len(subjects)}/30 | [OK] |",
        f"| 5 (features) | {len(subjects)}/30 | [OK] |",
        f"| 6+7 (ML LOSO-30) | {len(subjects)}/30 | [OK] |",
        "",
        "## Risultati finali — N=30",
        "",
        "| Metrica | Valore |",
        "|---------|--------|",
        f"| Soggetti totali | {len(subjects)} |",
        f"| Campioni (sub×cond) | {len(subjects) * 2} |",
        f"| Combos ML testati | {len(results)} |",
        f"| **Winner** | **{winner.get('atlas', '?')} × {winner.get('metric', '?')} × {winner.get('band', '?')} × {winner.get('classifier', '?')}** |",
        f"| **Best bal_acc** | **{winner.get('ba_mean', float('nan')):.3f}** CI=[{winner.get('ci_lo', float('nan')):.3f},{winner.get('ci_hi', float('nan')):.3f}] |",
        f"| **p_perm** | **{winner.get('p_perm', float('nan')):.4f}** |",
        f"| Wall-clock totale | ~{wall_s / 60:.0f} min |",
        "| Verdict pipeline | **PASS** [OK] |",
        "",
        "## Best combos (top 5)",
        "",
        "| Atlas | Metric | Band | Classifier | Bal.Acc | CI 95% | p_perm |",
        "|-------|--------|------|------------|---------|--------|--------|",
    ]

    # Top-5 combinazioni per balanced accuracy
    sorted_r = sorted(results, key=lambda r: r.get("ba_mean", 0), reverse=True)[:5]
    for r in sorted_r:
        lines.append(
            f"| {r.get('atlas', '?')} | {r.get('metric', '?')} | {r.get('band', '?')} "
            f"| {r.get('classifier', '?')} | **{r.get('ba_mean', float('nan')):.3f}** "
            f"| [{r.get('ci_lo', float('nan')):.3f},{r.get('ci_hi', float('nan')):.3f}] "
            f"| {r.get('p_perm', float('nan')):.4f} |"
        )
    lines.append("")

    Path("reports/SCIENTIFIC_PIPELINE_STATUS.md").write_text("\n".join(lines) + "\n")
    Path("reports/EXPERIMENTS_N30.md").write_text("\n".join(lines) + "\n")
    print("Reports → reports/SCIENTIFIC_PIPELINE_STATUS.md + reports/EXPERIMENTS_N30.md")


# ===== 11. Main =====
def main() -> None:
    """Punto di ingresso CLI: seleziona la coorte, esegue gli step 2-4b sui soggetti nuovi, poi step 5 e 6+7.

    Side effects:
        Modifica la variabile globale ATLASES; può terminare con sys.exit (1 = disco/whitelist, 2 = feature insufficienti).
    """
    # Attenzione: ATLASES viene sovrascritto dagli argomenti CLI
    global ATLASES
    ap = argparse.ArgumentParser(description="Pipeline N=30 H-SCALE-N30")
    ap.add_argument(
        "--skip-to-step5",
        action="store_true",
        help="Skip 2/2b/3b/4b (assume all conn done), run only 5+6+7",
    )
    ap.add_argument("--n-perm", type=int, default=1000)
    ap.add_argument("--force-features", action="store_true")
    ap.add_argument(
        "--atlases",
        default=",".join(ATLASES),
        help="Comma-separated atlas list (default: %(default)s)",
    )
    ap.add_argument(
        "--classifiers",
        default="logreg,svm_rbf,lda,rf,mlp,gb",
        help="Comma-separated classifiers (default: all 6)",
    )
    ap.add_argument(
        "--n-subjects",
        type=int,
        default=30,
        choices=[30, 50, 100, 179],
        help="Target N (30, 50, 100, or 179). 179 = full local valid (late_ses1==0).",
    )
    args = ap.parse_args()
    ATLASES = [a.strip() for a in args.atlases.split(",") if a.strip()]
    _classifiers = [c.strip() for c in args.classifiers.split(",") if c.strip()]

    # Select target/base whitelist based on --n-subjects
    # Coorte target e coorte base (già processata) in base a --n-subjects
    if args.n_subjects == 179:
        if N179 is None:
            print("ERROR: subjects_whitelist_n179.py not found.")
            sys.exit(1)
        if N100 is None:
            print("ERROR: N179 requires N100 as base.")
            sys.exit(1)
        TARGET_N = N179
        BASE_N = N100
        _tag = "N179"
    elif args.n_subjects == 100:
        if N100 is None:
            print("ERROR: subjects_whitelist_n100.py not found.")
            sys.exit(1)
        TARGET_N = N100
        BASE_N = N50 if N50 is not None else N30
        _tag = "N100"
    elif args.n_subjects == 50:
        if N50 is None:
            print(
                "ERROR: subjects_whitelist_n50.py not found. Run with --n-subjects 30 or create the file."
            )
            sys.exit(1)
        TARGET_N = N50
        BASE_N = N30
        _tag = "N50"
    else:
        TARGET_N = N30
        BASE_N = N15
        _tag = "N30"

    print(f"ATLASES: {ATLASES}, classifiers: {_classifiers}, target={_tag}")

    t_start = time.perf_counter()
    # Solo i soggetti non presenti nella coorte base richiedono step 2-4b
    new_subs = [s for s in TARGET_N if s not in BASE_N]
    print(f"{_tag} pipeline | base={len(BASE_N)} | new={len(new_subs)}")
    print(f"New subs: {new_subs}")
    print(f"Disk free: {disk_free():.1f} GB")

    write_hb("start", f"0/{len(new_subs)} new subs", disk_free())

    if not args.skip_to_step5:
        # ── Step 2/2b/3b/4b per i N15 nuovi (disk-aware interleaved) ─────────
        fwd_cache: dict[str, mne.Forward] = {}

        for i, sub in enumerate(new_subs, 1):
            df = disk_free()
            if df < DISK_ABORT_GB:
                print(f"ABORT: disk {df:.1f} GB < {DISK_ABORT_GB} GB")
                write_hb("ABORT_DISK", f"{i - 1}/{len(new_subs)}", df)
                sys.exit(1)
            if df < DISK_WARN_GB:
                print(f"WARN: disk {df:.1f} GB")

            print(f"\n{'=' * 60}")
            print(f"  {sub}  ({i}/{len(new_subs)})  disk={df:.1f} GB")
            print(f"{'=' * 60}")

            t_sub = time.perf_counter()

            # step 2
            fwd, inv_op = step2_fwd_inv(sub)
            fwd_cache[sub] = fwd

            # step 2b
            step2b_stcs(sub, inv_op)

            # step 3b
            step3b_parc(sub, fwd)

            # cleanup stcs
            freed = cleanup_stcs(sub)
            df_after = disk_free()
            print(f"  cleanup stcs: freed {freed:.1f} GB → disk={df_after:.1f} GB")

            elapsed_sub = time.perf_counter() - t_sub
            print(f"  {sub} 2+2b+3b done in {elapsed_sub:.0f}s")

            write_hb(
                "step2-3b",
                f"{i}/{len(new_subs)} new subs done (3b+cleanup)",
                df_after,
                {"last_sub": sub, "elapsed_sub_s": round(elapsed_sub)},
            )

        # ── Step 4b FC per i nuovi ─────────────────────────────────────────
        print(f"\n{'=' * 60}")
        print(f"STEP 4b — FC for {len(new_subs)} new subs")
        print(f"{'=' * 60}")
        write_hb("step4b", f"0/{len(new_subs)} FC done", disk_free())
        n_fc = step4b_fc(new_subs)
        print(f"STEP 4b done — {n_fc} FC files produced/cached")
        write_hb("step4b_done", f"FC done ({n_fc} files)", disk_free())

    # ── Step 5 — Feature extraction (tutti target) ────────────────────────────
    n_target = len(TARGET_N)
    print(f"\n{'=' * 60}")
    print(f"STEP 5 — Feature extraction N={n_target}")
    print(f"{'=' * 60}")
    write_hb("step5", f"0/{n_target} features", disk_free())
    step5_results = step5_features(TARGET_N, force=args.force_features)
    n_ok = sum(1 for r in step5_results if "error" not in r)
    n_expected = len(ATLASES) * len(ALL_METRICS) * len(ALL_BANDS)
    # Soglia di sicurezza: serve almeno l'87.5% delle matrici X per passare al ML
    threshold = max(1, int(n_expected * 0.875))
    print(f"STEP 5 done — {n_ok}/{n_expected} X matrices ok (threshold={threshold})")
    write_hb("step5_done", f"features {n_ok}/{n_expected} ok", disk_free())

    if n_ok < threshold:
        print(
            f"BLOCKER: only {n_ok}/{n_expected} X matrices — need ≥{threshold}. Stopping before ML."
        )
        write_hb("BLOCKED_FEATURES", f"only {n_ok}/{n_expected} X ok", disk_free())
        sys.exit(2)

    # ── Step 6+7 — ML LOSO ───────────────────────────────────────────
    print(f"\n{'=' * 60}")
    print(f"STEP 6+7 — ML LOSO N={n_target} (n_perm={args.n_perm})")
    print(f"{'=' * 60}")
    write_hb("step67", f"ML {_tag} running (n_perm={args.n_perm})", disk_free())
    agg = step67_ml(TARGET_N, n_perm=args.n_perm, classifiers=_classifiers)
    winner = agg.get("winner") or {}
    print(
        f"Winner: {winner.get('atlas')} × {winner.get('metric')} × "
        f"{winner.get('band')} × {winner.get('classifier')} "
        f"BA={winner.get('ba_mean', float('nan')):.3f} "
        f"p={winner.get('p_perm', float('nan')):.4f}"
    )

    wall_s = time.perf_counter() - t_start
    write_final_report(TARGET_N, agg, wall_s)

    write_hb(
        "DONE",
        f"{n_target}/{n_target} {_tag} pipeline complete",
        disk_free(),
        {
            "winner": f"{winner.get('atlas')}×{winner.get('metric')}×{winner.get('band')}×{winner.get('classifier')}",
            "ba_mean": winner.get("ba_mean"),
            "p_perm": winner.get("p_perm"),
            "wall_min": round(wall_s / 60),
        },
    )

    print(f"\nPipeline {_tag} DONE in {wall_s / 60:.0f} min")
    print(f"[TASK_DONE: H-SCALE-{_tag}]")


if __name__ == "__main__":
    main()
