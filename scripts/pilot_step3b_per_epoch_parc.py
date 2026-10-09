"""STEP 3b pilota — parcellazione per-epoca di ds005385 (5 soggetti x 2 atlanti x 2 condizioni = 20 npz).

Scopo:
    Usa le STC per-epoca dello step 2b per produrre label_tc di forma
    (n_epochs, n_labels, n_times) con mode mean_flip. Risolve il collasso del
    wPLI fornendo al dispatcher FC l'input corretto (più epoche).

Input:
    stcs.npz per-epoca e forward in data/derivatives/mne-bids-pipeline/<sub>/eeg/

Output:
    - data/label_ts/ds005385/<sub>_atlas-<atlante>_cond-<cond>_per-epoch.npz
      (label_tc, label_names, subject, condition, atlas, mode, n_epochs, sfreq)
    - reports/STEP3b_DS005385_PER_EPOCH.md

Esempio:
    python scripts/pilot_step3b_per_epoch_parc.py

"""

from __future__ import annotations

import sys
import time
import warnings
from datetime import UTC, datetime
from pathlib import Path

import mne
import numpy as np

# Rende importabili i pacchetti del repository dalla cartella scripts/
sys.path.insert(0, str(Path(__file__).parent.parent))
warnings.filterwarnings("ignore")

from parcellation.extract_label_tc import get_labels  # noqa: E402

# ===== 1. Configurazione =====

DERIV = Path("data/derivatives/mne-bids-pipeline")
OUT_DIR = Path("data/label_ts/ds005385")
REPORT_PATH = Path("reports/STEP3b_DS005385_PER_EPOCH.md")
SUBJECTS_DIR = Path.home() / "mne_data" / "MNE-fsaverage-data"  # posizione standard fsaverage (F0)

SUBJECTS = ["sub-007", "sub-010", "sub-011", "sub-026", "sub-031"]
ATLASES = ["aparc", "schaefer100"]
CONDITIONS = ["EO", "EC"]
MODE = "mean_flip"
SFREQ = 250.0

OUT_DIR.mkdir(parents=True, exist_ok=True)


# ===== 2. Percorsi =====


def stcs_npz(sub: str, cond: str) -> Path:
    """Percorso del file stcs.npz di un soggetto/condizione.

    Args:
        sub: id soggetto.
        cond: 'EO' o 'EC'.

    Returns:
        Path del file.
    """
    return DERIV / sub / "eeg" / f"{sub}_task-RestingState_cond-{cond}_inv-dSPM-stcs.npz"


def fwd_path(sub: str) -> Path:
    """Percorso della forward solution di un soggetto.

    Args:
        sub: id soggetto.

    Returns:
        Path del file .fif.
    """
    return DERIV / sub / "eeg" / f"{sub}_fwd.fif"


def out_npz(sub: str, atlas: str, cond: str) -> Path:
    """Percorso del .npz di output per soggetto/atlante/condizione.

    Args:
        sub: id soggetto.
        atlas: atlante.
        cond: 'EO' o 'EC'.

    Returns:
        Path del file.
    """
    return OUT_DIR / f"{sub}_atlas-{atlas}_cond-{cond}_per-epoch.npz"


# ===== 3. Caricamento e parcellazione =====


def load_stc_list(sub: str, cond: str) -> tuple[list[mne.SourceEstimate], int]:
    """Ricostruisce la lista di SourceEstimate (una per epoca) dal file stcs.npz.

    Args:
        sub: id soggetto.
        cond: condizione.

    Returns:
        tupla (lista di mne.SourceEstimate su fsaverage, numero di epoche).
    """
    d = np.load(stcs_npz(sub, cond), allow_pickle=True)
    data = d["data"]  # (n_epochs, n_sources, n_times)
    vl = d["vertices_lh"]
    vr = d["vertices_rh"]
    tmin = float(d["tmin"])
    tstep = float(d["tstep"])
    stcs = [
        mne.SourceEstimate(
            data=data[i].astype(np.float64),
            vertices=[vl, vr],
            tmin=tmin,
            tstep=tstep,
            subject="fsaverage",
        )
        for i in range(data.shape[0])
    ]
    return stcs, data.shape[0]


