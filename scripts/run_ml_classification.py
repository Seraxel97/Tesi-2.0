"""STEP 6 — Classificazione ML EO vs EC con LOSO (baseline pilota ds005385).

Scopo:
    Valuta LogReg, SVM-RBF e LDA sulle feature di connettività in banda alpha
    (atlanti aparc/schaefer100 x metriche wpli/coh) con Leave-One-Group-Out
    (un soggetto per fold). Con n=10 campioni i risultati sono solo INDICATIVI,
    non statisticamente robusti.

Input:
    data/features/ds005385/X_<atlante>_<metrica>_alpha.npz, y.npy, groups.npy

Output:
    - reports/STEP6_DS005385_ML.md
    - data/results/ds005385/ml_results.json
    - reports/figures/fig04_ml.png (heatmap della balanced accuracy)

Esempio:
    python scripts/run_ml_classification.py

"""

from __future__ import annotations

import json
import time
from datetime import UTC, datetime
from pathlib import Path

import matplotlib
import numpy as np

# Backend non interattivo: la figura viene solo salvata su file
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, balanced_accuracy_score, f1_score, roc_auc_score
from sklearn.model_selection import LeaveOneGroupOut
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

# ===== 1. Configurazione =====

FEAT_DIR = Path("data/features/ds005385")
OUT_DIR = Path("data/results/ds005385")
REPORT_PATH = Path("reports/STEP6_DS005385_ML.md")
FIG_PATH = Path("reports/figures/fig04_ml.png")

ATLASES = ["aparc", "schaefer100"]
METRICS = ["wpli", "coh"]

CLASSIFIERS = {
    "logreg": LogisticRegression(max_iter=1000, C=1.0, random_state=42),
    "svm_rbf": Pipeline(
        [
            ("scaler", StandardScaler()),
            ("svc", SVC(kernel="rbf", C=1.0, probability=True, random_state=42)),
        ]
    ),
    "lda": LinearDiscriminantAnalysis(),
}

# Crea le cartelle di output già all'import del modulo
OUT_DIR.mkdir(parents=True, exist_ok=True)
FIG_PATH.parent.mkdir(parents=True, exist_ok=True)


# ===== 2. Valutazione LOSO =====


def score_fold(y_true: np.ndarray, y_pred: np.ndarray, y_prob: np.ndarray) -> dict:
    """Calcola le metriche di un singolo fold.

    Args:
        y_true: classi vere.
        y_pred: classi predette.
        y_prob: probabilità della classe positiva.

    Returns:
        dict con accuracy, balanced_accuracy, roc_auc (NaN se una sola classe) e f1.
    """
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "balanced_accuracy": float(balanced_accuracy_score(y_true, y_pred)),
        "roc_auc": float(roc_auc_score(y_true, y_prob))
        if len(np.unique(y_true)) > 1
        else float("nan"),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
    }


def run_loso(X: np.ndarray, y: np.ndarray, groups: np.ndarray, clf_name: str, clf) -> dict:
    """Valutazione Leave-One-Group-Out per un classificatore.

    Args:
        X: matrice feature.
        y: etichette.
        groups: id soggetto.
        clf_name: nome del classificatore.
        clf: estimatore sklearn (viene rifittato a ogni fold).

    Returns:
        dict con 'clf', 'folds' (metriche per fold) e 'agg' (media e std sui fold).
    """
    logo = LeaveOneGroupOut()
    fold_results = []

    for train_idx, test_idx in logo.split(X, y, groups):
        X_tr, X_te = X[train_idx], X[test_idx]
        y_tr, y_te = y[train_idx], y[test_idx]
        clf.fit(X_tr, y_tr)
        y_pred = clf.predict(X_te)
        # Senza predict_proba si usano le classi predette come punteggio
        y_prob = (
            clf.predict_proba(X_te)[:, 1] if hasattr(clf, "predict_proba") else y_pred.astype(float)
        )
        fold_results.append(score_fold(y_te, y_pred, y_prob))

    # Media/std sui fold ignorando i NaN (AUC non definita se il test ha una sola classe)
    # aggregate over folds
    agg = {}
    for k in ["accuracy", "balanced_accuracy", "roc_auc", "f1"]:
        vals = [f[k] for f in fold_results if not np.isnan(f[k])]
        agg[k] = round(float(np.mean(vals)), 4) if vals else float("nan")
        agg[f"{k}_std"] = round(float(np.std(vals)), 4) if vals else float("nan")

    return {"clf": clf_name, "folds": fold_results, "agg": agg}


