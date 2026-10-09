"""STEP 4 pilota — connettività funzionale su ds005385 (5 sub x 2 atlanti x 2 cond x 2 metriche = 40 npz).

Scopo:
    Carica i label_tc dello step 3 (serie da evoked medio) e calcola la FC con
    wPLI e coerenza in banda alpha (8-13 Hz, multitaper) tramite
    connectivity.fc_dispatcher.compute_fc.

Input:
    data/label_ts/ds005385/<sub>_atlas-<atlante>_cond-<cond>.npz

Output:
    - data/connectivity/ds005385/<sub>_atlas-<atlante>_cond-<cond>_metric-<metrica>_band-alpha.npz
    - reports/STEP4_DS005385_PILOT.md

Esempio:
    python scripts/pilot_step4_connectivity.py

"""

from __future__ import annotations

import sys
import time
import warnings
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

# Rende importabili i pacchetti del repository dalla cartella scripts/
sys.path.insert(0, str(Path(__file__).parent.parent))
warnings.filterwarnings("ignore")

from connectivity.fc_dispatcher import compute_fc  # noqa: E402

# ===== 1. Configurazione =====

LABEL_TS_DIR = Path("data/label_ts/ds005385")
OUT_DIR = Path("data/connectivity/ds005385")
REPORT_PATH = Path("reports/STEP4_DS005385_PILOT.md")

SUBJECTS = ["sub-007", "sub-010", "sub-011", "sub-026", "sub-031"]
ATLASES = ["aparc", "schaefer100"]
CONDITIONS = ["EO", "EC"]
METRICS = ["wpli", "coh"]
BAND = {"alpha": (8.0, 13.0)}
SFREQ = 250.0

OUT_DIR.mkdir(parents=True, exist_ok=True)


# ===== 2. Percorsi =====


def npz_in(sub: str, atlas: str, cond: str) -> Path:
    """Percorso del file label_ts di input.

    Args:
        sub: id soggetto.
        atlas: atlante.
        cond: 'EO' o 'EC'.

    Returns:
        Path del file.
    """
    return LABEL_TS_DIR / f"{sub}_atlas-{atlas}_cond-{cond}.npz"


def npz_out(sub: str, atlas: str, cond: str, metric: str) -> Path:
    """Percorso del file FC di output.

    Args:
        sub: id soggetto.
        atlas: atlante.
        cond: 'EO' o 'EC'.
        metric: metrica FC.

    Returns:
        Path del file.
    """
    return OUT_DIR / f"{sub}_atlas-{atlas}_cond-{cond}_metric-{metric}_band-alpha.npz"


# ===== 3. Calcolo FC =====


def run_all() -> list[dict]:
    """Calcola la FC per tutte le combinazioni soggetto x atlante x condizione x metrica.

    Returns:
        lista di dict con forma, media/std del triangolo superiore, NaN, tempi e file.

    Side effects:
        Scrive 40 file .npz in OUT_DIR.
    """
    results = []
    total = len(SUBJECTS) * len(ATLASES) * len(CONDITIONS) * len(METRICS)
    done = 0

    for sub in SUBJECTS:
        for atlas in ATLASES:
            for cond in CONDITIONS:
                # Load label_tc once per (sub, atlas, cond) — reuse for both metrics
                npz = npz_in(sub, atlas, cond)
                d = np.load(npz, allow_pickle=True)
                label_tc_2d = d["label_tc"]  # (n_labels, n_times)
                label_names = list(d["label_names"])
                # compute_fc richiede (n_epoche, n_ROI, n_tempi): qui una sola "epoca"
                label_tc = label_tc_2d[np.newaxis, :, :]  # (1, n_labels, n_times)

                for metric in METRICS:
                    out = npz_out(sub, atlas, cond, metric)
                    t0 = time.perf_counter()

                    fc_dict = compute_fc(label_tc, SFREQ, metric, bands=BAND, mode="multitaper")
                    mat = fc_dict["alpha"]  # (n_labels, n_labels)

                    # Compute stats for report
                    # Statistiche sul triangolo superiore (esclusa la diagonale), ignorando i NaN
                    upper_idx = np.triu_indices(mat.shape[0], k=1)
                    upper = mat[upper_idx]
                    n_nan = int(np.isnan(upper).sum())
                    upper_clean = upper[~np.isnan(upper)]
                    mean_upper = float(np.mean(upper_clean)) if len(upper_clean) else float("nan")
                    std_upper = float(np.std(upper_clean)) if len(upper_clean) else float("nan")

                    np.savez_compressed(
                        out,
                        fc_matrix=mat,
                        label_names=np.array(label_names),
                        subject=sub,
                        condition=cond,
                        atlas=atlas,
                        metric=metric,
                        band="alpha",
                        band_hz=np.array([8.0, 13.0]),
                        sfreq=SFREQ,
                        mode="multitaper",
                    )
                    elapsed = time.perf_counter() - t0
                    done += 1
                    print(
                        f"[{done:02d}/{total}] {sub} {atlas:12s} {cond} {metric:4s} "
                        f"shape=({mat.shape[0]},{mat.shape[1]}) "
                        f"mean={mean_upper:.4f} std={std_upper:.4f} "
                        f"nan={n_nan} {elapsed:.2f}s"
                    )
                    results.append(
                        {
                            "sub": sub,
                            "atlas": atlas,
                            "cond": cond,
                            "metric": metric,
                            "shape": mat.shape,
                            "mean_upper": round(mean_upper, 4),
                            "std_upper": round(std_upper, 4),
                            "n_nan": n_nan,
                            "elapsed_s": round(elapsed, 3),
                            "out": str(out),
                        }
                    )

    return results


