"""STEP 3 pilota — parcellazione di ds005385 (5 soggetti x 2 atlanti x 2 condizioni = 20 .npz).

Scopo:
    Estrae le serie temporali per ROI (mean_flip) dalle STC prodotte dallo
    step 2 (evoked medio, quindi senza dimensione epoche) con
    parcellation.extract_label_tc.extract_tc_from_files, per gli atlanti
    aparc e schaefer100.

Input:
    STC .stc e forward in data/derivatives/mne-bids-pipeline/<sub>/eeg/

Output:
    - data/label_ts/ds005385/<sub>_atlas-<atlante>_cond-<cond>.npz (label_tc, label_names, ...)
    - reports/STEP3_DS005385_PILOT.md

Esempio:
    python scripts/pilot_step3_parcellation.py

"""

from __future__ import annotations

import sys
import time
import warnings
from datetime import UTC, datetime
from pathlib import Path

# Rende importabili i pacchetti del repository dalla cartella scripts/
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np

warnings.filterwarnings("ignore")

# ===== 1. Configurazione =====

DERIV = Path("data/derivatives/mne-bids-pipeline")
OUT_DIR = Path("data/label_ts/ds005385")
REPORT_PATH = Path("reports/STEP3_DS005385_PILOT.md")

PILOT_SUBJECTS = ["sub-007", "sub-010", "sub-011", "sub-026", "sub-031"]
ATLASES = ["aparc", "schaefer100"]
CONDITIONS = ["EO", "EC"]
TASK = "RestingState"
METHOD = "dSPM"
MODE = "mean_flip"

OUT_DIR.mkdir(parents=True, exist_ok=True)


# ===== 2. Percorsi =====


def stc_stem(sub: str, cond: str) -> Path:
    """Prefisso (senza -lh/-rh) dei file STC di un soggetto/condizione.

    Args:
        sub: id soggetto.
        cond: 'EO' o 'EC'.

    Returns:
        Path prefisso.
    """
    return DERIV / sub / "eeg" / f"{sub}_task-{TASK}_cond-{cond}_inv-{METHOD}"


def fwd_path(sub: str) -> Path:
    """Percorso della forward solution di un soggetto.

    Args:
        sub: id soggetto.

    Returns:
        Path del file .fif.
    """
    return DERIV / sub / "eeg" / f"{sub}_fwd.fif"


def npz_path(sub: str, atlas: str, cond: str) -> Path:
    """Percorso del .npz di output per soggetto/atlante/condizione.

    Args:
        sub: id soggetto.
        atlas: atlante.
        cond: 'EO' o 'EC'.

    Returns:
        Path del file.
    """
    return OUT_DIR / f"{sub}_atlas-{atlas}_cond-{cond}.npz"


# ===== 3. Estrazione serie temporali =====


def run_extraction() -> list[dict]:
    """Estrae le serie per ROI per tutte le combinazioni soggetto x atlante x condizione.

    Returns:
        lista di dict con n_labels, n_times, tempi e file prodotto.

    Side effects:
        Scrive 20 file .npz in OUT_DIR.
    """
    from parcellation.extract_label_tc import extract_tc_from_files

    results = []
    total = len(PILOT_SUBJECTS) * len(ATLASES) * len(CONDITIONS)
    done = 0

    for sub in PILOT_SUBJECTS:
        fwd = fwd_path(sub)
        for atlas in ATLASES:
            for cond in CONDITIONS:
                stem = stc_stem(sub, cond)
                out = npz_path(sub, atlas, cond)
                t0 = time.perf_counter()

                # tc ha forma (n_ROI, n_tempi): serie da evoked medio, senza epoche
                tc, names = extract_tc_from_files(stem, atlas, fwd_path=fwd, mode=MODE)
                np.savez_compressed(
                    out,
                    label_tc=tc,
                    label_names=np.array(names),
                    atlas=atlas,
                    subject=sub,
                    condition=cond,
                    task=TASK,
                    mode=MODE,
                )
                elapsed = time.perf_counter() - t0
                done += 1
                print(
                    f"[{done:02d}/{total}] {sub} {atlas:12s} {cond}  "
                    f"shape=({tc.shape[0]},{tc.shape[1]})  {elapsed:.2f}s"
                )
                results.append(
                    {
                        "sub": sub,
                        "atlas": atlas,
                        "cond": cond,
                        "n_labels": tc.shape[0],
                        "n_times": tc.shape[1],
                        "label_names_5": names[:5],
                        "elapsed_s": round(elapsed, 3),
                        "out": str(out),
                    }
                )

    return results


# ===== 4. Report =====


def write_report(results: list[dict], total_elapsed: float) -> None:
    """Scrive il report Markdown dello step 3.

    Args:
        results: output di run_extraction.
        total_elapsed: durata in secondi.

    Returns:
        None.

    Side effects:
        Scrive reports/STEP3_DS005385_PILOT.md.
    """
    ts = datetime.now(UTC).isoformat(timespec="seconds")
    lines = [
        "# STEP 3 Parcellation — ds005385 PILOT",
        "",
        f"**Timestamp**: {ts}",
        f"**Soggetti**: {PILOT_SUBJECTS}",
        f"**Atlases**: {ATLASES}",
        f"**Condizioni**: {CONDITIONS}",
        f"**Mode**: `{MODE}`",
        "",
        "---",
        "",
        "## Risultati (sub × atlas × cond)",
        "",
        "| Sub | Atlas | Cond | n_labels | n_times | Wall (s) |",
        "|-----|-------|------|----------|---------|----------|",
    ]
    all_ok = True
    for r in results:
        lines.append(
            f"| {r['sub']} | {r['atlas']} | {r['cond']} "
            f"| {r['n_labels']} | {r['n_times']} | {r['elapsed_s']} |"
        )
        if r["n_labels"] == 0:
            all_ok = False

    # Example: first result
    ex = results[0]
    lines += [
        "",
        "---",
        "",
        f"## Esempio output — {ex['sub']} × {ex['atlas']} × {ex['cond']}",
        "",
        f"**File**: `{ex['out']}`",
        "",
        "```python",
        "import numpy as np",
        f"d = np.load('{ex['out']}', allow_pickle=True)",
        "# Keys: label_tc, label_names, atlas, subject, condition, task, mode",
        f"# label_tc.shape = ({ex['n_labels']}, {ex['n_times']})",
        f"# label_names[:5] = {ex['label_names_5']}",
        "```",
        "",
        "---",
        "",
        "## Summary",
        "",
        "| Metrica | Valore |",
        "|---------|--------|",
        f"| File .npz prodotti | {len(results)} / 20 |",
        f"| Atlases | {', '.join(ATLASES)} |",
        f"| Wall-clock totale | {total_elapsed:.1f}s |",
        f"| Verdict | {'**PASS** [OK]' if all_ok else '**WARN** [WARNING]'} |",
        "",
    ]
    REPORT_PATH.write_text("\n".join(lines) + "\n")


# ===== 5. Main =====


def main() -> None:
    """Punto di ingresso: esegue l'estrazione e scrive il report.

    Side effects:
        Scrive i file .npz e il report.
    """
    print(
        f"STEP 3 Parcellation pilot — {len(PILOT_SUBJECTS)} sub × {len(ATLASES)} atlases × {len(CONDITIONS)} cond"
    )
    print(f"Mode: {MODE}")
    t0 = time.perf_counter()
    results = run_extraction()
    total = time.perf_counter() - t0
    print(f"\nTotal: {total:.1f}s | {len(results)} file .npz")
    write_report(results, total)
    print(f"Report → {REPORT_PATH}")


if __name__ == "__main__":
    main()
