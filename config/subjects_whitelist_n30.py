"""Subjects whitelist N=30 ds005385 — estensione di N=15 (seed=42, hard-rule N=15 ⊂ N=30).

Sprint: H-SCALE-01 (sonnet1-tesi, 2026-05-07)
Policy: random_seed_42_N15_subset_N30
Pool: 179 validi (200 totali - 21 late_ses1 > 0)
Criterio: N=15 (whitelist esistente) + 15 nuovi da random.sample(extra_pool_164, 15) con seed=42

Vincolo operatore (hard-rule): N=15 ⊂ N=30 — tutti i sub attuali inclusi, intra-cohort riproducibile.
Derivazione: extra_pool = sorted(valid_179 - N15); rng=random.Random(42); new_15=sorted(rng.sample(extra_pool, 15))
"""

from __future__ import annotations

from config.subjects_whitelist import SUBJECT_WHITELIST as _N15

# Etichetta della politica di campionamento (provenienza della lista)
SUBSET_POLICY = "random_seed_42_N15_subset_N30"
# Numero di soggetti nella whitelist
N_SUBJECTS = 30
# Seed del generatore casuale usato per estrarre i soggetti
RANDOM_SEED = 42

# Soggetti aggiunti rispetto alla lista N=15
_NEW_15: list[str] = [
    "sub-012",
    "sub-014",
    "sub-015",
    "sub-032",
    "sub-034",
    "sub-038",
    "sub-040",
    "sub-048",
    "sub-076",
    "sub-082",
    "sub-091",
    "sub-136",
    "sub-171",
    "sub-187",
    "sub-200",
]

# Lista finale N=30 = N15 unito ai nuovi, ordinata
SUBJECT_WHITELIST_N30: list[str] = sorted(set(_N15) | set(_NEW_15))

assert len(SUBJECT_WHITELIST_N30) == 30, f"expected 30, got {len(SUBJECT_WHITELIST_N30)}"
assert set(_N15).issubset(set(SUBJECT_WHITELIST_N30)), "hard-rule violated: N15 ⊄ N30"

# Sessione BIDS usata di default (prima sessione)
DEFAULT_SESSION = "ses-1"
# Acquisizione di default: registrazione pre-compito
DEFAULT_ACQ = "acq-pre"
# Soggetti validi nel pool (late_ses1 == 0)
POOL_SIZE = 179
# Soggetti esclusi (late_ses1 > 0)
POOL_EXCLUDED = 21
# Soggetti totali del dataset ds005385
POOL_TOTAL = 200
# Impronta di controllo della lista ordinata (rileva modifiche accidentali)
N30_HASH = "1594bf5d4914a864"  # sha256(sorted N30 joined by comma)[:16]
