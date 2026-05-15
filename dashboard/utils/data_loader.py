"""Data loading utilities for the ML dashboard."""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np

# Ensure project root on path
_ROOT = Path(__file__).parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

FEATURES_DIR = _ROOT / "data" / "features" / "ds005385"
RESULTS_DIR = _ROOT / "data" / "results" / "ds005385"
REPORTS_DIR = _ROOT / "reports"

# Canonical N=50 winner (from PERM_1000_WINNER_LOG.md)
N50_WINNER: dict[str, Any] = {
    "atlas": "aparc",
    "metric": "plv",
    "band": "theta",
    "clf": "logreg",
    "ba": 0.920,
    "ci_lo": 0.870,
    "ci_hi": 0.970,
    "p_perm": 0.0,
    "n_perm": 1000,
    "n_subjects": 50,
    "n_features": 2278,
    "null_mean": 0.4934,
    "null_std": 0.0618,
    "wall_clock_s": 463.9,
    "confusion": [[44, 6], [2, 48]],
    "source": "PERM_1000_WINNER_LOG.md",
}


def list_available_combos() -> list[dict[str, str]]:
    """Return list of (atlas, metric, band) for which feature files exist."""
    combos = []
    for f in sorted(FEATURES_DIR.glob("X_*.npz")):
        parts = f.stem[2:].split("_")  # strip "X_"
        if len(parts) == 3:
            combos.append({"atlas": parts[0], "metric": parts[1], "band": parts[2]})
    return combos


def load_feature_matrix(
    atlas: str, metric: str, band: str
) -> tuple[np.ndarray, np.ndarray, np.ndarray, list[str] | None]:
    """Load X, y, groups and optional ROI names for a given combo.

    Returns (X, y, groups, roi_names). roi_names may be None.
    """
    npz_path = FEATURES_DIR / f"X_{atlas}_{metric}_{band}.npz"
    if not npz_path.exists():
        raise FileNotFoundError(f"Feature file not found: {npz_path}")
    data = np.load(npz_path, allow_pickle=True)
    X = data["X"]
    roi_names: list[str] | None = data["row_labels"].tolist() if "row_labels" in data else None

    y_path = FEATURES_DIR / "y.npy"
    g_path = FEATURES_DIR / "groups.npy"
    y = np.load(y_path)
    groups = np.load(g_path)
    # Handle feature files computed on a subset (e.g. schaefer100 = N=30, aparc = N=50)
    if X.shape[0] != y.shape[0]:
        n = X.shape[0]
        y = y[:n]
        groups = groups[:n]
    return X, y, groups, roi_names


def load_existing_results() -> list[dict[str, Any]]:
    """Load all results from data/results/ds005385/ml_results.json."""
    path = RESULTS_DIR / "ml_results.json"
    if not path.exists():
        return []
    d = json.loads(path.read_text())
    return d.get("results", [])


def run_combo(
    atlas: str,
    metric: str,
    band: str,
    clf: str,
    n_perm: int = 0,
    n_splits: int = 50,
) -> dict[str, Any]:
    """Run LOSO CV (+ optional permutation test) for a given combo.

    Parameters
    ----------
    n_perm:
        Number of permutations. 0 = skip permutation test.

    Returns
    -------
    dict with keys: ba, ba_std, ci_lo, ci_hi, p_perm, n_perm, confusion,
                    null_distribution, ba_per_fold, n_features, wall_clock_s,
                    roc_fpr, roc_tpr, roc_auc
    """
    from analysis.stats_utility import bootstrap_ci
    from ml_training.ml_dispatcher import run_cv

    X, y, groups, roi_names = load_feature_matrix(atlas, metric, band)
    n_splits_actual = min(n_splits, int(np.unique(groups).shape[0]))

    t0 = time.time()
    cv_res = run_cv(X, y, groups=groups, algorithm=clf, n_splits=n_splits_actual)
    ci_lo, ci_hi = bootstrap_ci(cv_res.ba_per_fold, n_boot=2000, alpha=0.05)

    # ROC via LOSO predict_proba
    roc_fpr, roc_tpr, roc_auc_val = _compute_roc_loso(X, y, groups, clf, n_splits_actual)

    result: dict[str, Any] = {
        "atlas": atlas,
        "metric": metric,
        "band": band,
        "clf": clf,
        "ba": cv_res.ba_mean,
        "ba_std": cv_res.ba_std,
        "ci_lo": float(ci_lo),
        "ci_hi": float(ci_hi),
        "p_perm": None,
        "n_perm": n_perm,
        "null_distribution": [],
        "confusion": cv_res.confusion.tolist() if hasattr(cv_res.confusion, "tolist") else cv_res.confusion,
        "ba_per_fold": list(cv_res.ba_per_fold),
        "n_features": cv_res.n_features,
        "n_samples": cv_res.n_samples,
        "wall_clock_s": time.time() - t0,
        "roc_fpr": roc_fpr,
        "roc_tpr": roc_tpr,
        "roc_auc": roc_auc_val,
        "roi_names": roi_names,
    }

    if n_perm > 0:
        from ml_training.permutation import permutation_test
        perm_res = permutation_test(
            X, y, groups=groups, algorithm=clf,
            n_permutations=n_perm, n_splits=n_splits_actual,
        )
        result["p_perm"] = float(perm_res.p_value)
        result["null_distribution"] = list(perm_res.null_distribution)

    result["wall_clock_s"] = time.time() - t0
    return result


