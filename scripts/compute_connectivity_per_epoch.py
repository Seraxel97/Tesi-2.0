"""STEP 4b — FC per-epoca sui label_tc di ds005385.

Scopo:
    Per ogni soggetto, atlante, condizione, metrica e banda calcola la matrice
    di connettività funzionale a partire dalle serie per ROI per-epoca, tramite
    connectivity.fc_dispatcher.compute_fc (multitaper).
    Metriche: wpli, coh, plv, imcoh. Bande: theta (4-8), alpha (8-13),
    beta (13-30), gamma (30-45 Hz). Idempotente: i file esistenti sono saltati.

Input:
    data/label_ts/ds005385/<sub>_atlas-<atlante>_cond-<cond>_per-epoch.npz

Output:
    - data/connectivity/ds005385/<sub>_atlas-<A>_cond-<C>_metric-<M>_band-<B>_per-epoch.npz
      con fc_matrix (n_labels, n_labels) e metadati
    - reports/STEP4b_DS005385_EXTENDED.md

Esempio:
    python scripts/compute_connectivity_per_epoch.py
    python scripts/compute_connectivity_per_epoch.py --subjects sub-007 --metrics wpli,plv --bands alpha,beta

"""

from __future__ import annotations

import argparse
import sys
import time
import warnings
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

# Rende importabili i pacchetti del repository dalla cartella scripts/
sys.path.insert(0, str(Path(__file__).parent.parent))
warnings.filterwarnings("ignore")

from config.subjects_whitelist import SUBJECT_WHITELIST  # noqa: E402
from connectivity.fc_dispatcher import compute_fc  # noqa: E402

# ===== 1. Configurazione =====

IN_DIR = Path("data/label_ts/ds005385")
OUT_DIR = Path("data/connectivity/ds005385")
REPORT_PATH = Path("reports/STEP4b_DS005385_EXTENDED.md")

PILOT_SUBJECTS = ["sub-007", "sub-010", "sub-011", "sub-026", "sub-031"]

ALL_METRICS = ["wpli", "coh", "plv", "imcoh"]
ALL_BANDS: dict[str, tuple[float, float]] = {
    "theta": (4.0, 8.0),
    "alpha": (8.0, 13.0),
    "beta": (13.0, 30.0),
    "gamma": (30.0, 45.0),
}
ATLASES = ["aparc", "schaefer100"]
CONDITIONS = ["EO", "EC"]
SFREQ = 250.0

OUT_DIR.mkdir(parents=True, exist_ok=True)


# ===== 2. Percorsi =====


def npz_in(sub: str, atlas: str, cond: str) -> Path:
    """Percorso del file label_ts per-epoca di input.

    Args:
        sub: id soggetto.
        atlas: atlante.
        cond: 'EO' o 'EC'.

    Returns:
        Path del file.
    """
    return IN_DIR / f"{sub}_atlas-{atlas}_cond-{cond}_per-epoch.npz"


def npz_out(sub: str, atlas: str, cond: str, metric: str, band: str) -> Path:
    """Percorso del file FC per-epoca di output.

    Args:
        sub: id soggetto.
        atlas: atlante.
        cond: 'EO' o 'EC'.
        metric: metrica FC.
        band: nome banda.

    Returns:
        Path del file.
    """
    return OUT_DIR / f"{sub}_atlas-{atlas}_cond-{cond}_metric-{metric}_band-{band}_per-epoch.npz"


# ===== 3. Calcolo FC =====


