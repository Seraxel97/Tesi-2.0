"""Test degli helper di permutation testing (F0 fix).

Verificano le due correzioni:
  1. `_permute_labels` è DESIGN-AWARE (between-subject vs within-subject) e mai sample-level se groups.
  2. `_empirical_pvalue` usa la correzione di continuità +1/+1 (mai p=0).
I test toccano SOLO gli helper puri → niente CV pesante, deterministici.
"""
from __future__ import annotations

import numpy as np

from ml_training.permutation import _empirical_pvalue, _permute_labels


def test_empirical_pvalue_never_zero():
    """Con tutte le null sotto l'osservato, p = 1/(n+1), non 0."""
    null = np.zeros(99)          # tutte 0
    p = _empirical_pvalue(null, observed_ba=0.9)
    assert p == 1 / 100
    assert p > 0


def test_empirical_pvalue_all_above():
    """Con tutte le null >= osservato, p = (n+1)/(n+1) = 1."""
    null = np.ones(49)
    assert _empirical_pvalue(null, observed_ba=0.5) == 1.0


def test_empirical_pvalue_formula():
    """p = (#{null>=obs} + 1)/(n+1)."""
    null = np.array([0.4, 0.6, 0.8, 0.5, 0.9])  # 3 valori >= 0.6
    assert _empirical_pvalue(null, 0.6) == (3 + 1) / (5 + 1)


def test_permute_between_subject_constant_within():
    """Disegno between-subject (label costante per soggetto, es. sesso): la permutazione
    mantiene la label COSTANTE entro ogni soggetto (permuta tra soggetti)."""
    groups = np.array([0, 0, 1, 1, 2, 2, 3, 3])
    y = np.array([0, 0, 1, 1, 0, 0, 1, 1])      # ogni soggetto ha una sola label
    rng = np.random.default_rng(0)
    yp = _permute_labels(y, groups, rng)
    for g in np.unique(groups):
        assert len(np.unique(yp[groups == g])) == 1, "label deve restare costante entro soggetto"
    # l'insieme delle label-per-soggetto è preservato (è una permutazione)
    subj_before = sorted(y[groups == g][0] for g in np.unique(groups))
    subj_after = sorted(yp[groups == g][0] for g in np.unique(groups))
    assert subj_before == subj_after


def test_permute_within_subject_paired():
    """Disegno within-subject (label varia entro soggetto, es. EO/EC): la permutazione
    avviene ENTRO ogni soggetto → ogni soggetto conserva il suo multiset di label."""
    groups = np.array([0, 0, 1, 1, 2, 2])
    y = np.array([0, 1, 0, 1, 0, 1])            # ogni soggetto ha entrambe le condizioni
    rng = np.random.default_rng(1)
    yp = _permute_labels(y, groups, rng)
    for g in np.unique(groups):
        assert sorted(yp[groups == g]) == sorted(y[groups == g]), \
            "il multiset di label per soggetto deve essere preservato (permutazione paired)"


def test_permute_groups_none_is_sample_shuffle():
    y = np.array([0, 1, 2, 3, 4])
    rng = np.random.default_rng(2)
    yp = _permute_labels(y, None, rng)
    assert sorted(yp.tolist()) == sorted(y.tolist())   # stessa composizione, riordino


def test_permute_deterministic_with_seed():
    groups = np.array([0, 0, 1, 1, 2, 2])
    y = np.array([0, 0, 1, 1, 0, 0])
    a = _permute_labels(y, groups, np.random.default_rng(42))
    b = _permute_labels(y, groups, np.random.default_rng(42))
    assert np.array_equal(a, b)
