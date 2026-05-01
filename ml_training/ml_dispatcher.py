"""
STEP 6 — ML dispatcher: 5 classificatori + GroupKFold subject-level CV.

Algoritmi supportati:
  - "logreg"  : LogisticRegression (max_iter=2000, C=1.0)
  - "svm"     : SVC (kernel=rbf, C=1.0, probability=True)
  - "mlp"     : MLPClassifier (hidden=(100,50), max_iter=500)
  - "rf"      : RandomForestClassifier (n_estimators=200)
  - "gb"      : GradientBoostingClassifier (n_estimators=200)

CV: GroupKFold (k=5 di default) per prevenire data leakage inter-soggetto.
Output: balanced_accuracy per fold + media/std + confusion matrix aggregata.

Preprocessing: StandardScaler fittato solo sul train fold (no data leakage).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

import numpy as np
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score, confusion_matrix
from sklearn.model_selection import GroupKFold, StratifiedKFold
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

Algorithm = Literal["logreg", "svm", "mlp", "rf", "gb"]

_CLASSIFIERS: dict[str, object] = {
    "logreg": LogisticRegression(max_iter=2000, C=1.0, random_state=42),
    "svm": SVC(kernel="rbf", C=1.0, probability=True, random_state=42),
    "mlp": MLPClassifier(hidden_layer_sizes=(100, 50), max_iter=500, random_state=42),
    "rf": RandomForestClassifier(n_estimators=200, random_state=42),
    "gb": GradientBoostingClassifier(n_estimators=200, random_state=42),
}


@dataclass
class CVResult:
    """Risultato di una cross-validation run.

    Attributes
    ----------
    algorithm:
        Nome classificatore.
    ba_per_fold:
        Balanced accuracy per fold.
    ba_mean:
        Media balanced accuracy.
    ba_std:
        Deviazione standard balanced accuracy.
    confusion:
        Confusion matrix aggregata su tutti i fold.
    n_features:
        Numero di feature in input.
    n_samples:
        Numero di campioni totali.
    """

    algorithm: str
    ba_per_fold: list[float]
    ba_mean: float
    ba_std: float
    confusion: np.ndarray
    n_features: int
    n_samples: int
    fold_train_sizes: list[int] = field(default_factory=list)


def _make_pipeline(algorithm: Algorithm) -> Pipeline:
    clf = _CLASSIFIERS[algorithm]
    return Pipeline([("scaler", StandardScaler()), ("clf", clf)])


def run_cv(
    X: np.ndarray,
    y: np.ndarray,
    groups: np.ndarray | None = None,
    algorithm: Algorithm = "logreg",
    *,
    n_splits: int = 5,
    random_state: int = 42,
) -> CVResult:
    """Esegue GroupKFold CV (o StratifiedKFold se groups=None).

    Parameters
    ----------
    X:
        Feature matrix, shape (n_samples, n_features).
    y:
        Label array, shape (n_samples,). Valori interi o 0/1.
    groups:
        Group array per GroupKFold, shape (n_samples,). Se None, usa StratifiedKFold.
    algorithm:
        Chiave classificatore (logreg, svm, mlp, rf, gb).
    n_splits:
        Numero di fold CV.
    random_state:
        Seed per StratifiedKFold (ignorato per GroupKFold).

    Returns
    -------
    CVResult con balanced_accuracy per fold + media/std.
    """
    if groups is not None:
        cv = GroupKFold(n_splits=n_splits)
        splits = cv.split(X, y, groups=groups)
    else:
        cv_strat = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=random_state)
        splits = cv_strat.split(X, y)

    ba_folds: list[float] = []
    conf_agg = np.zeros((len(np.unique(y)),) * 2, dtype=int)
    train_sizes: list[int] = []

    for train_idx, test_idx in splits:
        X_tr, X_te = X[train_idx], X[test_idx]
        y_tr, y_te = y[train_idx], y[test_idx]

        pipe = _make_pipeline(algorithm)
        pipe.fit(X_tr, y_tr)
        y_pred = pipe.predict(X_te)

        ba_folds.append(float(balanced_accuracy_score(y_te, y_pred)))
        conf_agg += confusion_matrix(y_te, y_pred, labels=np.unique(y))
        train_sizes.append(len(train_idx))

    return CVResult(
        algorithm=algorithm,
        ba_per_fold=ba_folds,
        ba_mean=float(np.mean(ba_folds)),
        ba_std=float(np.std(ba_folds)),
        confusion=conf_agg,
        n_features=X.shape[1],
        n_samples=X.shape[0],
        fold_train_sizes=train_sizes,
    )


def run_all_algorithms(
    X: np.ndarray,
    y: np.ndarray,
    groups: np.ndarray | None = None,
    *,
    algorithms: list[Algorithm] | None = None,
    n_splits: int = 5,
) -> dict[str, CVResult]:
    """Esegue CV per tutti gli algoritmi richiesti.

    Parameters
    ----------
    X:
        Feature matrix (n_samples, n_features).
    y:
        Label array (n_samples,).
    groups:
        Group IDs per GroupKFold.
    algorithms:
        Subset di algoritmi. None = tutti e 5.
    n_splits:
        Numero fold.

    Returns
    -------
    dict {algorithm: CVResult}
    """
    algos = algorithms or list(_CLASSIFIERS.keys())
    return {
        algo: run_cv(X, y, groups=groups, algorithm=algo, n_splits=n_splits)  # type: ignore[arg-type]
        for algo in algos
    }
