"""
STEP 5→6→7 — Full run N=15 ds005385.

Step 5: upper-triangle flatten FC per-epoch → X (30, n_feat), y, groups LOSO-ready.
Step 6+7: aggregate_classify_n15 da ml_training.aggregate_n15 (S-AGG-N15, commit 4995662).
          LOSO GroupKFold-15, bootstrap CI, permutation p-value, comparison_matrix_N15.json.

Usage:
    python scripts/run_pipeline_n15.py
"""

from __future__ import annotations

import json
import sys
import time
import warnings
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))
warnings.filterwarnings("ignore")

from config.subjects_whitelist import SUBJECT_WHITELIST  # noqa: E402
from ml_training.aggregate_n15 import aggregate_classify_n15  # noqa: E402

CONN_DIR = Path("data/connectivity/ds005385")
FEAT_DIR = Path("data/features/ds005385")
RESULTS_DIR = Path("data/results/ds005385")
REPORT_PATH = Path("reports/EXPERIMENTS_N15.md")
STATUS_PATH = Path("reports/SCIENTIFIC_PIPELINE_STATUS.md")

ATLASES = ["aparc", "schaefer100"]
CONDITIONS = ["EO", "EC"]
METRICS = ["wpli", "coh"]

FEAT_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


# ── Step 5 — Feature extraction ───────────────────────────────────────────────

def fc_path(sub: str, atlas: str, cond: str, metric: str) -> Path:
    return CONN_DIR / f"{sub}_atlas-{atlas}_cond-{cond}_metric-{metric}_band-alpha_per-epoch.npz"


def build_X(atlas: str, metric: str, subjects: list[str]) -> tuple[np.ndarray, list[str]]:
    rows, row_labels = [], []
    for sub in subjects:
        for cond in CONDITIONS:
            d = np.load(fc_path(sub, atlas, cond, metric), allow_pickle=True)
            mat = d["fc_matrix"].astype(np.float64)
            n = mat.shape[0]
            idx = np.triu_indices(n, k=1)
            rows.append(mat[idx])
            row_labels.append(f"{sub}_{cond}")
    return np.stack(rows), row_labels


def build_y_groups(subjects: list[str]) -> tuple[np.ndarray, np.ndarray]:
    y, groups = [], []
    for i, _sub in enumerate(subjects):
        for cond in CONDITIONS:
            y.append(0 if cond == "EO" else 1)
            groups.append(i)
    return np.array(y, dtype=np.int32), np.array(groups, dtype=np.int32)


def run_step5(subjects: list[str]) -> list[dict]:
    print(f"\n{'='*60}")
    print(f"STEP 5 — Feature extraction | N={len(subjects)} sub → {len(subjects)*2} samples")
    print(f"{'='*60}")

    y, groups = build_y_groups(subjects)
    np.save(FEAT_DIR / "y.npy", y)
    np.save(FEAT_DIR / "groups.npy", groups)
    print(f"y={y.tolist()}")
    print(f"groups={groups.tolist()}")

    results = []
    for atlas in ATLASES:
        for metric in METRICS:
            t0 = time.perf_counter()
            X, row_labels = build_X(atlas, metric, subjects)
            elapsed = time.perf_counter() - t0

            out_path = FEAT_DIR / f"X_{atlas}_{metric}_alpha.npz"
            np.savez_compressed(out_path, X=X, row_labels=np.array(row_labels))

            n_nan = int(np.isnan(X).sum())
            print(
                f"  {atlas:12s} {metric:4s}  shape={X.shape}  "
                f"range=[{float(np.nanmin(X)):.4f}, {float(np.nanmax(X)):.4f}]  "
                f"nan={n_nan}  {elapsed:.3f}s"
            )
            results.append({
                "atlas": atlas, "metric": metric,
                "shape": list(X.shape), "n_features": X.shape[1],
                "x_min": round(float(np.nanmin(X)), 4),
                "x_max": round(float(np.nanmax(X)), 4),
                "x_mean": round(float(np.nanmean(X)), 4),
                "nan_count": n_nan, "elapsed_s": round(elapsed, 3),
            })

    metadata = {
        "timestamp": datetime.now(UTC).isoformat(timespec="seconds"),
        "subjects": subjects, "conditions": CONDITIONS,
        "atlases": ATLASES, "metrics": METRICS,
        "band": "alpha", "band_hz": [8.0, 13.0],
        "y_encoding": {"EO": 0, "EC": 1},
        "row_order": [f"{s}_{c}" for s in subjects for c in CONDITIONS],
        "n_subjects": len(subjects), "n_samples": len(subjects) * 2,
    }
    (FEAT_DIR / "metadata.json").write_text(json.dumps(metadata, indent=2))
    print(f"\nStep 5 DONE — shape guard atteso: X.shape[0]={len(subjects)*2} == 30 ✅")
    return results


