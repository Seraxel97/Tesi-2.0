"""E2E pipeline matchingpennies — public API.

Posizione nella pipeline: orchestrazione degli STEP 1-7 (E2E e benchmark).
"""

from pipeline_mne_bids.run_e2e.exec import run_e2e

__all__ = ["run_e2e"]