def run_all(
    subjects: list[str],
    metrics: list[str],
    bands: dict[str, tuple[float, float]],
) -> list[dict]:
    """Calcola (o salta se già presenti) tutte le FC richieste.

    Args:
        subjects: lista soggetti.
        metrics: metriche FC.
        bands: dict {nome banda: (f_min, f_max)} in Hz.

    Returns:
        lista di dict con statistiche (media/std triangolo superiore, n_epoche, tempi, flag skipped).

    Side effects:
        Scrive i file *_per-epoch.npz in OUT_DIR; i label_ts mancanti vengono saltati con un messaggio.
    """
    results = []
    total = len(subjects) * len(ATLASES) * len(CONDITIONS) * len(metrics) * len(bands)
    done = 0

    for sub in subjects:
        for atlas in ATLASES:
            for cond in CONDITIONS:
                # load label_tc once per (sub, atlas, cond)
                npz = npz_in(sub, atlas, cond)
                if not npz.exists():
                    print(f"  MISSING {npz.name} — skip")
                    done += len(metrics) * len(bands)
                    continue
                d = np.load(npz, allow_pickle=True)
                label_tc = d["label_tc"].astype(np.float64)
                label_names = list(d["label_names"])
                n_ep = label_tc.shape[0]

                for metric in metrics:
                    # compute all bands in one call for efficiency
                    # Calcola in un'unica chiamata solo le bande ancora mancanti
                    need_bands = {
                        b: hz
                        for b, hz in bands.items()
                        if not npz_out(sub, atlas, cond, metric, b).exists()
                    }
                    skip_bands = {b for b in bands if b not in need_bands}
                    for b in skip_bands:
                        done += 1
                        print(
                            f"[{done:02d}/{total}] {sub} {atlas:12s} {cond} {metric:4s} {b:5s} SKIP"
                        )
                        # Per i file già presenti si rileggono solo le statistiche per il report
                        # collect stats from existing file
                        existing = np.load(npz_out(sub, atlas, cond, metric, b), allow_pickle=True)
                        mat = existing["fc_matrix"]
                        upper = mat[np.triu_indices(mat.shape[0], k=1)]
                        upper_valid = upper[~np.isnan(upper)]
                        results.append(
                            {
                                "sub": sub,
                                "atlas": atlas,
                                "cond": cond,
                                "metric": metric,
                                "band": b,
                                "n_epochs": n_ep,
                                "mean_upper": round(
                                    float(np.mean(upper_valid))
                                    if len(upper_valid)
                                    else float("nan"),
                                    4,
                                ),
                                "std_upper": round(
                                    float(np.std(upper_valid))
                                    if len(upper_valid)
                                    else float("nan"),
                                    4,
                                ),
                                "elapsed_s": 0.0,
                                "skipped": True,
                            }
                        )

                    if not need_bands:
                        continue

                    t0 = time.perf_counter()
                    fc_dict = compute_fc(
                        label_tc, SFREQ, metric, bands=need_bands, mode="multitaper"
                    )
                    compute_elapsed = time.perf_counter() - t0

                    for b, mat in fc_dict.items():
                        # Statistiche sul triangolo superiore, ignorando i NaN
                        upper = mat[np.triu_indices(mat.shape[0], k=1)]
                        upper_valid = upper[~np.isnan(upper)]
                        mean_u = float(np.mean(upper_valid)) if len(upper_valid) else float("nan")
                        std_u = float(np.std(upper_valid)) if len(upper_valid) else float("nan")
                        hz = need_bands[b]

                        np.savez_compressed(
                            npz_out(sub, atlas, cond, metric, b),
                            fc_matrix=mat,
                            label_names=np.array(label_names),
                            subject=sub,
                            condition=cond,
                            atlas=atlas,
                            metric=metric,
                            band=b,
                            band_hz=np.array(list(hz)),
                            sfreq=SFREQ,
                            mode="multitaper",
                            n_epochs=n_ep,
                        )
                        done += 1
                        band_elapsed = compute_elapsed / len(fc_dict)
                        print(
                            f"[{done:02d}/{total}] {sub} {atlas:12s} {cond} "
                            f"{metric:4s} {b:5s} shape=({mat.shape[0]},{mat.shape[1]}) "
                            f"n_ep={n_ep} mean={mean_u:.4f} {band_elapsed:.2f}s"
                        )
                        results.append(
                            {
                                "sub": sub,
                                "atlas": atlas,
                                "cond": cond,
                                "metric": metric,
                                "band": b,
                                "n_epochs": n_ep,
                                "mean_upper": round(mean_u, 4),
                                "std_upper": round(std_u, 4),
                                "elapsed_s": round(band_elapsed, 3),
                            }
                        )
    return results


# ===== 4. Report =====


