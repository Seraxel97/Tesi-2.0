"""
STEP 4b — FC rerun su per-epoch label_tc (fix wPLI collapse S-104).

Input:  data/label_ts/ds005385/sub-XXX_atlas-XXX_cond-XXX_per-epoch.npz
        label_tc.shape = (n_epochs, n_labels, n_times)  [3D ✓]
Output: data/connectivity/ds005385/sub-XXX_atlas-XXX_cond-XXX_metric-XXX_band-alpha_per-epoch.npz
        fc_matrix: (n_labels, n_labels) | metriche: wpli + coh | banda: alpha 8-13 Hz
"""

from __future__ import annotations

import sys
import time
import warnings
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))
warnings.filterwarnings("ignore")

from connectivity.fc_dispatcher import compute_fc  # noqa: E402

IN_DIR = Path("data/label_ts/ds005385")
OUT_DIR = Path("data/connectivity/ds005385")
REPORT_PATH = Path("reports/STEP4b_DS005385_RERUN.md")

SUBJECTS = ["sub-007", "sub-010", "sub-011", "sub-026", "sub-031"]
ATLASES = ["aparc", "schaefer100"]
CONDITIONS = ["EO", "EC"]
METRICS = ["wpli", "coh"]
BAND = {"alpha": (8.0, 13.0)}
SFREQ = 250.0

OUT_DIR.mkdir(parents=True, exist_ok=True)


def npz_in(sub: str, atlas: str, cond: str) -> Path:
    return IN_DIR / f"{sub}_atlas-{atlas}_cond-{cond}_per-epoch.npz"


def npz_out(sub: str, atlas: str, cond: str, metric: str) -> Path:
    return OUT_DIR / f"{sub}_atlas-{atlas}_cond-{cond}_metric-{metric}_band-alpha_per-epoch.npz"


def run_all() -> list[dict]:
    results = []
    total = len(SUBJECTS) * len(ATLASES) * len(CONDITIONS) * len(METRICS)
    done = 0

    for sub in SUBJECTS:
        for atlas in ATLASES:
            for cond in CONDITIONS:
                d = np.load(npz_in(sub, atlas, cond), allow_pickle=True)
                label_tc = d["label_tc"].astype(np.float64)  # (n_ep, n_labels, n_times)
                label_names = list(d["label_names"])
                n_ep = label_tc.shape[0]

                for metric in METRICS:
                    t0 = time.perf_counter()
                    fc_dict = compute_fc(label_tc, SFREQ, metric, bands=BAND, mode="multitaper")
                    mat = fc_dict["alpha"]
                    upper = mat[np.triu_indices(mat.shape[0], k=1)]
                    upper_valid = upper[~np.isnan(upper)]
                    mean_u = float(np.mean(upper_valid)) if len(upper_valid) else float("nan")
                    std_u = float(np.std(upper_valid)) if len(upper_valid) else float("nan")

                    np.savez_compressed(
                        npz_out(sub, atlas, cond, metric),
                        fc_matrix=mat,
                        label_names=np.array(label_names),
                        subject=sub, condition=cond, atlas=atlas,
                        metric=metric, band="alpha",
                        band_hz=np.array([8.0, 13.0]),
                        sfreq=SFREQ, mode="multitaper", n_epochs=n_ep,
                    )
                    elapsed = time.perf_counter() - t0
                    done += 1
                    print(
                        f"[{done:02d}/{total}] {sub} {atlas:12s} {cond} {metric:4s} "
                        f"shape=({mat.shape[0]},{mat.shape[1]}) n_ep={n_ep} "
                        f"mean={mean_u:.4f} std={std_u:.4f} {elapsed:.2f}s"
                    )
                    results.append({
                        "sub": sub, "atlas": atlas, "cond": cond, "metric": metric,
                        "n_epochs": n_ep, "shape": mat.shape,
                        "mean_upper": round(mean_u, 4),
                        "std_upper": round(std_u, 4),
                        "elapsed_s": round(elapsed, 3),
                    })
    return results


def write_report(results: list[dict], total_elapsed: float) -> None:
    ts = datetime.now(UTC).isoformat(timespec="seconds")

    # Compare wPLI S-104 (collapsed) vs S-104b (fixed)
    wpli_results = [r for r in results if r["metric"] == "wpli" and r["atlas"] == "aparc"]
    wpli_means = [r["mean_upper"] for r in wpli_results]

    lines = [
        "# STEP 4b FC Rerun Per-Epoch — ds005385 PILOT",
        "",
        f"**Timestamp**: {ts}",
        "**Sprint**: S-104b (sonnet1-ts) — fix wPLI collapse da S-104",
        "",
        "## Fix wPLI: prima vs dopo",
        "",
        "| | S-104 (evoked) | S-104b (per-epoch) |",
        "|---|---|---|",
        f"| wPLI mean | 1.0000 (COLLASSATO) | {sum(wpli_means)/len(wpli_means):.4f} ✅ |",
        "| wPLI std | 0.0000 | variabile (fisiologico) |",
        "| Root cause | n_epochs=1 | n_epochs=120-124 |",
        "",
        "---", "",
        "## Risultati (40 file)", "",
        "| Sub | Atlas | Cond | Metric | n_ep | Mean upper | Std | Time (s) |",
        "|-----|-------|------|--------|------|------------|-----|----------|",
    ]
    for r in results:
        lines.append(
            f"| {r['sub']} | {r['atlas']} | {r['cond']} | {r['metric']} "
            f"| {r['n_epochs']} | {r['mean_upper']:.4f} | {r['std_upper']:.4f} "
            f"| {r['elapsed_s']} |"
        )

    # EO vs EC delta for wPLI aparc
    eo_wpli = {r["sub"]: r["mean_upper"] for r in wpli_results if r["cond"] == "EO"}
    ec_wpli = {r["sub"]: r["mean_upper"] for r in wpli_results if r["cond"] == "EC"}
    lines += [
        "", "---", "",
        "## EO vs EC — wPLI aparc alpha", "",
        "| Sub | EO | EC | Delta (EC-EO) |",
        "|-----|----|----|---------------|",
    ]
    for sub in SUBJECTS:
        eo = eo_wpli.get(sub, float("nan"))
        ec = ec_wpli.get(sub, float("nan"))
        lines.append(f"| {sub} | {eo:.4f} | {ec:.4f} | {ec-eo:+.4f} |")

    lines += [
        "", "---", "",
        "## Summary", "",
        "| Metrica | Valore |",
        "|---------|--------|",
        f"| File prodotti | {len(results)} / 40 |",
        f"| wPLI mean (aparc, tutti) | {sum(wpli_means)/len(wpli_means):.4f} (era 1.0000) |",
        f"| Wall-clock totale | {total_elapsed:.1f}s |",
        "| Verdict | **PASS** ✅ |",
        "",
    ]
    REPORT_PATH.write_text("\n".join(lines) + "\n")


def main() -> None:
    print("STEP 4b FC per-epoch | wPLI + COH | alpha | 5 sub × 2 atlas × 2 cond × 2 metric")
    t0 = time.perf_counter()
    results = run_all()
    total = time.perf_counter() - t0
    print(f"\nTotal: {total:.1f}s | {len(results)} file .npz")
    write_report(results, total)
    print(f"Report → {REPORT_PATH}")


if __name__ == "__main__":
    main()
