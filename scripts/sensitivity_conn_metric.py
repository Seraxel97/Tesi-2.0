"""ALTO-3 (Fable) — Sensitivity della classificazione sesso alla metrica di connettività.

Il winner è **PLV** (phase-locking value), che è SENSIBILE al volume conduction: due ROI
possono apparire connesse solo perché la stessa sorgente si proietta su entrambe a lag-zero
(connettività spuria, non fisiologica). Un revisore chiede sempre: il segnale del sesso
sopravvive con metriche ROBUSTE al volume conduction?

- **imcoh** (imaginary part of coherency) e **wPLI** (weighted phase-lag index) IGNORANO per
  costruzione le interazioni a lag-zero → immuni al volume conduction.
- Se BA_sesso resta alta anche con imcoh/wPLI → il segnale NON è un artefatto di conduzione.
- Se crolla verso 0.5 → il winner-PLV rifletteva in parte conduzione spuria (limitazione).

Stesso identico classificatore/CV/permutation di run_ml_age_sex_n179 (LogReg-L2 + GroupKFold
5/3 + permutation subject-level + bootstrap-cluster). Stessa banda (theta) e atlante (aparc):
si cambia SOLO la metrica di connettività. Feature già calcolate in data/features/ds005385/.

Uso: python scripts/sensitivity_conn_metric.py [--n-perm 1000] [--n-boot 1000]
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.run_ml_age_sex_n179 import _load_data, run_ml_sex  # noqa: E402

_REPO = Path(__file__).resolve().parents[1]
# winner (riferimento, sensibile a volume-conduction) + 2 metriche robuste, stessa banda/atlante
METRICS = {
    "plv": "X_aparc_plv_theta",       # winner, riferimento
    "wpli": "X_aparc_wpli_theta",     # robusto a volume conduction
    "imcoh": "X_aparc_imcoh_theta",   # robusto a volume conduction
}
ROBUST = ("wpli", "imcoh")
OUT = _REPO / "data" / "results" / "ds005385" / "sensitivity_conn_metric.json"
REPORT = _REPO / "reports" / "SENSITIVITY_CONN_METRIC_F3.md"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-perm", type=int, default=1000)
    ap.add_argument("--n-boot", type=int, default=1000)
    args = ap.parse_args()

    np.random.seed(42)
    results: dict[str, dict] = {}
    for key, feat in METRICS.items():
        print(f"[F3-ALTO3] {key} ({feat}) — CV sesso "
              f"(n_perm={args.n_perm}, n_boot={args.n_boot})…")
        X, _y_age, y_sex, groups, _ = _load_data(feat)
        res = run_ml_sex(X, y_sex, groups, n_perm=args.n_perm, n_boot=args.n_boot)
        results[key] = {"feature": feat, **res}
        ci = res["ba_ci95"]
        print(f"           BA={res['ba_mean']:.3f} CI95[{ci[0]:.3f},{ci[1]:.3f}] "
              f"p_perm={res['p_perm']:.4f}")

    plv_ba = results["plv"]["ba_mean"]
    robust_mean_ba = float(np.mean([results[k]["ba_mean"] for k in ROBUST]))
    robust_significant = all(
        results[k]["ba_ci95"][0] > 0.5 and results[k]["p_perm"] < 0.05 for k in ROBUST
    )
    # crollo relativo dell'effetto rispetto al caso (0.5): quanto del "sopra-il-caso" PLV resta
    plv_effect = plv_ba - 0.5
    robust_effect = robust_mean_ba - 0.5
    retained_frac = robust_effect / plv_effect if plv_effect > 0 else 0.0
    big_drop = retained_frac < 0.5  # metà o più dell'effetto sopra-il-caso perso

    if robust_significant and not big_drop:
        verdict = ("SEGNALE DEL SESSO NON È VOLUME-CONDUCTION: sopravvive con metriche robuste "
                   "(wPLI + imcoh), CI95 sopra il caso, p significativo, effetto in gran parte "
                   "conservato")
    elif robust_significant and big_drop:
        verdict = (f"SEGNALE PARZIALMENTE REALE MA PLV GONFIATO DA VOLUME-CONDUCTION: con wPLI/"
                   f"imcoh il sesso resta decodificabile sopra il caso (BA≈{robust_mean_ba:.2f}, "
                   f"p<0.05) ma l'effetto sopra-il-caso crolla da {plv_effect:.3f} (PLV) a "
                   f"{robust_effect:.3f} (solo il {retained_frac*100:.0f}% conservato) → il "
                   f"BA-headline PLV 0.795 è sostanzialmente inflazionato dalla conduzione "
                   f"spuria a lag-zero. Limitazione da dichiarare in evidenza")
    else:
        verdict = ("ATTENZIONE: con metriche robuste al volume-conduction il segnale NON è "
                   "significativo → il winner-PLV riflette in larga parte conduzione spuria")

    out = {
        "band": "theta", "atlas": "aparc",
        "rationale": "PLV sensibile a volume-conduction; wPLI/imcoh robuste (ignorano lag-zero)",
        "results": results,
        "robust_significant": robust_significant,
        "plv_ba": plv_ba,
        "robust_mean_ba": robust_mean_ba,
        "effect_retained_frac": retained_frac,
        "verdict": verdict,
        "timestamp": datetime.now(UTC).isoformat(timespec="seconds"),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=2))

    lines = [
        "# ALTO-3 — Sensitivity classificazione sesso alla metrica di connettività\n",
        "Stessa banda (**theta**) e atlante (**aparc**), stesso classificatore/CV/permutation. "
        "Cambia SOLO la metrica. PLV = winner (sensibile a volume-conduction); "
        "wPLI/imcoh = robuste (ignorano interazioni a lag-zero).\n",
        "| Metrica | Volume-conduction | BA sesso | CI95 | p_perm |",
        "|---|---|---|---|---|",
    ]
    for key in ("plv", "wpli", "imcoh"):
        r = results[key]
        ci = r["ba_ci95"]
        vc = "sensibile" if key == "plv" else "robusta"
        lines.append(f"| {key} | {vc} | **{r['ba_mean']:.3f}** | "
                     f"{ci[0]:.3f}–{ci[1]:.3f} | {r['p_perm']:.4f} |")
    lines += [
        f"\nPLV (winner) BA = {plv_ba:.3f} · robuste (media wPLI/imcoh) BA = {robust_mean_ba:.3f}.",
        f"Effetto sopra-il-caso conservato con metriche robuste: **{retained_frac*100:.0f}%** "
        f"(PLV {plv_effect:.3f} → robuste {robust_effect:.3f}).\n",
        f"## Verdetto\n**{verdict}.**",
        "\n> Se wPLI e imcoh restano ben sopra 0.5 con CI95 che non tocca il caso e p "
        "significativo, la classificazione del sesso riflette connettività fisiologica reale, "
        "non un artefatto di volume conduction del PLV.",
    ]
    REPORT.write_text("\n".join(lines) + "\n")
    print(f"\n[F3-ALTO3] {verdict}")
    print(f"[F3-ALTO3] Scritti: {OUT.name}, {REPORT.name}")


if __name__ == "__main__":
    main()
