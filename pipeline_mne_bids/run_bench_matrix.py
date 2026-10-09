"""Benchmark matrix (700 run: 7 FC x 4 atlas x 5 ML x 5 bande) — shim di compatibilita'.

L'implementazione vive nel package :mod:`pipeline_mne_bids.bench`
(``matrix.py``, ``reporter.py``, ``cli.py``). Questo modulo mantiene
l'entry point ``python -m pipeline_mne_bids.run_bench_matrix`` e i simboli
pubblici storici.

Uso:
  python -m pipeline_mne_bids.run_bench_matrix --subject sub-05 \\
      --deriv data/derivatives/mne-bids-pipeline --sfreq-target 500 --n-epochs-max 0
"""

from __future__ import annotations

from pipeline_mne_bids.bench.cli import main
from pipeline_mne_bids.bench.matrix import (
    ALGORITHMS,
    ATLASES,
    BANDS,
    METRICS,
    run_bench,
)
from pipeline_mne_bids.bench.reporter import dump_json as _dump_json
from pipeline_mne_bids.bench.reporter import write_summary as _write_summary

__all__ = [
    "ALGORITHMS",
    "ATLASES",
    "BANDS",
    "METRICS",
    "_dump_json",
    "_write_summary",
    "main",
    "run_bench",
]

if __name__ == "__main__":
    main()
