"""F2 — Transferability check: train su N=100, valuta sui 79 soggetti NUOVI (N=179 ∖ N=100).

Risponde alla domanda-chiave del relatore: «il modello regge sui soggetti che NON hai mai
usato per scegliere la feature?». Il winner-feature (X_aparc_plv_theta) è stato selezionato su
N=50/N=100, che sono ⊂ N=179 → la CV su N=179 NON è held-out per la selezione (double-dipping).
Questo script isola l'unico test davvero held-out: addestra solo sui 100 e misura sui 79 mai-visti.

Metodo (stessa pipeline dei risultati ufficiali):
  - StandardScaler fit-only-su-train + LogReg-L2 (class_weight=balanced) con GridSearchCV
    GroupKFold interno per la C → addestrato SOLO sui 100.
  - Predizione sui 79 nuovi → balanced_accuracy held-out.
  - Significatività: permutation test subject-level sulle label dei 79 (predizioni FISSE) → p.
  - Incertezza: cluster-bootstrap a livello soggetto sui 79.
Deterministico (seed=42). Confronto col BA della CV-N=179 (0.795) per quantificare l'ottimismo.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score
from sklearn.model_selection import GridSearchCV, GroupKFold
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config.labels_phenotype import load_phenotype  # noqa: E402
from config.subjects_whitelist_n100 import SUBJECT_WHITELIST_N100 as N100  # noqa: E402
from config.subjects_whitelist_n179 import SUBJECT_WHITELIST_N179 as N179  # noqa: E402

_REPO = Path(__file__).resolve().parents[1]
FEAT_DIR = _REPO / "data" / "features" / "ds005385"
WINNER = "X_aparc_plv_theta"
BA_CV_N179 = 0.795  # risultato CV ufficiale N=179 (per confronto ottimismo)


def split_indices(subjects_n179: list[str], n100: set[str]) -> tuple[list[int], list[int]]:
    """Indici-soggetto: train = quelli in N=100; test = i NUOVI (N=179 ∖ N=100)."""
    train = [i for i, s in enumerate(subjects_n179) if s in n100]
    test = [i for i, s in enumerate(subjects_n179) if s not in n100]
    return train, test


def _mask(groups: np.ndarray, subj_idx: list[int]) -> np.ndarray:
    return np.isin(groups, subj_idx)


def fit_on_train_eval_holdout(X, y, groups, train_subj, test_subj, seed=42):
    """Addestra sui soggetti-train, predice sui soggetti-test. Ritorna (y_true, y_pred, g_test, bestC)."""
    tr, te = _mask(groups, train_subj), _mask(groups, test_subj)
    scaler = StandardScaler()
    X_tr = scaler.fit_transform(X[tr])
    X_te = scaler.transform(X[te])
    g_tr = groups[tr]
    inner = GroupKFold(n_splits=min(5, len(np.unique(g_tr))))
    clf = GridSearchCV(
        LogisticRegression(max_iter=2000, class_weight="balanced",
                           solver="liblinear", random_state=seed),
        param_grid={"C": [0.01, 0.1, 1.0, 10.0]},
        cv=inner, scoring="balanced_accuracy", refit=True,
    )
    clf.fit(X_tr, y[tr], groups=g_tr)
    return y[te], clf.predict(X_te), groups[te], clf.best_params_["C"]


def _subject_perm(y_true, groups, rng):
    uniq = np.unique(groups)
    per_sub = rng.permutation(np.array([y_true[groups == g][0] for g in uniq]))
    y_sh = np.empty_like(y_true)
    for i, g in enumerate(uniq):
        y_sh[groups == g] = per_sub[i]
    return y_sh


def perm_pvalue(y_true, y_pred, groups, n_perm, seed=42):
    """p-value held-out: permuta le label-soggetto dei test, predizioni FISSE (Phipson-Smyth +1/+1)."""
    rng = np.random.default_rng(seed)
    ba_obs = balanced_accuracy_score(y_true, y_pred)
    cnt = sum(balanced_accuracy_score(_subject_perm(y_true, groups, rng), y_pred) >= ba_obs
              for _ in range(n_perm))
    return float((cnt + 1) / (n_perm + 1)), float(ba_obs)


def cluster_bootstrap_ci(y_true, y_pred, groups, n_boot, seed=42):
    rng = np.random.default_rng(seed)
    uniq = np.unique(groups)
    bas = []
    for _ in range(n_boot):
        sel = rng.choice(uniq, len(uniq), replace=True)
        idx = np.concatenate([np.where(groups == g)[0] for g in sel])
        bas.append(balanced_accuracy_score(y_true[idx], y_pred[idx]))
    return float(np.percentile(bas, 2.5)), float(np.percentile(bas, 97.5))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-perm", type=int, default=1000)
    ap.add_argument("--n-boot", type=int, default=1000)
    ap.add_argument("--dry-run", action="store_true", help="solo check split, niente fit")
    args = ap.parse_args()

    n100_set = set(N100)
    train_subj, test_subj = split_indices(N179, n100_set)
    print(f"[F2] train={len(train_subj)} soggetti (N=100) | test held-out={len(test_subj)} NUOVI")
    assert len(train_subj) == 100 and len(test_subj) == 79, "split N100/79 inatteso"
    if args.dry_run:
        return

    X_file = FEAT_DIR / f"{WINNER}.npz"
    if not X_file.exists():
        raise FileNotFoundError(f"Feature winner mancante: {X_file}")
    X = np.load(X_file)["X"].astype(np.float64)
    if X.shape[0] != len(N179) * 2:
        raise ValueError(f"X.shape[0]={X.shape[0]} atteso {len(N179) * 2}")
    groups = np.repeat(np.arange(len(N179)), 2)
    _, y_sex_per_sub = load_phenotype(N179)
    y = y_sex_per_sub[groups]

    y_true, y_pred, g_te, best_c = fit_on_train_eval_holdout(X, y, groups, train_subj, test_subj)
    p_perm, ba_hold = perm_pvalue(y_true, y_pred, g_te, args.n_perm)
    ci_lo, ci_hi = cluster_bootstrap_ci(y_true, y_pred, g_te, args.n_boot)

    res = {
        "timestamp": datetime.now(UTC).isoformat(timespec="seconds"),
        "feature": WINNER, "n_train": len(train_subj), "n_test_holdout": len(test_subj),
        "best_C": best_c, "ba_holdout_79": ba_hold, "ci95_holdout": [ci_lo, ci_hi],
        "p_perm_holdout": p_perm, "n_perm": args.n_perm, "n_boot": args.n_boot,
        "ba_cv_n179_reference": BA_CV_N179, "optimism_gap": round(BA_CV_N179 - ba_hold, 4),
    }
    out_json = _REPO / "data" / "results" / "ds005385" / "transferability_n79.json"
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(res, indent=2))
    print(json.dumps(res, indent=2))
    print(f"\n[F2] BA held-out sui 79 nuovi = {ba_hold:.3f} "
          f"(CV-N179 ref = {BA_CV_N179}; gap-ottimismo = {res['optimism_gap']:+.3f}); "
          f"p_perm = {p_perm:.4f}")


if __name__ == "__main__":
    main()