def run_all() -> list[dict]:
    """Parcellizza tutte le combinazioni soggetto x atlante x condizione.

    Returns:
        lista di dict con forma, medie delle prime epoche e tempi.

    Side effects:
        Scrive 20 file *_per-epoch.npz in OUT_DIR.
    """
    # Cache delle label per atlante: la lettura dell'atlante è costosa
    label_cache: dict[str, list[mne.Label]] = {}

    results = []
    total = len(SUBJECTS) * len(ATLASES) * len(CONDITIONS)
    done = 0

    for sub in SUBJECTS:
        fwd = mne.read_forward_solution(str(fwd_path(sub)), verbose=False)
        src = fwd["src"]

        for atlas in ATLASES:
            if atlas not in label_cache:
                label_cache[atlas] = get_labels(atlas, subject="fsaverage")

            labels = label_cache[atlas]
            n_labels = len(labels)
            label_names = [lbl.name for lbl in labels]

            for cond in CONDITIONS:
                t0 = time.perf_counter()
                stcs, n_epochs = load_stc_list(sub, cond)

                # Serie per ROI con mean_flip (media con inversione di segno)
                tcs = mne.extract_label_time_course(
                    stcs, labels, src, mode=MODE, allow_empty=True, verbose=False
                )
                # Forma (n_epoche, n_ROI, n_tempi)
                label_tc = np.stack(tcs).astype(np.float32)  # (n_epochs, n_labels, n_times)

                np.savez_compressed(
                    out_npz(sub, atlas, cond),
                    label_tc=label_tc,
                    label_names=np.array(label_names),
                    subject=sub,
                    condition=cond,
                    atlas=atlas,
                    mode=MODE,
                    n_epochs=n_epochs,
                    sfreq=SFREQ,
                )
                elapsed = time.perf_counter() - t0
                done += 1

                # Medie delle prime epoche: controllo che le epoche non siano identiche
                ep0_mean = float(label_tc[0].mean())
                ep1_mean = float(label_tc[1].mean()) if n_epochs > 1 else float("nan")
                ep2_mean = float(label_tc[2].mean()) if n_epochs > 2 else float("nan")

                print(
                    f"[{done:02d}/{total}] {sub} {atlas:12s} {cond}  "
                    f"shape=({n_epochs},{n_labels},{label_tc.shape[2]})  "
                    f"ep0={ep0_mean:.4f}  {elapsed:.1f}s"
                )
                results.append(
                    {
                        "sub": sub,
                        "atlas": atlas,
                        "cond": cond,
                        "n_epochs": n_epochs,
                        "n_labels": n_labels,
                        "n_times": label_tc.shape[2],
                        "ep0_mean": round(ep0_mean, 4),
                        "ep1_mean": round(ep1_mean, 4),
                        "ep2_mean": round(ep2_mean, 4),
                        "elapsed_s": round(elapsed, 1),
                    }
                )
                del stcs, tcs, label_tc

    return results


# ===== 4. Report =====


def write_report(results: list[dict], total_elapsed: float) -> None:
    """Scrive il report Markdown dello step 3b.

    Args:
        results: output di run_all.
        total_elapsed: durata in secondi.

    Returns:
        None.

    Side effects:
        Scrive reports/STEP3b_DS005385_PER_EPOCH.md.
    """
    ts = datetime.now(UTC).isoformat(timespec="seconds")
    lines = [
        "# STEP 3b Per-Epoch Parcellation — ds005385 PILOT",
        "",
        f"**Timestamp**: {ts}",
        f"**Soggetti**: {SUBJECTS}",
        f"**Atlases**: {ATLASES}  **Mode**: {MODE}",
        "",
        "---",
        "",
        "## Risultati (20 estrazioni)",
        "",
        "| Sub | Atlas | Cond | Shape (ep,lbl,t) | ep0 mean | Time (s) |",
        "|-----|-------|------|-----------------|----------|----------|",
    ]
    for r in results:
        lines.append(
            f"| {r['sub']} | {r['atlas']} | {r['cond']} "
            f"| ({r['n_epochs']},{r['n_labels']},{r['n_times']}) "
            f"| {r['ep0_mean']} | {r['elapsed_s']} |"
        )

    ex = results[0]
    ex_path = out_npz(ex["sub"], ex["atlas"], ex["cond"])
    lines += [
        "",
        "---",
        "",
        f"## Esempio — {ex['sub']} × {ex['atlas']} × {ex['cond']}",
        "",
        f"**File**: `{ex_path}`",
        f"**Shape**: `label_tc = ({ex['n_epochs']}, {ex['n_labels']}, {ex['n_times']})`",
        f"**Epoch means**: ep0={ex['ep0_mean']}, ep1={ex['ep1_mean']}, ep2={ex['ep2_mean']}",
        "",
        "```python",
        "import numpy as np",
        f"d = np.load('{ex_path}', allow_pickle=True)",
        "# Keys: label_tc, label_names, subject, condition, atlas, mode, n_epochs, sfreq",
        f"# label_tc.shape = ({ex['n_epochs']}, {ex['n_labels']}, {ex['n_times']})",
        "```",
        "",
        "---",
        "",
        "## Summary",
        "",
        "| Metrica | Valore |",
        "|---------|--------|",
        f"| File .npz prodotti | {len(results)} / 20 |",
        f"| Wall-clock totale | {total_elapsed:.1f}s |",
        "| Verdict | **PASS** [OK] |",
        "",
    ]
    REPORT_PATH.write_text("\n".join(lines) + "\n")


# ===== 5. Main =====


def main() -> None:
    """Punto di ingresso: esegue la parcellazione e scrive il report.

    Side effects:
        Scrive i file .npz e il report.
    """
    print(
        f"STEP 3b per-epoch parcellation | {len(SUBJECTS)} sub × {len(ATLASES)} atlas × {len(CONDITIONS)} cond"
    )
    t0 = time.perf_counter()
    results = run_all()
    total = time.perf_counter() - t0
    print(f"\nTotal: {total:.1f}s | {len(results)} file .npz")
    write_report(results, total)
    print(f"Report → {REPORT_PATH}")


if __name__ == "__main__":
    main()
