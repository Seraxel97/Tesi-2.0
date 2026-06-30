"""Test della logica di split del transferability check (F2). Deterministico, niente fit."""
from __future__ import annotations

import numpy as np

from scripts.transferability_n79 import _mask, split_indices


def test_split_sizes_and_disjoint():
    n179 = [f"sub-{i:03d}" for i in range(1, 180)]   # 179 fittizi
    n100 = set(n179[:100])
    train, test = split_indices(n179, n100)
    assert len(train) == 100
    assert len(test) == 79
    assert set(train).isdisjoint(test), "train e test non devono sovrapporsi"
    assert sorted(train + test) == list(range(179)), "coprono tutti i 179"


def test_test_is_exactly_new_subjects():
    n179 = [f"sub-{i:03d}" for i in range(1, 180)]
    n100 = set(n179[:100])
    _, test = split_indices(n179, n100)
    test_ids = {n179[i] for i in test}
    assert test_ids == set(n179) - n100, "i test sono ESATTAMENTE i nuovi (N179 ∖ N100)"


def test_mask_selects_right_samples():
    groups = np.repeat(np.arange(4), 2)   # 8 sample, 4 soggetti × 2
    m = _mask(groups, [1, 3])
    assert m.tolist() == [False, False, True, True, False, False, True, True]


def test_split_handles_unsorted_n100():
    """N100 come set non ordinato: lo split resta corretto e indicizzato su N179."""
    n179 = [f"sub-{i:03d}" for i in range(1, 180)]
    n100 = set(n179[50:150])   # 100 soggetti centrali
    train, test = split_indices(n179, n100)
    assert len(train) == 100 and len(test) == 79
    assert {n179[i] for i in train} == n100
