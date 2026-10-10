"""Tab 5 — ML & Predictions.

Classificazione / regressione interattiva con GroupKFold enforced.
Vincoli scientifici:
  - GroupKFold subject-level (no leakage)
  - Permutation p-value mostrato sempre
  - Bootstrap CI mostrato sempre
  - EO/EC = positive-control, non biomarker

Posizione nella pipeline: visualizzazione dei risultati degli STEP 1-7 (nessuna elaborazione di pipeline).
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import plotly.graph_objects as go
import streamlit as st

_ROOT = Path(__file__).parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from analysis.stats_utility import format_pvalue  # noqa: E402
from dashboard.components.data_loader import (  # noqa: E402
    list_available_combos,
    load_feature_matrix,
    load_ml_n179,
)
from dashboard.components.ml_runner import run_classification, run_regression  # noqa: E402

st.set_page_config(page_title="ML & Predictions — Tesi 2.0", page_icon="", layout="wide")

st.title(" ML & Predictions")
st.caption("GroupKFold subject-level · permutation p-value · bootstrap CI · FDR-BH adjustment")

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("Selettori ML")
    target = st.selectbox(
        "Target",
        ["Sesso (M/F)", "Età (regressione)", "EO vs EC (positive-control)"],
        index=0,
        help="Sesso/Età = target scientifici (risultati finali N=179). EO/EC = effetto Berger (positive-control pipeline).",
    )
    st.divider()

    combos = list_available_combos()
    atlases = sorted({c["atlas"] for c in combos})
    metrics = sorted({c["metric"] for c in combos})
    bands = sorted({c["band"] for c in combos})

    atlas = st.selectbox(
        "Atlante", atlases, index=atlases.index("aparc") if "aparc" in atlases else 0
    )
    metric = st.selectbox(
        "Metrica FC", metrics, index=metrics.index("plv") if "plv" in metrics else 0
    )
    band = st.selectbox("Banda", bands, index=bands.index("theta") if "theta" in bands else 0)

    st.divider()
    if target.startswith("Età"):
        clf_options = ["ridge", "rf_reg", "svr", "mlp_reg"]
    else:
        clf_options = ["logreg", "svm", "mlp", "rf", "gb"]
    clf_name = st.selectbox("Algoritmo", clf_options, index=0)

    n_perm = st.select_slider(
        "Permutazioni (0 = skip)",
        [0, 50, 100, 200],
        value=0,
        help="0 = skip permutation. 200 perm ≈ 2-3 min. Risultati scientifici usano n_perm≥200.",
    )
    n_boot = st.select_slider("Bootstrap resample CI", [100, 200, 500, 1000], value=200)

    run_btn = st.button("▶ Esegui ML", type="primary", use_container_width=True)

# ---------------------------------------------------------------------------
# Carica risultati finali N=179 (FASE 3)
# ---------------------------------------------------------------------------
st.markdown("---")

_is_sex = target.startswith("Sesso")
_is_age = target.startswith("Età")
_is_eceo = target.startswith("EO")

if _is_eceo:
    st.info(
        "**Positive-control (effetto Berger)**: EO vs EC è il **positive-control** della pipeline. "
        "BA≈0.92 è attesa — l'effetto Berger è noto dal 1929. "
        "I target scientifici sono **sesso** e **età**."
    )

# Mostra risultati FINALI N=179 (FASE 3) — coerenti col manoscritto
precomp_col, run_col = st.columns([1, 2])


def _ci(d: dict, key: str) -> str:
    """Formatta CI95 [lo, hi] in modo robusto."""
    ci = d.get(key) or [float("nan"), float("nan")]
    return f"[{ci[0]:.3f}, {ci[1]:.3f}]"


with precomp_col:
    import pandas as pd

    n179 = load_ml_n179()
    if (_is_sex or _is_age) and n179:
        st.subheader("Risultati N=179 (finali — FASE 3)")
        st.caption(
            f"N={n179.get('n_subjects', 179)} soggetti · feat: {n179.get('feat_name', '?')} · "
            "GroupKFold subject-level · permutation n=1000 · FDR-BH"
        )
        p_fdr = n179.get("fdr", {}).get("p_fdr", {})
        if _is_sex:
            base, gt = n179.get("sex_baseline", {}), n179.get("sex_gt", {})
            rows = [
                {
                    "Modello": "Baseline 2278-dim (logreg)",
                    "BA": f"{base.get('ba_mean', 0):.3f}",
                    "CI 95%": _ci(base, "ba_ci95"),
                    "p_fdr": format_pvalue(p_fdr.get("sex_baseline", 1.0), 1000),
                },
                {
                    "Modello": "Graph-theory 8-dim",
                    "BA": f"{gt.get('ba_mean', 0):.3f}",
                    "CI 95%": _ci(gt, "ba_ci95"),
                    "p_fdr": format_pvalue(p_fdr.get("sex_gt", 1.0), 1000),
                },
            ]
        else:
            base, gt = n179.get("age_baseline", {}), n179.get("age_gt", {})
            rows = [
                {
                    "Modello": "Baseline 2278-dim (RF)",
                    "MAE": f"{base.get('mae', 0):.2f}",
                    "R²": f"{base.get('r2', 0):.3f}",
                    "p_fdr": format_pvalue(p_fdr.get("age_baseline", 1.0), 1000),
                },
                {
                    "Modello": "Graph-theory 8-dim",
                    "MAE": f"{gt.get('mae', 0):.2f}",
                    "R²": f"{gt.get('r2', 0):.3f}",
                    "p_fdr": format_pvalue(p_fdr.get("age_gt", 1.0), 1000),
                },
            ]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        # Progressione trasparente N=100 → N=179 (replica + estensione)
        cmp = n179.get("comparison_n100", {})
        if cmp and _is_sex:
            st.caption(
                f"Replica N=100→N=179: BA {cmp.get('sex_ba_n100', '?')} → "
                f"{base.get('ba_mean', 0):.3f} (Δ +{base.get('ba_mean', 0) - cmp.get('sex_ba_n100', 0):.3f})"
            )
        elif cmp and _is_age:
            st.caption(
                f"Replica N=100→N=179: MAE {cmp.get('age_mae_n100', '?')} → "
                f"{base.get('mae', 0):.2f} anni · R² {cmp.get('age_r2_n100', '?')} → {base.get('r2', 0):.3f}"
            )
    elif _is_eceo:
        st.subheader("Positive-control N=50")
        st.markdown(
            "**N=50 winner** (aparc×plv×θ×logreg):\n\n"
            "BA=**0.920** · CI=[0.870, 0.970] · p_perm<0.001\n\n"
            "_Effetto Berger (noto dal 1929): valida la pipeline end-to-end, non è un biomarker._"
        )
    else:
        st.info("Risultati N=179 non disponibili")

# ---------------------------------------------------------------------------
# Run interattivo
# ---------------------------------------------------------------------------
with run_col:
    if run_btn:
        combo_check = any(
            c["atlas"] == atlas and c["metric"] == metric and c["band"] == band for c in combos
        )
        if not combo_check:
            st.error(f"Feature file non trovato: X_{atlas}_{metric}_{band}.npz")
        else:
            with st.spinner(f"Carico feature {atlas}×{metric}×{band}..."):
                X, y_eceo, groups, roi_names = load_feature_matrix(atlas, metric, band)

            if _is_sex or _is_age:
                # Carica y sesso o età allineato ai soggetti nel metadata
                from dashboard.components.data_loader import load_metadata

                meta = load_metadata()
                subjects_list = meta.get("subjects", [])
                # y dal file phenotype
                try:
                    from config.labels_phenotype import load_phenotype  # noqa: E402,PLC0415

                    # TSV risolto repo-relativo dentro labels_phenotype (F0): default corretto.
                    y_age_all, y_sex_all = load_phenotype(subjects_list)
                    # Ogni soggetto ha 2 campioni (EO + EC) → ripeti
                    y_age = np.repeat(y_age_all, 2)
                    y_sex = np.repeat(y_sex_all, 2)
                    if X.shape[0] != y_age.shape[0]:
                        n = X.shape[0]
                        y_age = y_age[:n]
                        y_sex = y_sex[:n]
                    y_target = y_sex if _is_sex else y_age
                except Exception as exc:
                    st.error(f"Errore caricamento fenotipi: {exc}")
                    st.stop()
            else:
                y_target = y_eceo

            with st.spinner(f"Running {clf_name} · {atlas}×{metric}×{band} · perm={n_perm}..."):
                if _is_age:
                    result = run_regression(
                        X, y_target, groups, reg_name=clf_name, n_perm=n_perm, n_boot=n_boot
                    )
                else:
                    result = run_classification(
                        X, y_target, groups, clf_name=clf_name, n_perm=n_perm, n_boot=n_boot
                    )

            st.success(f"[OK] Done in {result['wall_clock_s']:.1f}s")

            # Metriche principali
            st.markdown("---")
            if _is_age:
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("MAE", f"{result['mae']:.2f} anni")
                c2.metric("CI 95%", f"[{result['ci_mae_lo']:.2f}, {result['ci_mae_hi']:.2f}]")
                c3.metric("R²", f"{result['r2']:.3f}")
                c4.metric(
                    "p_perm",
                    format_pvalue(result["p_perm"], result["n_perm"])
                    if result["p_perm"] is not None
                    else "skip",
                )
            else:
                c1, c2, c3, c4, c5 = st.columns(5)
                c1.metric("BA", f"{result['ba']:.3f}")
                c2.metric("CI 95%", f"[{result['ci_lo']:.3f}, {result['ci_hi']:.3f}]")
                c3.metric("AUC", f"{result['roc_auc']:.3f}")
                c4.metric(
                    "p_perm",
                    format_pvalue(result["p_perm"], result["n_perm"])
                    if result["p_perm"] is not None
                    else "skip",
                )
                c5.metric("N soggetti", result["n_subjects"])

            # Plot sub-tabs
            if _is_age:
                tab_scatter, tab_perm = st.tabs(["Scatter pred vs reale", "Permutation Null"])

                with tab_scatter:
                    y_t = np.array(result["y_true"])
                    y_p = np.array(result["y_pred"])
                    fig_sc = go.Figure()
                    fig_sc.add_trace(go.Scatter(x=y_t, y=y_p, mode="markers", marker={"size": 5}))
                    rng_ = [min(y_t.min(), y_p.min()), max(y_t.max(), y_p.max())]
                    fig_sc.add_trace(
                        go.Scatter(
                            x=rng_, y=rng_, mode="lines", line={"dash": "dash", "color": "red"}
                        )
                    )
                    fig_sc.update_layout(
                        xaxis_title="Età reale (anni)",
                        yaxis_title="Età predetta (anni)",
                        title=f"MAE={result['mae']:.2f} · R²={result['r2']:.3f}",
                        height=400,
                    )
                    st.plotly_chart(fig_sc, use_container_width=True)

                with tab_perm:
                    if result["p_perm"] is not None:
                        st.info(
                            f"Permutation test (n_perm={result['n_perm']}): p={result['p_perm']:.4f}"
                        )
                    else:
                        st.info(
                            "Permutation test non eseguito (n_perm=0). Aumenta n_perm per stimare p-value."
                        )
            else:
                tab_cm, tab_roc, tab_folds, tab_perm = st.tabs(
                    ["Confusion Matrix", "ROC Curve", "Per-Fold BA", "Permutation Null"]
                )

                with tab_cm:
                    conf = np.array(result["confusion"])
                    if conf.shape == (2, 2):
                        from dashboard.utils.plots import plot_confusion_matrix

                        fig_cm = plot_confusion_matrix(conf.tolist())
                        st.plotly_chart(fig_cm, use_container_width=False)

                with tab_roc:
                    fpr = result["roc_fpr"]
                    tpr = result["roc_tpr"]
                    auc_v = result["roc_auc"]
                    if fpr:
                        from dashboard.utils.plots import plot_roc_curve

                        fig_roc = plot_roc_curve(fpr, tpr, auc_v)
                        st.plotly_chart(fig_roc, use_container_width=False)

                with tab_folds:
                    ba_folds = result["ba_per_fold"]
                    if ba_folds:
                        from dashboard.utils.plots import plot_learning_curve

                        fig_lc = plot_learning_curve(ba_folds)
                        st.plotly_chart(fig_lc, use_container_width=False)

                with tab_perm:
                    null_dist = result.get("null_distribution", [])
                    if null_dist:
                        from dashboard.utils.plots import plot_permutation_null

                        fig_perm = plot_permutation_null(
                            null_dist, result["ba"], p_perm=result["p_perm"], n_perm=len(null_dist)
                        )
                        st.plotly_chart(fig_perm, use_container_width=False)
                    else:
                        st.info(
                            "Permutation test non eseguito (n_perm=0). "
                            "Aumenta n_perm nella sidebar per stimare p-value empirico."
                        )
    else:
        st.info(
            " Seleziona combo e premi **Esegui ML** per il run interattivo.\n\n"
            "I risultati finali N=179 sono mostrati nella colonna sinistra."
        )

# ---------------------------------------------------------------------------
# Note metodologiche
# ---------------------------------------------------------------------------
st.markdown("---")
with st.expander("Note metodologiche", expanded=False):
    st.markdown(
        """
**GroupKFold subject-level**
Ogni fold esclude tutti i campioni (EO+EC) di un soggetto dal test set.
Elimina il subject leakage (+25 pp se si usa k-fold naïve, Gemein et al. 2023).

**Bootstrap CI (percentile)**
n_boot resample con rimpiazzo su ba_per_fold. La dashboard interattiva usa
n_boot=200 per velocità; risultati scientifici ufficiali usano n_boot=10000 (BCa).

**Permutation test**
Permuta le etichette y mantenendo la struttura GroupKFold.
p_perm = #{null ≥ obs} / (N_perm+1). Risoluzione minima: 1/(n_perm+1).
Con n_perm=200, risoluzione p=0.005.

**Etichetta onesta**
EO vs EC = **Berger effect (positive-control)** — effetto atteso dal 1929,
usato per validare la pipeline end-to-end, non come risultato scientifico.
I target scientifici principali sono età e sesso.

**FDR-BH**
Per confronto multi-algoritmo, correggi p-value con Benjamini-Hochberg
(statsmodels `multipletests` con method='fdr_bh').
        """
    )

st.caption("ds004504 (LEMON) → **Tab 6 Cross-Dataset** · BA_sex=0.500 domain shift sano→clinico")
