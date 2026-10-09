"""F3-bis — Neutralizzazione del confound età↔sesso via age-matching (N=179).

`confound_age_sex.py` ha RILEVATO il confound: l'età differisce per sesso (Mann-Whitney
p=0.0061, M mediana 50 vs F 42.5). Un revisore chiede: la classificazione del sesso
(BA≈0.795 in CV su X_aparc_plv_theta) sfrutta in parte pattern ETÀ-correlati?

Questo script lo NEUTRALIZZA e ri-stima:
  1. accoppia 1:1 ogni maschio con una femmina di età più vicina possibile (assignment
     ottimale globale = Hungarian su |age_M − age_F|), senza rimpiazzo → sottoinsieme
     age-matched (67M + 67F = 134 soggetti) in cui l'età NON differisce più per sesso;
  2. verifica che il confound sia sparito (Mann-Whitney sull'età nel subset → p atteso >0.05);
  3. ri-esegue ESATTAMENTE lo stesso classificatore (LogReg-L2 + GroupKFold 5/3 +
     permutation subject-level + bootstrap-cluster) sul solo subset age-matched.

Interpretazione:
  - BA_matched ancora alta e p_perm significativo → il segnale del sesso SOPRAVVIVE alla
    rimozione del confound d'età → risultato robusto (non è un artefatto dell'età).
  - BA_matched crolla verso 0.5 → parte del segnale era età-correlato → limitazione seria.

Riusa senza modifiche le interfacce di run_ml_age_sex_n179.py (stesso X, y, CV, modello).

Input:  feature X_aparc_plv_theta e fenotipo N=179 (via run_ml_age_sex_n179 e config.labels_phenotype).
Output: data/results/ds005385/confound_age_sex_rematch.json e
        reports/CONFOUND_AGE_SEX_REMATCH_F3.md.
Uso: python scripts/confound_age_sex_rematch.py [--n-perm 1000] [--n-boot 1000] [--caliper 0]
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
from scipy.optimize import linear_sum_assignment
from scipy.stats import mannwhitneyu

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config.labels_phenotype import load_phenotype  # noqa: E402
from config.subjects_whitelist_n179 import SUBJECT_WHITELIST_N179 as SUBJECTS_N179  # noqa: E402
from scripts.run_ml_age_sex_n179 import _load_data, run_ml_sex  # noqa: E402

# ===== 1. Configurazione =====
_REPO = Path(__file__).resolve().parents[1]  # radice del repo
# feature vincitrice (atlante aparc, PLV, banda theta) su cui si ri-stima il sesso
WINNER = "X_aparc_plv_theta"
# JSON dei risultati e report Markdown di output
OUT = _REPO / "data" / "results" / "ds005385" / "confound_age_sex_rematch.json"
REPORT = _REPO / "reports" / "CONFOUND_AGE_SEX_REMATCH_F3.md"


# ===== 2. Age-matching e test del confound =====
def age_match(
    age_per_sub: np.ndarray, sex_per_sub: np.ndarray, caliper: float = 0.0
) -> tuple[np.ndarray, dict]:
    """Accoppia 1:1 M↔F minimizzando la somma delle differenze d'età (assignment ottimale).

    Ritorna gli indici-soggetto (0..178) del subset age-matched + statistiche del matching.
    `caliper`>0 scarta le coppie con differenza d'età superiore alla soglia (anni).

    Args:
        age_per_sub: età in anni per soggetto, shape (n,).
        sex_per_sub: sesso per soggetto, shape (n,); 0 = F, 1 = M.
        caliper: differenza d'età massima ammessa per coppia (anni); 0 = nessun limite.

    Returns:
        ``(keep, stats)``: ``keep`` = indici ordinati dei soggetti tenuti;
        ``stats`` = dict con numero di coppie, soggetti, differenza d'età media
        e massima nelle coppie e caliper usato. Nessun side effect.
    """
    f_idx = np.where(sex_per_sub == 0)[0]
    m_idx = np.where(sex_per_sub == 1)[0]
    # cost[i, j] = |età(M_i) − età(F_j)|; assignment ottimale su matrice rettangolare
    cost = np.abs(age_per_sub[m_idx][:, None] - age_per_sub[f_idx][None, :])
    rows, cols = linear_sum_assignment(cost)  # min(len(m), len(f)) coppie
    pair_diffs = cost[rows, cols]
    if caliper > 0:
        ok = pair_diffs <= caliper
        rows, cols, pair_diffs = rows[ok], cols[ok], pair_diffs[ok]
    keep_m = m_idx[rows]
    keep_f = f_idx[cols]
    keep = np.sort(np.concatenate([keep_m, keep_f]))
    stats = {
        "n_pairs": int(len(rows)),
        "n_matched_subjects": int(len(keep)),
        "mean_age_diff_within_pair": float(np.mean(pair_diffs)),
        "max_age_diff_within_pair": float(np.max(pair_diffs)),
        "caliper_years": caliper,
    }
    return keep, stats


def _mann_whitney_age(age_sub: np.ndarray, sex_sub: np.ndarray) -> dict:
    """Mann-Whitney U (bilaterale) sull'età tra femmine e maschi.

    Args:
        age_sub: età per soggetto.
        sex_sub: sesso per soggetto (0 = F, 1 = M).

    Returns:
        Dict con numerosità, mediane, U, p-value e flag ``age_differs_by_sex``
        (p < 0.05).
    """
    age_f = age_sub[sex_sub == 0]
    age_m = age_sub[sex_sub == 1]
    u, p = mannwhitneyu(age_f, age_m, alternative="two-sided")
    return {
        "n_F": int(len(age_f)),
        "n_M": int(len(age_m)),
        "age_F_median": float(np.median(age_f)),
        "age_M_median": float(np.median(age_m)),
        "mannwhitney_U": float(u),
        "p_value": float(p),
        "age_differs_by_sex": bool(p < 0.05),
    }


# ===== 3. Esecuzione (CLI) =====
def main() -> None:
    """Esegue age-matching, ri-stima il sesso sul subset e scrive i risultati.

    Side effects:
        Scrive ``OUT`` (JSON) e ``REPORT`` (Markdown); imposta il seed globale
        numpy a 42; stampa progresso e verdetto. Argomenti CLI: ``--n-perm``,
        ``--n-boot``, ``--caliper``.
    """
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-perm", type=int, default=1000)
    ap.add_argument("--n-boot", type=int, default=1000)
    ap.add_argument(
        "--caliper",
        type=float,
        default=0.0,
        help="max differenza d'età per coppia (0 = nessun limite)",
    )
    args = ap.parse_args()

    np.random.seed(42)
    X, y_age, y_sex, groups, y_age_per_sub = _load_data(WINNER)
    _, y_sex_per_sub = load_phenotype(SUBJECTS_N179)

    # confound PRIMA (tutti i 179), per confronto
    before = _mann_whitney_age(y_age_per_sub, y_sex_per_sub)

    # age-matching → subset di indici-soggetto
    keep, match_stats = age_match(y_age_per_sub, y_sex_per_sub, caliper=args.caliper)

    # confound DOPO (subset matched): deve sparire
    after = _mann_whitney_age(y_age_per_sub[keep], y_sex_per_sub[keep])

    # maschera i sample (2 per soggetto) e RINUMERA i groups per GroupKFold
    mask = np.isin(groups, keep)
    X_m = X[mask]
    y_m = y_sex[mask]
    groups_m = np.unique(groups[mask], return_inverse=True)[1]

    print(
        f"[F3-bis] Subset age-matched: {match_stats['n_pairs']} coppie "
        f"({match_stats['n_matched_subjects']} soggetti), "
        f"diff-età media {match_stats['mean_age_diff_within_pair']:.2f} anni"
    )
    print(
        f"[F3-bis] Confound PRIMA p={before['p_value']:.4f} → "
        f"DOPO p={after['p_value']:.4f} "
        f"({'RIMOSSO' if not after['age_differs_by_sex'] else 'ANCORA PRESENTE'})"
    )
    print(f"[F3-bis] Ri-stima sesso su subset (n_perm={args.n_perm}, n_boot={args.n_boot})…")

    sex_matched = run_ml_sex(X_m, y_m, groups_m, n_perm=args.n_perm, n_boot=args.n_boot)

    res = {
        "feature": WINNER,
        "method": "1:1 optimal age-matching (Hungarian su |age_M-age_F|), poi LogReg-L2 "
        "GroupKFold 5/3 + permutation subject-level + bootstrap-cluster",
        "confound_before": before,
        "confound_after_matching": after,
        "matching": match_stats,
        "sex_matched": sex_matched,
        "timestamp": datetime.now(UTC).isoformat(timespec="seconds"),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(res, indent=2))

    ba = sex_matched["ba_mean"]
    ci = sex_matched["ba_ci95"]
    p = sex_matched["p_perm"]
    survives = ci[0] > 0.5 and p < 0.05
    verdict = (
        "SEGNALE DEL SESSO ROBUSTO: sopravvive alla rimozione del confound d'età"
        if survives
        else "ATTENZIONE: dopo age-matching il segnale si indebolisce → confound d'età rilevante"
    )
    lines = [
        "# F3-bis — Neutralizzazione confound età↔sesso (age-matching)\n",
        f"Feature winner: **{WINNER}**  ·  N matched: **{match_stats['n_matched_subjects']}** "
        f"({match_stats['n_pairs']} coppie M↔F)\n",
        "## Confound d'età",
        f"- PRIMA (N=179): Mann-Whitney p = **{before['p_value']:.4f}** "
        f"(M mediana {before['age_M_median']:.1f} vs F {before['age_F_median']:.1f}) → differisce",
        f"- DOPO (age-matched): p = **{after['p_value']:.4f}** → "
        f"{'confound RIMOSSO' if not after['age_differs_by_sex'] else 'ancora presente'} "
        f"(diff-età media entro-coppia {match_stats['mean_age_diff_within_pair']:.2f} anni)\n",
        "## Classificazione sesso sul subset age-matched",
        f"- Balanced accuracy = **{ba:.3f}**  (CI95 {ci[0]:.3f}–{ci[1]:.3f})",
        f"- p permutation = **{p:.4f}**  ·  null-BA media {sex_matched['null_ba_mean']:.3f}\n",
        f"## Verdetto\n**{verdict}.**",
        "\n> Confronto: BA in CV piena N=179 = 0.795. Se BA_matched resta ben sopra 0.5 con "
        "CI95 che non tocca il caso e p significativo, la classificazione del sesso NON è un "
        "artefatto dell'età.",
    ]
    REPORT.write_text("\n".join(lines) + "\n")
    print(f"\n[F3-bis] BA_matched={ba:.3f} CI95[{ci[0]:.3f},{ci[1]:.3f}] p_perm={p:.4f}")
    print(f"[F3-bis] {verdict}")
    print(f"[F3-bis] Scritti: {OUT.name}, {REPORT.name}")


if __name__ == "__main__":
    main()
