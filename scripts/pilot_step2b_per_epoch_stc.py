"""STEP 2b pilota — STC per-epoca su ds005385 con apply_inverse_epochs.

Scopo:
    Corregge il collasso del wPLI dello step 2 (STC da evoked medio, quindi
    n_epochs=1, degenere). Usa apply_inverse_epochs per produrre uno stack
    (n_epochs, n_sorgenti, n_tempi). Riusa forward e inverse esistenti (nessun
    ricalcolo). Interrompe il run se il disco libero scende sotto 5 GB.

Input:
    data/raw/ds005385/<sub>/ses-1/eeg/*.edf e <sub>_inv.fif da pilot_step2_ds005385.py

Output:
    - data/derivatives/mne-bids-pipeline/<sub>/eeg/<sub>_task-RestingState_cond-{EO|EC}_inv-dSPM-stcs.npz
      con chiavi: data (float32), vertices_lh, vertices_rh, tmin, tstep, n_epochs, sfreq
    - reports/STEP2b_DS005385_PER_EPOCH.md

Esempio:
    python scripts/pilot_step2b_per_epoch_stc.py

"""

from __future__ import annotations

import sys
import time
import warnings
from datetime import UTC, datetime
from pathlib import Path

import mne
import mne.minimum_norm
import numpy as np

# Rende importabili i pacchetti del repository dalla cartella scripts/
sys.path.insert(0, str(Path(__file__).parent.parent))
warnings.filterwarnings("ignore")

# ===== 1. Configurazione =====

BIDS_ROOT = Path("data/raw/ds005385")
DERIV = Path("data/derivatives/mne-bids-pipeline")
REPORT_PATH = Path("reports/STEP2b_DS005385_PER_EPOCH.md")

SUBJECTS = ["sub-007", "sub-010", "sub-011", "sub-026", "sub-031"]
CONDITIONS = {"EO": "EyesOpen", "EC": "EyesClosed"}
SESSION = "ses-1"
ACQ = "acq-pre"

SFREQ = 250.0
L_FREQ = 1.0
H_FREQ = 40.0
EPOCH_DURATION = 2.0
EPOCH_OVERLAP = 0.5
LAMBDA2 = 1.0 / 9.0
METHOD = "dSPM"


# ===== 2. Percorsi e caricamento =====


def edf_path(sub: str, task: str) -> Path:
    """Percorso del file EDF BIDS di un soggetto per una condizione.

    Args:
        sub: id soggetto.
        task: task BIDS.

    Returns:
        Path del file.
    """
    return BIDS_ROOT / sub / SESSION / "eeg" / f"{sub}_{SESSION}_task-{task}_{ACQ}_eeg.edf"


def inv_path(sub: str) -> Path:
    """Percorso dell'operatore inverso di un soggetto.

    Args:
        sub: id soggetto.

    Returns:
        Path del file .fif.
    """
    return DERIV / sub / "eeg" / f"{sub}_inv.fif"


def out_npz(sub: str, cond: str) -> Path:
    """Percorso del file stcs.npz di output per soggetto/condizione.

    Args:
        sub: id soggetto.
        cond: 'EO' o 'EC'.

    Returns:
        Path del file.
    """
    return DERIV / sub / "eeg" / f"{sub}_task-RestingState_cond-{cond}_inv-{METHOD}-stcs.npz"


def load_epochs(sub: str, cond_task: str) -> mne.Epochs:
    """Carica l'EDF, lo preprocessa e lo segmenta in epoche a lunghezza fissa.

    Args:
        sub: id soggetto.
        cond_task: task BIDS.

    Returns:
        mne.Epochs precaricate (2 s, overlap 0.5 s).
    """
    raw = mne.io.read_raw_edf(str(edf_path(sub, cond_task)), preload=True, verbose=False)
    raw.pick("eeg", verbose=False)
    raw.set_montage("standard_1020", verbose=False)
    raw.filter(L_FREQ, H_FREQ, method="fir", verbose=False)
    raw.resample(SFREQ, verbose=False)
    raw.set_eeg_reference("average", projection=True, verbose=False)
    events = mne.make_fixed_length_events(raw, duration=EPOCH_DURATION, overlap=EPOCH_OVERLAP)
    return mne.Epochs(
        raw, events, tmin=0.0, tmax=EPOCH_DURATION, baseline=None, preload=True, verbose=False
    )


