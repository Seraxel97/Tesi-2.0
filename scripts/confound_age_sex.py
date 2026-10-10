"""F3 — Confound check età↔sesso (N=179).

Un revisore lo chiede sempre: se la distribuzione d'ETÀ differisce tra M e F nel campione,
la classificazione del SESSO potrebbe riflettere un pattern età-correlato invece del segnale
biologico del sesso. Questo script verifica esplicitamente se età e sesso sono confusi nel
campione N=179 (Mann-Whitney U sulla distribuzione d'età tra i due sessi) + bilanciamento classi.

Solo phenotype (niente ML, niente feature) → leggero e deterministico.

Input:  participants.tsv di ds005385 (colonne età/sesso) via ``config.labels_phenotype``,
        soggetti da ``config.subjects_whitelist_n179``.
Output: data/results/ds005385/confound_age_sex.json (+ verdetto su stdout).
Uso: python scripts/confound_age_sex.py
"""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
from scipy.stats import mannwhitneyu

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config.labels_phenotype import load_phenotype  # noqa: E402
from config.subjects_whitelist_n179 import SUBJECT_WHITELIST_N179 as N179  # noqa: E402

# ===== 1. Configurazione =====
_REPO = Path(__file__).resolve().parents[1]  # radice del repo
# codice numerico del sesso -> etichetta (inverso di SEX_MAP in config)
SEX_MAP = {0: "F", 1: "M"}


# ===== 2. Test statistico =====
def age_sex_confound(age: np.ndarray, sex: np.ndarray) -> dict:
    """Mann-Whitney U sull'età tra i due sessi + statistiche descrittive per gruppo.

    p alto (>0.05) → nessuna differenza d'età significativa tra i sessi → confound improbabile.

    Args:
        age: età in anni per soggetto, shape (n,).
        sex: sesso per soggetto, shape (n,); 0 = F, 1 = M.

    Returns:
        Dict con numerosità, mediane e medie d'età per sesso, statistica U,
        p-value (bilaterale) e flag ``age_differs_by_sex`` (p < 0.05).
        Nessun side effect.
    """
    age = np.asarray(age, dtype=float)
    sex = np.asarray(sex)
    age_f = age[sex == 0]
    age_m = age[sex == 1]
    u, p = mannwhitneyu(age_f, age_m, alternative="two-sided")
    return {
        "n_F": int(len(age_f)),
        "n_M": int(len(age_m)),
        "age_F_median": float(np.median(age_f)),
        "age_M_median": float(np.median(age_m)),
        "age_F_mean": float(np.mean(age_f)),
        "age_M_mean": float(np.mean(age_m)),
        "mannwhitney_U": float(u),
        "p_value": float(p),
        "age_differs_by_sex": bool(p < 0.05),
    }


# ===== 3. Esecuzione =====
def main() -> None:
    """Carica il fenotipo N=179, esegue il test e salva il JSON dei risultati.

    Side effects:
        Scrive ``data/results/ds005385/confound_age_sex.json`` e stampa il verdetto.
    """
    age_per_sub, sex_per_sub = load_phenotype(N179)
    res = age_sex_confound(age_per_sub, sex_per_sub)
    res["timestamp"] = datetime.now(UTC).isoformat(timespec="seconds")
    res["n_total"] = len(N179)
    res["class_balance"] = f"{res['n_F']}F / {res['n_M']}M"

    out = _REPO / "data" / "results" / "ds005385" / "confound_age_sex.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, indent=2))
    print(json.dumps(res, indent=2))
    verdict = (
        "ETÀ DIFFERISCE per sesso → POSSIBILE confound, da controllare"
        if res["age_differs_by_sex"]
        else "nessuna differenza d'età significativa tra i sessi → confound età IMPROBABILE"
    )
    print(f"\n[F3] {verdict} (Mann-Whitney p={res['p_value']:.4f})")


if __name__ == "__main__":
    main()
