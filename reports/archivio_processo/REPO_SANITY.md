# Repository Sanity Check

**Generated**: 2026-05-01T07:06:00+02:00  
**Script**: `scripts/repo_sanity.sh`

---

## Broken Symlinks

✓ None found

---

## Empty Directories (excluding __pycache__)

11 empty directories detected (expected: git internal structures):

```
/data/eeg_matchingpennies/.git/objects/info
/data/eeg_matchingpennies/.git/branches
/data/eeg_matchingpennies/.git/annex/transfer/download/2a7781a5-9888-4b43-af06-b46a40d8a70f
/data/eeg_matchingpennies/.git/annex/tmp
/data/eeg_matchingpennies/.git/annex/journal
/data/eeg_matchingpennies/.git/refs/tags
.planning/archive
.git/objects/pack
.git/objects/info
.git/branches
.git/refs/tags
```

**Assessment**: ✓ All git-internal or archive-reserved. No orphan app directories.

---

## Files >100MB

4 large files detected (expected: BIDS dataset + derivatives):

| File | Size | Purpose |
|------|------|---------|
| `data/eeg_matchingpennies/sub-05/eeg/sub-05_task-matchingpennies_eeg.eeg` | ~373 MB | BIDS EEG raw data (BrainVision format) |
| `data/derivatives/mne-bids-pipeline/sub-05/eeg/sub-05_task-matchingpennies_proc-filt_raw.fif` | ~190 MB | Preprocessed EEG (after filtering/artifact rejection) |
| `.git/objects/9d/d4ab1...` | ~130 MB | Git object (compressed commit history) |
| `data/eeg_matchingpennies/.git/annex/objects/MJ/Q5/...` | ~373 MB | Git-annex object (dataset tracking) |

**Assessment**: ✓ All justified (BIDS data, derivatives, git tracking).

---

## Orphan __pycache__ Directories

17 __pycache__ directories detected (normal after test runs):

```
analysis, common, config, connectivity, dashboard, features, ml_training,
parcellation, pipeline_mne_bids, pipeline_mne_bids/bench,
pipeline_mne_bids/run_e2e, .planning, .planning/migrations, scripts,
source_reconstruction, tests
```

**Assessment**: ✓ Expected. Use `make clean` to remove before committing.

---

## Required Files

| File | Status |
|------|--------|
| README.md | ✓ |
| PROGRESS.md | ✓ |
| CONTRIBUTING.md | ✓ |
| pyproject.toml | ✓ |
| requirements.txt | ✓ |
| environment.yml | ✓ |
| .gitignore | ✓ |
| Makefile | ✓ |

**Assessment**: ✓ All 8 required files present.

---

## Summary

| Check | Result | Count | Status |
|-------|--------|-------|--------|
| Broken symlinks | Clean | 0 | ✓ |
| Empty dirs (non-git) | Clean | 0 | ✓ |
| Large files | Justified | 4 | ✓ |
| __pycache__ | Expected | 17 | ✓ |
| Required files | Complete | 8/8 | ✓ |

---

## Verdict

**✓ CLEAN** — Repository structure is sound. No broken references, missing required files, or orphan data.

**Recommendations**:
- Run `make clean` before committing to remove __pycache__ directories
- Data files (data/eeg_matchingpennies, derivatives) are properly git-ignored and tracked separately

---

*Repository sanity check: PASSED*