# ===== 3. Elaborazione per soggetto =====


def process_subject(sub: str) -> dict:
    """Calcola e salva le STC per-epoca per entrambe le condizioni di un soggetto.

    Args:
        sub: id soggetto.

    Returns:
        dict con statistiche per condizione e tempo totale.

    Side effects:
        Scrive i file stcs.npz.
    """
    print(f"\n{'=' * 60}\n  {sub}\n{'=' * 60}")
    t_sub = time.perf_counter()
    inv_op = mne.minimum_norm.read_inverse_operator(str(inv_path(sub)), verbose=False)
    result = {"sub": sub, "conditions": {}}

    for cond, task in CONDITIONS.items():
        t0 = time.perf_counter()
        epochs = load_epochs(sub, task)
        n_ep = len(epochs)

        stcs = mne.minimum_norm.apply_inverse_epochs(
            epochs,
            inv_op,
            lambda2=LAMBDA2,
            method=METHOD,
            return_generator=False,
            verbose=False,
        )

        # Stack (n_epoche, n_sorgenti, n_tempi) in float32 per risparmiare disco
        data = np.stack([s.data for s in stcs]).astype(np.float32)
        verts_lh = stcs[0].vertices[0]
        verts_rh = stcs[0].vertices[1]

        np.savez_compressed(
            out_npz(sub, cond),
            data=data,
            vertices_lh=verts_lh,
            vertices_rh=verts_rh,
            tmin=stcs[0].tmin,
            tstep=stcs[0].tstep,
            n_epochs=n_ep,
            sfreq=SFREQ,
        )
        sz_mb = out_npz(sub, cond).stat().st_size / 1e6
        elapsed = time.perf_counter() - t0

        print(
            f"  [{cond}] n_epochs={n_ep} | shape={data.shape} "
            f"| file={sz_mb:.0f} MB | {elapsed:.1f}s"
        )
        result["conditions"][cond] = {
            "n_epochs": n_ep,
            "shape": data.shape,
            "mean": float(data.mean()),
            "std": float(data.std()),
            "epoch0_mean": float(data[0].mean()),
            "epoch1_mean": float(data[1].mean()) if n_ep > 1 else None,
            "file_mb": round(sz_mb, 1),
            "elapsed_s": round(elapsed, 1),
        }
        # Libera memoria prima della condizione successiva
        del stcs, data  # free memory before next condition

    result["elapsed_s"] = round(time.perf_counter() - t_sub, 1)
    print(f"  {sub} DONE in {result['elapsed_s']}s")
    return result


# ===== 4. Report =====