# ===== 4. Report =====


def write_report(results: list[dict], total_elapsed: float) -> None:
    """Scrive il report Markdown dello step 4.

    Args:
        results: output di run_all.
        total_elapsed: durata in secondi.

    Returns:
        None.

    Side effects:
        Scrive reports/STEP4_DS005385_PILOT.md.
    """
    ts = datetime.now(UTC).isoformat(timespec="seconds")
    n_nan_total = sum(r["n_nan"] for r in results)
    all_ok = n_nan_total == 0

    lines = [
        "# STEP 4 Functional Connectivity — ds005385 PILOT",
        "",
        f"**Timestamp**: {ts}",
        f"**Soggetti**: {SUBJECTS}",
        "**Metriche**: wpli, coh",
        "**Banda**: alpha (8-13 Hz)",
        "**Mode**: multitaper",
        f"**sfreq**: {SFREQ} Hz",
        "",
        "---",
        "",
        "## Risultati (40 file)",
        "",
        "| Sub | Atlas | Cond | Metric | Shape FC | Mean upper | Std upper | NaN | Time (s) |",
        "|-----|-------|------|--------|----------|------------|-----------|-----|----------|",
    ]
    for r in results:
        lines.append(
            f"| {r['sub']} | {r['atlas']} | {r['cond']} | {r['metric']} "
            f"| {r['shape'][0]}×{r['shape'][1]} "
            f"| {r['mean_upper']:.4f} | {r['std_upper']:.4f} "
            f"| {r['n_nan']} | {r['elapsed_s']} |"
        )

    ex = results[0]
    d = np.load(ex["out"], allow_pickle=True)
    mat = d["fc_matrix"]
    upper = mat[np.triu_indices(mat.shape[0], k=1)]

    lines += [
        "",
        "---",
        "",
        f"## Esempio — {ex['sub']} × {ex['atlas']} × {ex['cond']} × {ex['metric']}",
        "",
        f"**File**: `{ex['out']}`",
        "",
        "```python",
        "import numpy as np",
        f"d = np.load('{ex['out']}', allow_pickle=True)",
        "# Keys: fc_matrix, label_names, subject, condition, atlas, metric, band, band_hz, sfreq, mode",
        f"# fc_matrix.shape = {mat.shape}",
        f"# upper triangle: mean={upper[~np.isnan(upper)].mean():.4f}, "
        f"std={upper[~np.isnan(upper)].std():.4f}, "
        f"range=[{upper[~np.isnan(upper)].min():.4f}, {upper[~np.isnan(upper)].max():.4f}]",
        "```",
        "",
        "---",
        "",
        "## Summary",
        "",
        "| Metrica | Valore |",
        "|---------|--------|",
        f"| File .npz prodotti | {len(results)} / 40 |",
        f"| NaN totali (upper triangle) | {n_nan_total} |",
        f"| Wall-clock totale | {total_elapsed:.1f}s |",
        f"| Verdict | {'**PASS** [OK]' if all_ok else '**WARN** [WARNING] (NaN presenti)'} |",
        "",
    ]
    REPORT_PATH.write_text("\n".join(lines) + "\n")


# ===== 5. Main =====


def main() -> None:
    """Punto di ingresso: calcola la FC e scrive il report.

    Side effects:
        Scrive i file .npz e il report.
    """
    print("STEP 4 Connectivity pilot — 5 sub × 2 atlas × 2 cond × 2 metric = 40 file")
    print(f"Band: alpha (8-13 Hz) | Mode: multitaper | sfreq: {SFREQ} Hz")
    t0 = time.perf_counter()
    results = run_all()
    total = time.perf_counter() - t0
    print(f"\nTotal: {total:.1f}s | {len(results)} file .npz")
    write_report(results, total)
    print(f"Report → {REPORT_PATH}")


if __name__ == "__main__":
    main()