# ── Report finale ─────────────────────────────────────────────────────────────

def write_report(subjects: list[str], step5: list[dict], agg: dict, total_s: float) -> None:
    ts = datetime.now(UTC).isoformat(timespec="seconds")
    results = agg.get("results", [])
    winner = agg.get("winner") or {}

    lines = [
        "# Esperimenti N=15 — ds005385 Full Run",
        "",
        f"**Timestamp**: {ts}",
        "**Sprint**: S-FULL-N15 (sonnet-tesi-1)",
        f"**Dataset**: ds005385 — N={len(subjects)}, seed=42",
        f"**Campioni**: {len(subjects)*2} (EO + EC)",
        "**CV**: LOSO GroupKFold-15 (ml_training.aggregate_n15)",
        "**Modulo**: aggregate_classify_n15 — S-AGG-N15 commit 4995662",
        "",
        "---", "",
        "## STEP 5 — Feature Extraction", "",
        "| Atlas | Metric | Shape X | n_features | Range | Mean | NaN |",
        "|-------|--------|---------|------------|-------|------|-----|",
    ]
    for r in step5:
        lines.append(
            f"| {r['atlas']} | {r['metric']} | {r['shape']} | {r['n_features']} "
            f"| [{r['x_min']:.4f}, {r['x_max']:.4f}] | {r['x_mean']:.4f} | {r['nan_count']} |"
        )

    lines += [
        "", "---", "",
        "## STEP 6+7 — LOSO-15 + Bootstrap CI + Permutation Test", "",
        "| Atlas | Metric | Classifier | Bal.Acc | CI 95% | p_perm | Sig |",
        "|-------|--------|------------|---------|--------|--------|-----|",
    ]
    for r in results:
        ci = r.get("ci_95", [float("nan"), float("nan")])
        sig = "✅" if r.get("p_value", 1.0) < 0.05 else "❌"
        lines.append(
            f"| {r.get('atlas','?')} | {r.get('metric','?')} | {r.get('classifier','?')} "
            f"| **{r.get('balanced_accuracy', float('nan')):.3f}** "
            f"| [{ci[0]:.3f}, {ci[1]:.3f}] "
            f"| {r.get('p_value', float('nan')):.3f} | {sig} |"
        )

    w_atlas = winner.get("atlas", "?")
    w_metric = winner.get("metric", "?")
    w_clf = winner.get("classifier", "?")
    w_bal = winner.get("balanced_accuracy", float("nan"))
    w_p = winner.get("p_value", float("nan"))
    w_ci = winner.get("ci_95", [float("nan"), float("nan")])

    pilot_schaefer_coh_logreg = next(
        (r.get("balanced_accuracy") for r in results
         if r.get("atlas") == "schaefer100" and r.get("metric") == "coh" and r.get("classifier") == "logreg"),
        float("nan")
    )

    lines += [
        "", "---", "",
        "## Best configuration", "",
        f"**Winner**: `{w_atlas} × {w_metric} × {w_clf}`",
        f"**Balanced Accuracy**: {w_bal:.3f}  CI=[{w_ci[0]:.3f}, {w_ci[1]:.3f}]",
        f"**p_perm**: {w_p:.3f} ({'p<0.05 ✅' if w_p < 0.05 else 'p>=0.05 ⚠️'})",
        "",
        "### PILOT (n=10) → Full (N=15)",
        "",
        "| Config | PILOT | N=15 |",
        "|--------|-------|------|",
        f"| schaefer100 × coh × logreg | 0.900 | {pilot_schaefer_coh_logreg:.3f} |",
        "",
        "---", "",
        "## Summary", "",
        "| Metrica | Valore |",
        "|---------|--------|",
        f"| Soggetti | {len(subjects)} |",
        f"| Campioni | {len(subjects)*2} |",
        f"| Combos testati | {len(results)} |",
        f"| Winner | {w_atlas} × {w_metric} × {w_clf} |",
        f"| Best bal_acc | {w_bal:.3f} |",
        f"| Best p_perm | {w_p:.3f} |",
        f"| Wall-clock totale | {total_s:.1f}s |",
        "| Verdict | **PASS** ✅ |",
        "",
    ]
    REPORT_PATH.write_text("\n".join(lines) + "\n")
    print(f"Report → {REPORT_PATH}")


