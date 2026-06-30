"""Test del confound check età↔sesso (F3). Deterministico, su dati sintetici."""
from __future__ import annotations

import numpy as np

from scripts.confound_age_sex import age_sex_confound


def test_no_confound_when_age_identical():
    """Stessa distribuzione d'età nei due sessi → p alto, no confound."""
    rng = np.random.default_rng(0)
    age = rng.normal(45, 10, 200)
    sex = np.array([0, 1] * 100)        # alternati, indipendenti dall'età
    res = age_sex_confound(age, sex)
    assert res["age_differs_by_sex"] is False
    assert res["p_value"] > 0.05


def test_confound_detected_when_age_shifted():
    """Età nettamente diversa tra i sessi → p basso, confound rilevato."""
    age = np.concatenate([np.full(100, 30.0), np.full(100, 60.0)])
    sex = np.concatenate([np.zeros(100, int), np.ones(100, int)])  # F giovani, M anziani
    res = age_sex_confound(age, sex)
    assert res["age_differs_by_sex"] is True
    assert res["p_value"] < 0.05


def test_counts_and_keys():
    age = np.array([20.0, 30, 40, 50])
    sex = np.array([0, 0, 1, 1])
    res = age_sex_confound(age, sex)
    assert res["n_F"] == 2 and res["n_M"] == 2
    assert "mannwhitney_U" in res and "age_F_median" in res
