.PHONY: test lint format clean run-step1 run-step2 bench help

PYTHON ?= python
CONFIG_STEP1 = config/config_step1_matchingpennies.py
CONFIG_STEP2 = config/config_step2_source_matchingpennies.py
DERIV = data/derivatives/mne-bids-pipeline

help:
	@echo "Targets: test, lint, format, run-step1, run-step2, bench, clean"

test:
	pytest tests/ -v

lint:
	ruff check .
	ruff format --check .

format:
	ruff check . --fix
	ruff format .

run-step1:
	mne_bids_pipeline --config $(CONFIG_STEP1) --steps preprocessing

run-step2:
	mne_bids_pipeline --config $(CONFIG_STEP2) --steps preprocessing,sensor,source
	$(PYTHON) source_reconstruction/finalize_inverse.py --subject 05 --task matchingpennies

bench:
	$(PYTHON) pipeline_mne_bids/run_bench_matrix.py --out-json reports/BENCH_MATRIX_RESULTS.json

clean:
	rm -rf $(DERIV)/_cache __pycache__ .pytest_cache .ruff_cache
