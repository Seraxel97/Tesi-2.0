"""ALTO-2 (Fable) — Validazione esterna SESSO su coorte SANA: ds005385 → LEMON.

Chiude il buco della generalizzazione con un confronto PULITO (finora il solo cross-dataset
era ds004504 = coorte Alzheimer, età-diversa → confuso). LEMON = adulti SANI, resting-state,
con gender esatto → è il test onesto: la classificazione del sesso addestrata su ds005385
generalizza a persone diverse e sane?

Metodo (nessun leakage, inference-only, come analysis/cross_dataset_eval.py):
- TRAIN: ds005385 completo (N=179, 358 sample) sulla feature-winner.
- TEST: LEMON (47 sogg, 94 sample) prodotto dalla STESSA pipeline (run_pipeline_lemon.py).
- StandardScaler fit SOLO su train; LogReg-L2 (stessa famiglia del classificatore-CV, C via
  GridSearchCV GroupKFold su train); predict su LEMON; balanced accuracy.
- Ripetuto su PLV-theta (winner, sensibile a volume-conduction) + wPLI/imcoh-theta (robuste),
  per legare ALTO-2 ad ALTO-3.


Input:  data/features/ds005385/ (train, via run_ml_age_sex_n179._load_data) e
        data/features/lemon/{X_aparc_<metrica>_theta.npz, y.npy} (test).
Output: data/results/lemon/cross_dataset_sex_lemon.json e
        reports/CROSS_DATASET_LEMON_SEX_ALTO2.md.
Uso: python scripts/cross_dataset_lemon.py
"""

from __future__ import annotations

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
from scripts.run_ml_age_sex_n179 import _load_data  # noqa: E402

# ===== 1. Configurazione =====
_REPO = Path(__file__).resolve().parents[1]  # radice del repo
# cartella delle feature LEMON (test set)
LEMON_FEAT = _REPO / "data" / "features" / "lemon"
# metrica di connettivita' -> nome del file di feature (atlante aparc, banda theta)
METRICS = {
    "plv": "X_aparc_plv_theta",  # winner (sensibile volume-conduction)
    "wpli": "X_aparc_wpli_theta",  # robusta
    "imcoh": "X_aparc_imcoh_theta",  # robusta
}
# JSON dei risultati e report Markdown
OUT = _REPO / "data" / "results" / "lemon" / "cross_dataset_sex_lemon.json"
REPORT = _REPO / "reports" / "CROSS_DATASET_LEMON_SEX_ALTO2.md"


# ===== 2. Trasferimento ds005385 -> LEMON =====
def _load_lemon(feat: str) -> tuple[np.ndarray, np.ndarray]:
    """Carica la matrice di feature LEMON e le etichette di sesso.

    Args:
        feat: nome del file di feature senza estensione (es. ``X_aparc_plv_theta``).

    Returns:
        ``(X, y)``: X float64 (campioni, archi) e y per campione (0 = F, 1 = M).
        Legge file da ``LEMON_FEAT``.
    """
    X = np.load(LEMON_FEAT / f"{feat}.npz")["X"].astype(np.float64)
    y = np.load(LEMON_FEAT / "y.npy")  # sex per-sample (0=F,1=M), allineato a X
    return X, y


def transfer_sex(feat: str) -> dict:
    """Addestra su ds005385 e valuta su LEMON la classificazione del sesso.

    Lo scaler e' adattato solo sul train (nessun leakage); la regolarizzazione C
    e' scelta con GridSearchCV + GroupKFold(3) sui soggetti del train.

    Args:
        feat: nome della feature (es. ``X_aparc_plv_theta``).

    Returns:
        Dict con balanced accuracy di trasferimento, C migliore, numerosita'
        di train/test e bilanciamento di sesso nel test. Nessun file scritto.
    """
    # train = ds005385 completo (N=179)
    X_tr, _y_age, y_tr, g_tr, _ = _load_data(feat)
    X_te, y_te = _load_lemon(feat)

    scaler = StandardScaler().fit(X_tr)
    X_tr_s, X_te_s = scaler.transform(X_tr), scaler.transform(X_te)

    inner = GroupKFold(n_splits=3)
    clf = GridSearchCV(
        LogisticRegression(
            max_iter=2000, class_weight="balanced", solver="liblinear", random_state=42
        ),
        param_grid={"C": [0.01, 0.1, 1.0, 10.0]},
        cv=inner,
        scoring="balanced_accuracy",
        refit=True,
    )
    clf.fit(X_tr_s, y_tr, groups=g_tr)
    y_pred = clf.predict(X_te_s)
    ba = float(balanced_accuracy_score(y_te, y_pred))
    return {
        "feature": feat,
        "ba_transfer": ba,
        "best_C": clf.best_params_["C"],
        "n_train_samples": int(X_tr.shape[0]),
        "n_test_samples": int(X_te.shape[0]),
        "test_sex_balance": {
            int(k): int(v) for k, v in zip(*np.unique(y_te, return_counts=True), strict=False)
        },
    }