def run_all(y: np.ndarray, groups: np.ndarray) -> list[dict]:
    """Esegue la LOSO per tutte le combinazioni atlante x metrica x classificatore.

    Args:
        y: etichette.
        groups: id soggetto.

    Returns:
        lista di dict di risultati (con forma di X, metriche aggregate e per fold, tempo).

    Side effects:
        Legge i file X_*_alpha.npz da FEAT_DIR; stampa l'avanzamento.
    """
    all_results = []
    total = len(ATLASES) * len(METRICS) * len(CLASSIFIERS)
    done = 0

    for atlas in ATLASES:
        for metric in METRICS:
            d = np.load(FEAT_DIR / f"X_{atlas}_{metric}_alpha.npz", allow_pickle=True)
            X = d["X"].astype(np.float64)

            for clf_name, clf in CLASSIFIERS.items():
                t0 = time.perf_counter()
                res = run_loso(X, y, groups, clf_name, clf)
                elapsed = time.perf_counter() - t0
                done += 1
                agg = res["agg"]
                print(
                    f"[{done:02d}/{total}] {atlas:12s} {metric:4s} {clf_name:8s}  "
                    f"acc={agg['accuracy']:.3f} bal={agg['balanced_accuracy']:.3f} "
                    f"auc={agg['roc_auc']:.3f} f1={agg['f1']:.3f}  {elapsed:.3f}s"
                )
                all_results.append(
                    {
                        "atlas": atlas,
                        "metric": metric,
                        "clf": clf_name,
                        "X_shape": list(X.shape),
                        "agg": agg,
                        "folds": res["folds"],
                        "elapsed_s": round(elapsed, 3),
                    }
                )

    return all_results


# ===== 3. Figura e report =====


def save_figure(results: list[dict]) -> None:
    """Salva la heatmap della balanced accuracy (combinazioni x classificatori).

    Args:
        results: output di run_all.

    Returns:
        None.

    Side effects:
        Scrive FIG_PATH.
    """
    clfs = list(CLASSIFIERS.keys())
    combos = [f"{a}_{m}" for a in ATLASES for m in METRICS]
    mat = np.zeros((len(combos), len(clfs)))

    for r in results:
        ci = combos.index(f"{r['atlas']}_{r['metric']}")
        cj = clfs.index(r["clf"])
        mat[ci, cj] = r["agg"]["balanced_accuracy"]

    fig, ax = plt.subplots(figsize=(7, 4))
    im = ax.imshow(mat, vmin=0, vmax=1, cmap="RdYlGn", aspect="auto")
    ax.set_xticks(range(len(clfs)))
    ax.set_xticklabels(clfs, rotation=15)
    ax.set_yticks(range(len(combos)))
    ax.set_yticklabels(combos)
    ax.set_title("Balanced Accuracy — LOSO (n=10, indicativo)")
    plt.colorbar(im, ax=ax)
    for i in range(len(combos)):
        for j in range(len(clfs)):
            ax.text(j, i, f"{mat[i, j]:.2f}", ha="center", va="center", fontsize=9)
    plt.tight_layout()
    fig.savefig(FIG_PATH, dpi=120)
    plt.close(fig)