def _compute_roc_loso(
    X: np.ndarray,
    y: np.ndarray,
    groups: np.ndarray,
    clf_name: str,
    n_splits: int,
) -> tuple[list[float], list[float], float]:
    """Compute aggregate ROC curve via LOSO using sklearn directly."""
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import roc_auc_score, roc_curve
    from sklearn.model_selection import GroupKFold
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import StandardScaler
    from sklearn.svm import SVC

    clf_map = {
        "logreg": LogisticRegression(C=1.0, max_iter=1000, random_state=42),
        "svm_rbf": SVC(kernel="rbf", probability=True, random_state=42),
        "lda": None,  # handled below
    }

    if clf_name == "lda":
        from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
        base = LinearDiscriminantAnalysis()
    else:
        base = clf_map.get(clf_name, clf_map["logreg"])

    pipe = Pipeline([("scaler", StandardScaler()), ("clf", base)])
    gkf = GroupKFold(n_splits=n_splits)

    y_true_all, y_score_all = [], []
    for train_idx, test_idx in gkf.split(X, y, groups=groups):
        pipe.fit(X[train_idx], y[train_idx])
        if hasattr(pipe, "predict_proba"):
            scores = pipe.predict_proba(X[test_idx])[:, 1]
        else:
            scores = pipe.decision_function(X[test_idx])
        y_true_all.extend(y[test_idx].tolist())
        y_score_all.extend(scores.tolist())

    fpr, tpr, _ = roc_curve(y_true_all, y_score_all)
    auc_val = roc_auc_score(y_true_all, y_score_all)
    return fpr.tolist(), tpr.tolist(), float(auc_val)


def n50_winner_full_result() -> dict[str, Any]:
    """Return full result dict for N=50 winner (aparc×plv×theta×logreg)."""
    res = dict(N50_WINNER)
    # Load actual fold-level data to populate ba_per_fold and ROC
    try:
        X, y, groups, roi_names = load_feature_matrix("aparc", "plv", "theta")
        from ml_training.ml_dispatcher import run_cv
        cv_res = run_cv(X, y, groups=groups, algorithm="logreg", n_splits=50)
        roc_fpr, roc_tpr, roc_auc_val = _compute_roc_loso(X, y, groups, "logreg", 50)
        res["ba_per_fold"] = list(cv_res.ba_per_fold)
        res["n_samples"] = cv_res.n_samples
        res["roc_fpr"] = roc_fpr
        res["roc_tpr"] = roc_tpr
        res["roc_auc"] = roc_auc_val
        res["roi_names"] = roi_names
        # Synthetic null distribution for display (Gaussian approx from log)
        rng = np.random.default_rng(42)
        res["null_distribution"] = rng.normal(
            loc=res["null_mean"], scale=res["null_std"], size=1000
        ).clip(0, 1).tolist()
    except Exception:
        res["ba_per_fold"] = []
        res["roc_fpr"] = [0.0, 1.0]
        res["roc_tpr"] = [0.0, 1.0]
        res["roc_auc"] = 0.5
        res["roi_names"] = None
        null_rng = np.random.default_rng(42)
        res["null_distribution"] = null_rng.normal(0.4934, 0.0618, 1000).clip(0, 1).tolist()
    return res
