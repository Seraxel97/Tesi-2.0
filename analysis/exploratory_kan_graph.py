"""
ANALISI ESPLORATIVA — NON CONFERMATIVA, NON PRE-REGISTRATA.

Questo script è hypothesis-generating. I risultati NON costituiscono
evidenza confermativa e non fanno parte del protocollo pre-registrato.

Obiettivo: confrontare KAN (spline) vs baseline LogReg-L2 (pre-registrata)
sulle 8 graph-theory feature (X_aparc_plv_theta_gt) con GroupKFold(5).
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
import warnings
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score
from sklearn.model_selection import GroupKFold
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config.labels_phenotype import load_phenotype  # noqa: E402

# ---------------------------------------------------------------------------
# Costanti
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data" / "features" / "ds005385"
SEED = 42
N_SPLITS = 5
KAN_EPOCHS = 50
KAN_LR = 1e-3
KAN_HIDDEN = 4  # neuroni hidden layer: 8→4→1 (binario)

GT_FEATURE_NAMES = [
    "mean_degree",
    "mean_strength",
    "clustering_coeff",
    "path_length",
    "global_efficiency",
    "local_efficiency",
    "modularity_q",
    "small_worldness",
]

torch.manual_seed(SEED)
np.random.seed(SEED)


# ---------------------------------------------------------------------------
# KAN minimale con B-spline Chebyshev (implementazione standalone)
# Usa pykan solo se disponibile; altrimenti fallback su MLP-spline approssimato
# ---------------------------------------------------------------------------

def _try_import_kan():
    """Importa KAN da pykan; restituisce None se non disponibile."""
    try:
        # pykan crea checkpoint dir — reindirizza su tmpdir
        old_cwd = os.getcwd()
        tmp = tempfile.mkdtemp()
        os.chdir(tmp)
        from kan import KAN as _KAN  # noqa: PLC0415
        os.chdir(old_cwd)
        return _KAN
    except ImportError:
        return None


class _ChebyshevKANLayer(nn.Module):
    """Un singolo layer KAN con base Chebyshev di grado `degree`."""

    def __init__(self, in_features: int, out_features: int, degree: int = 4):
        super().__init__()
        self.in_features = in_features
        self.out_features = out_features
        self.degree = degree
        # coefficienti per ogni coppia (in, out, grado)
        self.coeffs = nn.Parameter(
            torch.randn(in_features, out_features, degree + 1) * 0.1
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (batch, in_features), normalizzato in [-1,1]
        x = torch.tanh(x)
        # Polinomi di Chebyshev T_0 ... T_degree
        T = [torch.ones_like(x), x]
        for n in range(2, self.degree + 1):
            T.append(2 * x * T[-1] - T[-2])
        # T[k]: (batch, in_features)
        T_stack = torch.stack(T, dim=-1)  # (batch, in, degree+1)
        # contrai su in_features e degree → (batch, out_features)
        out = torch.einsum("bid,iod->bo", T_stack, self.coeffs)
        return out

    def n_params(self) -> int:
        return self.in_features * self.out_features * (self.degree + 1)

    def feature_importance(self) -> np.ndarray:
        """Norma L1 dei coefficienti per feature di input (sum over out e grado)."""
        with torch.no_grad():
            imp = self.coeffs.abs().sum(dim=(1, 2))  # (in_features,)
        return imp.cpu().numpy()


class ChebyshevKAN(nn.Module):
    """KAN binario: 8 → hidden → 1 con layer Chebyshev."""

    def __init__(self, in_features: int = 8, hidden: int = 4, degree: int = 4):
        super().__init__()
        self.layer1 = _ChebyshevKANLayer(in_features, hidden, degree)
        self.layer2 = _ChebyshevKANLayer(hidden, 1, degree)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        h = torch.relu(self.layer1(x))
        return self.layer2(h).squeeze(-1)

    def n_params(self) -> int:
        return self.layer1.n_params() + self.layer2.n_params()

    def feature_importance(self) -> np.ndarray:
        """Importanza delle 8 feature di input dal primo layer."""
        return self.layer1.feature_importance()


# ---------------------------------------------------------------------------
# Training / evaluation
# ---------------------------------------------------------------------------

def _train_kan(
    X_tr: np.ndarray,
    y_tr: np.ndarray,
    epochs: int = KAN_EPOCHS,
    lr: float = KAN_LR,
    device: str = "cpu",
) -> ChebyshevKAN:
    model = ChebyshevKAN(in_features=X_tr.shape[1], hidden=KAN_HIDDEN, degree=4)
    model = model.to(device)
    optimizer = optim.Adam(model.parameters(), lr=lr)
    loss_fn = nn.BCEWithLogitsLoss()

    X_t = torch.tensor(X_tr, dtype=torch.float32, device=device)
    y_t = torch.tensor(y_tr, dtype=torch.float32, device=device)

    model.train()
    for _ in range(epochs):
        optimizer.zero_grad()
        logits = model(X_t)
        loss = loss_fn(logits, y_t)
        loss.backward()
        optimizer.step()

    return model


def _predict_kan(model: ChebyshevKAN, X_te: np.ndarray, device: str = "cpu") -> np.ndarray:
    model.eval()
    with torch.no_grad():
        X_t = torch.tensor(X_te, dtype=torch.float32, device=device)
        logits = model(X_t)
        preds = (torch.sigmoid(logits) >= 0.5).long().cpu().numpy()
    return preds


# ---------------------------------------------------------------------------
# Pipeline principale
# ---------------------------------------------------------------------------

def load_data() -> tuple[np.ndarray, np.ndarray, np.ndarray, bool]:
    """Restituisce (X, groups, y_sex, real_labels)."""
    X = np.load(DATA_DIR / "X_aparc_plv_theta_gt.npy")
    groups = np.load(DATA_DIR / "groups.npy")

    meta = json.loads((DATA_DIR / "metadata.json").read_text())
    subjects = meta["subjects"]

    try:
        _, y_sex = load_phenotype(subjects)
        real_labels = True
    except Exception as exc:
        warnings.warn(
            f"load_phenotype fallito ({exc}): uso label PERMUTATE per SMOKE TEST"
        )
        rng = np.random.default_rng(SEED)
        y_sex = rng.integers(0, 2, size=len(subjects), dtype=np.int64)
        # allineamento: subjects × condizioni → y per riga di X
        # groups.npy codifica il soggetto per ogni riga; mappa subject→label
        # groups contiene indici soggetto (0-based unique) o sub-IDs
        unique_grps = np.unique(groups)
        grp_to_label = {g: rng.integers(0, 2) for g in unique_grps}
        y_sex = np.array([grp_to_label[g] for g in groups], dtype=np.int64)
        real_labels = False

    return X, groups, y_sex, real_labels


def run_cv(
    X: np.ndarray,
    groups: np.ndarray,
    y: np.ndarray,
) -> dict:
    gkf = GroupKFold(n_splits=N_SPLITS)
    device = "cuda" if torch.cuda.is_available() else "cpu"

    ba_kan_folds: list[float] = []
    ba_lr_folds: list[float] = []
    imp_folds: list[np.ndarray] = []
    n_params_kan: int | None = None

    for fold, (tr_idx, te_idx) in enumerate(gkf.split(X, y, groups=groups)):
        X_tr, X_te = X[tr_idx], X[te_idx]
        y_tr, y_te = y[tr_idx], y[te_idx]

        # StandardScaler DENTRO il fold — no leakage
        scaler = StandardScaler()
        X_tr_s = scaler.fit_transform(X_tr)
        X_te_s = scaler.transform(X_te)

        # --- KAN ---
        torch.manual_seed(SEED + fold)
        kan_model = _train_kan(X_tr_s, y_tr, device=device)
        y_pred_kan = _predict_kan(kan_model, X_te_s, device=device)
        ba_kan = balanced_accuracy_score(y_te, y_pred_kan)
        ba_kan_folds.append(ba_kan)
        imp_folds.append(kan_model.feature_importance())

        if n_params_kan is None:
            n_params_kan = kan_model.n_params()

        # --- LogReg-L2 (baseline pre-registrata) ---
        lr_model = LogisticRegression(C=1.0, max_iter=1000, random_state=SEED)
        lr_model.fit(X_tr_s, y_tr)
        y_pred_lr = lr_model.predict(X_te_s)
        ba_lr = balanced_accuracy_score(y_te, y_pred_lr)
        ba_lr_folds.append(ba_lr)

        print(
            f"  Fold {fold + 1}/{N_SPLITS} | "
            f"KAN BA={ba_kan:.3f} | LogReg BA={ba_lr:.3f}"
        )

    mean_imp = np.mean(imp_folds, axis=0)
    ranked = np.argsort(mean_imp)[::-1]

    return {
        "ba_kan_mean": float(np.mean(ba_kan_folds)),
        "ba_kan_std": float(np.std(ba_kan_folds)),
        "ba_lr_mean": float(np.mean(ba_lr_folds)),
        "ba_lr_std": float(np.std(ba_lr_folds)),
        "n_params_kan": n_params_kan,
        "n_params_lr": X.shape[1] + 1,  # pesi + bias
        "feature_importance": {
            GT_FEATURE_NAMES[i]: float(mean_imp[i]) for i in range(len(GT_FEATURE_NAMES))
        },
        "top_features_ranked": [GT_FEATURE_NAMES[i] for i in ranked],
        "ba_kan_folds": ba_kan_folds,
        "ba_lr_folds": ba_lr_folds,
    }


def print_report(results: dict, real_labels: bool) -> None:
    sep = "=" * 62
    print(f"\n{sep}")
    print("  RISULTATI ESPLORATIVI — NON CONFERMATORI")
    print(sep)
    label_note = "label REALI" if real_labels else "label SINTETICHE (SMOKE TEST)"
    print(f"  Etichette: {label_note}")
    print(f"  KAN  BA = {results['ba_kan_mean']:.3f} ± {results['ba_kan_std']:.3f}")
    print(f"  LR   BA = {results['ba_lr_mean']:.3f} ± {results['ba_lr_std']:.3f}")
    print(f"  KAN n_params = {results['n_params_kan']}")
    print(f"  LR  n_params = {results['n_params_lr']}")
    print("\n  Feature importance KAN (layer1, norma L1 coefficienti):")
    for feat, imp in sorted(
        results["feature_importance"].items(), key=lambda kv: -kv[1]
    ):
        bar = "#" * int(imp / max(results["feature_importance"].values()) * 20)
        print(f"    {feat:<22} {imp:.4f}  {bar}")
    print(f"\n  Top feature: {results['top_features_ranked'][0]}")
    print(sep)
    if not real_labels:
        print("\nSMOKE OK — run reale richiede participants.tsv")


def main() -> None:
    print("-- ANALISI ESPLORATIVA KAN su graph-theory feature --")
    print("   NON pre-registrata, NON confermativa\n")

    X, groups, y, real_labels = load_data()
    print(f"  X shape: {X.shape}, gruppi unici: {len(np.unique(groups))}")
    print(f"  Label distribuzione: {np.bincount(y)} (0=F, 1=M)\n")
    print(f"  Device: {'cuda' if torch.cuda.is_available() else 'cpu'}")
    print(f"  GroupKFold(n_splits={N_SPLITS})\n")

    results = run_cv(X, groups, y)
    print_report(results, real_labels)

    # Salva JSON risultati
    out_path = REPO_ROOT / "analysis" / "exploratory_kan_graph_results.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n  Risultati salvati in: {out_path.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