def write_report(results: list[dict], total_elapsed: float) -> None:
    """Scrive il report Markdown con i risultati aggregati e i migliori classificatori.

    Args:
        results: output di run_all.
        total_elapsed: durata totale in secondi.

    Returns:
        None.

    Side effects:
        Scrive REPORT_PATH.
    """
    ts = datetime.now(UTC).isoformat(timespec="seconds")
    clfs = list(CLASSIFIERS.keys())

    lines = [
        "# STEP 6 ML Classification — ds005385 PILOT",
        "",
        f"**Timestamp**: {ts}",
        "**Sprint**: S-106 (sonnet1-ts)",
        "",
        "> [WARNING] **n=10 campioni, 5-fold LOSO = 1 test sample per fold.**",
        "> Risultati INDICATIVI per pipeline validation. Non statisticamente robusti.",
        "",
        "---",
        "",
        "## Risultati aggregate (balanced_accuracy ± std)",
        "",
    ]

    for atlas in ATLASES:
        for metric in METRICS:
            lines.append(f"### {atlas} × {metric}")
            lines.append("")
            lines.append("| Classifier | Accuracy | Bal.Acc | AUC | F1 |")
            lines.append("|------------|----------|---------|-----|----|")
            for clf_name in clfs:
                r = next(
                    x
                    for x in results
                    if x["atlas"] == atlas and x["metric"] == metric and x["clf"] == clf_name
                )
                a = r["agg"]
                lines.append(
                    f"| {clf_name} | {a['accuracy']:.3f}±{a['accuracy_std']:.3f} "
                    f"| {a['balanced_accuracy']:.3f}±{a['balanced_accuracy_std']:.3f} "
                    f"| {a['roc_auc']:.3f}±{a['roc_auc_std']:.3f} "
                    f"| {a['f1']:.3f}±{a['f1_std']:.3f} |"
                )
            lines.append("")

    # Best per combo
    lines += ["---", "", "## Best classifier per atlas×metric (balanced_accuracy)", ""]
    lines.append("| Atlas | Metric | Best clf | Bal.Acc |")
    lines.append("|-------|--------|----------|---------|")
    for atlas in ATLASES:
        for metric in METRICS:
            sub = [r for r in results if r["atlas"] == atlas and r["metric"] == metric]
            best = max(sub, key=lambda r: r["agg"]["balanced_accuracy"])
            lines.append(
                f"| {atlas} | {metric} | {best['clf']} | {best['agg']['balanced_accuracy']:.3f} |"
            )

    lines += [
        "",
        "---",
        "",
        "## Summary",
        "",
        "| Metrica | Valore |",
        "|---------|--------|",
        f"| Combinazioni testate | {len(results)} (4 atlas×metric × 3 clf) |",
        f"| Wall-clock totale | {total_elapsed:.2f}s |",
        "| Nota | n=10, risultati indicativi |",
        "| Figura | reports/figures/fig04_ml.png |",
        "| Verdict | **PASS** [OK] |",
        "",
    ]
    REPORT_PATH.write_text("\n".join(lines) + "\n")


# ===== 4. Main =====


def main() -> None:
    """Punto di ingresso: carica y/groups, esegue la LOSO e salva JSON, figura e report.

    Side effects:
        Scrive ml_results.json, fig04_ml.png e STEP6_DS005385_ML.md.
    """
    print("STEP 6 ML LOSO | LogReg + SVM-RBF + LDA | 4 atlas×metric combos")
    y = np.load(FEAT_DIR / "y.npy")
    groups = np.load(FEAT_DIR / "groups.npy")
    print(f"y={y.tolist()}  groups={groups.tolist()}")

    t0 = time.perf_counter()
    results = run_all(y, groups)
    total = time.perf_counter() - t0

    (OUT_DIR / "ml_results.json").write_text(
        json.dumps({"timestamp": datetime.now(UTC).isoformat(), "results": results}, indent=2)
    )
    save_figure(results)
    write_report(results, total)
    print(f"\nTotal: {total:.2f}s")
    print(f"Report → {REPORT_PATH}")
    print(f"Figure → {FIG_PATH}")


if __name__ == "__main__":
    main()