def main() -> None:
    """Esegue il trasferimento per PLV, wPLI e imcoh e scrive i risultati.

    Side effects:
        Scrive ``OUT`` (JSON) e ``REPORT`` (Markdown); seed numpy globale = 42.
    """
    np.random.seed(42)
    results = {}
    for key, feat in METRICS.items():
        print(f"[ALTO2] transfer ds005385→LEMON, {key} ({feat})…")
        r = transfer_sex(feat)
        results[key] = r
        print(
            f"        BA transfer = {r['ba_transfer']:.3f} (C={r['best_C']}, "
            f"test n={r['n_test_samples']})"
        )

    plv_ba = results["plv"]["ba_transfer"]
    robust_mean = float(np.mean([results[k]["ba_transfer"] for k in ("wpli", "imcoh")]))
    # verdetto onesto: generalizza se ben sopra il caso (0.5)
    generalizes = plv_ba >= 0.60
    verdict = (
        f"IL SESSO GENERALIZZA a coorte SANA indipendente (LEMON): BA transfer={plv_ba:.3f} "
        f"(PLV) ben sopra il caso → la scoperta NON è specifica del solo ds005385"
        if generalizes
        else f"GENERALIZZAZIONE DEBOLE/ASSENTE su coorte sana: BA transfer={plv_ba:.3f} (PLV) vicino "
        f"al caso → la classificazione del sesso è in gran parte specifica di ds005385, non "
        f"trasferibile; da dichiarare come limite (risultato dataset-specifico)"
    )

    out = {
        "train": "ds005385 (N=179, 358 sample)",
        "test": "LEMON (coorte sana, 47 sogg/94 sample)",
        "method": "no-leakage scaler-su-train, LogReg-L2 GridSearchCV GroupKFold-inner, inference-only",
        "in_dataset_cv_ba_plv": 0.795,
        "results": results,
        "plv_transfer_ba": plv_ba,
        "robust_transfer_mean_ba": robust_mean,
        "generalizes": generalizes,
        "verdict": verdict,
        "timestamp": datetime.now(UTC).isoformat(timespec="seconds"),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=2))

    lines = [
        "# ALTO-2 — Validazione esterna SESSO su coorte SANA (ds005385 → LEMON)\n",
        "Train: **ds005385** N=179. Test: **LEMON** (adulti SANI, 47 sogg/94 sample), stessa "
        "pipeline. No leakage (scaler fit solo su train), inference-only. Questo SOSTITUISCE il "
        "vecchio transfer confuso su ds004504 (Alzheimer) e i numeri-fantasma dell'ADR-004.\n",
        "| Metrica | Volume-conduction | BA transfer → LEMON |",
        "|---|---|---|",
    ]
    for key in ("plv", "wpli", "imcoh"):
        vc = "sensibile" if key == "plv" else "robusta"
        lines.append(f"| {key} | {vc} | **{results[key]['ba_transfer']:.3f}** |")
    lines += [
        "\nRiferimento in-dataset (CV su ds005385): PLV BA = 0.795.\n",
        f"## Verdetto\n**{verdict}.**",
        "\n> Interpretazione onesta combinata con ALTO-1 (regge age-matching, BA=0.719) e ALTO-3 "
        "(volume-conduction: effetto onesto ~0.57): il segnale-sesso è reale entro-dataset; questo "
        "test dice se sopravvive anche FUORI dal dataset, su persone sane diverse.",
    ]
    REPORT.write_text("\n".join(lines) + "\n")
    print(f"\n[ALTO2] {verdict}")
    print(f"[ALTO2] Scritti: {OUT.name}, {REPORT.name}")


if __name__ == "__main__":
    main()