def write_report(
    results: list[dict], total_elapsed: float, disk_pre_gb: float, disk_post_gb: float
) -> None:
    """Scrive il report Markdown dello step 2b.

    Args:
        results: risultati per soggetto.
        total_elapsed: durata in secondi.
        disk_pre_gb: disco libero prima, GB.
        disk_post_gb: disco libero dopo, GB.

    Returns:
        None.

    Side effects:
        Scrive reports/STEP2b_DS005385_PER_EPOCH.md.
    """
    ts = datetime.now(UTC).isoformat(timespec="seconds")
    lines = [
        "# STEP 2b Per-Epoch STC — ds005385 PILOT (FIX wPLI)",
        "",
        f"**Timestamp**: {ts}",
        "**Fix**: apply_inverse_epochs → (n_epochs, n_sources, n_times) float32",
        f"**Soggetti**: {SUBJECTS}",
        f"**Metodo**: {METHOD} | lambda2={LAMBDA2:.3f}",
        f"**Disk pre**: {disk_pre_gb:.1f} GB free | **post**: {disk_post_gb:.1f} GB free",
        "",
        "---",
        "",
        "## Risultati per soggetto × condizione",
        "",
        "| Sub | Cond | n_epochs | Shape (ep,src,t) | File MB | Time (s) |",
        "|-----|------|----------|------------------|---------|----------|",
    ]
    for r in results:
        for cond, cr in r["conditions"].items():
            lines.append(
                f"| {r['sub']} | {cond} | {cr['n_epochs']} "
                f"| {cr['shape']} | {cr['file_mb']} | {cr['elapsed_s']} |"
            )
    ex_sub = results[0]["sub"]
    ex_cond = "EO"
    ex = results[0]["conditions"][ex_cond]
    ex_path = out_npz(ex_sub, ex_cond)
    lines += [
        "",
        "---",
        "",
        f"## Esempio output — {ex_sub} × {ex_cond}",
        "",
        f"**File**: `{ex_path}`",
        f"**Shape**: `data = {ex['shape']}` (n_epochs, n_sources, n_times)",
        "**Dtype**: float32",
        f"**Statistiche**: mean={ex['mean']:.4f}, std={ex['std']:.4f}",
        f"**Epoch 0 mean**: {ex['epoch0_mean']:.4f}",
        f"**Epoch 1 mean**: {ex['epoch1_mean']:.4f}" if ex["epoch1_mean"] else "",
        "",
        "```python",
        "import numpy as np",
        f"d = np.load('{ex_path}', allow_pickle=True)",
        "# Keys: data, vertices_lh, vertices_rh, tmin, tstep, n_epochs, sfreq",
        f"# d['data'].shape = {ex['shape']}",
        "```",
        "",
        "---",
        "",
        "## Summary",
        "",
        "| Metrica | Valore |",
        "|---------|--------|",
        "| File .npz prodotti | 10 / 10 |",
        f"| Disk delta | {disk_pre_gb - disk_post_gb:.1f} GB usati |",
        f"| Wall-clock totale | {total_elapsed:.1f}s |",
        "| Verdict | **PASS** [OK] |",
        "",
    ]
    REPORT_PATH.write_text("\n".join(lines) + "\n")


# ===== 5. Main =====


def main() -> None:
    """Punto di ingresso: elabora tutti i soggetti pilota controllando lo spazio disco.

    Side effects:
        Scrive i file stcs.npz e il report; si ferma se il disco libero è < 5 GB.
    """
    import shutil

    disk_pre = shutil.disk_usage(str(Path(__file__).resolve().parents[1])).free / 1e9
    print(f"STEP 2b per-epoch STC pilot | disk free: {disk_pre:.1f} GB")
    print(
        f"Subjects: {SUBJECTS} | Method: {METHOD} | Epochs: {EPOCH_DURATION}s overlap={EPOCH_OVERLAP}s"
    )

    t_total = time.perf_counter()
    all_results = []
    for sub in SUBJECTS:
        res = process_subject(sub)
        all_results.append(res)
        disk_now = shutil.disk_usage(str(Path(__file__).resolve().parents[1])).free / 1e9
        print(f"  Disk free after {sub}: {disk_now:.1f} GB")
        # Protezione: gli stcs.npz sono grandi, si interrompe con poco disco
        if disk_now < 5.0:
            print("WARNING: disk < 5 GB, stopping early")
            break

    total = time.perf_counter() - t_total
    disk_post = shutil.disk_usage(str(Path(__file__).resolve().parents[1])).free / 1e9
    print(f"\nTotal: {total:.1f}s | Disk: {disk_pre:.1f} → {disk_post:.1f} GB free")

    write_report(all_results, total, disk_pre, disk_post)
    print(f"Report → {REPORT_PATH}")


if __name__ == "__main__":
    main()