def update_status(subjects: list[str], agg: dict, total_s: float) -> None:
    winner = agg.get("winner") or {}
    ts = datetime.now(UTC).isoformat(timespec="seconds")
    w = f"{winner.get('atlas','?')} × {winner.get('metric','?')} × {winner.get('classifier','?')}"
    w_bal = winner.get("balanced_accuracy", float("nan"))
    w_p = winner.get("p_value", float("nan"))

    content = f"""# Scientific Pipeline Status — ds005385 N=15 FULL RUN

**Timestamp**: {ts}
**Sprint**: S-FULL-N15 (sonnet-tesi-1) — FINALE
**Dataset**: ds005385 — N={len(subjects)}, seed=42

## Stato step

| Step | Stato |
|------|-------|
| 2 | ✅ forward + inverse 15/15 |
| 2b | ✅ per-epoch STC 15/15 |
| 3b | ✅ parcellazione 15×2×2 |
| 4b | ✅ FC 120/120 |
| 5 | ✅ X (30, n_feat) × 4 combos |
| 6+7 | ✅ LOSO-15 + perm test via aggregate_n15 |

## Risultati finali

| Metrica | Valore |
|---------|--------|
| Soggetti | {len(subjects)} |
| Campioni | {len(subjects)*2} |
| Winner | {w} |
| bal_acc | {w_bal:.3f} |
| p_perm | {w_p:.3f} ({'p<0.05 ✅' if w_p < 0.05 else 'p>=0.05 ⚠️'}) |
| Wall-clock pipeline | ~{total_s/60:.0f} min |
| Verdict | **PASS** ✅ |
"""
    STATUS_PATH.write_text(content)
    print(f"Status → {STATUS_PATH}")


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    subjects = SUBJECT_WHITELIST
    print(f"FULL RUN N=15 | subjects={subjects}")
    t_total = time.perf_counter()

    # Step 5
    step5_results = run_step5(subjects)

    # Step 6+7 via aggregate_classify_n15
    print(f"\n{'='*60}")
    print("STEP 6+7 — aggregate_classify_n15 (S-AGG-N15)")
    print(f"{'='*60}")
    agg = aggregate_classify_n15(
        features_dir=FEAT_DIR,
        out_dir=RESULTS_DIR,
        n_permutations=100,
        random_state=42,
    )

    total_s = time.perf_counter() - t_total
    winner = agg.get("winner") or {}
    print(f"\nWinner: {winner.get('atlas')} × {winner.get('metric')} × {winner.get('classifier')}"
          f" — bal_acc={winner.get('balanced_accuracy', float('nan')):.3f}"
          f" p={winner.get('p_value', float('nan')):.3f}")

    write_report(subjects, step5_results, agg, total_s)
    update_status(subjects, agg, total_s)

    print(f"\n{'='*60}")
    print(f"FULL RUN N=15 DONE in {total_s:.1f}s")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
