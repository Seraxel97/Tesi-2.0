"""Subjects whitelist ds005385 — operator HARD constraint N max=20.

Sprint: S-100b (sonnet2-ts, 2026-05-01)
Policy: random_seed_42_N15
Pool: 179 validi (200 totali - 21 late_ses1 > 0)
Criterio: random.sample(pool, 15) con seed=42 (riproducibile)

Vincolo operatore: max N=10-20 sub. NO 200-full run.
"""

from __future__ import annotations

# Etichetta della politica di campionamento (provenienza della lista)
SUBSET_POLICY = "random_seed_42_N15"
# Numero di soggetti nella whitelist
N_SUBJECTS = 15
# Seed del generatore casuale usato per estrarre i soggetti
RANDOM_SEED = 42

# Soggetti selezionati: random.sample(pool, 15) con seed fissato
SUBJECT_WHITELIST: list[str] = [
    "sub-007",
    "sub-010",
    "sub-011",
    "sub-026",
    "sub-031",
    "sub-033",
    "sub-041",
    "sub-066",
    "sub-071",
    "sub-080",
    "sub-125",
    "sub-157",
    "sub-169",
    "sub-185",
    "sub-195",
]

# Sessione e acquisizione di default (acq-pre = baseline, massima copertura)
# Sessione BIDS usata di default (prima sessione)
DEFAULT_SESSION = "ses-1"
# Acquisizione di default: registrazione pre-compito
DEFAULT_ACQ = "acq-pre"

# Pool di riferimento per riproducibilita'
POOL_SIZE = 179  # soggetti validi (no late_ses1)
POOL_EXCLUDED = 21  # sub con late_ses1 > 0 (vedi config/labels_ds005385.py)
POOL_TOTAL = 200  # soggetti presenti su disco
