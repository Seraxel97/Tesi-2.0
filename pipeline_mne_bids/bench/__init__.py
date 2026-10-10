"""Bench subpackage — benchmark matrix 7×4×5×5 = 700 run.

Posizione nella pipeline: orchestrazione degli STEP 1-7 (E2E e benchmark).
"""

from pipeline_mne_bids.bench.matrix import (
    ALGORITHMS,
    ATLASES,
    BANDS,
    METRICS,
    run_bench,
)

__all__ = ["run_bench", "ATLASES", "METRICS", "ALGORITHMS", "BANDS"]