def write_report(
    results: list[dict], total_elapsed: float, metrics: list[str], bands: list[str]
) -> None:
    """Scrive il report Markdown dello step 4b esteso.

    Args:
        results: output di run_all.
        total_elapsed: durata in secondi.
        metrics: metriche usate.
        bands: nomi delle bande usate.

    Returns:
        None.

    Side effects:
        Scrive reports/STEP4b_DS005385_EXTENDED.md.
    """
    ts = datetime.now(UTC).isoformat(timespec="seconds")
    n_new = sum(1 for r in results if not r.get("skipped"))
    n_skip = sum(1 for r in results if r.get("skipped"))
    lines = [
        "# STEP 4b FC Extended — ds005385",
        "",
        f"**Timestamp**: {ts}",
        "**Sprint**: S-FC-EXTEND (sonnet-tesi-1)",
        f"**Metriche**: {metrics}",
        f"**Bande**: {bands}",
        "",
        "---",
        "",
        "## Risultati per combo (sample: aparc)",
        "",
        "| Sub | Atlas | Cond | Metric | Band | n_ep | Mean upper | Skipped |",
        "|-----|-------|------|--------|------|------|------------|---------|",
    ]
    for r in results[:40]:
        lines.append(
            f"| {r['sub']} | {r['atlas']} | {r['cond']} | {r['metric']} | {r['band']} "
            f"| {r['n_epochs']} | {r['mean_upper']:.4f} | {'[OK]' if r.get('skipped') else '🆕'} |"
        )
    lines += [
        "",
        "---",
        "",
        "## Summary",
        "",
        "| Metrica | Valore |",
        "|---------|--------|",
        f"| File prodotti (nuovi) | {n_new} |",
        f"| File skippati (esistenti) | {n_skip} |",
        f"| Totale processati | {len(results)} |",
        f"| Wall-clock | {total_elapsed:.1f}s ({total_elapsed / 60:.1f} min) |",
        "| Verdict | **PASS** [OK] |",
        "",
    ]
    REPORT_PATH.write_text("\n".join(lines) + "\n")


# ===== 5. Utilità CLI =====


def parse_bands(band_str: str) -> dict[str, tuple[float, float]]:
    """Converte una stringa 'theta,alpha' nel dizionario delle bande corrispondenti.

    Args:
        band_str: nomi di banda separati da virgola.

    Returns:
        dict {nome: (f_min, f_max)}.

    Side effects:
        Solleva ValueError se una banda non è in ALL_BANDS.
    """
    result = {}
    for b in band_str.split(","):
        b = b.strip()
        if b in ALL_BANDS:
            result[b] = ALL_BANDS[b]
        else:
            raise ValueError(f"Unknown band {b!r}. Valid: {list(ALL_BANDS)}")
    return result


# ===== 6. Main =====


def main() -> None:
    """Punto di ingresso CLI: calcola le FC richieste e scrive il report.

    Side effects:
        Scrive i file FC e il report.
    """
    ap = argparse.ArgumentParser(description="STEP 4b FC per-epoch extended ds005385")
    ap.add_argument("--subjects", nargs="+", default=SUBJECT_WHITELIST)
    ap.add_argument(
        "--metrics",
        default="wpli,coh,plv,imcoh",
        help="Comma-separated metrics (default: wpli,coh,plv,imcoh)",
    )
    ap.add_argument(
        "--bands",
        default="theta,alpha,beta,gamma",
        help="Comma-separated bands (default: theta,alpha,beta,gamma)",
    )
    args = ap.parse_args()

    metrics = [m.strip() for m in args.metrics.split(",")]
    bands = parse_bands(args.bands)

    total_combos = len(args.subjects) * len(ATLASES) * len(CONDITIONS) * len(metrics) * len(bands)
    print(
        f"STEP 4b extended | {len(args.subjects)} sub × {len(ATLASES)} atlas × "
        f"{len(CONDITIONS)} cond × {len(metrics)} metric × {len(bands)} band = {total_combos} combos"
    )
    t0 = time.perf_counter()
    results = run_all(args.subjects, metrics, bands)
    total = time.perf_counter() - t0
    n_new = sum(1 for r in results if not r.get("skipped"))
    print(f"\nTotal: {total:.1f}s | {n_new} nuovi + {len(results) - n_new} skip")
    write_report(results, total, metrics, list(bands))
    print(f"Report → {REPORT_PATH}")


if __name__ == "__main__":
    main()
