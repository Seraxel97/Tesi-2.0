"""Cross-dataset evaluation ONESTA: train ds005385 (N=179) → test LEMON (coorte SANA).

Rispetto al precedente cross_dataset_eval.py (test=ds004504, coorte Alzheimer =
confondente), qui il test è LEMON, una coorte SANA — validazione esterna pulita
della classificazione SESSO.

Protocollo:
- Train: ds005385, feature X_aparc_plv_theta (N=179 soggetti × 2 cond = 358 sample)
- Test:  LEMON (inference-only, nessun retraining)
- NO leakage: StandardScaler fit SOLO su train, transform su test
- Metriche robuste: oltre a PLV, wPLI + imCoh se le feature LEMON sono disponibili
- In-dataset baseline ds005385 via GroupKFold K=5 (confronto con 0.795 riportato)

Usage:
    python analysis/cross_dataset_eval_lemon.py
    python analysis/cross_dataset_eval_lemon.py --feat X_aparc_wpli_theta

Posizione nella pipeline: post-STEP 6/7: analisi e confronto dei risultati (non e' uno step di elaborazione).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score
from sklearn.model_selection import GroupKFold
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, str(Path(__file__).parent.parent))

DS005385_FEAT = Path("data/features/ds005385")

# ===== Configurazione =====

LEMON_FEAT = Path("data/features/lemon")
REPORT_PATH = Path("reports/CROSS_DATASET_TRANSFER_LEMON.md")

DEFAULT_FEATS = ["X_aparc_plv_theta", "X_aparc_wpli_theta", "X_aparc_imcoh_theta"]


# ===== Caricamento dati =====


def load_train(feat_name: str):
    """ds005385 N=179 come train (whitelist deterministica)."""
    from config.labels_phenotype import load_phenotype
    from config.subjects_whitelist_n179 import SUBJECT_WHITELIST_N179 as SUBS

    arr = np.load(DS005385_FEAT / f"{feat_name}.npz")
    X = arr[arr.files[0]].astype(np.float64)

    n_expected = len(SUBS) * 2
    if X.shape[0] != n_expected:
        raise ValueError(
            f"{feat_name}: X.shape[0]={X.shape[0]} atteso {n_expected} (N=179×2). "
            "Pipeline ds005385 N=179 non completa per questa feature?"
        )
    groups = np.repeat(np.arange(len(SUBS)), 2)
    _, y_sex_sub = load_phenotype(list(SUBS))
    y_sex = y_sex_sub[groups]
    return X, y_sex, groups


def load_test(feat_name: str):
    """LEMON come test."""
    from config.labels_phenotype_lemon import load_phenotype_lemon

    meta = json.loads((LEMON_FEAT / "metadata.json").read_text())
    subject_ids = meta["subject_ids"]
    conds = meta["conditions"]

    arr = np.load(LEMON_FEAT / f"{feat_name}.npz")
    X = arr[arr.files[0]].astype(np.float64)

    n_expected = len(subject_ids) * len(conds)
    if X.shape[0] != n_expected:
        raise ValueError(f"LEMON {feat_name}: X.shape[0]={X.shape[0]} atteso {n_expected}")
    _, y_sex_sub = load_phenotype_lemon(subject_ids)
    y_sex = np.repeat(y_sex_sub, len(conds)).astype(np.int64)
    groups = np.load(LEMON_FEAT / "groups.npy")
    return X, y_sex, groups, subject_ids


# ===== Valutazione =====


def in_dataset_ba(X, y, groups) -> float:
    """Baseline in-dataset ds005385 (GroupKFold K=5, scaler per fold)."""
    cv = GroupKFold(n_splits=5)
    bas = []
    for tr, te in cv.split(X, y, groups):
        s = StandardScaler().fit(X[tr])
        clf = LogisticRegression(
            C=0.1, class_weight="balanced", max_iter=2000, solver="liblinear", random_state=42
        )
        clf.fit(s.transform(X[tr]), y[tr])
        bas.append(balanced_accuracy_score(y[te], clf.predict(s.transform(X[te]))))
    return float(np.mean(bas))


def eval_feat(feat_name: str) -> dict | None:
    """Transfer per una singola feature. None se feature LEMON assente."""
    if not (LEMON_FEAT / f"{feat_name}.npz").exists():
        print(f"[{feat_name}] feature LEMON assente → skip")
        return None
    if not (DS005385_FEAT / f"{feat_name}.npz").exists():
        print(f"[{feat_name}] feature ds005385 assente → skip")
        return None

    X_tr, y_tr, g_tr = load_train(feat_name)
    X_te, y_te, _, _ = load_test(feat_name)

    if X_tr.shape[1] != X_te.shape[1]:
        raise ValueError(
            f"{feat_name}: mismatch dim archi train={X_tr.shape[1]} test={X_te.shape[1]}"
        )

    scaler = StandardScaler().fit(X_tr)  # fit SOLO su train
    clf = LogisticRegression(
        C=0.1, class_weight="balanced", max_iter=2000, solver="liblinear", random_state=42
    )
    clf.fit(scaler.transform(X_tr), y_tr)
    y_pred = clf.predict(scaler.transform(X_te))
    ba_transfer = balanced_accuracy_score(y_te, y_pred)
    ba_in = in_dataset_ba(X_tr, y_tr, g_tr)

    res = {
        "feat": feat_name,
        "ba_transfer": round(float(ba_transfer), 3),
        "ba_indataset": round(ba_in, 3),
        "n_train": int(X_tr.shape[0]),
        "n_test": int(X_te.shape[0]),
        "dim": int(X_tr.shape[1]),
        "test_sex_dist": np.bincount(y_te).tolist(),
    }
    print(
        f"[{feat_name}] transfer BA={ba_transfer:.3f} | in-dataset BA={ba_in:.3f} "
        f"| N_test={X_te.shape[0]} | sexdist={res['test_sex_dist']}"
    )
    return res


# ===== Entry point CLI =====


def main():
    """Entry point CLI: valuta il transfer ds005385 -> LEMON per le feature richieste.

    Per ogni feature calcola la balanced accuracy di transfer e in-dataset
    e scrive il report Markdown di sintesi.
    """
    ap = argparse.ArgumentParser()
    ap.add_argument("--feat", nargs="*", default=DEFAULT_FEATS)
    args = ap.parse_args()

    results = [r for f in args.feat if (r := eval_feat(f)) is not None]
    if not results:
        print("Nessuna feature valutabile (pipeline LEMON non completa?)")
        return

    primary = results[0]
    lines = [
        "# Cross-Dataset Transfer ONESTO: ds005385 (N=179) → LEMON (coorte SANA)",
        "",
        f"**Data**: {__import__('datetime').date.today()}",
        "**Train**: ds005385 N=179 soggetti (×2 cond = 358 sample)",
        f"**Test**: LEMON N={primary['n_test'] // 2} soggetti (×2 cond EC/EO = {primary['n_test']} sample)",
        "**Protocollo**: inference-only, scaler fit SOLO su train (no leakage), LogReg C=0.1 balanced",
        "",
        "## Classificazione SESSO — transfer vs in-dataset",
        "",
        "| Feature | Transfer BA (→LEMON) | In-dataset BA (ds005385 5-fold) |",
        "|---------|----------------------|---------------------------------|",
    ]
    for r in results:
        lines.append(f"| {r['feat']} | **{r['ba_transfer']:.3f}** | {r['ba_indataset']:.3f} |")
    lines += [
        "",
        f"Distribuzione sesso test LEMON (F/M per-sample): {primary['test_sex_dist']}",
        "",
        "## Note",
        "",
        "- LEMON = coorte SANA (no confondente patologico, a differenza del vecchio test ds004504=Alzheimer).",
        "- Chance = 0.500. Confronto in-dataset ds005385 riportato = 0.795.",
        "- Nessun retraining su LEMON: solo inference.",
        "",
    ]
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines) + "\n")
    print(f"\nReport → {REPORT_PATH}")
    print("RESULTS:", json.dumps(results))


if __name__ == "__main__":
    main()
